from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Subject, Department, Semester
from app.utils.helpers import parse_int
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(subject):
    subject.code = (request.form.get("code") or "").strip().upper()
    subject.name = (request.form.get("name") or "").strip()
    subject.credit_hours = parse_int(request.form.get("credit_hours"), 3)
    subject.department_id = parse_int(request.form.get("department_id"))
    subject.semester_id = parse_int(request.form.get("semester_id"))
    if not all([subject.code, subject.name, subject.department_id, subject.semester_id]):
        flash("Code, name, department and semester are required.", "warning")
        return False
    clash = Subject.query.filter_by(code=subject.code).filter(
        Subject.id != subject.id).first()
    if clash:
        flash("A subject with this code already exists.", "danger")
        return False
    return True


def _context():
    return {
        "departments": Department.query.order_by(Department.name).all(),
        "semesters": Semester.query.order_by(
            Semester.academic_year.desc(), Semester.name).all(),
    }


@admin_bp.route("/subjects")
@admin_required
def subjects():
    q = (request.args.get("q") or "").strip()
    department_id = request.args.get("department_id", type=int)
    semester_id = request.args.get("semester_id", type=int)
    page = request.args.get("page", 1, type=int)

    query = Subject.query
    if q:
        like = f"%{q}%"
        query = query.filter(Subject.name.ilike(like) | Subject.code.ilike(like))
    if department_id:
        query = query.filter_by(department_id=department_id)
    if semester_id:
        query = query.filter_by(semester_id=semester_id)

    pagination = query.order_by(Subject.code).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/subjects/list.html", pagination=pagination, q=q,
        department_id=department_id, semester_id=semester_id, **_context(),
    )


@admin_bp.route("/subjects/add", methods=["GET", "POST"])
@admin_required
def subject_add():
    if request.method == "POST":
        subject = Subject()
        if _fill(subject):
            db.session.add(subject)
            db.session.commit()
            flash("Subject created.", "success")
            return redirect(url_for("admin.subjects"))
    return render_template("admin/subjects/form.html", subject=None, **_context())


@admin_bp.route("/subjects/<int:subject_id>/edit", methods=["GET", "POST"])
@admin_required
def subject_edit(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    if request.method == "POST":
        if _fill(subject):
            db.session.commit()
            flash("Subject updated.", "success")
            return redirect(url_for("admin.subjects"))
        db.session.rollback()
    return render_template("admin/subjects/form.html", subject=subject, **_context())


@admin_bp.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@admin_required
def subject_delete(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "success")
    return redirect(url_for("admin.subjects"))
