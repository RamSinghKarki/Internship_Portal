"""Application configuration.

Configuration precedence: explicit kwargs > environment variables > defaults.
Everything lives under a single data directory so the whole library
(DB + caches) can be backed up or moved as one unit.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


@dataclass
class AppConfig:
    # Storage
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("FACEVAULT_DATA_DIR", Path.home() / ".facevault")
        )
    )
    models_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("FACEVAULT_MODELS_DIR", PROJECT_ROOT / "models")
        )
    )

    # AI thresholds
    # Cosine similarity above which two SFace embeddings are considered the
    # same person. 0.363 is the OpenCV-published verification threshold; we
    # default slightly higher to favour precision when auto-grouping.
    match_threshold: float = 0.40
    # A face is auto-assigned only when its best person match beats the
    # runner-up by this cosine margin. Two look-alike people produce close
    # scores — such faces go to Unknown for human review instead of being
    # guessed, which is how different-but-similar people stop merging.
    match_margin: float = 0.06
    # "auto" uses ArcFace (512-d, much better look-alike separation) when
    # models/arcface_w600k_r50.onnx exists, else SFace. Can be pinned to
    # "sface" or "arcface". After switching models run `scan --full` so
    # every face is re-embedded consistently.
    recognition_model: str = "auto"
    # Faces below this composite quality score (0-100) are stored but not
    # used for clustering, so blurry/tiny faces don't pollute person groups.
    min_cluster_quality: float = 40.0
    detection_score_threshold: float = 0.65
    # "fast": one detection pass. "accurate": multi-pass refinement
    # (higher resolution + contrast-enhanced + mirrored passes, merged) —
    # catches small, dark and profile faces at ~3x the scan cost.
    detection_mode: str = "accurate"
    min_face_size: int = 36  # px, smaller detections are ignored
    min_cluster_size: int = 2  # faces needed to auto-create a person
    # Hamming distance (on 64-bit dHash) at or below which two images are
    # flagged as near-duplicates.
    near_duplicate_distance: int = 5

    # Extract text from photos during scans (searchable documents).
    # Auto-disabled when rapidocr-onnxruntime isn't installed.
    ocr_enabled: bool = True
    # Auto-tag photos with detected objects (dog, car, laptop, …).
    objects_enabled: bool = True

    # Processing
    worker_threads: int = max(2, (os.cpu_count() or 4) - 1)
    write_batch_size: int = 32

    # Thumbnails
    thumbnail_size: int = 512
    face_thumbnail_size: int = 160

    @property
    def db_path(self) -> Path:
        return self.data_dir / "facevault.db"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def thumbs_dir(self) -> Path:
        return self.cache_dir / "thumbs"

    @property
    def faces_dir(self) -> Path:
        return self.cache_dir / "faces"

    @property
    def detector_model(self) -> Path:
        return self.models_dir / "face_detection_yunet_2023mar.onnx"

    @property
    def recognizer_model(self) -> Path:
        return self.models_dir / "face_recognition_sface_2021dec.onnx"

    @property
    def arcface_model(self) -> Path:
        return self.models_dir / "arcface_w600k_r50.onnx"

    @property
    def objects_model(self) -> Path:
        return self.models_dir / "yolo_objects.onnx"

    def objects_available(self) -> bool:
        try:
            from .ai.objects import objects_runtime_available
        except ImportError:
            return False
        return objects_runtime_available() and self.objects_model.is_file()

    def active_recognition(self) -> str:
        """Which face-embedding model scans will use: 'arcface' or 'sface'."""
        if self.recognition_model == "sface":
            return "sface"
        try:
            from .ai.arcface import arcface_runtime_available
        except ImportError:
            return "sface"
        arcface_ok = arcface_runtime_available() and self.arcface_model.is_file()
        if self.recognition_model == "arcface":
            if not arcface_ok:
                raise FileNotFoundError(
                    "recognition_model is pinned to 'arcface' but the model is "
                    "missing — run: python models/download_models.py --arcface"
                )
            return "arcface"
        return "arcface" if arcface_ok else "sface"  # auto

    @property
    def embedding_dim(self) -> int:
        return 512 if self.active_recognition() == "arcface" else 128

    @property
    def clip_vision_model(self) -> Path:
        return self.models_dir / "clip_vision.onnx"

    @property
    def clip_text_model(self) -> Path:
        return self.models_dir / "clip_text.onnx"

    @property
    def clip_tokenizer(self) -> Path:
        return self.models_dir / "clip_tokenizer.json"

    def semantic_available(self) -> bool:
        """Semantic search is optional: needs the CLIP models on disk plus
        the onnxruntime + tokenizers packages."""
        try:
            from .ai.semantic import runtime_available
        except ImportError:
            return False
        return (
            runtime_available()
            and self.clip_vision_model.is_file()
            and self.clip_text_model.is_file()
            and self.clip_tokenizer.is_file()
        )

    @property
    def settings_file(self) -> Path:
        return self.data_dir / "settings.json"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.cache_dir, self.thumbs_dir, self.faces_dir):
            d.mkdir(parents=True, exist_ok=True)

    def models_available(self) -> bool:
        return self.detector_model.is_file() and self.recognizer_model.is_file()

    # Tunable settings persist as JSON so the GUI settings page and CLI
    # share them across runs. Paths are intentionally not persisted.
    _PERSISTED = (
        "match_threshold",
        "match_margin",
        "recognition_model",
        "min_cluster_quality",
        "detection_score_threshold",
        "detection_mode",
        "min_face_size",
        "min_cluster_size",
        "near_duplicate_distance",
        "worker_threads",
        "ocr_enabled",
        "objects_enabled",
    )

    def save(self) -> None:
        self.ensure_dirs()
        data = {k: getattr(self, k) for k in self._PERSISTED}
        self.settings_file.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, data_dir: Path | None = None) -> "AppConfig":
        cfg = cls() if data_dir is None else cls(data_dir=Path(data_dir))
        if cfg.settings_file.is_file():
            try:
                stored = json.loads(cfg.settings_file.read_text())
                for k in cls._PERSISTED:
                    if k in stored:
                        setattr(cfg, k, stored[k])
            except (json.JSONDecodeError, OSError):
                pass  # corrupt settings fall back to defaults
        return cfg

    def as_dict(self) -> dict:
        d = asdict(self)
        d["data_dir"] = str(self.data_dir)
        d["models_dir"] = str(self.models_dir)
        return d
