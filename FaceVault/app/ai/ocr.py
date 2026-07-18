"""OCR — extract text from photos so documents become searchable.

Uses RapidOCR (PP-OCRv4 models bundled inside the pip package, ONNX
Runtime under the hood) — fully offline, nothing to download. Makes
passports, invoices, certificates, receipts and screenshots findable by
their text. Latin scripts + Chinese out of the box.

Optional: everything works without it. Enabled automatically when
`pip install rapidocr-onnxruntime` is present.
"""

import threading

import numpy as np

try:
    from rapidocr_onnxruntime import RapidOCR

    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False

# Skip text fragments the model is unsure about — noise pollutes search.
_MIN_CONFIDENCE = 0.65


def ocr_available() -> bool:
    return _HAS_OCR


class OcrEngine:
    """Shared engine guarded by a lock (RapidOCR isn't documented as
    thread-safe; OCR is the slowest pipeline step anyway)."""

    def __init__(self):
        if not _HAS_OCR:
            raise RuntimeError("OCR needs: pip install rapidocr-onnxruntime")
        self._engine = RapidOCR()
        self._lock = threading.Lock()

    def extract_text(self, image_bgr: np.ndarray) -> str | None:
        with self._lock:
            result, _elapsed = self._engine(image_bgr)
        if not result:
            return None
        lines = [text for _box, text, score in result if float(score) >= _MIN_CONFIDENCE]
        joined = "\n".join(lines).strip()
        return joined or None
