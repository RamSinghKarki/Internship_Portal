from flask import render_template, request, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Semester
from app.utils.decorators import admin_required
from . import admin_bp


def _fill(sem):
    sem.name = (request.form.get("name") or "").strip()
    sem.academic_year = (request.form.get("academic_year") or "").strip()
    sem.status = request.form.get("status") or "active"
    if not sem.name or not sem.academic_year:
        flash("Semester name and academic year are required.", "warning")
        return False
    clash = Semester.query.filter_by(
        name=sem.name, academic_year=sem.academic_year
    ).filter(Semester.id != sem.id).first()
    if clash:
        flash("This semester already exists for that academic year.", "danger")
        return False
    return True


@admin_bp.route("/semesters")
@admin_required
def semesters():
    q = (request.args.get("q") or "").strip()
    page = request.args.get("page", 1, type=int)
    query = Semester.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            Semester.name.ilike(like) | Semester.academic_year.ilike(like)
        )
    pagination = query.order_by(
        Semester.academic_year.desc(), Semester.name
    ).paginate(page=page, per_page=current_app.config["PER_PAGE"], error_out=False)
    return render_template("admin/semesters/list.html", pagination=pagination, q=q)


@admin_bp.route("/semesters/add", methods=["GET", "POST"])
@admin_required
def semester_add():
    if request.method == "POST":
        sem = Semester()
        if _fill(sem):
            db.session.add(sem)
            db.session.commit()
            flash("Semester created.", "success")
            return redirect(url_for("admin.semesters"))
    return render_template("admin/semesters/form.html", sem=None)


@admin_bp.route("/semesters/<int:sem_id>/edit", methods=["GET", "POST"])
@admin_required
def semester_edit(sem_id):
    sem = db.get_or_404(Semester, sem_id)
    if request.method == "POST":
        if _fill(sem):
            db.session.commit()
            flash("Semester updated.", "success")
            return redirect(url_for("admin.semesters"))
        db.session.rollback()
    return render_template("admin/semesters/form.html", sem=sem)


@admin_bp.route("/semesters/<int:sem_id>/delete", methods=["POST"])
@admin_required
def semester_delete(sem_id):
    sem = db.get_or_404(Semester, sem_id)
    if sem.sections.count() or sem.subjects.count() or sem.students.count():
        flash("Cannot delete a semester that still has sections, subjects or students.", "danger")
        return redirect(url_for("admin.semesters"))
    db.session.delete(sem)
    db.session.commit()
    flash("Semester deleted.", "success")
    return redirect(url_for("admin.semesters"))
