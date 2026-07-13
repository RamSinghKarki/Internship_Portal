from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Teacher, Department, User, Role
from app.utils.helpers import parse_date, parse_int, save_photo, delete_photo
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(teacher):
    teacher.employee_id = (request.form.get("employee_id") or "").strip()
    teacher.full_name = (request.form.get("full_name") or "").strip()
    teacher.gender = request.form.get("gender") or None
    teacher.date_of_birth = parse_date(request.form.get("date_of_birth"))
    teacher.qualification = (request.form.get("qualification") or "").strip()
    teacher.designation = (request.form.get("designation") or "").strip()
    teacher.department_id = parse_int(request.form.get("department_id"))
    teacher.email = (request.form.get("email") or "").strip().lower()
    teacher.phone = (request.form.get("phone") or "").strip()
    teacher.address = (request.form.get("address") or "").strip()
    teacher.joining_date = parse_date(request.form.get("joining_date"))
    teacher.employment_status = request.form.get("employment_status") or "active"

    if not teacher.employee_id or not teacher.full_name or not teacher.email:
        flash("Employee ID, full name and email are required.", "warning")
        return False
    clash = Teacher.query.filter(
        (Teacher.employee_id == teacher.employee_id) | (Teacher.email == teacher.email)
    ).filter(Teacher.id != teacher.id).first()
    if clash:
        flash("A teacher with this employee ID or email already exists.", "danger")
        return False

    photo = save_photo(request.files.get("photo"))
    if photo:
        delete_photo(teacher.photo)
        teacher.photo = photo
    return True


def _sync_user(teacher, password=None):
    """Create or update the login account tied to this teacher profile."""
    role = Role.query.filter_by(name="teacher").first()
    if teacher.user is None:
        user = User(
            username=teacher.employee_id.lower(),
            email=teacher.email,
            role=role,
        )
        user.set_password(password or "teacher123")
        db.session.add(user)
        teacher.user = user
    else:
        teacher.user.email = teacher.email
        if password:
            teacher.user.set_password(password)
        teacher.user.is_active_flag = teacher.employment_status == "active"


@admin_bp.route("/teachers")
@admin_required
def teachers():
    q = (request.args.get("q") or "").strip()
    department_id = request.args.get("department_id", type=int)
    status = request.args.get("status") or ""
    page = request.args.get("page", 1, type=int)

    query = Teacher.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            Teacher.full_name.ilike(like)
            | Teacher.employee_id.ilike(like)
            | Teacher.email.ilike(like)
        )
    if department_id:
        query = query.filter_by(department_id=department_id)
    if status:
        query = query.filter_by(employment_status=status)

    pagination = query.order_by(Teacher.full_name).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "admin/teachers/list.html", pagination=pagination, q=q,
        departments=departments, department_id=department_id, status=status,
    )


@admin_bp.route("/teachers/add", methods=["GET", "POST"])
@admin_required
def teacher_add():
    if request.method == "POST":
        teacher = Teacher()
        if _fill(teacher):
            _sync_user(teacher, request.form.get("password") or None)
            db.session.add(teacher)
            db.session.commit()
            flash("Teacher created. Default login uses the employee ID as username.", "success")
            return redirect(url_for("admin.teachers"))
        db.session.rollback()
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/teachers/form.html", teacher=None, departments=departments)


@admin_bp.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
@admin_required
def teacher_edit(teacher_id):
    teacher = db.get_or_404(Teacher, teacher_id)
    if request.method == "POST":
        if _fill(teacher):
            _sync_user(teacher, request.form.get("password") or None)
            db.session.commit()
            flash("Teacher updated.", "success")
            return redirect(url_for("admin.teachers"))
        db.session.rollback()
    departments = Department.query.order_by(Department.name).all()
    return render_template("admin/teachers/form.html", teacher=teacher, departments=departments)


@admin_bp.route("/teachers/<int:teacher_id>")
@admin_required
def teacher_view(teacher_id):
    teacher = db.get_or_404(Teacher, teacher_id)
    assignments = teacher.assignments.all()
    schedules = teacher.schedules.all()
    session_count = teacher.sessions.count()
    return render_template(
        "admin/teachers/view.html", teacher=teacher,
        assignments=assignments, schedules=schedules, session_count=session_count,
    )


@admin_bp.route("/teachers/<int:teacher_id>/delete", methods=["POST"])
@admin_required
def teacher_delete(teacher_id):
    teacher = db.get_or_404(Teacher, teacher_id)
    if teacher.sessions.count():
        flash("Cannot delete a teacher with recorded attendance sessions. "
              "Set employment status to 'inactive' instead.", "danger")
        return redirect(url_for("admin.teachers"))
    user = teacher.user
    delete_photo(teacher.photo)
    db.session.delete(teacher)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Teacher deleted.", "success")
    return redirect(url_for("admin.teachers"))
