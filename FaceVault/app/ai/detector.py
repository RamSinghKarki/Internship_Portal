"""Face detection with YuNet (OpenCV FaceDetectorYN).

YuNet is a ~230 KB ONNX model that runs in a few ms per image on CPU —
no GPU, no network. Each detection keeps the raw 15-element row because
SFace's alignCrop needs the 5 landmark points from it.

Two modes:

  fast      one pass at <=1280 px — the right default for huge libraries.
  accurate  multi-pass refinement, still fully offline (~3x slower):
              - higher detection resolution (<=1920 px) for small faces
              - 2x upscale of low-resolution images
              - CLAHE contrast pass to recover dark / backlit faces
              - horizontally mirrored pass to recover profile faces
            Passes are merged with IoU de-duplication, keeping the
            highest-confidence detection of each face.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

# YuNet row layout: x, y, w, h, then landmark pairs
# (right eye, left eye, nose, right mouth corner, left mouth corner), score.
_MERGE_IOU = 0.4


@dataclass
class Detection:
    box: tuple[int, int, int, int]  # x, y, w, h (clamped to image bounds)
    score: float
    raw: np.ndarray  # full YuNet row, needed for SFace alignment


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    ax, ay, aw, ah = a[:4]
    bx, by, bw, bh = b[:4]
    x1, y1 = max(ax, bx), max(ay, by)
    x2, y2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _mirror_row(row: np.ndarray, width: int) -> np.ndarray:
    """Map a detection on the horizontally flipped image back to the
    original: mirror x coordinates and swap left/right landmark pairs."""
    r = row.copy()
    r[0] = width - row[0] - row[2]  # box x
    r[8] = width - row[8]  # nose x
    # The flipped image's "right eye" is anatomically the left eye in the
    # original, so mirrored pairs also swap slots (same for mouth corners).
    r[4], r[5] = width - row[6], row[7]
    r[6], r[7] = width - row[4], row[5]
    r[10], r[11] = width - row[12], row[13]
    r[12], r[13] = width - row[10], row[11]
    return r


def _clahe(img: np.ndarray) -> np.ndarray:
    """Adaptive contrast enhancement on luminance only — recovers faces
    in underexposed or backlit photos without shifting colors."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)
    l_chan = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(l_chan)
    return cv2.cvtColor(cv2.merge((l_chan, a_chan, b_chan)), cv2.COLOR_LAB2BGR)


class FaceDetector:
    """One instance per thread — OpenCV DNN objects are not thread-safe."""

    def __init__(self, model_path: Path, score_threshold: float = 0.65,
                 nms_threshold: float = 0.3, mode: str = "fast"):
        self.mode = mode
        self._det = cv2.FaceDetectorYN.create(
            str(model_path), "", (320, 320), score_threshold, nms_threshold, 5000
        )

    def _run(self, img: np.ndarray) -> list[np.ndarray]:
        """One YuNet pass; rows are in `img` coordinates."""
        self._det.setInputSize((img.shape[1], img.shape[0]))
        _, faces = self._det.detect(img)
        return [] if faces is None else [row for row in faces]

    def detect(self, image_bgr: np.ndarray, min_face_size: int = 0) -> list[Detection]:
        h, w = image_bgr.shape[:2]
        if h < 20 or w < 20:
            return []
        accurate = self.mode == "accurate"

        # Choose the working resolution. YuNet degrades on very large
        # inputs; conversely tiny images benefit from upscaling.
        max_side = 1920 if accurate else 1280
        scale = 1.0
        if max(h, w) > max_side:
            scale = max_side / max(h, w)
        elif accurate and max(h, w) < 480:
            scale = 2.0
        base = image_bgr
        if scale != 1.0:
            interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            base = cv2.resize(image_bgr, (int(w * scale), int(h * scale)),
                              interpolation=interp)

        rows = self._run(base)
        if accurate:
            rows += self._run(_clahe(base))
            bw = base.shape[1]
            rows += [_mirror_row(r, bw) for r in self._run(cv2.flip(base, 1))]
            rows = self._merge(rows)

        out: list[Detection] = []
        for row in rows:
            r = row.copy()
            r[:14] /= scale  # map box + landmarks back to original coords
            x, y, fw, fh = (int(v) for v in r[:4])
            x, y = max(0, x), max(0, y)
            fw, fh = min(int(fw), w - x), min(int(fh), h - y)
            if fw < min_face_size or fh < min_face_size:
                continue
            out.append(Detection(box=(x, y, fw, fh), score=float(row[14]), raw=r))
        return out

    @staticmethod
    def _merge(rows: list[np.ndarray]) -> list[np.ndarray]:
        """De-duplicate detections from multiple passes: greedy NMS keeping
        the highest-confidence row per physical face."""
        rows = sorted(rows, key=lambda r: -r[14])
        kept: list[np.ndarray] = []
        for row in rows:
            if all(_iou(row, k) < _MERGE_IOU for k in kept):
                kept.append(row)
        return kept
