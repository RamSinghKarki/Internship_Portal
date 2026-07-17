"""Content and perceptual hashing.

Two distinct hashes serve two distinct features:
  - sha256: byte-exact duplicates (same file stored twice).
  - dHash:  near-duplicates (resized/re-encoded/lightly edited copies).
"""

import hashlib
from pathlib import Path

import cv2
import numpy as np


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def dhash(image_bgr: np.ndarray, hash_size: int = 8) -> int:
    """64-bit difference hash: robust to resizing and re-compression."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    return int(sum(1 << i for i, v in enumerate(diff.flatten()) if v))


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def load_image_bgr(path: Path) -> np.ndarray | None:
    """Decode an image, tolerating non-ASCII paths (cv2.imread cannot)."""
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except (OSError, ValueError):
        return None
