from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Schedule, Subject, Teacher, Semester, Section
from app.models.schedule import DAYS_OF_WEEK
from app.utils.helpers import parse_int, parse_time
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(schedule):
    schedule.subject_id = parse_int(request.form.get("subject_id"))
    schedule.teacher_id = parse_int(request.form.get("teacher_id"))
    schedule.semester_id = parse_int(request.form.get("semester_id"))
    schedule.section_id = parse_int(request.form.get("section_id"))
    schedule.room_number = (request.form.get("room_number") or "").strip()
    schedule.day_of_week = request.form.get("day_of_week") or ""
    schedule.start_time = parse_time(request.form.get("start_time"))
    schedule.end_time = parse_time(request.form.get("end_time"))

    if not all([schedule.subject_id, schedule.teacher_id, schedule.semester_id,
                schedule.section_id, schedule.day_of_week,
                schedule.start_time, schedule.end_time]):
        flash("All fields except room number are required.", "warning")
        return False
    if schedule.day_of_week not in DAYS_OF_WEEK:
        flash("Invalid day of week.", "warning")
        return False
    if schedule.start_time >= schedule.end_time:
        flash("Start time must be before end time.", "warning")
        return False

    # Overlap checks: same section or same teacher cannot be double-booked.
    overlapping = Schedule.query.filter(
        Schedule.id != schedule.id,
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.start_time < schedule.end_time,
        Schedule.end_time > schedule.start_time,
    )
    if overlapping.filter(Schedule.section_id == schedule.section_id).first():
        flash("The section already has a class in that time slot.", "danger")
        return False
    if overlapping.filter(Schedule.teacher_id == schedule.teacher_id).first():
        flash("The teacher already has a class in that time slot.", "danger")
        return False
    return True


def _context():
    return {
        "subjects": Subject.query.order_by(Subject.code).all(),
        "teachers": Teacher.query.filter_by(employment_status="active")
                    .order_by(Teacher.full_name).all(),
        "semesters": Semester.query.order_by(
            Semester.academic_year.desc(), Semester.name).all(),
        "sections": Section.query.order_by(Section.name).all(),
        "days": DAYS_OF_WEEK,
    }


@admin_bp.route("/schedules")
@admin_required
def schedules():
    day = request.args.get("day") or ""
    section_id = request.args.get("section_id", type=int)
    teacher_id = request.args.get("teacher_id", type=int)
    page = request.args.get("page", 1, type=int)

    query = Schedule.query
    if day:
        query = query.filter_by(day_of_week=day)
    if section_id:
        query = query.filter_by(section_id=section_id)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)

    pagination = query.order_by(Schedule.day_of_week, Schedule.start_time).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/schedules/list.html", pagination=pagination, day=day,
        section_id=section_id, teacher_id=teacher_id, **_context(),
    )


@admin_bp.route("/schedules/timetable")
@admin_required
def timetable():
    section_id = request.args.get("section_id", type=int)
    query = Schedule.query
    if section_id:
        query = query.filter_by(section_id=section_id)
    rows = query.order_by(Schedule.start_time).all()
    grid = {day: [] for day in DAYS_OF_WEEK}
    for s in rows:
        grid[s.day_of_week].append(s)
    return render_template(
        "admin/schedules/timetable.html", grid=grid, section_id=section_id,
        **_context(),
    )


@admin_bp.route("/schedules/add", methods=["GET", "POST"])
@admin_required
def schedule_add():
    if request.method == "POST":
        schedule = Schedule()
        if _fill(schedule):
            db.session.add(schedule)
            db.session.commit()
            flash("Class period added to the routine.", "success")
            return redirect(url_for("admin.schedules"))
    return render_template("admin/schedules/form.html", schedule=None, **_context())


@admin_bp.route("/schedules/<int:schedule_id>/edit", methods=["GET", "POST"])
@admin_required
def schedule_edit(schedule_id):
    schedule = db.get_or_404(Schedule, schedule_id)
    if request.method == "POST":
        if _fill(schedule):
            db.session.commit()
            flash("Schedule updated.", "success")
            return redirect(url_for("admin.schedules"))
        db.session.rollback()
    return render_template("admin/schedules/form.html", schedule=schedule, **_context())


@admin_bp.route("/schedules/<int:schedule_id>/delete", methods=["POST"])
@admin_required
def schedule_delete(schedule_id):
    schedule = db.get_or_404(Schedule, schedule_id)
    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule removed.", "success")
    return redirect(url_for("admin.schedules"))
