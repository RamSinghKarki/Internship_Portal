from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)  # admin / teacher / student

    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    is_active_flag = db.Column("is_active", db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    role = db.relationship("Role", back_populates="users")
    teacher = db.relationship("Teacher", back_populates="user", uselist=False)
    student = db.relationship("Student", back_populates="user", uselist=False)
    notifications = db.relationship(
        "Notification", back_populates="user", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    @property
    def is_active(self):  # consumed by Flask-Login
        return self.is_active_flag

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def role_name(self):
        return self.role.name if self.role else None

    def is_admin(self):
        return self.role_name == "admin"

    def is_teacher(self):
        return self.role_name == "teacher"

    def is_student(self):
        return self.role_name == "student"

    @property
    def display_name(self):
        if self.teacher:
            return self.teacher.full_name
        if self.student:
            return self.student.full_name
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
