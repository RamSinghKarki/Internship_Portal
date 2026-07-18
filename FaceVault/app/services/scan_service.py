"""Scan orchestration: pipeline -> database -> identity assignment.

Incremental by default: files whose (mtime, size) match the DB are
skipped, so re-scanning a folder only pays for what changed.
`index_files` ingests specific files (e.g. a freshly saved edit) through
the exact same pipeline.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session, sessionmaker

from ..config import AppConfig
from ..database.models import Face, Image, ScanHistory
from ..database.repository import Repository
from ..workers.pipeline import ProcessedImage, ScanPipeline, discover_images
from .people_service import PeopleService


class ScanService:
    def __init__(self, config: AppConfig, session_factory: sessionmaker[Session]):
        self.config = config
        self.session_factory = session_factory

    def _require_models(self) -> None:
        if not self.config.models_available():
            raise FileNotFoundError(
                f"AI models not found in {self.config.models_dir}. "
                "Run models/download_models.py once (see models/README.md)."
            )

    def _write_processed(self, session: Session, repo: Repository,
                         res: ProcessedImage) -> int | None:
        """Upsert one pipeline result. Returns faces stored, None on error."""
        if res.error:
            return None
        img = repo.image_by_path(res.path)
        if img is None:
            img = Image(path=res.path)
            session.add(img)
        else:
            img.faces.clear()  # file changed: re-detect from scratch
        img.mtime = res.mtime
        img.size_bytes = res.size_bytes
        img.file_hash = res.file_hash
        img.phash = res.phash
        img.width, img.height = res.width, res.height
        img.camera = res.exif.get("camera")
        img.lens = res.exif.get("lens")
        img.taken_at = res.exif.get("taken_at")
        img.gps_lat = res.exif.get("gps_lat")
        img.gps_lon = res.exif.get("gps_lon")
        img.scanned_at = datetime.now(timezone.utc)
        if res.clip_embedding is not None:
            img.clip_embedding = res.clip_embedding
        if res.ocr_text is not None:
            img.ocr_text = res.ocr_text
        for f in res.faces:
            img.faces.append(
                Face(
                    x=f.x, y=f.y, w=f.w, h=f.h,
                    det_score=f.det_score,
                    blur_score=f.blur,
                    quality=f.quality,
                    embedding=f.embedding,
                )
            )
        return len(res.faces)

    def index_files(self, paths: list[Path]) -> dict:
        """Process specific files (new or changed) and assign identities."""
        self._require_models()
        pipeline = ScanPipeline(self.config)
        new_images = failed = faces_found = 0
        with self.session_factory() as session:
            repo = Repository(session)
            for res in pipeline.run([Path(p) for p in paths]):
                stored = self._write_processed(session, repo, res)
                if stored is None:
                    failed += 1
                else:
                    new_images += 1
                    faces_found += stored
            session.commit()
            assignment = PeopleService(self.config, self.session_factory).assign_identities(session)
        return {
            "new_images": new_images, "failed": failed,
            "faces_found": faces_found, **assignment,
        }

    def scan(
        self,
        folder: Path,
        progress: Callable[[int, int, str], None] | None = None,
        full_rescan: bool = False,
        cancel_event=None,
    ) -> dict:
        folder = Path(folder).expanduser().resolve()
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a folder: {folder}")
        self._require_models()

        with self.session_factory() as session:
            history = ScanHistory(folder=str(folder))
            session.add(history)
            session.commit()

            repo = Repository(session)
            all_paths = discover_images(folder)
            known = {} if full_rescan else repo.known_files()

            todo: list[Path] = []
            skipped = 0
            for p in all_paths:
                prev = known.get(str(p))
                st = p.stat()
                if prev and prev[0] == st.st_mtime and prev[1] == st.st_size:
                    skipped += 1
                else:
                    todo.append(p)

            pipeline = ScanPipeline(self.config)
            new_images = failed = faces_found = 0
            pending = 0

            for res in pipeline.run(todo, progress=progress, cancel=cancel_event):
                stored = self._write_processed(session, repo, res)
                if stored is None:
                    failed += 1
                else:
                    new_images += 1
                    faces_found += stored
                pending += 1
                if pending >= self.config.write_batch_size:
                    session.commit()
                    pending = 0
            session.commit()

            cancelled = cancel_event is not None and cancel_event.is_set()

            # Identity assignment for everything ingested (even partial scans).
            assignment = PeopleService(self.config, self.session_factory).assign_identities(session)

            history.finished_at = datetime.now(timezone.utc)
            history.status = "cancelled" if cancelled else "done"
            history.total_files = len(all_paths)
            history.new_images = new_images
            history.skipped = skipped
            history.failed = failed
            history.faces_found = faces_found
            session.commit()

            return {
                "folder": str(folder),
                "total_files": len(all_paths),
                "new_images": new_images,
                "skipped": skipped,
                "failed": failed,
                "faces_found": faces_found,
                "cancelled": cancelled,
                **assignment,
            }
