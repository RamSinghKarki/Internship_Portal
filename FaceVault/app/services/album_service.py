"""Album management: user-curated collections of photos."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from ..config import AppConfig
from ..database.models import Album, Image, ImageAlbum


class AlbumService:
    def __init__(self, config: AppConfig, session_factory: sessionmaker[Session]):
        self.config = config
        self.session_factory = session_factory

    def create(self, name: str) -> int:
        name = name.strip()
        if not name:
            raise ValueError("Album name cannot be empty")
        with self.session_factory() as session:
            existing = session.scalar(select(Album).where(Album.name == name))
            if existing is not None:
                raise ValueError(f"Album {name!r} already exists")
            album = Album(name=name)
            session.add(album)
            session.commit()
            return album.id

    def rename(self, album_id: int, name: str) -> None:
        with self.session_factory() as session:
            album = session.get(Album, album_id)
            if album is None:
                raise ValueError(f"No album with id {album_id}")
            album.name = name.strip() or album.name
            session.commit()

    def delete(self, album_id: int) -> None:
        """Delete the album only — photos stay in the library."""
        with self.session_factory() as session:
            album = session.get(Album, album_id)
            if album is not None:
                session.delete(album)
                session.commit()

    def add_images(self, album_id: int, image_ids: list[int]) -> int:
        with self.session_factory() as session:
            if session.get(Album, album_id) is None:
                raise ValueError(f"No album with id {album_id}")
            existing = set(
                session.scalars(
                    select(ImageAlbum.image_id).where(ImageAlbum.album_id == album_id)
                )
            )
            added = 0
            for image_id in image_ids:
                if image_id in existing or session.get(Image, image_id) is None:
                    continue
                session.add(ImageAlbum(album_id=album_id, image_id=image_id))
                added += 1
            session.commit()
            return added

    def remove_images(self, album_id: int, image_ids: list[int]) -> None:
        with self.session_factory() as session:
            for link in session.scalars(
                select(ImageAlbum).where(
                    ImageAlbum.album_id == album_id,
                    ImageAlbum.image_id.in_(image_ids),
                )
            ):
                session.delete(link)
            session.commit()

    def list_albums(self) -> list[dict]:
        with self.session_factory() as session:
            rows = session.execute(
                select(Album, func.count(ImageAlbum.id))
                .join(ImageAlbum, ImageAlbum.album_id == Album.id, isouter=True)
                .group_by(Album.id)
                .order_by(Album.name)
            ).all()
            return [
                {"id": a.id, "name": a.name, "photo_count": c} for a, c in rows
            ]

    def images_in_album(self, album_id: int) -> list[Image]:
        with self.session_factory() as session:
            return list(
                session.scalars(
                    select(Image)
                    .join(ImageAlbum, ImageAlbum.image_id == Image.id)
                    .where(ImageAlbum.album_id == album_id)
                    .order_by(Image.taken_at.desc().nullslast(), Image.id.desc())
                )
            )
