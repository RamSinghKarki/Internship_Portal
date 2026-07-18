"""Semantic search tests — skipped unless the CLIP models are installed."""

import cv2
import numpy as np
import pytest

from app.config import AppConfig
from app.database.session import create_session_factory
from app.services.scan_service import ScanService
from app.services.search_service import SearchService
from tests.test_e2e_scan import _find_portrait

portrait = _find_portrait()
_cfg = AppConfig()

pytestmark = [
    pytest.mark.skipif(portrait is None, reason="no portrait fixture available"),
    pytest.mark.skipif(not _cfg.models_available(), reason="face models missing"),
    pytest.mark.skipif(not _cfg.semantic_available(), reason="CLIP models missing"),
]


def test_text_image_alignment():
    from app.ai.semantic import ClipEncoder

    enc = ClipEncoder(_cfg.clip_vision_model, _cfg.clip_text_model, _cfg.clip_tokenizer)
    img = cv2.imread(str(portrait))
    img_vec = enc.embed_image(img)
    assert img_vec is not None and img_vec.shape == (512,)
    assert abs(np.linalg.norm(img_vec) - 1.0) < 1e-5

    relevant = enc.embed_text("a photo of a person")
    irrelevant = enc.embed_text("a spreadsheet of quarterly numbers")
    assert float(img_vec @ relevant) > float(img_vec @ irrelevant)


def test_scan_embeds_and_semantic_search_ranks(tmp_path):
    lib = tmp_path / "photos"
    lib.mkdir()
    img = cv2.imread(str(portrait))
    cv2.imwrite(str(lib / "person.jpg"), img)
    # A synthetic non-person image for contrast.
    grad = np.linspace(0, 255, 400, dtype=np.uint8)
    pattern = cv2.applyColorMap(np.tile(grad, (400, 1)), cv2.COLORMAP_JET)
    cv2.imwrite(str(lib / "pattern.jpg"), pattern)

    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    ScanService(cfg, factory).scan(lib)

    search = SearchService(cfg, factory)
    # Discriminative queries must rank the right image first, both ways.
    hits = search.semantic_search("a portrait photograph of a woman", min_score=0.0)
    assert hits, "semantic index should be populated during scan"
    assert hits[0][0].path.endswith("person.jpg")

    hits = search.semantic_search("a rainbow gradient", min_score=0.0)
    assert hits[0][0].path.endswith("pattern.jpg")
