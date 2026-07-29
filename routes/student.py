# ============================================================
# Student pages: apply, my applications, withdraw, weekly logs
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from models import (db, Application, ProgressLog, Internship,
                    current_student, notify, audit, verified_only)


# ---------- APPLY (CREATE - with cover letter) ----------
def apply(internship_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    # an account must be approved by the admin before applying
    problem = verified_only('apply for internships')
    if problem:
        flash(problem)
        return redirect(url_for('internships'))

    me = current_student()

    # do not allow applying twice
    if Application.query.filter_by(student_id=me.id, internship_id=internship_id).first():
        flash('You already applied to this internship.')
    else:
        application = Application(student_id=me.id, internship_id=internship_id,
                                  cover_letter=request.form['cover_letter'])
        db.session.add(application)
        internship = db.session.get(Internship, internship_id)
        notify(internship.company.user_id,
               f'New application for "{internship.title}" from {session["name"]}',
               url_for('applicants', internship_id=internship_id))
        audit(session['user_id'], 'apply', f'internship #{internship_id}')
        db.session.commit()
        flash('Application submitted!')
    return redirect(url_for('my_applications'))


# ---------- MY APPLICATIONS (READ) ----------
def my_applications():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    me = current_student()
    apps = Application.query.filter_by(student_id=me.id).all()
    return render_template('my_applications.html', applications=apps)


# ---------- WITHDRAW (DELETE) ----------
def withdraw(id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    me = current_student()
    application = Application.query.filter_by(id=id, student_id=me.id).first()
    if application:
        audit(session['user_id'], 'withdraw', f'application #{id}')
        db.session.delete(application)
        db.session.commit()
        flash('Application withdrawn.')
    return redirect(url_for('my_applications'))


# ---------- WEEKLY LOG BOOK (CREATE + READ) ----------
# a student can write logs only for a 'selected' application
def my_logs(application_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    me = current_student()
    application = Application.query.filter_by(id=application_id, student_id=me.id,
                                              status='selected').first()
    if not application:
        flash('Log book is only available for selected applications.')
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        log = ProgressLog(application_id=application_id,
                          week_number=request.form['week_number'] or None,
                          description=request.form['description'])
        db.session.add(log)
        # tell the supervisors of the company about the new log
        for sup in application.internship.company.supervisors:
            notify(sup.user_id,
                   f'{session["name"]} submitted a weekly log for "{application.internship.title}"',
                   url_for('view_logs', application_id=application_id))
        audit(session['user_id'], 'submit_log', f'application #{application_id}')
        db.session.commit()
        flash('Weekly log submitted.')
        return redirect(url_for('my_logs', application_id=application_id))

    logs = (ProgressLog.query.filter_by(application_id=application_id)
            .order_by(ProgressLog.week_number).all())
    return render_template('my_logs.html', application=application, logs=logs)
