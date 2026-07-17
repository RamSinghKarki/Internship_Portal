"""Person management: identity assignment, rename, merge, listing."""

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..ai.clustering import cluster_faces
from ..config import AppConfig
from ..database.models import Face, Person
from ..database.repository import Repository, embedding_from_bytes


class PeopleService:
    def __init__(self, config: AppConfig, session_factory: sessionmaker[Session]):
        self.config = config
        self.session_factory = session_factory

    # ---- identity assignment ----------------------------------------
    def assign_identities(self, session: Session) -> dict:
        """Match unassigned quality faces to existing persons, then cluster
        the remainder into new persons. Called after every scan."""
        repo = Repository(session)
        faces = repo.unassigned_faces(self.config.min_cluster_quality)
        if not faces:
            return {"faces_matched": 0, "new_people": 0, "unknown_faces": 0}

        ids = [f.id for f in faces]
        embs = np.stack([embedding_from_bytes(f.embedding) for f in faces])
        result = cluster_faces(
            ids,
            embs,
            repo.person_centroids(),
            match_threshold=self.config.match_threshold,
            min_cluster_size=self.config.min_cluster_size,
        )

        by_id = {f.id: f for f in faces}
        for face_id, person_id in result.matched.items():
            by_id[face_id].person_id = person_id

        for members in result.new_clusters:
            person = Person()
            session.add(person)
            session.flush()  # obtain person.id
            for face_id in members:
                by_id[face_id].person_id = person.id
            self._refresh_cover(session, person)

        session.commit()
        return {
            "faces_matched": len(result.matched),
            "new_people": len(result.new_clusters),
            "unknown_faces": len(result.leftover),
        }

    # ---- management ---------------------------------------------------
    def _refresh_cover(self, session: Session, person: Person) -> None:
        best = Repository(session).best_face_of_person(person.id)
        person.cover_face_id = best.id if best else None

    def rename(self, person_id: int, name: str) -> None:
        with self.session_factory() as session:
            person = session.get(Person, person_id)
            if person is None:
                raise ValueError(f"No person with id {person_id}")
            person.name = name.strip() or None
            person.verified = bool(person.name)
            session.commit()

    def merge(self, source_id: int, target_id: int) -> None:
        """Move all faces from source into target and delete source."""
        if source_id == target_id:
            raise ValueError("Cannot merge a person into itself")
        with self.session_factory() as session:
            source = session.get(Person, source_id)
            target = session.get(Person, target_id)
            if source is None or target is None:
                raise ValueError("Both persons must exist")
            for face in session.scalars(select(Face).where(Face.person_id == source_id)):
                face.person_id = target_id
            # Keep the human-entered name if the target lacks one.
            if not target.name and source.name:
                target.name = source.name
                target.verified = source.verified
            session.delete(source)
            self._refresh_cover(session, target)
            session.commit()

    def delete_person(self, person_id: int) -> None:
        """Delete a person; its faces return to the unknown pool (SET NULL)."""
        with self.session_factory() as session:
            person = session.get(Person, person_id)
            if person is not None:
                session.delete(person)
                session.commit()

    # ---- queries ------------------------------------------------------
    def list_people(self) -> list[dict]:
        with self.session_factory() as session:
            repo = Repository(session)
            out = []
            for person, count in repo.persons_with_counts():
                cover = repo.best_face_of_person(person.id)
                out.append(
                    {
                        "id": person.id,
                        "name": person.display_name,
                        "verified": person.verified,
                        "face_count": count,
                        "cover_face_id": cover.id if cover else None,
                    }
                )
            return out

    def person_detail(self, person_id: int) -> dict:
        with self.session_factory() as session:
            repo = Repository(session)
            person = session.get(Person, person_id)
            if person is None:
                raise ValueError(f"No person with id {person_id}")
            images = repo.images_of_person(person_id)
            faces = list(
                session.scalars(select(Face).where(Face.person_id == person_id))
            )
            taken = sorted(i.taken_at for i in images if i.taken_at)
            return {
                "id": person.id,
                "name": person.display_name,
                "verified": person.verified,
                "photo_count": len(images),
                "face_count": len(faces),
                "avg_quality": round(
                    float(np.mean([f.quality for f in faces])), 1
                ) if faces else 0.0,
                "first_seen": taken[0] if taken else None,
                "last_seen": taken[-1] if taken else None,
                "images": [(i.id, i.path) for i in images],
            }
