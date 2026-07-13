from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user

from app.extensions import db
from app.models import User, Role
from app.utils.decorators import admin_required
from . import admin_bp


@admin_bp.route("/users")
@admin_required
def users():
    q = (request.args.get("q") or "").strip()
    role = request.args.get("role") or ""
    page = request.args.get("page", 1, type=int)

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(User.username.ilike(like) | User.email.ilike(like))
    if role:
        query = query.join(Role).filter(Role.name == role)

    pagination = query.order_by(User.username).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/users/list.html", pagination=pagination, q=q, role=role,
        roles=Role.query.order_by(Role.name).all(),
    )


@admin_bp.route("/users/add", methods=["GET", "POST"])
@admin_required
def user_add():
    """Create a stand-alone account (typically another administrator)."""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role_id = request.form.get("role_id", type=int)

        if not username or not email or len(password) < 6 or not role_id:
            flash("Username, email, role and a password of at least "
                  "6 characters are required.", "warning")
        elif User.query.filter(
            (User.username == username) | (User.email == email)
        ).first():
            flash("A user with this username or email already exists.", "danger")
        else:
            user = User(username=username, email=email, role_id=role_id)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("User account created.", "success")
            return redirect(url_for("admin.users"))
    return render_template(
        "admin/users/form.html", roles=Role.query.order_by(Role.name).all(),
    )


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def user_toggle(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("You cannot disable your own account.", "warning")
        return redirect(url_for("admin.users"))
    user.is_active_flag = not user.is_active_flag
    db.session.commit()
    state = "enabled" if user.is_active_flag else "disabled"
    flash(f"Account '{user.username}' {state}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def user_reset_password(user_id):
    user = db.get_or_404(User, user_id)
    new_password = request.form.get("new_password") or ""
    if len(new_password) < 6:
        flash("Password must be at least 6 characters.", "warning")
    else:
        user.set_password(new_password)
        db.session.commit()
        flash(f"Password reset for '{user.username}'.", "success")
    return redirect(url_for("admin.users"))
