"""Engine / session management.

SQLite is configured for concurrent-friendly access:
  - WAL journal so readers don't block the single writer thread.
  - foreign_keys ON so ondelete rules in the schema actually fire.
"""

from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def create_session_factory(db_path: Path) -> sessionmaker[Session]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(engine, "connect")
    def _configure(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    Base.metadata.create_all(engine)
    _migrate(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def _migrate(engine) -> None:
    """Lightweight in-place migrations for libraries created by older
    versions (create_all only creates missing tables, never columns)."""
    with engine.begin() as conn:
        cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(images)")}
        if "favorite" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE images ADD COLUMN favorite BOOLEAN NOT NULL DEFAULT 0"
            )
        if "trashed" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE images ADD COLUMN trashed BOOLEAN NOT NULL DEFAULT 0"
            )
        if "clip_embedding" not in cols:
            conn.exec_driver_sql("ALTER TABLE images ADD COLUMN clip_embedding BLOB")
        if "ocr_text" not in cols:
            conn.exec_driver_sql("ALTER TABLE images ADD COLUMN ocr_text TEXT")
