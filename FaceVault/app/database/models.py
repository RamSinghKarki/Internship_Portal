"""Database schema.

Key design decisions (see docs/ARCHITECTURE.md for rationale):
  - Embeddings live in the DB as float32 BLOBs; the in-memory vector index
    is a disposable cache rebuilt from here. The DB is the source of truth.
  - Images carry BOTH a sha256 (exact duplicates) and a dHash
    (near-duplicates) — these are different features.
  - Faces reference persons with ON DELETE SET NULL so deleting a person
    returns its faces to the "unknown" pool instead of destroying data.
  - mtime/size are stored to make re-scans incremental.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(Text, unique=True, index=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    phash: Mapped[str | None] = mapped_column(String(16), index=True)  # 64-bit dHash, hex
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    size_bytes: Mapped[int | None] = mapped_column(Integer)
    mtime: Mapped[float | None] = mapped_column(Float)
    camera: Mapped[str | None] = mapped_column(String(128))
    lens: Mapped[str | None] = mapped_column(String(128))
    gps_lat: Mapped[float | None] = mapped_column(Float)
    gps_lon: Mapped[float | None] = mapped_column(Float)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime)
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    # CLIP ViT-B/32 image embedding (512 x float32) for semantic search;
    # null until the image is semantically indexed.
    clip_embedding: Mapped[bytes | None] = mapped_column(LargeBinary)
    # Text found in the photo by OCR (documents, receipts, screenshots).
    ocr_text: Mapped[str | None] = mapped_column(Text)
    # Soft delete: trashed photos disappear from every view except Trash
    # and can be restored; the file on disk is never touched.
    trashed: Mapped[bool] = mapped_column(Boolean, default=False)

    faces: Mapped[list["Face"]] = relationship(
        back_populates="image", cascade="all, delete-orphan"
    )


class Face(Base):
    __tablename__ = "faces"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id", ondelete="CASCADE"), index=True
    )
    person_id: Mapped[int | None] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), index=True
    )
    x: Mapped[int] = mapped_column(Integer)
    y: Mapped[int] = mapped_column(Integer)
    w: Mapped[int] = mapped_column(Integer)
    h: Mapped[int] = mapped_column(Integer)
    det_score: Mapped[float] = mapped_column(Float)
    blur_score: Mapped[float] = mapped_column(Float, default=0.0)
    quality: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary)  # 128 x float32

    image: Mapped["Image"] = relationship(back_populates="faces")
    person: Mapped["Person | None"] = relationship(back_populates="faces")


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_face_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    faces: Mapped[list["Face"]] = relationship(back_populates="person")

    @property
    def display_name(self) -> str:
        return self.name or f"Person {self.id}"


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    cover_image_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ImageAlbum(Base):
    __tablename__ = "image_albums"
    __table_args__ = (UniqueConstraint("album_id", "image_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id", ondelete="CASCADE"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"))


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class ImageTag(Base):
    __tablename__ = "image_tags"
    __table_args__ = (UniqueConstraint("tag_id", "image_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"))


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    folder: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(16), default="running")  # running|done|failed
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    new_images: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    faces_found: Mapped[int] = mapped_column(Integer, default=0)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)
