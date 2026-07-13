"""JSON endpoints: cascading dropdowns and Chart.js data sources."""
from datetime import date

from flask import jsonify, request
from flask_login import login_required, current_user

from app.models import Semester, Section, Subject, TeacherSubjectAssignment
from app.utils import stats
from app.utils.decorators import teacher_required, admin_required
from . import api_bp


# ---------------------------------------------------------------- dropdowns
@api_bp.route("/sections")
@login_required
def sections():
    semester_id = request.args.get("semester_id", type=int)
    q = Section.query
    if semester_id:
        q = q.filter_by(semester_id=semester_id)
    return jsonify([
        {"id": s.id, "name": s.name} for s in q.order_by(Section.name).all()
    ])


@api_bp.route("/subjects")
@login_required
def subjects():
    q = Subject.query
    semester_id = request.args.get("semester_id", type=int)
    department_id = request.args.get("department_id", type=int)
    section_id = request.args.get("section_id", type=int)
    if semester_id:
        q = q.filter_by(semester_id=semester_id)
    if department_id:
        q = q.filter_by(department_id=department_id)

    # Teachers only see subjects assigned to them for the chosen section.
    if current_user.is_teacher() and current_user.teacher:
        assigned = TeacherSubjectAssignment.query.filter_by(
            teacher_id=current_user.teacher.id
        )
        if section_id:
            assigned = assigned.filter_by(section_id=section_id)
        subject_ids = {a.subject_id for a in assigned.all()}
        q = q.filter(Subject.id.in_(subject_ids)) if subject_ids else q.filter(False)

    return jsonify([
        {"id": s.id, "label": s.label} for s in q.order_by(Subject.code).all()
    ])


@api_bp.route("/semesters")
@login_required
def semesters():
    rows = Semester.query.order_by(
        Semester.academic_year.desc(), Semester.name
    ).all()
    return jsonify([{"id": s.id, "label": s.label} for s in rows])


# ---------------------------------------------------------------- chart data
@api_bp.route("/charts/monthly-trend")
@teacher_required
def chart_monthly_trend():
    return jsonify(stats.monthly_trend(months=int(request.args.get("months", 6))))


@api_bp.route("/charts/department-comparison")
@admin_required
def chart_department_comparison():
    return jsonify(stats.department_comparison())


@api_bp.route("/charts/subject-comparison")
@teacher_required
def chart_subject_comparison():
    teacher_id = None
    if current_user.is_teacher() and current_user.teacher:
        teacher_id = current_user.teacher.id
    return jsonify(stats.subject_comparison(teacher_id=teacher_id))


@api_bp.route("/charts/semester-comparison")
@admin_required
def chart_semester_comparison():
    return jsonify(stats.semester_comparison())


@api_bp.route("/charts/status-totals")
@teacher_required
def chart_status_totals():
    teacher_id = None
    if current_user.is_teacher() and current_user.teacher:
        teacher_id = current_user.teacher.id
    return jsonify(stats.status_totals(teacher_id=teacher_id))


@api_bp.route("/charts/teacher-sessions")
@admin_required
def chart_teacher_sessions():
    return jsonify(stats.teacher_session_counts())


@api_bp.route("/charts/daily-trend")
@teacher_required
def chart_daily_trend():
    return jsonify(stats.daily_trend(days=int(request.args.get("days", 14))))


@api_bp.route("/charts/weekday-heatmap")
@admin_required
def chart_weekday_heatmap():
    return jsonify(stats.weekday_heatmap())


@api_bp.route("/charts/today-status")
@admin_required
def chart_today_status():
    today = date.today()
    return jsonify(stats.status_totals(start=today, end=today))
