"""ArcFace face recognition (optional accuracy upgrade over SFace).

InsightFace's w600k_r50 ArcFace model produces 512-d embeddings that
separate look-alike people far better than SFace's 128-d — this is the
model to use when different-but-similar people keep getting merged.

The model (~166 MB) is too large to ship in the repo; fetch it once with
`python models/download_models.py --arcface`. When the file exists,
FaceVault uses it automatically for all new scans (re-run a full scan so
every face is re-embedded by the same model: `python -m app scan FOLDER
--full`).

Runs on ONNX Runtime — shared session, thread-safe, CUDA auto-detected.
"""

from pathlib import Path

import cv2
import numpy as np

from .detector import Detection

try:
    import onnxruntime as ort

    _HAS_ORT = True
except ImportError:
    _HAS_ORT = False

ARCFACE_DIM = 512

# Canonical 5-point template (112x112) used by every ArcFace model,
# ordered image-left eye, image-right eye, nose, image-left mouth
# corner, image-right mouth corner — matching YuNet's landmark order.
_ARCFACE_DST = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


def arcface_runtime_available() -> bool:
    return _HAS_ORT


class ArcFaceRecognizer:
    """Thread-safe (ONNX Runtime sessions may be shared across threads)."""

    dim = ARCFACE_DIM

    def __init__(self, model_path: Path):
        if not _HAS_ORT:
            raise RuntimeError("ArcFace needs: pip install onnxruntime")
        from .runtime import ort_providers

        self._session = ort.InferenceSession(str(model_path), providers=ort_providers())
        self._input = self._session.get_inputs()[0].name

    @staticmethod
    def _align(image_bgr: np.ndarray, detection: Detection) -> np.ndarray | None:
        """Similarity-transform the face to the canonical 112x112 pose
        using the detector's 5 landmarks."""
        src = detection.raw[4:14].reshape(5, 2).astype(np.float32)
        matrix, _ = cv2.estimateAffinePartial2D(src, _ARCFACE_DST, method=cv2.LMEDS)
        if matrix is None:
            return None
        return cv2.warpAffine(image_bgr, matrix, (112, 112))

    def embed(self, image_bgr: np.ndarray, detection: Detection) -> np.ndarray | None:
        aligned = self._align(image_bgr, detection)
        if aligned is None:
            return None
        rgb = cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB).astype(np.float32)
        blob = ((rgb - 127.5) / 127.5).transpose(2, 0, 1)[None]
        (feat,) = self._session.run(None, {self._input: blob})
        vec = feat.flatten().astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0 or not np.isfinite(norm):
            return None
        return vec / norm
