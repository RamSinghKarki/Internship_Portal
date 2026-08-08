# ============================================================
# Company pages: post/edit/delete internships, view applicants,
# select or reject applications
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
import csv
import io
from flask import Response
from models import (db, Internship, Application, current_company,
                    notify, verified_only)


# ---------- ADD INTERNSHIP (CREATE) ----------
def add_internship():
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    # an account must be approved by the admin before posting
    problem = verified_only('post internships')
    if problem:
        flash(problem)
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        me = current_company()
        intern = Internship(company_id=me.id,
                            title=request.form['title'],
                            description=request.form['description'],
                            required_skills=request.form['required_skills'],
                            duration_weeks=request.form['duration_weeks'] or None,
                            stipend=request.form['stipend'],
                            vacancies=request.form['vacancies'] or None)
        db.session.add(intern)
        db.session.commit()
        flash('Internship posted.')
        return redirect(url_for('internships'))

    return render_template('add_internship.html')


# ---------- EDIT INTERNSHIP (UPDATE - own posts only) ----------
def edit_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    me = current_company()
    internship = Internship.query.filter_by(id=id, company_id=me.id).first()
    if not internship:
        flash('Internship not found.')
        return redirect(url_for('internships'))

    if request.method == 'POST':
        internship.title = request.form['title']
        internship.description = request.form['description']
        internship.required_skills = request.form['required_skills']
        internship.duration_weeks = request.form['duration_weeks'] or None
        internship.stipend = request.form['stipend']
        internship.vacancies = request.form['vacancies'] or None
        internship.status = request.form['status']
        db.session.commit()
        flash('Internship updated.')
        return redirect(url_for('internships'))

    return render_template('edit_internship.html', internship=internship)


# ---------- DELETE INTERNSHIP (DELETE - own posts only) ----------
# its applications and logs are removed automatically (cascade)
def delete_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    me = current_company()
    internship = Internship.query.filter_by(id=id, company_id=me.id).first()
    if internship:
        db.session.delete(internship)
        db.session.commit()
        flash('Internship deleted.')
    return redirect(url_for('internships'))


# ---------- VIEW APPLICANTS (READ) ----------
def applicants(internship_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    me = current_company()
    internship = Internship.query.filter_by(id=internship_id, company_id=me.id).first()
    if not internship:
        flash('Internship not found.')
        return redirect(url_for('internships'))

    # applications come through the relationship on the model
    return render_template('applicants.html', internship=internship,
                           applications=internship.applications)


# ---------- UPDATE APPLICATION STATUS (UPDATE) ----------
def update_status(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    me = current_company()
    application = db.session.get(Application, id)
    # only applications of this company's internships
    if not application or application.internship.company_id != me.id:
        flash('Not found.')
        return redirect(url_for('internships'))

    application.status = request.form['status']
    notify(application.student.user_id,
           f'Your application for "{application.internship.title}" '
           f'was marked {application.status}',
           url_for('my_applications'))
    db.session.commit()
    flash('Status updated.')
    return redirect(url_for('applicants', internship_id=application.internship_id))


# ---------- EXPORT APPLICANTS AS CSV ----------
def applicants_export(internship_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    me = current_company()
    internship = Internship.query.filter_by(id=internship_id, company_id=me.id).first()
    if not internship:
        flash('Internship not found.')
        return redirect(url_for('internships'))

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(['Student', 'Email', 'Roll No', 'Department', 'Semester',
                     'Skills', 'Status', 'Applied On'])
    for a in internship.applications:
        writer.writerow([a.student.user.name, a.student.user.email,
                         a.student.roll_number, a.student.department,
                         a.student.semester, a.student.skills, a.status,
                         a.applied_date.strftime('%Y-%m-%d') if a.applied_date else ''])
    return Response(out.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition':
                             f'attachment; filename=applicants_{internship_id}.csv'})
