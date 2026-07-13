"""Attendance aggregation queries shared by dashboards, reports and analytics."""
from datetime import date, timedelta

from sqlalchemy import func, case

from app.extensions import db
from app.models import (
    AttendanceRecord, AttendanceSession, Student, Subject, Department,
    Semester, Section, Teacher, Setting,
)
from app.models.attendance import PRESENT_LIKE

present_like_case = case(
    (AttendanceRecord.status.in_(PRESENT_LIKE), 1), else_=0
)


def pct(present, total):
    return round(present * 100.0 / total, 2) if total else 0.0


def low_attendance_threshold():
    try:
        return float(Setting.get("low_attendance_threshold", "75"))
    except (TypeError, ValueError):
        return 75.0


# ----------------------------------------------------------------------
def student_overall(student_id, subject_id=None, start=None, end=None):
    """Return (attended, total, percentage) for a student."""
    q = (
        db.session.query(
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceRecord.student_id == student_id)
    )
    if subject_id:
        q = q.filter(AttendanceSession.subject_id == subject_id)
    if start:
        q = q.filter(AttendanceSession.date >= start)
    if end:
        q = q.filter(AttendanceSession.date <= end)
    attended, total = q.one()
    return int(attended), int(total), pct(attended, total)


def student_subject_breakdown(student_id):
    """Per-subject attendance rows for a student."""
    rows = (
        db.session.query(
            Subject,
            func.coalesce(func.sum(present_like_case), 0).label("attended"),
            func.count(AttendanceRecord.id).label("total"),
        )
        .join(AttendanceSession, AttendanceSession.subject_id == Subject.id)
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceRecord.student_id == student_id)
        .group_by(Subject.id)
        .order_by(Subject.code)
        .all()
    )
    return [
        {"subject": s, "attended": int(a), "total": int(t), "percentage": pct(a, t)}
        for s, a, t in rows
    ]


def student_monthly(student_id, months=6):
    """[(YYYY-MM, attended, total, pct)] for the last N months."""
    month_col = _month_expr(AttendanceSession.date)
    rows = (
        db.session.query(
            month_col.label("month"),
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceRecord.student_id == student_id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [
        {"month": m, "attended": int(a), "total": int(t), "percentage": pct(a, t)}
        for m, a, t in rows[-months:]
    ]


# ----------------------------------------------------------------------
def _month_expr(col):
    """Portable YYYY-MM expression for SQLite and MySQL."""
    dialect = db.engine.dialect.name
    if dialect == "sqlite":
        return func.strftime("%Y-%m", col)
    return func.date_format(col, "%Y-%m")


def monthly_trend(months=6, department_id=None):
    month_col = _month_expr(AttendanceSession.date)
    q = (
        db.session.query(
            month_col.label("month"),
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
    )
    if department_id:
        q = (q.join(Subject, AttendanceSession.subject_id == Subject.id)
              .filter(Subject.department_id == department_id))
    rows = q.group_by("month").order_by("month").all()
    return [
        {"month": m, "percentage": pct(a, t), "attended": int(a), "total": int(t)}
        for m, a, t in rows[-months:]
    ]


def department_comparison():
    rows = (
        db.session.query(
            Department.name,
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(Subject, Subject.department_id == Department.id)
        .join(AttendanceSession, AttendanceSession.subject_id == Subject.id)
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .group_by(Department.id)
        .order_by(Department.name)
        .all()
    )
    return [{"label": n, "percentage": pct(a, t)} for n, a, t in rows]


def subject_comparison(limit=12, teacher_id=None):
    q = (
        db.session.query(
            Subject.code,
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceSession, AttendanceSession.subject_id == Subject.id)
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
    )
    if teacher_id:
        q = q.filter(AttendanceSession.teacher_id == teacher_id)
    rows = q.group_by(Subject.id).order_by(Subject.code).limit(limit).all()
    return [{"label": c, "percentage": pct(a, t)} for c, a, t in rows]


def semester_comparison():
    rows = (
        db.session.query(
            Semester.name, Semester.academic_year,
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceSession, AttendanceSession.semester_id == Semester.id)
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .group_by(Semester.id)
        .order_by(Semester.academic_year, Semester.name)
        .all()
    )
    return [{"label": f"{n} ({y})", "percentage": pct(a, t)} for n, y, a, t in rows]


def teacher_session_counts(limit=10):
    rows = (
        db.session.query(Teacher.full_name, func.count(AttendanceSession.id))
        .join(AttendanceSession, AttendanceSession.teacher_id == Teacher.id)
        .group_by(Teacher.id)
        .order_by(func.count(AttendanceSession.id).desc())
        .limit(limit)
        .all()
    )
    return [{"label": n, "count": int(c)} for n, c in rows]


def status_totals(start=None, end=None, teacher_id=None):
    q = (
        db.session.query(AttendanceRecord.status, func.count(AttendanceRecord.id))
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
    )
    if start:
        q = q.filter(AttendanceSession.date >= start)
    if end:
        q = q.filter(AttendanceSession.date <= end)
    if teacher_id:
        q = q.filter(AttendanceSession.teacher_id == teacher_id)
    out = {"Present": 0, "Absent": 0, "Late": 0, "Leave": 0}
    for status, count in q.group_by(AttendanceRecord.status).all():
        out[status] = int(count)
    return out


def daily_trend(days=14):
    start = date.today() - timedelta(days=days - 1)
    rows = (
        db.session.query(
            AttendanceSession.date,
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceSession.date >= start)
        .group_by(AttendanceSession.date)
        .order_by(AttendanceSession.date)
        .all()
    )
    return [
        {"label": d.strftime("%Y-%m-%d"), "percentage": pct(a, t)}
        for d, a, t in rows
    ]


def low_attendance_students(threshold=None, limit=None, subject_id=None,
                            department_id=None, min_sessions=1):
    """Students whose overall attendance percentage is below the threshold."""
    threshold = threshold if threshold is not None else low_attendance_threshold()
    q = (
        db.session.query(
            Student,
            func.coalesce(func.sum(present_like_case), 0).label("attended"),
            func.count(AttendanceRecord.id).label("total"),
        )
        .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
    )
    if subject_id:
        q = q.filter(AttendanceSession.subject_id == subject_id)
    if department_id:
        q = q.filter(Student.department_id == department_id)
    rows = (
        q.group_by(Student.id)
        .having(func.count(AttendanceRecord.id) >= min_sessions)
        .all()
    )
    result = []
    for student, attended, total in rows:
        p = pct(attended, total)
        if p < threshold:
            result.append({
                "student": student, "attended": int(attended),
                "total": int(total), "percentage": p,
            })
    result.sort(key=lambda r: r["percentage"])
    return result[:limit] if limit else result


def student_ranking(limit=10, ascending=False):
    rows = (
        db.session.query(
            Student,
            func.coalesce(func.sum(present_like_case), 0).label("attended"),
            func.count(AttendanceRecord.id).label("total"),
        )
        .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
        .group_by(Student.id)
        .having(func.count(AttendanceRecord.id) > 0)
        .all()
    )
    ranked = [
        {"student": s, "attended": int(a), "total": int(t), "percentage": pct(a, t)}
        for s, a, t in rows
    ]
    ranked.sort(key=lambda r: r["percentage"], reverse=not ascending)
    return ranked[:limit]


def weekday_heatmap():
    """Attendance percentage per weekday (for the heatmap-style chart)."""
    rows = (
        db.session.query(
            AttendanceSession.date,
            func.coalesce(func.sum(present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceRecord, AttendanceRecord.session_id == AttendanceSession.id)
        .group_by(AttendanceSession.date)
        .all()
    )
    buckets = {}  # weekday index -> [attended, total]
    for d, a, t in rows:
        b = buckets.setdefault(d.weekday(), [0, 0])
        b[0] += int(a)
        b[1] += int(t)
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [
        {"label": names[i], "percentage": pct(*buckets[i])}
        for i in sorted(buckets)
    ]
