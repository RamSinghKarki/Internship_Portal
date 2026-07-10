# ============================================================
# Supervisor pages: my students, view logs, give feedback
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from models import db, Internship, Application, ProgressLog, current_supervisor


# ---------- MY STUDENTS (READ) ----------
# selected students doing internships at the supervisor's company
def students():
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    me = current_supervisor()
    rows = (Application.query.join(Internship)
            .filter(Internship.company_id == me.company_id,
                    Application.status == 'selected').all())
    return render_template('students.html', rows=rows)


# ---------- VIEW LOGS of one student (READ) ----------
def view_logs(application_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    me = current_supervisor()
    application = (Application.query.join(Internship)
                   .filter(Application.id == application_id,
                           Internship.company_id == me.company_id).first())
    if not application:
        flash('Not found.')
        return redirect(url_for('students'))

    logs = (ProgressLog.query.filter_by(application_id=application_id)
            .order_by(ProgressLog.week_number).all())
    return render_template('view_logs.html', application=application, logs=logs)


# ---------- GIVE FEEDBACK on a log (UPDATE) ----------
def give_feedback(log_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    me = current_supervisor()
    log = db.session.get(ProgressLog, log_id)
    # only logs of applications at the supervisor's company
    if not log or log.application.internship.company_id != me.company_id:
        flash('Not found.')
        return redirect(url_for('students'))

    log.feedback = request.form['feedback']
    log.marks = request.form['marks'] or None
    log.supervisor_id = me.id
    db.session.commit()
    flash('Feedback saved.')
    return redirect(url_for('view_logs', application_id=log.application_id))
