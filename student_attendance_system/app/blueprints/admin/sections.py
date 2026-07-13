from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Section, Semester
from app.utils.helpers import parse_int
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(section):
    section.name = (request.form.get("name") or "").strip()
    section.semester_id = parse_int(request.form.get("semester_id"))
    section.capacity = parse_int(request.form.get("capacity"), 60)
    if not section.name or not section.semester_id:
        flash("Section name and semester are required.", "warning")
        return False
    clash = Section.query.filter_by(
        name=section.name, semester_id=section.semester_id
    ).filter(Section.id != section.id).first()
    if clash:
        flash("This section already exists in the selected semester.", "danger")
        return False
    return True


@admin_bp.route("/sections")
@admin_required
def sections():
    q = (request.args.get("q") or "").strip()
    semester_id = request.args.get("semester_id", type=int)
    page = request.args.get("page", 1, type=int)
    query = Section.query
    if q:
        query = query.filter(Section.name.ilike(f"%{q}%"))
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    pagination = query.order_by(Section.semester_id.desc(), Section.name).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    semesters = Semester.query.order_by(
        Semester.academic_year.desc(), Semester.name).all()
    return render_template(
        "admin/sections/list.html", pagination=pagination, q=q,
        semesters=semesters, semester_id=semester_id,
    )


@admin_bp.route("/sections/add", methods=["GET", "POST"])
@admin_required
def section_add():
    if request.method == "POST":
        section = Section()
        if _fill(section):
            db.session.add(section)
            db.session.commit()
            flash("Section created.", "success")
            return redirect(url_for("admin.sections"))
    semesters = Semester.query.order_by(
        Semester.academic_year.desc(), Semester.name).all()
    return render_template("admin/sections/form.html", section=None, semesters=semesters)


@admin_bp.route("/sections/<int:section_id>/edit", methods=["GET", "POST"])
@admin_required
def section_edit(section_id):
    section = db.get_or_404(Section, section_id)
    if request.method == "POST":
        if _fill(section):
            db.session.commit()
            flash("Section updated.", "success")
            return redirect(url_for("admin.sections"))
        db.session.rollback()
    semesters = Semester.query.order_by(
        Semester.academic_year.desc(), Semester.name).all()
    return render_template("admin/sections/form.html", section=section, semesters=semesters)


@admin_bp.route("/sections/<int:section_id>/delete", methods=["POST"])
@admin_required
def section_delete(section_id):
    section = db.get_or_404(Section, section_id)
    if section.students.count():
        flash("Cannot delete a section that still has students.", "danger")
        return redirect(url_for("admin.sections"))
    db.session.delete(section)
    db.session.commit()
    flash("Section deleted.", "success")
    return redirect(url_for("admin.sections"))
