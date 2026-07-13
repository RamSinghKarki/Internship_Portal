"""Small shared helpers: parsing, uploads, validation."""
import os
import uuid
from datetime import datetime, date, time

from flask import current_app, request
from werkzeug.utils import secure_filename


def parse_date(value, default=None):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return default


def parse_time(value, default=None):
    if not value:
        return default
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except (ValueError, TypeError):
            continue
    return default


def parse_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def form_value(name, default=""):
    return (request.form.get(name) or default).strip() if isinstance(
        request.form.get(name, default), str) else request.form.get(name, default)


def save_photo(file_storage):
    """Persist an uploaded photo and return its stored filename (or None)."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if ext not in current_app.config["ALLOWED_PHOTO_EXTENSIONS"]:
        return None
    filename = f"{uuid.uuid4().hex}.{secure_filename(ext)}"
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return filename


def delete_photo(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass


def month_bounds(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end
