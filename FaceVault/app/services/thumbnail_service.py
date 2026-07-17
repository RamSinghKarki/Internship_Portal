"""Thumbnail generation with a content-addressed disk cache.

Cache keys derive from (path, mtime, size) so edited files regenerate
automatically while unchanged files are never re-encoded.
"""

import hashlib
from pathlib import Path

import cv2

from ..config import AppConfig
from ..utils.hashing import load_image_bgr


class ThumbnailService:
    def __init__(self, config: AppConfig):
        self.config = config
        config.ensure_dirs()

    def _cache_key(self, path: Path, suffix: str) -> str:
        try:
            st = path.stat()
            raw = f"{path}|{st.st_mtime}|{st.st_size}|{suffix}"
        except OSError:
            raw = f"{path}|{suffix}"
        return hashlib.sha1(raw.encode()).hexdigest() + ".jpg"

    def image_thumbnail(self, path: str | Path) -> Path | None:
        """Return a cached thumbnail path for an image, creating it if needed."""
        path = Path(path)
        out = self.config.thumbs_dir / self._cache_key(path, "thumb")
        if out.is_file():
            return out
        img = load_image_bgr(path)
        if img is None:
            return None
        h, w = img.shape[:2]
        side = self.config.thumbnail_size
        if max(h, w) > side:
            scale = side / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)),
                             interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            return None
        out.write_bytes(buf.tobytes())
        return out

    def face_thumbnail(self, image_path: str | Path,
                       box: tuple[int, int, int, int], face_id: int) -> Path | None:
        """Return a cached crop of one face (used as person covers)."""
        out = self.config.faces_dir / f"face_{face_id}.jpg"
        if out.is_file():
            return out
        img = load_image_bgr(Path(image_path))
        if img is None:
            return None
        x, y, w, h = box
        # Pad the crop 25% so covers show a bit of context around the face.
        pad_x, pad_y = int(w * 0.25), int(h * 0.25)
        ih, iw = img.shape[:2]
        x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
        x1, y1 = min(iw, x + w + pad_x), min(ih, y + h + pad_y)
        crop = img[y0:y1, x0:x1]
        if crop.size == 0:
            return None
        side = self.config.face_thumbnail_size
        crop = cv2.resize(crop, (side, side), interpolation=cv2.INTER_AREA)
        ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            return None
        out.write_bytes(buf.tobytes())
        return out
