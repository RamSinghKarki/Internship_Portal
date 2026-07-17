"""Export: copy a person's photos out, or dump library metadata to CSV."""

import csv
import shutil
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..config import AppConfig
from ..database.models import Image
from ..database.repository import Repository


class ExportService:
    def __init__(self, config: AppConfig, session_factory: sessionmaker[Session]):
        self.config = config
        self.session_factory = session_factory

    def export_person_photos(self, person_id: int, dest: Path) -> int:
        """Copy every photo containing this person into dest. Returns count."""
        dest = Path(dest).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
        copied = 0
        with self.session_factory() as session:
            for image in Repository(session).images_of_person(person_id):
                src = Path(image.path)
                if not src.is_file():
                    continue
                target = dest / src.name
                # Never overwrite: disambiguate name collisions with the id.
                if target.exists():
                    target = dest / f"{src.stem}_{image.id}{src.suffix}"
                shutil.copy2(src, target)
                copied += 1
        return copied

    def export_images_csv(self, dest: Path) -> int:
        """Write one row per image with metadata + face/person summary."""
        dest = Path(dest).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.session_factory() as session:
            images = list(session.scalars(select(Image).order_by(Image.id)))
            with open(dest, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["id", "path", "width", "height", "camera", "lens",
                     "taken_at", "gps_lat", "gps_lon", "faces", "people"]
                )
                for img in images:
                    people = sorted(
                        {f.person.display_name for f in img.faces if f.person}
                    )
                    writer.writerow(
                        [img.id, img.path, img.width, img.height, img.camera,
                         img.lens, img.taken_at, img.gps_lat, img.gps_lon,
                         len(img.faces), "; ".join(people)]
                    )
            return len(images)
