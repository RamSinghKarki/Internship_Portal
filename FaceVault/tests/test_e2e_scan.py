"""End-to-end scan test against the real ONNX models.

Needs a real photographed face: synthetic images won't trigger YuNet.
Drop any portrait photo(s) into tests/fixtures/ (git-ignored) or set
FACEVAULT_TEST_IMAGE to a portrait path; otherwise the test is skipped.
"""

import os
import shutil
from pathlib import Path

import cv2
import pytest

from app.config import AppConfig
from app.database.repository import Repository
from app.database.session import create_session_factory
from app.services.people_service import PeopleService
from app.services.scan_service import ScanService

FIXTURES = Path(__file__).parent / "fixtures"


def _find_portrait() -> Path | None:
    env = os.environ.get("FACEVAULT_TEST_IMAGE")
    if env and Path(env).is_file():
        return Path(env)
    if FIXTURES.is_dir():
        for p in sorted(FIXTURES.iterdir()):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                return p
    return None


portrait = _find_portrait()
_cfg_probe = AppConfig()

pytestmark = [
    pytest.mark.skipif(portrait is None, reason="no portrait fixture available"),
    pytest.mark.skipif(not _cfg_probe.models_available(), reason="ONNX models not downloaded"),
]


@pytest.fixture()
def library(tmp_path: Path) -> Path:
    """A photo folder: portrait, a brightness-shifted variant (same person),
    a resized copy (near-duplicate), an exact copy, and a no-face image."""
    lib = tmp_path / "photos"
    lib.mkdir()
    img = cv2.imread(str(portrait))
    assert img is not None

    cv2.imwrite(str(lib / "original.jpg"), img)
    bright = cv2.convertScaleAbs(img, alpha=1.15, beta=12)
    cv2.imwrite(str(lib / "bright.jpg"), bright)
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(lib / "small.jpg"), small)
    shutil.copy2(lib / "original.jpg", lib / "exact_copy.jpg")
    no_face = cv2.GaussianBlur(
        cv2.applyColorMap(
            cv2.resize(
                cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[:50, :50], (400, 400)
            ),
            cv2.COLORMAP_OCEAN,
        ),
        (31, 31),
        12,
    )
    cv2.imwrite(str(lib / "noface.jpg"), no_face)
    return lib


def test_scan_detects_groups_and_skips(tmp_path: Path, library: Path):
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    scan = ScanService(cfg, factory)

    summary = scan.scan(library)
    assert summary["new_images"] == 5
    assert summary["faces_found"] >= 3  # portrait variants have a face each

    with factory() as session:
        repo = Repository(session)
        stats = repo.stats()
        assert stats["images"] == 5
        # exact_copy.jpg shares bytes with original.jpg
        assert stats["exact_duplicate_groups"] == 1
        # face variants must cluster into one person
        assert stats["people"] == 1

    people = PeopleService(cfg, factory).list_people()
    assert people[0]["face_count"] >= 3

    # Second scan of the same folder is fully incremental.
    summary2 = scan.scan(library)
    assert summary2["new_images"] == 0
    assert summary2["skipped"] == 5


def test_rename_and_merge(tmp_path: Path, library: Path):
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    ScanService(cfg, factory).scan(library)

    svc = PeopleService(cfg, factory)
    person_id = svc.list_people()[0]["id"]
    svc.rename(person_id, "Test Person")
    detail = svc.person_detail(person_id)
    assert detail["name"] == "Test Person"
    assert detail["verified"] is True
