"""Tests for the Google-Photos-style features: favorites, trash,
export-by-person folders, memories, and the schema migration."""

from datetime import datetime

import numpy as np
import pytest

from app.config import AppConfig
from app.database.models import Face, Image
from app.database.repository import Repository, embedding_to_bytes
from app.database.session import create_session_factory
from app.services.export_service import ExportService, _safe_folder_name
from app.services.people_service import PeopleService
from app.services.search_service import SearchService


@pytest.fixture()
def env(tmp_path):
    """Library with 2 people (2 photos each, 1 shared), 1 unknown-face
    photo, 1 face-less photo. Real files on disk so export can copy."""
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    rng = np.random.default_rng(2)

    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()

    def make_image(session, name, taken=None):
        path = photo_dir / name
        path.write_bytes(b"fake-jpeg-" + name.encode())
        img = Image(path=str(path), taken_at=taken)
        session.add(img)
        session.flush()
        return img

    def add_face(session, img):
        face = Face(image_id=img.id, x=1, y=1, w=50, h=50, det_score=0.9,
                    quality=80.0, embedding=embedding_to_bytes(rng.normal(size=128)))
        session.add(face)
        session.flush()
        return face

    with factory() as session:
        img_a1 = make_image(session, "a1.jpg", datetime(2024, 7, 17, 12, 0))
        img_a2 = make_image(session, "a2.jpg", datetime(2025, 7, 17, 9, 0))
        img_shared = make_image(session, "shared.jpg", datetime(2025, 1, 5))
        img_unknown = make_image(session, "unknown.jpg")
        make_image(session, "nofaces.jpg")

        f_a1, f_a2 = add_face(session, img_a1), add_face(session, img_a2)
        f_s1, f_s2 = add_face(session, img_shared), add_face(session, img_shared)
        add_face(session, img_unknown)  # stays unassigned
        session.commit()

    people = PeopleService(cfg, factory)
    ram = people.create_person_from_faces([f_a1.id, f_a2.id, f_s1.id], "Ram")
    hari = people.create_person_from_faces([f_s2.id], "Hari")
    return cfg, factory, {"ram": ram, "hari": hari}


def test_export_people_to_folders(env, tmp_path):
    cfg, factory, ids = env
    out = tmp_path / "by-person"
    result = ExportService(cfg, factory).export_people_to_folders(
        out, include_unknown=True
    )
    assert result["folders"]["Ram"] == 3         # a1, a2, shared
    assert result["folders"]["Hari"] == 1        # shared
    assert result["folders"]["Unknown faces"] == 1
    assert result["copied"] == 5
    assert (out / "Ram" / "a1.jpg").is_file()
    assert (out / "Hari" / "shared.jpg").is_file()
    assert (out / "Unknown faces" / "unknown.jpg").is_file()
    # nofaces.jpg is exported nowhere
    assert not list(out.rglob("nofaces.jpg"))


def test_safe_folder_names():
    assert _safe_folder_name('Ram / "The:Best"?') == "Ram _ _The_Best__"
    assert _safe_folder_name("...") == "Unnamed"


def test_favorites_and_search_filter(env):
    cfg, factory, _ = env
    with factory() as session:
        repo = Repository(session)
        first = session.query(Image).first()
        repo.set_favorite([first.id], True)
        assert repo.stats()["favorites"] == 1
    favs = SearchService(cfg, factory).search_images(favorites_only=True)
    assert [i.id for i in favs] == [first.id]


def test_trash_hides_everywhere_and_restores(env):
    cfg, factory, ids = env
    search = SearchService(cfg, factory)
    people = PeopleService(cfg, factory)

    with factory() as session:
        repo = Repository(session)
        shared = session.query(Image).filter(Image.path.like("%shared%")).one()
        repo.set_trashed([shared.id], True)

        assert repo.stats()["images"] == 4  # excludes trashed
        assert repo.stats()["trashed"] == 1
        assert len(repo.trashed_images()) == 1

    assert all("shared" not in i.path for i in search.search_images())
    assert all("shared" not in p for _i, p in people.person_detail(ids["ram"])["images"])

    with factory() as session:
        Repository(session).set_trashed([shared.id], False)
    assert any("shared" in i.path for i in search.search_images())


def test_on_this_day_memories(env):
    cfg, factory, _ = env
    with factory() as session:
        hits = Repository(session).on_this_day(7, 17)
    years = sorted(i.taken_at.year for i in hits)
    assert years == [2024, 2025]


def test_migration_adds_columns_to_old_library(tmp_path):
    """A database created without favorite/trashed must be upgraded
    in place and stay usable."""
    import sqlite3

    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE images (id INTEGER PRIMARY KEY, path TEXT UNIQUE, "
        "file_hash VARCHAR(64), phash VARCHAR(16), width INTEGER, height INTEGER, "
        "size_bytes INTEGER, mtime FLOAT, camera VARCHAR(128), lens VARCHAR(128), "
        "gps_lat FLOAT, gps_lon FLOAT, taken_at DATETIME, scanned_at DATETIME)"
    )
    conn.execute("INSERT INTO images (path) VALUES ('/x/a.jpg')")
    conn.commit()
    conn.close()

    factory = create_session_factory(db)  # runs create_all + _migrate
    with factory() as session:
        img = session.query(Image).one()
        assert img.favorite is False and img.trashed is False
        img.favorite = True
        session.commit()
