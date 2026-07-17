import cv2
import numpy as np

from app.ai.quality import blur_score, quality_score


def _textured(size: int = 160) -> np.ndarray:
    rng = np.random.default_rng(3)
    return rng.integers(0, 255, (size, size, 3), dtype=np.uint8)


def test_blur_reduces_score():
    sharp = _textured()
    blurred = cv2.GaussianBlur(sharp, (15, 15), 6)
    assert blur_score(sharp) > blur_score(blurred) * 5


def test_quality_bounds_and_ordering():
    good = quality_score(det_score=0.95, blur=400, face_w=200, face_h=200)
    bad = quality_score(det_score=0.66, blur=20, face_w=40, face_h=40)
    assert 0 <= bad < good <= 100


def test_empty_crop_is_zero():
    assert blur_score(np.zeros((0, 0, 3), dtype=np.uint8)) == 0.0
