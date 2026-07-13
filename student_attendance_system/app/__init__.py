import os

from flask import Flask, redirect, url_for, render_template
from flask_login import current_user

from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ------------------------------------------------------------------
    # Blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.teacher import teacher_bp
    from app.blueprints.student import student_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(api_bp, url_prefix="/api")

    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.is_admin():
            return redirect(url_for("admin.dashboard"))
        if current_user.is_teacher():
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # ------------------------------------------------------------------
    # Template globals
    from app.models import Setting

    @app.context_processor
    def inject_globals():
        institute = "Attendance System"
        if current_user.is_authenticated:
            try:
                institute = Setting.get("institute_name", institute)
            except Exception:
                pass
        from datetime import datetime
        return {"institute_name": institute, "now": datetime.now()}

    # CLI helpers -------------------------------------------------------
    @app.cli.command("init-db")
    def init_db():
        """Create all tables."""
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed")
    def seed_command():
        """Create tables and load demo data."""
        from seed import run as seed_run
        seed_run()

    return app
