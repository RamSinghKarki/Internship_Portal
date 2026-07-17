import cv2
import numpy as np

from app.ai.duplicate_detector import near_duplicate_groups
from app.utils.hashing import dhash, hamming


def _photo_like(seed: int, size: int = 256) -> np.ndarray:
    """Smooth random image — structured enough for stable dHashes."""
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 255, (size // 8, size // 8, 3), dtype=np.uint8)
    return cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)


def test_resized_copy_has_close_hash():
    img = _photo_like(1)
    small = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
    assert hamming(dhash(img), dhash(small)) <= 5


def test_different_images_have_distant_hashes():
    assert hamming(dhash(_photo_like(1)), dhash(_photo_like(2))) > 10


def test_grouping():
    img_a = _photo_like(1)
    img_a_small = cv2.resize(img_a, (100, 100), interpolation=cv2.INTER_AREA)
    img_b = _photo_like(2)

    items = [(1, dhash(img_a)), (2, dhash(img_a_small)), (3, dhash(img_b))]
    groups = near_duplicate_groups(items, max_distance=5)

    assert groups == [[1, 2]]
