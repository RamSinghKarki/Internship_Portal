from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User
from . import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        identifier = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "danger")
        elif not user.is_active_flag:
            flash("This account has been disabled. Contact the administrator.", "warning")
        else:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_pw = request.form.get("current_password") or ""
        new_pw = request.form.get("new_password") or ""
        confirm = request.form.get("confirm_password") or ""

        if not current_user.check_password(current_pw):
            flash("Current password is incorrect.", "danger")
        elif len(new_pw) < 6:
            flash("New password must be at least 6 characters.", "warning")
        elif new_pw != confirm:
            flash("New password and confirmation do not match.", "warning")
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html")
