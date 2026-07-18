"""Multi-threaded scan pipeline.

    walk folder -> [worker pool: decode, hash, EXIF, detect, embed] -> results

Workers are CPU-bound but OpenCV releases the GIL during inference, so
threads parallelize well without multiprocessing's serialization cost.
Model objects are NOT thread-safe, so each worker thread lazily creates
its own detector/recognizer pair (threading.local).

The pipeline only computes — all database writes happen in the single
consumer that iterates the generator (see ScanService), which keeps
SQLite happy with exactly one writer.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

from ..ai.ocr import ocr_available

from ..ai.detector import FaceDetector
from ..ai.quality import blur_score, quality_score
from ..ai.recognizer import FaceRecognizer
from ..config import IMAGE_EXTENSIONS, AppConfig
from ..utils.exif import extract_exif
from ..utils.hashing import dhash, load_image_bgr, sha256_file


@dataclass
class ProcessedFace:
    x: int
    y: int
    w: int
    h: int
    det_score: float
    blur: float
    quality: float
    embedding: bytes | None  # 128 x float32, L2-normalized


@dataclass
class ProcessedImage:
    path: str
    mtime: float
    size_bytes: int
    file_hash: str | None = None
    phash: str | None = None
    width: int | None = None
    height: int | None = None
    exif: dict = field(default_factory=dict)
    faces: list[ProcessedFace] = field(default_factory=list)
    clip_embedding: bytes | None = None
    ocr_text: str | None = None
    error: str | None = None


def discover_images(folder: Path) -> list[Path]:
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


class ScanPipeline:
    def __init__(self, config: AppConfig):
        self.config = config
        self._tls = threading.local()
        # One shared CLIP encoder — ONNX Runtime sessions are thread-safe
        # (unlike OpenCV DNN models, which stay thread-local).
        self._clip = None
        if config.semantic_available():
            from ..ai.semantic import ClipEncoder

            self._clip = ClipEncoder(
                config.clip_vision_model, config.clip_text_model, config.clip_tokenizer
            )
        # ArcFace (when installed) is also an ONNX session: one shared
        # instance. SFace stays per-thread (OpenCV DNN).
        self._arcface = None
        if config.active_recognition() == "arcface":
            from ..ai.arcface import ArcFaceRecognizer

            self._arcface = ArcFaceRecognizer(config.arcface_model)
        self._ocr = None
        if config.ocr_enabled and ocr_available():
            from ..ai.ocr import OcrEngine

            self._ocr = OcrEngine()

    def _models(self):
        if not hasattr(self._tls, "detector"):
            self._tls.detector = FaceDetector(
                self.config.detector_model,
                score_threshold=self.config.detection_score_threshold,
                mode=self.config.detection_mode,
            )
            self._tls.recognizer = (
                self._arcface
                if self._arcface is not None
                else FaceRecognizer(self.config.recognizer_model)
            )
        return self._tls.detector, self._tls.recognizer

    def process_one(self, path: Path) -> ProcessedImage:
        stat = path.stat()
        result = ProcessedImage(
            path=str(path), mtime=stat.st_mtime, size_bytes=stat.st_size
        )
        try:
            img = load_image_bgr(path)
            if img is None:
                result.error = "undecodable image"
                return result

            result.height, result.width = img.shape[:2]
            result.file_hash = sha256_file(path)
            result.phash = f"{dhash(img):016x}"
            result.exif = extract_exif(path)

            if self._clip is not None:
                emb = self._clip.embed_image(img)
                result.clip_embedding = emb.tobytes() if emb is not None else None

            if self._ocr is not None:
                result.ocr_text = self._ocr.extract_text(img)

            detector, recognizer = self._models()
            for det in detector.detect(img, min_face_size=self.config.min_face_size):
                x, y, w, h = det.box
                crop = img[y : y + h, x : x + w]
                blur = blur_score(crop)
                q = quality_score(det.score, blur, w, h)
                emb = recognizer.embed(img, det)
                result.faces.append(
                    ProcessedFace(
                        x=x, y=y, w=w, h=h,
                        det_score=det.score,
                        blur=round(blur, 2),
                        quality=q,
                        embedding=emb.tobytes() if emb is not None else None,
                    )
                )
        except Exception as exc:  # a single bad file must never kill a scan
            result.error = f"{type(exc).__name__}: {exc}"
        return result

    def run(
        self,
        paths: list[Path],
        progress: Callable[[int, int, str], None] | None = None,
        cancel: threading.Event | None = None,
    ) -> Iterator[ProcessedImage]:
        """Process paths across the worker pool, yielding results as they
        finish. Setting `cancel` stops promptly: queued work is dropped,
        in-flight images finish and are yielded (so they aren't lost)."""
        total = len(paths)
        done = 0
        pool = ThreadPoolExecutor(max_workers=self.config.worker_threads)
        try:
            futures = {pool.submit(self.process_one, p): p for p in paths}
            for fut in as_completed(futures):
                if cancel is not None and cancel.is_set():
                    break
                done += 1
                res = fut.result()
                if progress:
                    progress(done, total, res.path)
                yield res
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
