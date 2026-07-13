"""Attendance taking / editing flow for teachers.

Flow: pick semester -> section -> subject -> date -> class period, the
enrolled students load automatically, marks are saved in one POST.
"""
from datetime import date

from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user

from app.extensions import db
from app.models import (
    AttendanceSession, AttendanceRecord, Schedule, Student, Subject,
    Section, Semester, TeacherSubjectAssignment, Setting, Notification,
)
from app.models.attendance import ATTENDANCE_STATUSES
from app.utils.helpers import parse_date, parse_int
from app.utils.decorators import role_required
from app.utils import stats
from . import teacher_bp
from .routes import current_teacher


def _teacher_assignment(teacher, subject_id, section_id):
    return TeacherSubjectAssignment.query.filter_by(
        teacher_id=teacher.id, subject_id=subject_id, section_id=section_id,
    ).first()


@teacher_bp.route("/attendance/take", methods=["GET"])
@role_required("teacher")
def attendance_take():
    """Selection screen + roster once all filters are chosen."""
    teacher = current_teacher()

    semester_id = request.args.get("semester_id", type=int)
    section_id = request.args.get("section_id", type=int)
    subject_id = request.args.get("subject_id", type=int)
    schedule_id = request.args.get("schedule_id", type=int)
    the_date = parse_date(request.args.get("date")) or date.today()

    assignments = teacher.assignments.all()
    semesters = sorted(
        {a.semester for a in assignments}, key=lambda s: (s.academic_year, s.name),
        reverse=True,
    )
    sections = sorted(
        {a.section for a in assignments if not semester_id or a.semester_id == semester_id},
        key=lambda s: s.name,
    )
    subjects = sorted(
        {a.subject for a in assignments
         if (not semester_id or a.semester_id == semester_id)
         and (not section_id or a.section_id == section_id)},
        key=lambda s: s.code,
    )

    periods = []
    if subject_id and section_id:
        periods = (
            Schedule.query.filter_by(
                subject_id=subject_id, section_id=section_id, teacher_id=teacher.id,
            ).order_by(Schedule.day_of_week, Schedule.start_time).all()
        )

    students = []
    existing = None
    if subject_id and section_id and semester_id:
        if not _teacher_assignment(teacher, subject_id, section_id):
            abort(403)
        students = (
            Student.query.filter_by(section_id=section_id, status="active")
            .order_by(Student.roll_number).all()
        )
        existing = AttendanceSession.query.filter_by(
            subject_id=subject_id, section_id=section_id,
            date=the_date, schedule_id=schedule_id,
        ).first()

    return render_template(
        "attendance/take.html",
        semesters=semesters, sections=sections, subjects=subjects,
        periods=periods, students=students, existing=existing,
        semester_id=semester_id, section_id=section_id,
        subject_id=subject_id, schedule_id=schedule_id,
        the_date=the_date, statuses=ATTENDANCE_STATUSES,
    )


@teacher_bp.route("/attendance/save", methods=["POST"])
@role_required("teacher")
def attendance_save():
    teacher = current_teacher()

    semester_id = parse_int(request.form.get("semester_id"))
    section_id = parse_int(request.form.get("section_id"))
    subject_id = parse_int(request.form.get("subject_id"))
    schedule_id = parse_int(request.form.get("schedule_id"))
    the_date = parse_date(request.form.get("date"))

    if not all([semester_id, section_id, subject_id, the_date]):
        flash("Missing selection — choose semester, section, subject and date.", "warning")
        return redirect(url_for("teacher.attendance_take"))
    if the_date > date.today():
        flash("Attendance cannot be taken for a future date.", "warning")
        return redirect(url_for("teacher.attendance_take"))
    if not _teacher_assignment(teacher, subject_id, section_id):
        abort(403)

    # duplicate guard: subject + section + date + period must be unique
    duplicate = AttendanceSession.query.filter_by(
        subject_id=subject_id, section_id=section_id,
        date=the_date, schedule_id=schedule_id,
    ).first()
    if duplicate:
        flash("Attendance has already been taken for this class and date. "
              "Use edit instead.", "danger")
        return redirect(url_for("teacher.attendance_session_view",
                                session_id=duplicate.id))

    session = AttendanceSession(
        subject_id=subject_id, section_id=section_id, semester_id=semester_id,
        schedule_id=schedule_id, teacher_id=teacher.id, date=the_date,
    )
    db.session.add(session)

    students = Student.query.filter_by(section_id=section_id, status="active").all()
    marked = 0
    for student in students:
        status = request.form.get(f"status_{student.id}")
        if status not in ATTENDANCE_STATUSES:
            continue
        remarks = (request.form.get(f"remarks_{student.id}") or "").strip() or None
        session.records.append(AttendanceRecord(
            student_id=student.id, status=status, remarks=remarks,
        ))
        marked += 1

    if marked == 0:
        db.session.rollback()
        flash("No students were marked — nothing saved.", "warning")
        return redirect(url_for("teacher.attendance_take",
                                semester_id=semester_id, section_id=section_id,
                                subject_id=subject_id, date=the_date.isoformat()))

    db.session.commit()

    # Notify admins about very low attendance in this session
    if session.total_count and (session.present_count / session.total_count) < 0.5:
        subject = db.session.get(Subject, subject_id)
        db.session.add(Notification(
            title="Low session attendance",
            message=(f"Only {session.present_count}/{session.total_count} present in "
                     f"{subject.code if subject else 'class'} on {the_date.isoformat()}."),
            category="warning",
        ))
        db.session.commit()

    flash(f"Attendance saved for {marked} students.", "success")
    return redirect(url_for("teacher.attendance_session_view", session_id=session.id))


# ----------------------------------------------------------------- history
@teacher_bp.route("/attendance/history")
@role_required("teacher")
def attendance_history():
    teacher = current_teacher()
    page = request.args.get("page", 1, type=int)
    date_from = parse_date(request.args.get("date_from"))
    date_to = parse_date(request.args.get("date_to"))
    subject_id = request.args.get("subject_id", type=int)

    query = AttendanceSession.query.filter_by(teacher_id=teacher.id)
    if date_from:
        query = query.filter(AttendanceSession.date >= date_from)
    if date_to:
        query = query.filter(AttendanceSession.date <= date_to)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    pagination = query.order_by(
        AttendanceSession.date.desc(), AttendanceSession.taken_at.desc()
    ).paginate(page=page, per_page=current_app.config["PER_PAGE"], error_out=False)

    subject_ids = {a.subject_id for a in teacher.assignments.all()}
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).order_by(
        Subject.code).all() if subject_ids else []

    return render_template(
        "attendance/history.html", pagination=pagination,
        departments=None, semesters=None, sections=None,
        subjects=subjects, teachers=None,
        filters={
            "date_from": request.args.get("date_from", ""),
            "date_to": request.args.get("date_to", ""),
            "subject_id": subject_id,
            "department_id": None, "semester_id": None,
            "section_id": None, "teacher_id": None,
        },
        base_endpoint="teacher.attendance_history",
    )


@teacher_bp.route("/attendance/<int:session_id>")
@role_required("teacher")
def attendance_session_view(session_id):
    teacher = current_teacher()
    session = db.get_or_404(AttendanceSession, session_id)
    if session.teacher_id != teacher.id:
        abort(403)
    records = sorted(session.records, key=lambda r: r.student.roll_number)
    can_edit = (
        Setting.get("allow_same_day_edit", "1") == "1"
        and session.date == date.today()
    )
    return render_template(
        "attendance/view.html", session=session, records=records,
        can_edit=can_edit,
    )


@teacher_bp.route("/attendance/<int:session_id>/edit", methods=["GET", "POST"])
@role_required("teacher")
def attendance_edit(session_id):
    teacher = current_teacher()
    session = db.get_or_404(AttendanceSession, session_id)
    if session.teacher_id != teacher.id:
        abort(403)
    if not (Setting.get("allow_same_day_edit", "1") == "1"
            and session.date == date.today()):
        flash("Editing is only allowed on the day the attendance was taken.", "warning")
        return redirect(url_for("teacher.attendance_session_view", session_id=session.id))

    if request.method == "POST":
        for record in session.records:
            status = request.form.get(f"status_{record.student_id}")
            if status in ATTENDANCE_STATUSES:
                record.status = status
            record.remarks = (request.form.get(f"remarks_{record.student_id}") or "").strip() or None
        db.session.commit()
        flash("Attendance updated.", "success")
        return redirect(url_for("teacher.attendance_session_view", session_id=session.id))

    records = sorted(session.records, key=lambda r: r.student.roll_number)
    return render_template(
        "attendance/edit.html", session=session, records=records,
        statuses=ATTENDANCE_STATUSES,
    )
