"""Structured search over the library + face similarity search."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..ai.detector import FaceDetector
from ..ai.indexing import VectorIndex
from ..ai.recognizer import FaceRecognizer
from ..config import AppConfig
from ..database.models import Face, Image, Person
from ..database.repository import Repository, embedding_from_bytes


class SearchService:
    def __init__(self, config: AppConfig, session_factory: sessionmaker[Session]):
        self.config = config
        self.session_factory = session_factory
        self._index: VectorIndex | None = None

    # ---- structured filters -------------------------------------------
    def search_images(
        self,
        person_name: str | None = None,
        camera: str | None = None,
        taken_after: datetime | None = None,
        taken_before: datetime | None = None,
        min_quality: float | None = None,
        has_gps: bool | None = None,
        unknown_faces_only: bool = False,
        favorites_only: bool = False,
        limit: int = 500,
    ) -> list[Image]:
        with self.session_factory() as session:
            q = select(Image).distinct().where(Image.trashed.is_(False))
            if favorites_only:
                q = q.where(Image.favorite.is_(True))
            if person_name or min_quality is not None or unknown_faces_only:
                q = q.join(Face, Face.image_id == Image.id)
            if person_name:
                q = q.join(Person, Person.id == Face.person_id).where(
                    Person.name.ilike(f"%{person_name}%")
                )
            if unknown_faces_only:
                q = q.where(Face.person_id.is_(None))
            if min_quality is not None:
                q = q.where(Face.quality >= min_quality)
            if camera:
                q = q.where(Image.camera.ilike(f"%{camera}%"))
            if taken_after:
                q = q.where(Image.taken_at >= taken_after)
            if taken_before:
                q = q.where(Image.taken_at <= taken_before)
            if has_gps:
                q = q.where(Image.gps_lat.is_not(None))
            q = q.order_by(Image.taken_at.desc().nullslast(), Image.id.desc()).limit(limit)
            return list(session.scalars(q))

    # ---- similarity ----------------------------------------------------
    def rebuild_index(self) -> int:
        with self.session_factory() as session:
            ids, matrix = Repository(session).all_embeddings()
        self._index = VectorIndex()
        self._index.build(ids, matrix)
        return len(self._index)

    def find_similar_faces(self, query_image: Path, k: int = 10) -> list[dict]:
        """Local reverse face search: detect the largest face in the query
        image and return the closest faces in the library."""
        if self._index is None:
            self.rebuild_index()

        from ..utils.hashing import load_image_bgr

        img = load_image_bgr(Path(query_image))
        if img is None:
            raise ValueError(f"Cannot read image: {query_image}")
        detector = FaceDetector(
            self.config.detector_model,
            score_threshold=self.config.detection_score_threshold,
            mode=self.config.detection_mode,
        )
        detections = detector.detect(img, min_face_size=self.config.min_face_size)
        if not detections:
            return []
        largest = max(detections, key=lambda d: d.box[2] * d.box[3])
        emb = FaceRecognizer(self.config.recognizer_model).embed(img, largest)
        if emb is None:
            return []

        hits = self._index.search(emb, k=k)
        out = []
        with self.session_factory() as session:
            for face_id, sim in hits:
                face = session.get(Face, face_id)
                if face is None:
                    continue
                out.append(
                    {
                        "face_id": face_id,
                        "similarity": round(sim, 4),
                        "image_path": face.image.path,
                        "person": face.person.display_name if face.person else None,
                    }
                )
        return out
