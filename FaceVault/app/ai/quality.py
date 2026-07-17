"""Face quality scoring.

A composite 0-100 score gates which faces participate in clustering:
blurry or tiny faces produce unreliable embeddings that smear person
clusters together, so they are stored but excluded from grouping.
"""

import cv2
import numpy as np


def blur_score(face_crop_bgr: np.ndarray) -> float:
    """Variance of the Laplacian — higher is sharper. ~<60 is visibly blurry."""
    if face_crop_bgr.size == 0:
        return 0.0
    gray = cv2.cvtColor(face_crop_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def quality_score(det_score: float, blur: float, face_w: int, face_h: int) -> float:
    """Composite quality in [0, 100].

    Weights: detector confidence 40%, sharpness 35%, resolution 25%.
    Sharpness saturates at Laplacian variance 300, resolution at 160 px.
    """
    conf = float(np.clip(det_score, 0.0, 1.0))
    sharp = float(np.clip(blur / 300.0, 0.0, 1.0))
    size = float(np.clip(min(face_w, face_h) / 160.0, 0.0, 1.0))
    return round(100.0 * (0.40 * conf + 0.35 * sharp + 0.25 * size), 2)
