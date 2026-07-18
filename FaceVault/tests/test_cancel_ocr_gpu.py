"""Scan cancellation, OCR extraction/search, and GPU provider selection."""

import threading

import cv2
import numpy as np
import pytest

from app.ai.runtime import gpu_summary, ort_providers
from app.config import AppConfig
from app.database.session import create_session_factory
from app.services.scan_service import ScanService
from app.services.search_service import SearchService
from tests.test_e2e_scan import _find_portrait

portrait = _find_portrait()
needs_models = pytest.mark.skipif(
    portrait is None or not AppConfig().models_available(),
    reason="models or portrait fixture missing",
)


# ---- GPU provider selection -------------------------------------------
def test_provider_order_and_summary():
    providers = ort_providers()
    assert providers[-1] == "CPUExecutionProvider" or len(providers) == 1
    info = gpu_summary()
    assert info["active"] in providers
    assert isinstance(info["gpu"], bool)


# ---- cancellation ------------------------------------------------------
@needs_models
def test_scan_cancel_saves_partial_progress(tmp_path):
    lib = tmp_path / "photos"
    lib.mkdir()
    img = cv2.imread(str(portrait))
    for i in range(12):
        cv2.imwrite(str(lib / f"p{i}.jpg"),
                    cv2.convertScaleAbs(img, alpha=1 + i * 0.02))

    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ocr_enabled = False  # keep the timing predictable
    cfg.worker_threads = 2
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)

    cancel = threading.Event()
    seen = []

    def progress(done, total, path):
        seen.append(done)
        if done >= 3:
            cancel.set()

    summary = ScanService(cfg, factory).scan(lib, progress=progress,
                                             cancel_event=cancel)
    assert summary["cancelled"] is True
    # Some but not all images were ingested, and the DB matches.
    assert 0 < summary["new_images"] < 12
    from app.database.repository import Repository

    with factory() as session:
        stats = Repository(session).stats()
        assert stats["images"] == summary["new_images"]
        last = stats["last_scan"]
        assert last.status == "cancelled"

    # A follow-up scan finishes the remainder incrementally.
    summary2 = ScanService(cfg, factory).scan(lib)
    assert summary2["cancelled"] is False
    assert summary2["new_images"] + summary2["skipped"] == 12


# ---- OCR ---------------------------------------------------------------
def _text_image(text: str) -> np.ndarray:
    img = np.full((300, 900, 3), 245, np.uint8)
    cv2.putText(img, text, (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 2.4,
                (20, 20, 20), 6, cv2.LINE_AA)
    return img


ocr_missing = False
try:
    from app.ai.ocr import OcrEngine, ocr_available

    ocr_missing = not ocr_available()
except ImportError:
    ocr_missing = True


@pytest.mark.skipif(ocr_missing, reason="rapidocr-onnxruntime not installed")
def test_ocr_reads_rendered_text():
    engine = OcrEngine()
    text = engine.extract_text(_text_image("INVOICE 2026"))
    # The synthetic Hershey font confuses O/0, so assert on the digits and
    # a stable prefix rather than the exact word.
    assert text is not None
    assert "2026" in text and text.upper().startswith("INV")


@needs_models
@pytest.mark.skipif(ocr_missing, reason="rapidocr-onnxruntime not installed")
def test_scan_stores_ocr_and_text_search_finds_it(tmp_path):
    lib = tmp_path / "photos"
    lib.mkdir()
    cv2.imwrite(str(lib / "doc.jpg"), _text_image("PASSPORT 1234"))
    cv2.imwrite(str(lib / "person.jpg"), cv2.imread(str(portrait)))

    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    ScanService(cfg, factory).scan(lib)

    # Digits are read reliably even when the synthetic font trips letters.
    hits = SearchService(cfg, factory).search_images(text_contains="1234")
    assert len(hits) == 1
    assert hits[0].path.endswith("doc.jpg")
    assert "1234" in hits[0].ocr_text
