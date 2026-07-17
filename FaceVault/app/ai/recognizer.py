"""Face embeddings with SFace (OpenCV FaceRecognizerSF).

alignCrop uses the YuNet landmarks to warp the face to a canonical pose
before embedding — this is the "face alignment" stage of the pipeline.
Embeddings are L2-normalized on the way out so cosine similarity is a
plain dot product everywhere else in the codebase.
"""

from pathlib import Path

import cv2
import numpy as np

from .detector import Detection

EMBEDDING_DIM = 128


class FaceRecognizer:
    """One instance per thread — OpenCV DNN objects are not thread-safe."""

    def __init__(self, model_path: Path):
        self._rec = cv2.FaceRecognizerSF.create(str(model_path), "")

    def embed(self, image_bgr: np.ndarray, detection: Detection) -> np.ndarray | None:
        try:
            aligned = self._rec.alignCrop(image_bgr, detection.raw)
            feat = self._rec.feature(aligned).flatten().astype(np.float32)
        except cv2.error:
            return None
        norm = np.linalg.norm(feat)
        if norm == 0 or not np.isfinite(norm):
            return None
        return feat / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """For normalized embeddings this is just the dot product."""
    return float(np.dot(a, b))
