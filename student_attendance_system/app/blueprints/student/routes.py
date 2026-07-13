from datetime import date

from flask import render_template, abort, request
from flask_login import current_user

from app.extensions import db
from app.models import AttendanceRecord, AttendanceSession, Subject
from app.utils import stats
from app.utils.exports import pdf_response, excel_response
from app.utils.helpers import month_bounds, parse_int
from app.utils.decorators import role_required
from . import student_bp


def current_student():
    student = current_user.student
    if student is None:
        abort(403)
    return student


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    student = current_student()
    attended, total, percentage = stats.student_overall(student.id)
    breakdown = stats.student_subject_breakdown(student.id)
    monthly = stats.student_monthly(student.id)
    recent = (
        AttendanceRecord.query.filter_by(student_id=student.id)
        .join(AttendanceSession)
        .order_by(AttendanceSession.date.desc())
        .limit(8).all()
    )
    return render_template(
        "dashboard/student.html", student=student,
        attended=attended, total=total, percentage=percentage,
        breakdown=breakdown, monthly=monthly, recent=recent,
        threshold=stats.low_attendance_threshold(),
    )


@student_bp.route("/attendance")
@role_required("student")
def attendance_history():
    student = current_student()
    page = request.args.get("page", 1, type=int)
    subject_id = request.args.get("subject_id", type=int)
    month = request.args.get("month")  # YYYY-MM

    query = (
        AttendanceRecord.query.filter_by(student_id=student.id)
        .join(AttendanceSession)
    )
    if subject_id:
        query = query.filter(AttendanceSession.subject_id == subject_id)
    if month:
        try:
            year, mon = (parse_int(x) for x in month.split("-"))
            start, end = month_bounds(year, mon)
            query = query.filter(
                AttendanceSession.date >= start, AttendanceSession.date < end,
            )
        except (ValueError, TypeError, AttributeError):
            month = None

    pagination = query.order_by(AttendanceSession.date.desc()).paginate(
        page=page, per_page=15, error_out=False,
    )
    subject_ids = {
        r["subject"].id for r in stats.student_subject_breakdown(student.id)
    }
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).order_by(
        Subject.code).all() if subject_ids else []

    return render_template(
        "student/attendance.html", pagination=pagination,
        subjects=subjects, subject_id=subject_id, month=month or "",
    )


@student_bp.route("/subjects")
@role_required("student")
def subjects():
    student = current_student()
    breakdown = stats.student_subject_breakdown(student.id)
    return render_template(
        "student/subjects.html", breakdown=breakdown,
        threshold=stats.low_attendance_threshold(),
    )


@student_bp.route("/report")
@role_required("student")
def report():
    """Downloadable personal attendance report (PDF / Excel)."""
    student = current_student()
    attended, total, percentage = stats.student_overall(student.id)
    breakdown = stats.student_subject_breakdown(student.id)

    headers = ["Subject", "Attended", "Total Classes", "Percentage"]
    rows = [
        [r["subject"].label, r["attended"], r["total"], f'{r["percentage"]}%']
        for r in breakdown
    ]
    rows.append(["Overall", attended, total, f"{percentage}%"])
    title = f"Attendance Report — {student.full_name} ({student.roll_number})"
    filename = f"my_attendance_{student.roll_number}"

    if request.args.get("format") == "excel":
        return excel_response(title, headers, rows, filename)
    return pdf_response(title, headers, rows, filename)
