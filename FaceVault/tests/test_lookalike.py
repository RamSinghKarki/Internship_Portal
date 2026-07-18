"""Look-alike protection: match margin, split tool, ArcFace upgrade path."""

import numpy as np
import pytest

from app.ai.clustering import centroid, cluster_faces
from app.config import AppConfig
from app.database.models import Face, Image, Person
from app.database.repository import Repository, embedding_to_bytes
from app.database.session import create_session_factory
from app.services.people_service import PeopleService


def _norm(v):
    return v / np.linalg.norm(v)


def _variants(base, n, noise, seed):
    rng = np.random.default_rng(seed)
    return [_norm(base + rng.normal(scale=noise, size=base.shape)) for _ in range(n)]


def test_margin_sends_ambiguous_faces_to_unknown():
    """A face similar to TWO existing people must not be guessed."""
    rng = np.random.default_rng(9)
    base = _norm(rng.normal(size=128))
    # Two look-alike persons: centroids deliberately close to each other.
    person_a = centroid(np.stack(_variants(base, 5, 0.05, 1)))
    person_b = centroid(np.stack(_variants(base, 5, 0.05, 2)))
    centroids = {1: person_a, 2: person_b}

    ambiguous = _norm(base + rng.normal(scale=0.04, size=128))  # near both
    clearly_a = _norm(person_a + rng.normal(scale=0.01, size=128))

    # Without a margin the ambiguous face gets guessed onto someone.
    r0 = cluster_faces([10], np.stack([ambiguous]), centroids,
                       match_threshold=0.5, match_margin=0.0)
    assert 10 in r0.matched

    # With the margin it is refused and waits for human review …
    r1 = cluster_faces([10, 11], np.stack([ambiguous, clearly_a]), centroids,
                       match_threshold=0.5, match_margin=0.05)
    assert 10 in r1.leftover
    # … while an unambiguous face still auto-assigns.
    assert r1.matched.get(11) == 1


def test_split_person_separates_two_lookalikes(tmp_path):
    """Two distinct-but-similar identity clusters wrongly merged into one
    person are separated by split_person."""
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.recognition_model = "sface"  # synthetic 128-d embeddings below
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    rng = np.random.default_rng(5)
    ident_a = _norm(rng.normal(size=128))
    ident_b = _norm(ident_a + rng.normal(scale=0.45, size=128))  # similar person

    with factory() as session:
        person = Person(name="Merged")
        session.add(person)
        session.flush()
        for i, vec in enumerate(_variants(ident_a, 4, 0.03, 3)
                                + _variants(ident_b, 3, 0.03, 4)):
            img = Image(path=str(tmp_path / f"p{i}.jpg"))
            session.add(img)
            session.flush()
            session.add(Face(image_id=img.id, person_id=person.id,
                             x=0, y=0, w=50, h=50, det_score=0.9, quality=80,
                             embedding=embedding_to_bytes(vec)))
        session.commit()
        pid = person.id

    people = PeopleService(cfg, factory)
    result = people.split_person(pid)
    assert result["split"] is True
    assert result["new_people"] == 1

    listed = people.list_people()
    assert len(listed) == 2
    counts = sorted(p["face_count"] for p in listed)
    assert counts == [3, 4]
    # The original person keeps its name and the larger group.
    keeper = next(p for p in listed if p["id"] == pid)
    assert keeper["name"] == "Merged" and keeper["face_count"] == 4


def test_split_consistent_person_is_noop(tmp_path):
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.recognition_model = "sface"  # synthetic 128-d embeddings below
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    rng = np.random.default_rng(6)
    ident = _norm(rng.normal(size=128))
    with factory() as session:
        person = Person(name="Solid")
        session.add(person)
        session.flush()
        for i, vec in enumerate(_variants(ident, 5, 0.02, 7)):
            img = Image(path=str(tmp_path / f"s{i}.jpg"))
            session.add(img)
            session.flush()
            session.add(Face(image_id=img.id, person_id=person.id,
                             x=0, y=0, w=50, h=50, det_score=0.9, quality=80,
                             embedding=embedding_to_bytes(vec)))
        session.commit()
        pid = person.id

    result = PeopleService(cfg, factory).split_person(pid)
    assert result["split"] is False
    assert len(PeopleService(cfg, factory).list_people()) == 1


def test_dim_mismatch_is_ignored_not_crashed(tmp_path):
    """After switching recognition models, old embeddings with a different
    dimension must be skipped safely during assignment."""
    cfg = AppConfig(data_dir=tmp_path / "vault")
    cfg.ensure_dirs()
    factory = create_session_factory(cfg.db_path)
    rng = np.random.default_rng(8)
    with factory() as session:
        img = Image(path=str(tmp_path / "old.jpg"))
        session.add(img)
        session.flush()
        # 512-d embedding while active model (SFace default here) is 128-d.
        session.add(Face(image_id=img.id, x=0, y=0, w=50, h=50, det_score=0.9,
                         quality=80,
                         embedding=embedding_to_bytes(rng.normal(size=512))))
        session.commit()

    # Force SFace so the 512-d row is guaranteed to mismatch.
    cfg.recognition_model = "sface"
    with factory() as session:
        summary = PeopleService(cfg, factory).assign_identities(session)
    assert summary == {"faces_matched": 0, "new_people": 0, "unknown_faces": 0}


ARCFACE = AppConfig().arcface_model

@pytest.mark.skipif(not ARCFACE.is_file(), reason="ArcFace model not downloaded")
@pytest.mark.skipif(not AppConfig().models_available(), reason="face models missing")
def test_arcface_embeddings_when_model_present(tmp_path):
    import cv2

    from app.ai.arcface import ArcFaceRecognizer
    from app.ai.detector import FaceDetector
    from tests.test_e2e_scan import _find_portrait

    portrait = _find_portrait()
    if portrait is None:
        pytest.skip("no portrait fixture")
    cfg = AppConfig()
    assert cfg.active_recognition() == "arcface"  # auto-upgrade kicks in
    assert cfg.embedding_dim == 512

    img = cv2.imread(str(portrait))
    det = FaceDetector(cfg.detector_model).detect(img, 30)
    assert det
    arc = ArcFaceRecognizer(cfg.arcface_model)
    e1 = arc.embed(img, det[0])
    bright = cv2.convertScaleAbs(img, alpha=1.2, beta=10)
    det2 = FaceDetector(cfg.detector_model).detect(bright, 30)
    e2 = arc.embed(bright, det2[0])
    assert e1 is not None and e1.shape == (512,)
    assert float(e1 @ e2) > 0.8  # same person, robust to exposure change
