"""Admin-side attendance monitoring and history."""
from flask import render_template, request, current_app

from app.extensions import db
from app.models import (
    AttendanceSession, Department, Semester, Section, Subject, Teacher,
)
from app.utils.helpers import parse_date
from app.utils.decorators import admin_required
from . import admin_bp


@admin_bp.route("/attendance")
@admin_required
def attendance_history():
    page = request.args.get("page", 1, type=int)
    date_from = parse_date(request.args.get("date_from"))
    date_to = parse_date(request.args.get("date_to"))
    department_id = request.args.get("department_id", type=int)
    semester_id = request.args.get("semester_id", type=int)
    section_id = request.args.get("section_id", type=int)
    subject_id = request.args.get("subject_id", type=int)
    teacher_id = request.args.get("teacher_id", type=int)

    query = AttendanceSession.query
    if date_from:
        query = query.filter(AttendanceSession.date >= date_from)
    if date_to:
        query = query.filter(AttendanceSession.date <= date_to)
    if department_id:
        query = query.join(Subject).filter(Subject.department_id == department_id)
    if semester_id:
        query = query.filter(AttendanceSession.semester_id == semester_id)
    if section_id:
        query = query.filter(AttendanceSession.section_id == section_id)
    if subject_id:
        query = query.filter(AttendanceSession.subject_id == subject_id)
    if teacher_id:
        query = query.filter(AttendanceSession.teacher_id == teacher_id)

    pagination = query.order_by(
        AttendanceSession.date.desc(), AttendanceSession.taken_at.desc()
    ).paginate(page=page, per_page=current_app.config["PER_PAGE"], error_out=False)

    return render_template(
        "attendance/history.html",
        pagination=pagination,
        departments=Department.query.order_by(Department.name).all(),
        semesters=Semester.query.order_by(
            Semester.academic_year.desc(), Semester.name).all(),
        sections=Section.query.order_by(Section.name).all(),
        subjects=Subject.query.order_by(Subject.code).all(),
        teachers=Teacher.query.order_by(Teacher.full_name).all(),
        filters={
            "date_from": request.args.get("date_from", ""),
            "date_to": request.args.get("date_to", ""),
            "department_id": department_id, "semester_id": semester_id,
            "section_id": section_id, "subject_id": subject_id,
            "teacher_id": teacher_id,
        },
        base_endpoint="admin.attendance_history",
    )


@admin_bp.route("/attendance/<int:session_id>")
@admin_required
def attendance_view(session_id):
    session = db.get_or_404(AttendanceSession, session_id)
    records = sorted(session.records, key=lambda r: r.student.roll_number)
    return render_template(
        "attendance/view.html", session=session, records=records,
        can_edit=False,
    )
