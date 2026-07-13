"""Report centre: student / teacher / subject / department reports with
printable, PDF and Excel outputs."""
from datetime import date

from flask import render_template, request
from sqlalchemy import func

from app.extensions import db
from app.models import (
    Student, Teacher, Subject, Department, AttendanceSession, AttendanceRecord,
)
from app.utils import stats
from app.utils.exports import pdf_response, excel_response
from app.utils.decorators import admin_required
from . import admin_bp


@admin_bp.route("/reports")
@admin_required
def reports():
    return render_template(
        "reports/index.html",
        students=Student.query.order_by(Student.roll_number).all(),
        teachers=Teacher.query.order_by(Teacher.full_name).all(),
        subjects=Subject.query.order_by(Subject.code).all(),
        departments=Department.query.order_by(Department.name).all(),
    )


# ------------------------------------------------------------------ student
def _student_report_data(student):
    attended, total, percentage = stats.student_overall(student.id)
    breakdown = stats.student_subject_breakdown(student.id)
    monthly = stats.student_monthly(student.id, months=12)
    return attended, total, percentage, breakdown, monthly


@admin_bp.route("/reports/student/<int:student_id>")
@admin_required
def report_student(student_id):
    student = db.get_or_404(Student, student_id)
    attended, total, percentage, breakdown, monthly = _student_report_data(student)
    fmt = request.args.get("format")

    if fmt in ("pdf", "excel"):
        headers = ["Subject", "Attended", "Total Classes", "Percentage"]
        rows = [
            [r["subject"].label, r["attended"], r["total"], f'{r["percentage"]}%']
            for r in breakdown
        ]
        rows.append(["Overall", attended, total, f"{percentage}%"])
        title = f"Attendance Report — {student.full_name} ({student.roll_number})"
        filename = f"student_attendance_{student.roll_number}"
        if fmt == "pdf":
            return pdf_response(title, headers, rows, filename)
        return excel_response(title, headers, rows, filename)

    return render_template(
        "reports/student.html", student=student, attended=attended,
        total=total, percentage=percentage, breakdown=breakdown,
        monthly=monthly, threshold=stats.low_attendance_threshold(),
        print_view=request.args.get("print") == "1",
    )


# ------------------------------------------------------------------ teacher
@admin_bp.route("/reports/teacher/<int:teacher_id>")
@admin_required
def report_teacher(teacher_id):
    teacher = db.get_or_404(Teacher, teacher_id)
    sessions = teacher.sessions.order_by(AttendanceSession.date.desc()).all()
    assignments = teacher.assignments.all()

    monthly = {}
    for s in sessions:
        key = s.date.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + 1
    monthly_rows = sorted(monthly.items())

    fmt = request.args.get("format")
    if fmt in ("pdf", "excel"):
        headers = ["Date", "Subject", "Section", "Present", "Total"]
        rows = [
            [s.date.isoformat(), s.subject.label if s.subject else "-",
             s.section.name if s.section else "-", s.present_count, s.total_count]
            for s in sessions
        ]
        title = f"Teacher Report — {teacher.full_name} ({teacher.employee_id})"
        filename = f"teacher_report_{teacher.employee_id}"
        if fmt == "pdf":
            return pdf_response(title, headers, rows, filename)
        return excel_response(title, headers, rows, filename)

    return render_template(
        "reports/teacher.html", teacher=teacher, sessions=sessions[:50],
        session_count=len(sessions), assignments=assignments,
        monthly_rows=monthly_rows,
        print_view=request.args.get("print") == "1",
    )


# ------------------------------------------------------------------ subject
@admin_bp.route("/reports/subject/<int:subject_id>")
@admin_required
def report_subject(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    total_classes = AttendanceSession.query.filter_by(subject_id=subject.id).count()

    rows = (
        db.session.query(
            Student,
            func.coalesce(func.sum(stats.present_like_case), 0),
            func.count(AttendanceRecord.id),
        )
        .join(AttendanceRecord, AttendanceRecord.student_id == Student.id)
        .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
        .filter(AttendanceSession.subject_id == subject.id)
        .group_by(Student.id)
        .order_by(Student.roll_number)
        .all()
    )
    students = [
        {"student": s, "attended": int(a), "total": int(t),
         "percentage": stats.pct(a, t)}
        for s, a, t in rows
    ]
    avg = round(sum(r["percentage"] for r in students) / len(students), 2) if students else 0
    threshold = stats.low_attendance_threshold()
    low = [r for r in students if r["percentage"] < threshold]

    fmt = request.args.get("format")
    if fmt in ("pdf", "excel"):
        headers = ["Roll No", "Student", "Attended", "Total", "Percentage"]
        data = [
            [r["student"].roll_number, r["student"].full_name,
             r["attended"], r["total"], f'{r["percentage"]}%']
            for r in students
        ]
        title = f"Subject Report — {subject.label}"
        filename = f"subject_report_{subject.code}"
        if fmt == "pdf":
            return pdf_response(title, headers, data, filename,
                                subtitle=f"Total classes conducted: {total_classes}")
        return excel_response(title, headers, data, filename)

    return render_template(
        "reports/subject.html", subject=subject, total_classes=total_classes,
        students=students, avg=avg, low=low, threshold=threshold,
        print_view=request.args.get("print") == "1",
    )


# --------------------------------------------------------------- department
@admin_bp.route("/reports/department/<int:dept_id>")
@admin_required
def report_department(dept_id):
    dept = db.get_or_404(Department, dept_id)
    subjects = dept.subjects.order_by(Subject.code).all()

    subject_rows = []
    for subject in subjects:
        agg = (
            db.session.query(
                func.coalesce(func.sum(stats.present_like_case), 0),
                func.count(AttendanceRecord.id),
            )
            .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)
            .filter(AttendanceSession.subject_id == subject.id)
            .one()
        )
        classes = AttendanceSession.query.filter_by(subject_id=subject.id).count()
        subject_rows.append({
            "subject": subject, "classes": classes,
            "percentage": stats.pct(agg[0], agg[1]),
        })

    trend = stats.monthly_trend(months=6, department_id=dept.id)
    low = stats.low_attendance_students(department_id=dept.id)

    fmt = request.args.get("format")
    if fmt in ("pdf", "excel"):
        headers = ["Subject", "Classes Conducted", "Average Attendance"]
        data = [
            [r["subject"].label, r["classes"], f'{r["percentage"]}%']
            for r in subject_rows
        ]
        title = f"Department Report — {dept.name}"
        filename = f"department_report_{dept.code}"
        if fmt == "pdf":
            return pdf_response(title, headers, data, filename)
        return excel_response(title, headers, data, filename)

    return render_template(
        "reports/department.html", dept=dept, subject_rows=subject_rows,
        trend=trend, low=low, threshold=stats.low_attendance_threshold(),
        print_view=request.args.get("print") == "1",
    )
