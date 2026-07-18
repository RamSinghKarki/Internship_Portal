"""Non-destructive photo editing operations.

Google-Photos semantics: every save produces a COPY next to the
original (`name_edited.jpg`, `name_edited_2.jpg`, …) — originals are
never modified. All ops are pure functions over BGR arrays.
"""

from pathlib import Path

import cv2
import numpy as np


def rotate90(img: np.ndarray, clockwise: bool = True) -> np.ndarray:
    return cv2.rotate(
        img, cv2.ROTATE_90_CLOCKWISE if clockwise else cv2.ROTATE_90_COUNTERCLOCKWISE
    )


def flip_horizontal(img: np.ndarray) -> np.ndarray:
    return cv2.flip(img, 1)


def crop(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    ih, iw = img.shape[:2]
    x, y = max(0, x), max(0, y)
    w, h = min(w, iw - x), min(h, ih - y)
    if w < 8 or h < 8:
        return img  # refuse degenerate crops
    return img[y:y + h, x:x + w].copy()


def adjust(img: np.ndarray, brightness: int = 0, contrast: int = 0,
           saturation: int = 0) -> np.ndarray:
    """Each parameter in [-100, 100]; 0 = unchanged."""
    out = img.astype(np.float32)
    if contrast:
        factor = 1.0 + contrast / 100.0
        out = (out - 127.5) * factor + 127.5
    if brightness:
        out += brightness * 1.27
    out = np.clip(out, 0, 255).astype(np.uint8)
    if saturation:
        hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + saturation / 100.0), 0, 255)
        out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return out


def auto_enhance(img: np.ndarray) -> np.ndarray:
    """One-click enhance: adaptive contrast on luminance + gentle saturation."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)
    l_chan = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l_chan)
    out = cv2.cvtColor(cv2.merge((l_chan, a_chan, b_chan)), cv2.COLOR_LAB2BGR)
    return adjust(out, saturation=12)


def save_copy(original_path: Path, img: np.ndarray) -> Path:
    """Write the edit as a sibling JPEG copy, never overwriting anything."""
    original_path = Path(original_path)
    base = original_path.with_name(f"{original_path.stem}_edited.jpg")
    n = 2
    while base.exists():
        base = original_path.with_name(f"{original_path.stem}_edited_{n}.jpg")
        n += 1
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise IOError("Failed to encode edited image")
    base.write_bytes(buf.tobytes())
    return base
