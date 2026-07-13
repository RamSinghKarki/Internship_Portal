from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import (
    TeacherSubjectAssignment, Teacher, Subject, Semester, Section, Setting,
)
from app.utils.helpers import parse_int
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(assignment):
    assignment.teacher_id = parse_int(request.form.get("teacher_id"))
    assignment.subject_id = parse_int(request.form.get("subject_id"))
    assignment.semester_id = parse_int(request.form.get("semester_id"))
    assignment.section_id = parse_int(request.form.get("section_id"))
    assignment.academic_year = (request.form.get("academic_year")
                                or Setting.get("academic_year", "")).strip()
    if not all([assignment.teacher_id, assignment.subject_id,
                assignment.semester_id, assignment.section_id,
                assignment.academic_year]):
        flash("All fields are required.", "warning")
        return False
    clash = TeacherSubjectAssignment.query.filter_by(
        subject_id=assignment.subject_id,
        section_id=assignment.section_id,
        semester_id=assignment.semester_id,
        academic_year=assignment.academic_year,
    ).filter(TeacherSubjectAssignment.id != assignment.id).first()
    if clash:
        flash("This subject already has a teacher assigned for that "
              "section and academic year.", "danger")
        return False
    return True


def _context():
    return {
        "teachers": Teacher.query.filter_by(employment_status="active")
                    .order_by(Teacher.full_name).all(),
        "subjects": Subject.query.order_by(Subject.code).all(),
        "semesters": Semester.query.order_by(
            Semester.academic_year.desc(), Semester.name).all(),
        "sections": Section.query.order_by(Section.name).all(),
        "default_year": Setting.get("academic_year", ""),
    }


@admin_bp.route("/assignments")
@admin_required
def assignments():
    teacher_id = request.args.get("teacher_id", type=int)
    subject_id = request.args.get("subject_id", type=int)
    page = request.args.get("page", 1, type=int)

    query = TeacherSubjectAssignment.query
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    pagination = query.order_by(TeacherSubjectAssignment.id.desc()).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/assignments/list.html", pagination=pagination,
        teacher_id=teacher_id, subject_id=subject_id, **_context(),
    )


@admin_bp.route("/assignments/add", methods=["GET", "POST"])
@admin_required
def assignment_add():
    if request.method == "POST":
        assignment = TeacherSubjectAssignment()
        if _fill(assignment):
            db.session.add(assignment)
            db.session.commit()
            flash("Subject assigned to teacher.", "success")
            return redirect(url_for("admin.assignments"))
    return render_template("admin/assignments/form.html", assignment=None, **_context())


@admin_bp.route("/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
@admin_required
def assignment_edit(assignment_id):
    assignment = db.get_or_404(TeacherSubjectAssignment, assignment_id)
    if request.method == "POST":
        if _fill(assignment):
            db.session.commit()
            flash("Assignment updated.", "success")
            return redirect(url_for("admin.assignments"))
        db.session.rollback()
    return render_template("admin/assignments/form.html", assignment=assignment, **_context())


@admin_bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@admin_required
def assignment_delete(assignment_id):
    assignment = db.get_or_404(TeacherSubjectAssignment, assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment removed.", "success")
    return redirect(url_for("admin.assignments"))
