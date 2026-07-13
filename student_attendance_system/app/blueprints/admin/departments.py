from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Department
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(dept):
    dept.name = (request.form.get("name") or "").strip()
    dept.code = (request.form.get("code") or "").strip().upper()
    dept.head_of_department = (request.form.get("head_of_department") or "").strip()
    dept.description = (request.form.get("description") or "").strip()
    if not dept.name or not dept.code:
        flash("Department name and code are required.", "warning")
        return False
    clash = Department.query.filter(
        (Department.name == dept.name) | (Department.code == dept.code)
    ).filter(Department.id != dept.id).first()
    if clash:
        flash("A department with this name or code already exists.", "danger")
        return False
    return True


@admin_bp.route("/departments")
@admin_required
def departments():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    query = Department.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            Department.name.ilike(like) | Department.code.ilike(like)
        )
    pagination = query.order_by(Department.name).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/departments/list.html", pagination=pagination, q=q,
    )


@admin_bp.route("/departments/add", methods=["GET", "POST"])
@admin_required
def department_add():
    if request.method == "POST":
        dept = Department()
        if _fill(dept):
            db.session.add(dept)
            db.session.commit()
            flash("Department created.", "success")
            return redirect(url_for("admin.departments"))
    return render_template("admin/departments/form.html", dept=None)


@admin_bp.route("/departments/<int:dept_id>/edit", methods=["GET", "POST"])
@admin_required
def department_edit(dept_id):
    dept = db.get_or_404(Department, dept_id)
    if request.method == "POST":
        if _fill(dept):
            db.session.commit()
            flash("Department updated.", "success")
            return redirect(url_for("admin.departments"))
        db.session.rollback()
    return render_template("admin/departments/form.html", dept=dept)


@admin_bp.route("/departments/<int:dept_id>/delete", methods=["POST"])
@admin_required
def department_delete(dept_id):
    dept = db.get_or_404(Department, dept_id)
    if dept.students.count() or dept.teachers.count() or dept.subjects.count():
        flash("Cannot delete a department that still has students, teachers or subjects.", "danger")
        return redirect(url_for("admin.departments"))
    db.session.delete(dept)
    db.session.commit()
    flash("Department deleted.", "success")
    return redirect(url_for("admin.departments"))
