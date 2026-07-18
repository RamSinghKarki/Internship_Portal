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

# Semantic search (optional): quantized CLIP ViT-B/32, ~155 MB total.
CLIP_BASE = "https://huggingface.co/Xenova/clip-vit-base-patch32/resolve/main/"
CLIP_MODELS = {
    "clip_vision.onnx": CLIP_BASE + "onnx/vision_model_quantized.onnx",
    "clip_text.onnx": CLIP_BASE + "onnx/text_model_quantized.onnx",
    "clip_tokenizer.json": CLIP_BASE + "tokenizer.json",
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


def fetch_url(name: str, url: str) -> bool:
    dest = MODELS_DIR / name
    if dest.is_file() and dest.stat().st_size > 10_000:
        print(f"already present: {name}")
        return True
    try:
        print(f"downloading {name} …")
        urllib.request.urlretrieve(url, dest)
        print(f"  ok ({dest.stat().st_size / 1e6:.1f} MB)")
        return True
    except OSError as exc:
        print(f"  failed: {exc}")
        return False


def main() -> int:
    ok = all(fetch(name, rel) for name, rel in MODELS.items())
    clip_ok = all(fetch_url(name, url) for name, url in CLIP_MODELS.items())
    if not ok:
        print("Face models could not be downloaded.", file=sys.stderr)
        return 1
    if not clip_ok:
        print("CLIP models failed — semantic search will stay disabled; "
              "everything else works.", file=sys.stderr)
    print("Models ready — FaceVault is fully offline from here on.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
