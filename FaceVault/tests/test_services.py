"""Service tests that need no AI models: albums, manual face assignment,
library removal. Faces are fabricated directly in the database."""

import numpy as np
import pytest

from app.config import AppConfig
from app.database.models import Face, Image
from app.database.repository import Repository, embedding_to_bytes
from app.database.session import create_session_factory
from app.services.album_service import AlbumService
from app.services.people_service import PeopleService


@pytest.fixture()
def env(tmp_path):
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    rng = np.random.default_rng(1)
    with factory() as session:
        for i in range(4):
            img = Image(path=str(tmp_path / f"photo_{i}.jpg"))
            img.faces.append(
                Face(
                    x=10, y=10, w=80, h=80, det_score=0.9, quality=70.0,
                    embedding=embedding_to_bytes(rng.normal(size=128)),
                )
            )
            session.add(img)
        session.commit()
    return cfg, factory


def test_albums_crud_and_membership(env):
    cfg, factory = env
    albums = AlbumService(cfg, factory)

    album_id = albums.create("Trip")
    with pytest.raises(ValueError):
        albums.create("Trip")  # duplicate name

    with factory() as session:
        image_ids = [i.id for i in session.query(Image).all()]

    assert albums.add_images(album_id, image_ids[:3]) == 3
    assert albums.add_images(album_id, image_ids[:3]) == 0  # idempotent
    assert albums.list_albums() == [{"id": album_id, "name": "Trip", "photo_count": 3}]

    albums.remove_images(album_id, image_ids[:1])
    assert len(albums.images_in_album(album_id)) == 2

    albums.delete(album_id)
    assert albums.list_albums() == []
    with factory() as session:  # photos survive album deletion
        assert session.query(Image).count() == 4


def test_manual_face_assignment(env):
    cfg, factory = env
    people = PeopleService(cfg, factory)

    with factory() as session:
        face_ids = [f.id for f in session.query(Face).all()]

    pid = people.create_person_from_faces(face_ids[:2], "Ram")
    detail = people.person_detail(pid)
    assert detail["name"] == "Ram" and detail["face_count"] == 2

    moved = people.assign_faces(face_ids[2:3], pid)
    assert moved == 1
    assert people.person_detail(pid)["face_count"] == 3

    with factory() as session:
        assert len(Repository(session).unknown_faces()) == 1


def test_remove_images_cascades_faces(env):
    cfg, factory = env
    with factory() as session:
        repo = Repository(session)
        ids = [i.id for i in session.query(Image).all()]
        assert repo.remove_images(ids[:2]) == 2
        assert session.query(Image).count() == 2
        assert session.query(Face).count() == 2  # cascaded
