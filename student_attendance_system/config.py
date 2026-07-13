"""Application configuration.

Reads settings from environment variables so the same code base runs in
development (SQLite fallback) and production (MySQL) without changes.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

    # MySQL is the primary target; SQLite is used as a zero-setup fallback
    # so the project can be demonstrated without a database server.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "attendance.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # File uploads (student / teacher photos)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB
    ALLOWED_PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # Session / security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None

    # Pagination default
    PER_PAGE = 10


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class MySQLExample(Config):
    """Example MySQL DSN, e.g.:
    mysql+pymysql://attendance_user:password@localhost:3306/attendance_db?charset=utf8mb4
    """
    pass
