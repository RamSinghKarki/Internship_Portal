"""Local REST API over the FaceVault library (Phase 2, milestone 12).

Runs on localhost for other apps (or a future web UI) to query the same
library the desktop app manages. Start it with:

    python -m app serve            # http://127.0.0.1:8090/docs

Endpoints:
    POST /api/search      {"query": "dog near river"}  → semantic search
                          {"person": "...", "camera": "...", "text": "...",
                           "tag": "...", "favorites": true}  → filters
    GET  /api/people      person list with counts
    GET  /api/stats       library statistics
    GET  /api/photos/{id}/thumbnail   JPEG thumbnail
    GET  /api/photos/{id}/file        original file

Local-only by design: binds 127.0.0.1 and there is no auth layer —
do not expose it to a network as-is.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func, select

from ..config import AppConfig
from ..database.models import Face, Image
from ..database.repository import Repository
from ..database.session import create_session_factory
from ..services.people_service import PeopleService
from ..services.search_service import SearchService
from ..services.thumbnail_service import ThumbnailService


class SearchRequest(BaseModel):
    query: str | None = None  # semantic (natural language)
    person: str | None = None
    camera: str | None = None
    text: str | None = None  # OCR contents
    tag: str | None = None  # detected object label
    favorites: bool = False
    limit: int = 100


def create_app(config: AppConfig | None = None) -> FastAPI:
    config = config or AppConfig.load()
    config.ensure_dirs()
    factory = create_session_factory(config.db_path)
    search = SearchService(config, factory)
    people = PeopleService(config, factory)
    thumbs = ThumbnailService(config)

    app = FastAPI(title="FaceVault API", version="1.0")

    def _face_counts(image_ids: list[int]) -> dict[int, int]:
        """Face count per image in one query — avoids lazy loads on detached
        ORM objects returned by the services."""
        if not image_ids:
            return {}
        with factory() as session:
            rows = session.execute(
                select(Face.image_id, func.count(Face.id))
                .where(Face.image_id.in_(image_ids))
                .group_by(Face.image_id)
            ).all()
        return {image_id: count for image_id, count in rows}

    def _photo(img: Image, faces: int, score: float | None = None) -> dict:
        out = {
            "id": img.id,
            "path": img.path,
            "filename": Path(img.path).name,
            "taken_at": img.taken_at.isoformat() if img.taken_at else None,
            "camera": img.camera,
            "favorite": img.favorite,
            "faces": faces,
        }
        if score is not None:
            out["score"] = round(score, 4)
        return out

    @app.post("/api/search")
    def api_search(req: SearchRequest) -> list[dict]:
        if req.query:
            hits = search.semantic_search(req.query, k=req.limit)
            counts = _face_counts([img.id for img, _ in hits])
            return [_photo(img, counts.get(img.id, 0), score) for img, score in hits]
        images = search.search_images(
            person_name=req.person,
            camera=req.camera,
            text_contains=req.text,
            tag=req.tag,
            favorites_only=req.favorites,
            limit=req.limit,
        )
        counts = _face_counts([i.id for i in images])
        return [_photo(i, counts.get(i.id, 0)) for i in images]

    @app.get("/api/people")
    def api_people() -> list[dict]:
        return people.list_people()

    @app.get("/api/stats")
    def api_stats() -> dict:
        with factory() as session:
            stats = Repository(session).stats()
        stats.pop("last_scan", None)  # ORM object, not JSON-friendly
        return stats

    @app.get("/api/photos/{image_id}/thumbnail")
    def api_thumbnail(image_id: int):
        with factory() as session:
            img = session.get(Image, image_id)
        if img is None:
            raise HTTPException(404, "no such photo")
        thumb = thumbs.image_thumbnail(img.path)
        if thumb is None:
            raise HTTPException(404, "thumbnail unavailable")
        return FileResponse(thumb, media_type="image/jpeg")

    @app.get("/api/photos/{image_id}/file")
    def api_file(image_id: int):
        with factory() as session:
            img = session.get(Image, image_id)
        if img is None or not Path(img.path).is_file():
            raise HTTPException(404, "no such photo")
        return FileResponse(img.path)

    return app
