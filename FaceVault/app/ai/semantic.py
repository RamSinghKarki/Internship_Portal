"""Semantic (natural-language) photo search with a local CLIP model.

CLIP maps images and text into the same 512-d space, so "sunset at the
beach" can be compared directly against every photo — fully offline,
via ONNX Runtime (quantized ViT-B/32, ~150 MB total).

GPU: if onnxruntime-gpu is installed (NVIDIA CUDA), the CUDA execution
provider is picked up automatically; otherwise CPU is used. Both give
identical results — GPU is just faster on large libraries.
"""

from pathlib import Path

import cv2
import numpy as np

try:
    import onnxruntime as ort
    from tokenizers import Tokenizer

    _HAS_RUNTIME = True
except ImportError:
    _HAS_RUNTIME = False

CLIP_DIM = 512
_MEAN = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
_STD = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)


def runtime_available() -> bool:
    return _HAS_RUNTIME


def _providers() -> list[str]:
    from .runtime import ort_providers

    return ort_providers()


class ClipEncoder:
    """Thread-safe: ONNX Runtime sessions may be shared across threads."""

    def __init__(self, vision_path: Path, text_path: Path, tokenizer_path: Path):
        if not _HAS_RUNTIME:
            raise RuntimeError(
                "Semantic search needs: pip install onnxruntime tokenizers"
            )
        providers = _providers()
        self.vision = ort.InferenceSession(str(vision_path), providers=providers)
        self.text = ort.InferenceSession(str(text_path), providers=providers)
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.active_provider = self.vision.get_providers()[0]

    # ---- images -------------------------------------------------------
    @staticmethod
    def _preprocess(image_bgr: np.ndarray) -> np.ndarray:
        """CLIP preprocessing: shortest side to 224, center crop, normalize."""
        h, w = image_bgr.shape[:2]
        scale = 224 / min(h, w)
        resized = cv2.resize(image_bgr, (round(w * scale), round(h * scale)),
                             interpolation=cv2.INTER_CUBIC)
        rh, rw = resized.shape[:2]
        top, left = (rh - 224) // 2, (rw - 224) // 2
        crop = resized[top:top + 224, left:left + 224]
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        rgb = (rgb - _MEAN) / _STD
        return rgb.transpose(2, 0, 1)[None]  # 1 x 3 x 224 x 224

    def embed_image(self, image_bgr: np.ndarray) -> np.ndarray | None:
        if image_bgr is None or min(image_bgr.shape[:2]) < 8:
            return None
        (embeds,) = self.vision.run(None, {"pixel_values": self._preprocess(image_bgr)})
        vec = embeds[0].astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else None

    # ---- text ---------------------------------------------------------
    def embed_text(self, text: str) -> np.ndarray:
        ids = self.tokenizer.encode(text).ids[:77]  # CLIP context limit
        input_ids = np.array([ids], dtype=np.int64)
        (embeds,) = self.text.run(None, {"input_ids": input_ids})
        vec = embeds[0].astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
