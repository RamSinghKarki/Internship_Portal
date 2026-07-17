"""Query helpers shared by services, CLI and GUI."""

from collections import defaultdict
from pathlib import Path

import numpy as np
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Face, Image, Person, ScanHistory


def embedding_to_bytes(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()


def embedding_from_bytes(raw: bytes) -> np.ndarray:
    return np.frombuffer(raw, dtype=np.float32)


class Repository:
    def __init__(self, session: Session):
        self.s = session

    # ---- images -----------------------------------------------------
    def image_by_path(self, path: str) -> Image | None:
        return self.s.scalar(select(Image).where(Image.path == path))

    def known_files(self) -> dict[str, tuple[float | None, int | None]]:
        """path -> (mtime, size) for incremental scan skipping."""
        rows = self.s.execute(select(Image.path, Image.mtime, Image.size_bytes)).all()
        return {p: (m, sz) for p, m, sz in rows}

    # ---- stats ------------------------------------------------------
    def stats(self) -> dict:
        images = self.s.scalar(select(func.count(Image.id))) or 0
        faces = self.s.scalar(select(func.count(Face.id))) or 0
        persons = self.s.scalar(select(func.count(Person.id))) or 0
        unknown = (
            self.s.scalar(select(func.count(Face.id)).where(Face.person_id.is_(None))) or 0
        )
        dup_groups = self.s.scalar(
            select(func.count()).select_from(
                select(Image.file_hash)
                .where(Image.file_hash.is_not(None))
                .group_by(Image.file_hash)
                .having(func.count(Image.id) > 1)
                .subquery()
            )
        ) or 0
        last_scan = self.s.scalars(
            select(ScanHistory).order_by(ScanHistory.id.desc()).limit(1)
        ).first()
        return {
            "images": images,
            "faces": faces,
            "people": persons,
            "unknown_faces": unknown,
            "exact_duplicate_groups": dup_groups,
            "last_scan": last_scan,
        }

    # ---- duplicates -------------------------------------------------
    def exact_duplicate_groups(self) -> list[list[Image]]:
        dup_hashes = self.s.scalars(
            select(Image.file_hash)
            .where(Image.file_hash.is_not(None))
            .group_by(Image.file_hash)
            .having(func.count(Image.id) > 1)
        ).all()
        groups = []
        for h in dup_hashes:
            groups.append(list(self.s.scalars(select(Image).where(Image.file_hash == h))))
        return groups

    def images_with_phash(self) -> list[tuple[int, int]]:
        rows = self.s.execute(
            select(Image.id, Image.phash).where(Image.phash.is_not(None))
        ).all()
        return [(i, int(p, 16)) for i, p in rows]

    # ---- faces / persons --------------------------------------------
    def unassigned_faces(self, min_quality: float) -> list[Face]:
        return list(
            self.s.scalars(
                select(Face)
                .where(Face.person_id.is_(None))
                .where(Face.embedding.is_not(None))
                .where(Face.quality >= min_quality)
            )
        )

    def person_centroids(self) -> dict[int, np.ndarray]:
        """Normalized mean embedding per person."""
        centroids: dict[int, np.ndarray] = {}
        buckets: dict[int, list[np.ndarray]] = defaultdict(list)
        rows = self.s.execute(
            select(Face.person_id, Face.embedding).where(
                Face.person_id.is_not(None), Face.embedding.is_not(None)
            )
        ).all()
        for pid, raw in rows:
            buckets[pid].append(embedding_from_bytes(raw))
        for pid, vecs in buckets.items():
            m = np.mean(np.stack(vecs), axis=0)
            n = np.linalg.norm(m)
            if n > 0:
                centroids[pid] = m / n
        return centroids

    def persons_with_counts(self) -> list[tuple[Person, int]]:
        rows = self.s.execute(
            select(Person, func.count(Face.id))
            .join(Face, Face.person_id == Person.id, isouter=True)
            .group_by(Person.id)
            .order_by(func.count(Face.id).desc())
        ).all()
        return [(p, c) for p, c in rows]

    def images_of_person(self, person_id: int) -> list[Image]:
        return list(
            self.s.scalars(
                select(Image)
                .join(Face, Face.image_id == Image.id)
                .where(Face.person_id == person_id)
                .distinct()
                .order_by(Image.taken_at.desc().nullslast(), Image.id.desc())
            )
        )

    def best_face_of_person(self, person_id: int) -> Face | None:
        return self.s.scalars(
            select(Face)
            .where(Face.person_id == person_id)
            .order_by(Face.quality.desc())
            .limit(1)
        ).first()

    def all_embeddings(self) -> tuple[list[int], np.ndarray | None]:
        """(face_ids, matrix) for building the vector index."""
        rows = self.s.execute(
            select(Face.id, Face.embedding).where(Face.embedding.is_not(None))
        ).all()
        if not rows:
            return [], None
        ids = [r[0] for r in rows]
        mat = np.stack([embedding_from_bytes(r[1]) for r in rows])
        return ids, mat
