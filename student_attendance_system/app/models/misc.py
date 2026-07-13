from datetime import datetime

from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True, index=True,  # NULL = broadcast to admins
    )
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text)
    category = db.Column(db.String(30), default="info")  # info / warning / danger
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")


class Setting(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(60), unique=True, nullable=False)
    value = db.Column(db.String(255))

    DEFAULTS = {
        "institute_name": "Model College of Engineering",
        "low_attendance_threshold": "75",
        "allow_same_day_edit": "1",
        "academic_year": "2025-2026",
    }

    @classmethod
    def get(cls, key, default=None):
        row = cls.query.filter_by(key=key).first()
        if row is not None and row.value is not None:
            return row.value
        return cls.DEFAULTS.get(key, default)

    @classmethod
    def set(cls, key, value):
        row = cls.query.filter_by(key=key).first()
        if row is None:
            row = cls(key=key)
            db.session.add(row)
        row.value = value
