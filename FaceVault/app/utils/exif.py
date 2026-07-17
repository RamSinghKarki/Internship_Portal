"""EXIF metadata extraction via Pillow (no external exiftool dependency)."""

from datetime import datetime
from pathlib import Path

from PIL import Image, ExifTags

Image.MAX_IMAGE_PIXELS = None  # trust local files; avoid DecompressionBomb errors

_TAGS = {v: k for k, v in ExifTags.TAGS.items()}
_GPS_TAGS = {v: k for k, v in ExifTags.GPSTAGS.items()}


def _to_degrees(value) -> float:
    d, m, s = (float(x) for x in value)
    return d + m / 60.0 + s / 3600.0


def extract_exif(path: Path) -> dict:
    """Return camera/lens/timestamp/GPS metadata; missing fields are None."""
    out = {"camera": None, "lens": None, "taken_at": None, "gps_lat": None, "gps_lon": None}
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            if not exif:
                return out

            make = exif.get(_TAGS.get("Make"))
            model = exif.get(_TAGS.get("Model"))
            if make or model:
                make, model = (make or "").strip(), (model or "").strip()
                # Many cameras repeat the make inside the model string.
                out["camera"] = model if make and model.startswith(make) else f"{make} {model}".strip()

            ifd = exif.get_ifd(ExifTags.IFD.Exif)
            out["lens"] = (ifd.get(_TAGS.get("LensModel")) or None) and str(
                ifd[_TAGS["LensModel"]]
            ).strip()

            dt = ifd.get(_TAGS.get("DateTimeOriginal")) or exif.get(_TAGS.get("DateTime"))
            if dt:
                try:
                    out["taken_at"] = datetime.strptime(str(dt), "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass

            gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if gps:
                lat, lat_ref = gps.get(_GPS_TAGS["GPSLatitude"]), gps.get(_GPS_TAGS["GPSLatitudeRef"])
                lon, lon_ref = gps.get(_GPS_TAGS["GPSLongitude"]), gps.get(_GPS_TAGS["GPSLongitudeRef"])
                if lat and lon:
                    out["gps_lat"] = _to_degrees(lat) * (-1 if lat_ref == "S" else 1)
                    out["gps_lon"] = _to_degrees(lon) * (-1 if lon_ref == "W" else 1)
    except (OSError, ValueError, KeyError, TypeError):
        pass  # unreadable/malformed EXIF must never break a scan
    return out


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with Image.open(path) as im:
            return im.width, im.height
    except OSError:
        return None, None
