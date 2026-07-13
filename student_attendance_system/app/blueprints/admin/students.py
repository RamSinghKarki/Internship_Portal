from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Student, Department, Semester, Section, User, Role
from app.utils import stats
from app.utils.helpers import parse_date, parse_int, save_photo, delete_photo
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(student):
    student.roll_number = (request.form.get("roll_number") or "").strip()
    student.registration_number = (request.form.get("registration_number") or "").strip()
    student.full_name = (request.form.get("full_name") or "").strip()
    student.gender = request.form.get("gender") or None
    student.date_of_birth = parse_date(request.form.get("date_of_birth"))
    student.department_id = parse_int(request.form.get("department_id"))
    student.semester_id = parse_int(request.form.get("semester_id"))
    student.section_id = parse_int(request.form.get("section_id"))
    student.email = (request.form.get("email") or "").strip().lower()
    student.phone = (request.form.get("phone") or "").strip()
    student.guardian_name = (request.form.get("guardian_name") or "").strip()
    student.guardian_contact = (request.form.get("guardian_contact") or "").strip()
    student.address = (request.form.get("address") or "").strip()
    student.admission_year = (request.form.get("admission_year") or "").strip()
    student.status = request.form.get("status") or "active"

    required = [student.roll_number, student.registration_number,
                student.full_name, student.email,
                student.department_id, student.semester_id, student.section_id]
    if not all(required):
        flash("Roll number, registration number, name, email, department, "
              "semester and section are required.", "warning")
        return False
    clash = Student.query.filter(
        (Student.registration_number == student.registration_number)
        | (Student.email == student.email)
    ).filter(Student.id != student.id).first()
    if clash:
        flash("A student with this registration number or email already exists.", "danger")
        return False

    photo = save_photo(request.files.get("photo"))
    if photo:
        delete_photo(student.photo)
        student.photo = photo
    return True


def _sync_user(student, password=None):
    role = Role.query.filter_by(name="student").first()
    if student.user is None:
        user = User(
            username=student.registration_number.lower(),
            email=student.email,
            role=role,
        )
        user.set_password(password or "student123")
        db.session.add(user)
        student.user = user
    else:
        student.user.email = student.email
        if password:
            student.user.set_password(password)
        student.user.is_active_flag = student.status == "active"


def _context():
    return {
        "departments": Department.query.order_by(Department.name).all(),
        "semesters": Semester.query.order_by(
            Semester.academic_year.desc(), Semester.name).all(),
        "sections": Section.query.order_by(Section.name).all(),
    }


@admin_bp.route("/students")
@admin_required
def students():
    q = (request.args.get("q") or "").strip()
    department_id = request.args.get("department_id", type=int)
    semester_id = request.args.get("semester_id", type=int)
    section_id = request.args.get("section_id", type=int)
    status = request.args.get("status") or ""
    page = request.args.get("page", 1, type=int)

    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            Student.full_name.ilike(like)
            | Student.roll_number.ilike(like)
            | Student.registration_number.ilike(like)
            | Student.email.ilike(like)
        )
    if department_id:
        query = query.filter_by(department_id=department_id)
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    if section_id:
        query = query.filter_by(section_id=section_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Student.roll_number).paginate(
        page=page, per_page=current_app.config["PER_PAGE"], error_out=False,
    )
    return render_template(
        "admin/students/list.html", pagination=pagination, q=q,
        department_id=department_id, semester_id=semester_id,
        section_id=section_id, status=status, **_context(),
    )


@admin_bp.route("/students/add", methods=["GET", "POST"])
@admin_required
def student_add():
    if request.method == "POST":
        student = Student()
        if _fill(student):
            _sync_user(student, request.form.get("password") or None)
            db.session.add(student)
            db.session.commit()
            flash("Student created. Default login uses the registration number as username.", "success")
            return redirect(url_for("admin.students"))
        db.session.rollback()
    return render_template("admin/students/form.html", student=None, **_context())


@admin_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@admin_required
def student_edit(student_id):
    student = db.get_or_404(Student, student_id)
    if request.method == "POST":
        if _fill(student):
            _sync_user(student, request.form.get("password") or None)
            db.session.commit()
            flash("Student updated.", "success")
            return redirect(url_for("admin.students"))
        db.session.rollback()
    return render_template("admin/students/form.html", student=student, **_context())


@admin_bp.route("/students/<int:student_id>")
@admin_required
def student_view(student_id):
    student = db.get_or_404(Student, student_id)
    attended, total, percentage = stats.student_overall(student.id)
    breakdown = stats.student_subject_breakdown(student.id)
    monthly = stats.student_monthly(student.id)
    return render_template(
        "admin/students/view.html", student=student,
        attended=attended, total=total, percentage=percentage,
        breakdown=breakdown, monthly=monthly,
        threshold=stats.low_attendance_threshold(),
    )


@admin_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@admin_required
def student_delete(student_id):
    student = db.get_or_404(Student, student_id)
    user = student.user
    delete_photo(student.photo)
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("admin.students"))
