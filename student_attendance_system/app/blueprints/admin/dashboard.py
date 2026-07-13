from datetime import date, datetime

from flask import render_template
from sqlalchemy import func

from app.extensions import db
from app.models import (
    Student, Teacher, Subject, Department, Schedule, AttendanceSession,
    Notification,
)
from app.models.schedule import DAYS_OF_WEEK
from app.utils import stats
from app.utils.decorators import admin_required
from . import admin_bp


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    today = date.today()
    today_name = DAYS_OF_WEEK[(today.weekday() + 1) % 7]

    totals = {
        "students": Student.query.filter_by(status="active").count(),
        "teachers": Teacher.query.filter_by(employment_status="active").count(),
        "subjects": Subject.query.count(),
        "departments": Department.query.count(),
        "classes_today": Schedule.query.filter_by(day_of_week=today_name).count(),
    }

    today_status = stats.status_totals(start=today, end=today)
    totals["present_today"] = today_status["Present"] + today_status["Late"]
    totals["absent_today"] = today_status["Absent"]
    today_total = sum(today_status.values())
    totals["today_percentage"] = stats.pct(totals["present_today"], today_total)

    low = stats.low_attendance_students(limit=8)
    totals["below_threshold"] = len(stats.low_attendance_students())
    threshold = stats.low_attendance_threshold()

    recent_sessions = (
        AttendanceSession.query
        .order_by(AttendanceSession.taken_at.desc())
        .limit(8).all()
    )

    # Classes scheduled today that have no attendance session yet
    pending = []
    for sched in Schedule.query.filter_by(day_of_week=today_name).all():
        taken = AttendanceSession.query.filter_by(
            schedule_id=sched.id, date=today
        ).first()
        if not taken:
            pending.append(sched)

    notifications = (
        Notification.query.filter(Notification.user_id.is_(None))
        .order_by(Notification.created_at.desc())
        .limit(6).all()
    )

    return render_template(
        "dashboard/admin.html",
        totals=totals, low_students=low, threshold=threshold,
        recent_sessions=recent_sessions, pending_classes=pending,
        notifications=notifications, today=today,
    )


@admin_bp.route("/analytics")
@admin_required
def analytics():
    ranking = stats.student_ranking(limit=10)
    bottom = stats.student_ranking(limit=10, ascending=True)
    return render_template(
        "admin/analytics.html", ranking=ranking, bottom=bottom,
    )
