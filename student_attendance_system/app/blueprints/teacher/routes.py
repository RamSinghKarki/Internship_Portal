from datetime import date

from flask import render_template, abort, request
from flask_login import current_user
from sqlalchemy import func

from app.extensions import db
from app.models import (
    AttendanceSession, AttendanceRecord, Schedule, Student, Subject,
)
from app.models.schedule import DAYS_OF_WEEK
from app.utils import stats
from app.utils.decorators import role_required
from . import teacher_bp


def current_teacher():
    teacher = current_user.teacher
    if teacher is None:
        abort(403)
    return teacher


@teacher_bp.route("/dashboard")
@role_required("teacher")
def dashboard():
    teacher = current_teacher()
    today = date.today()
    today_name = DAYS_OF_WEEK[(today.weekday() + 1) % 7]

    todays_classes = (
        Schedule.query.filter_by(teacher_id=teacher.id, day_of_week=today_name)
        .order_by(Schedule.start_time).all()
    )
    taken_ids = {
        s.schedule_id for s in AttendanceSession.query.filter_by(
            teacher_id=teacher.id, date=today).all()
    }

    session_count = teacher.sessions.count()
    assignment_count = teacher.assignments.count()
    recent = (
        teacher.sessions.order_by(AttendanceSession.taken_at.desc()).limit(6).all()
    )

    # Low-attendance students in this teacher's subjects
    subject_ids = [a.subject_id for a in teacher.assignments.all()]
    low = []
    if subject_ids:
        threshold = stats.low_attendance_threshold()
        rows = (
            db.session.query(
                Student,
                func.coalesce(func.sum(stats.present_like_case), 0),
                func.count(AttendanceRecord.id),
            )
            .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .filter(AttendanceSession.subject_id.in_(subject_ids))
            .group_by(Student.id)
            .all()
        )
        for student, attended, total in rows:
            p = stats.pct(attended, total)
            if p < threshold:
                low.append({"student": student, "percentage": p,
                            "attended": int(attended), "total": int(total)})
        low.sort(key=lambda r: r["percentage"])

    return render_template(
        "dashboard/teacher.html", teacher=teacher,
        todays_classes=todays_classes, taken_ids=taken_ids,
        session_count=session_count, assignment_count=assignment_count,
        recent=recent, low_students=low[:8], today=today,
    )


@teacher_bp.route("/subjects")
@role_required("teacher")
def subjects():
    teacher = current_teacher()
    assignments = teacher.assignments.all()
    rows = []
    for a in assignments:
        classes = AttendanceSession.query.filter_by(
            subject_id=a.subject_id, section_id=a.section_id,
            teacher_id=teacher.id,
        ).count()
        rows.append({"assignment": a, "classes": classes})
    return render_template("teacher/subjects.html", rows=rows)


@teacher_bp.route("/schedule")
@role_required("teacher")
def schedule():
    teacher = current_teacher()
    rows = teacher.schedules.order_by(Schedule.start_time).all()
    grid = {day: [] for day in DAYS_OF_WEEK}
    for s in rows:
        grid[s.day_of_week].append(s)
    return render_template("teacher/schedule.html", grid=grid, days=DAYS_OF_WEEK)


@teacher_bp.route("/reports")
@role_required("teacher")
def reports():
    """Subject-wise attendance reports for this teacher's own subjects."""
    teacher = current_teacher()
    subject_id = request.args.get("subject_id", type=int)

    assignments = teacher.assignments.all()
    subject_map = {}
    for a in assignments:
        subject_map[a.subject_id] = a.subject
    subjects = sorted(subject_map.values(), key=lambda s: s.code)

    report = None
    subject = None
    if subject_id and subject_id in subject_map:
        subject = subject_map[subject_id]
        rows = (
            db.session.query(
                Student,
                func.coalesce(func.sum(stats.present_like_case), 0),
                func.count(AttendanceRecord.id),
            )
            .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .filter(AttendanceSession.subject_id == subject_id,
                    AttendanceSession.teacher_id == teacher.id)
            .group_by(Student.id)
            .order_by(Student.roll_number)
            .all()
        )
        report = [
            {"student": s, "attended": int(a), "total": int(t),
             "percentage": stats.pct(a, t)}
            for s, a, t in rows
        ]

    return render_template(
        "teacher/reports.html", subjects=subjects, subject=subject,
        report=report, threshold=stats.low_attendance_threshold(),
    )
