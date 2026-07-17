"""Clean database initialisation — no demo data.

Creates the tables plus the bare essentials needed to use the system:
the three roles, one administrator account and the default settings.
Everything else (departments, teachers, students, …) is then added
through the admin panel.

Usage:
    python init_db.py

Default administrator login:
    admin / admin123        (change it from My Profile after first login)
"""
from app import create_app
from app.extensions import db
from app.models import Role, User, Setting


def run(fresh=False):
    """Create tables and baseline rows. With fresh=True, drop everything first."""
    if fresh:
        db.drop_all()
    db.create_all()

    roles = {}
    for name in ("admin", "teacher", "student"):
        role = Role.query.filter_by(name=name).first()
        if role is None:
            role = Role(name=name)
            db.session.add(role)
        roles[name] = role

    if User.query.filter_by(username="admin").first() is None:
        admin = User(username="admin", email="admin@college.edu", role=roles["admin"])
        admin.set_password("admin123")
        db.session.add(admin)

    for key, value in Setting.DEFAULTS.items():
        if Setting.query.filter_by(key=key).first() is None:
            db.session.add(Setting(key=key, value=value))

    db.session.commit()
    print("Database initialised (no demo data).")
    print("  Admin login: admin / admin123 — change the password after first login.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run(fresh=True)
