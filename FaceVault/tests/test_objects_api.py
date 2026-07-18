"""Object detection tags and the REST search API."""

import cv2
import pytest

from app.config import AppConfig
from app.database.session import create_session_factory
from app.services.scan_service import ScanService
from app.services.search_service import SearchService
from tests.test_e2e_scan import _find_portrait

portrait = _find_portrait()
_cfg = AppConfig()

needs_models = pytest.mark.skipif(
    portrait is None or not _cfg.models_available(),
    reason="models or portrait fixture missing",
)
needs_objects = pytest.mark.skipif(
    not _cfg.objects_available(), reason="YOLO objects model missing"
)

try:
    from fastapi.testclient import TestClient

    from app.api.server import create_app

    _HAS_API = True
except ImportError:
    _HAS_API = False

needs_api = pytest.mark.skipif(not _HAS_API, reason="fastapi not installed")


@needs_objects
def test_object_detector_finds_person():
    from app.ai.objects import ObjectDetector

    det = ObjectDetector(_cfg.objects_model)
    if portrait is None:
        pytest.skip("no portrait fixture")
    labels = dict(det.detect(cv2.imread(str(portrait))))
    assert "person" in labels
    assert labels["person"] >= 0.35


@needs_models
@needs_objects
def test_scan_stores_tags_and_tag_search(tmp_path):
    lib = tmp_path / "photos"
    lib.mkdir()
    cv2.imwrite(str(lib / "someone.jpg"), cv2.imread(str(portrait)))

    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ocr_enabled = False
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    ScanService(cfg, factory).scan(lib)

    hits = SearchService(cfg, factory).search_images(tag="person")
    assert len(hits) == 1
    assert SearchService(cfg, factory).search_images(tag="giraffe") == []


@needs_models
@needs_api
def test_api_endpoints(tmp_path):
    lib = tmp_path / "photos"
    lib.mkdir()
    img = cv2.imread(str(portrait))
    cv2.imwrite(str(lib / "a.jpg"), img)
    cv2.imwrite(str(lib / "b.jpg"), cv2.convertScaleAbs(img, alpha=1.15))

    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ocr_enabled = False
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    ScanService(cfg, factory).scan(lib)

    from app.services.people_service import PeopleService

    svc = PeopleService(cfg, factory)
    svc.rename(svc.list_people()[0]["id"], "Api Person")

    client = TestClient(create_app(cfg))

    stats = client.get("/api/stats").json()
    assert stats["images"] == 2 and stats["people"] == 1

    people = client.get("/api/people").json()
    assert people[0]["face_count"] == 2

    results = client.post("/api/search", json={"person": "Api Person"}).json()
    assert len(results) == 2
    photo_id = results[0]["id"]

    if cfg.semantic_available():
        sem = client.post(
            "/api/search", json={"query": "astronaut in an orange space suit"}
        ).json()
        assert sem and "score" in sem[0]

    thumb = client.get(f"/api/photos/{photo_id}/thumbnail")
    assert thumb.status_code == 200
    assert thumb.headers["content-type"] == "image/jpeg"

    assert client.get("/api/photos/999999/thumbnail").status_code == 404
