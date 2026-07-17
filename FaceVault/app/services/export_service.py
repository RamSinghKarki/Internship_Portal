"""Export: copy photos out organized by person, or dump metadata to CSV."""

import csv
import re
import shutil
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..config import AppConfig
from ..database.models import Face, Image
from ..database.repository import Repository


def _safe_folder_name(name: str) -> str:
    """Person names become folder names — strip filesystem-hostile chars."""
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name).strip(". ")
    return cleaned or "Unnamed"


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

    def export_people_to_folders(
        self, dest: Path, include_unknown: bool = False
    ) -> dict:
        """Google-Photos-style 'save by face': copy the whole library into
        dest/<Person Name>/ folders, one folder per person. A photo with
        several people is copied into each of their folders. Optionally
        photos whose faces are all unknown go to dest/Unknown faces/.
        Originals are never moved."""
        dest = Path(dest).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
        copied = 0
        folders: dict[str, int] = {}

        def copy_into(folder_name: str, image: Image) -> None:
            nonlocal copied
            src = Path(image.path)
            if not src.is_file():
                return
            folder = dest / _safe_folder_name(folder_name)
            folder.mkdir(exist_ok=True)
            target = folder / src.name
            if target.exists():
                target = folder / f"{src.stem}_{image.id}{src.suffix}"
            shutil.copy2(src, target)
            copied += 1
            folders[folder.name] = folders.get(folder.name, 0) + 1

        with self.session_factory() as session:
            repo = Repository(session)
            for person, count in repo.persons_with_counts():
                if count == 0:
                    continue
                for image in repo.images_of_person(person.id):
                    copy_into(person.display_name, image)

            if include_unknown:
                has_face = (
                    select(Face.id).where(Face.image_id == Image.id).exists()
                )
                has_known_face = (
                    select(Face.id)
                    .where(Face.image_id == Image.id, Face.person_id.is_not(None))
                    .exists()
                )
                unknown_images = session.scalars(
                    select(Image)
                    .where(Image.trashed.is_(False), has_face, ~has_known_face)
                ).all()
                for image in unknown_images:
                    copy_into("Unknown faces", image)

        return {"copied": copied, "folders": folders, "dest": str(dest)}

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
