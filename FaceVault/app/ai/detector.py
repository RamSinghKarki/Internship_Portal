"""Face detection with YuNet (OpenCV FaceDetectorYN).

YuNet is a ~230 KB ONNX model that runs in a few ms per image on CPU —
no GPU, no network. Each detection keeps the raw 15-element row because
SFace's alignCrop needs the 5 landmark points from it.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Detection:
    box: tuple[int, int, int, int]  # x, y, w, h (clamped to image bounds)
    score: float
    raw: np.ndarray  # full YuNet row, needed for SFace alignment


class FaceDetector:
    """One instance per thread — OpenCV DNN objects are not thread-safe."""

    def __init__(self, model_path: Path, score_threshold: float = 0.65,
                 nms_threshold: float = 0.3):
        self._det = cv2.FaceDetectorYN.create(
            str(model_path), "", (320, 320), score_threshold, nms_threshold, 5000
        )

    def detect(self, image_bgr: np.ndarray, min_face_size: int = 0) -> list[Detection]:
        h, w = image_bgr.shape[:2]
        if h < 20 or w < 20:
            return []

        # YuNet degrades on very large inputs; downscale for detection and
        # map boxes back to the original resolution.
        scale = 1.0
        max_side = 1280
        img = image_bgr
        if max(h, w) > max_side:
            scale = max_side / max(h, w)
            img = cv2.resize(image_bgr, (int(w * scale), int(h * scale)),
                             interpolation=cv2.INTER_AREA)

        self._det.setInputSize((img.shape[1], img.shape[0]))
        _, faces = self._det.detect(img)
        if faces is None:
            return []

        out: list[Detection] = []
        for row in faces:
            r = row.copy()
            r[:14] /= scale  # rescale box + 5 landmark pairs to original coords
            x, y, fw, fh = (int(v) for v in r[:4])
            x, y = max(0, x), max(0, y)
            fw, fh = min(fw, w - x), min(fh, h - y)
            if fw < min_face_size or fh < min_face_size:
                continue
            out.append(Detection(box=(x, y, fw, fh), score=float(row[14]), raw=r))
        return out
