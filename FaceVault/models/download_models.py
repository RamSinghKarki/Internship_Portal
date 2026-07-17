"""One-time model fetcher (only needed if the committed models are missing).

After this completes, FaceVault never touches the network again.
"""

import sys
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent

MODELS = {
    "face_detection_yunet_2023mar.onnx": (
        "face_detection_yunet/face_detection_yunet_2023mar.onnx"
    ),
    "face_recognition_sface_2021dec.onnx": (
        "face_recognition_sface/face_recognition_sface_2021dec.onnx"
    ),
}

# opencv_zoo stores models in Git LFS; media.githubusercontent serves the
# real bytes while raw.githubusercontent may return an LFS pointer stub.
MIRRORS = [
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/",
    "https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/",
]


def fetch(name: str, rel_path: str) -> bool:
    dest = MODELS_DIR / name
    if dest.is_file() and dest.stat().st_size > 10_000:
        print(f"already present: {name}")
        return True
    for base in MIRRORS:
        url = base + rel_path
        try:
            print(f"downloading {name} …")
            urllib.request.urlretrieve(url, dest)
            if dest.stat().st_size > 10_000:  # LFS pointer stubs are ~130 bytes
                print(f"  ok ({dest.stat().st_size / 1e6:.1f} MB)")
                return True
            dest.unlink()
        except OSError as exc:
            print(f"  failed from {base}: {exc}")
    return False


def main() -> int:
    ok = all(fetch(name, rel) for name, rel in MODELS.items())
    if not ok:
        print("Some models could not be downloaded.", file=sys.stderr)
        return 1
    print("All models ready — FaceVault is fully offline from here on.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
