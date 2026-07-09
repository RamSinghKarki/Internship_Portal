# ============================================================
# Supervisor pages: my students, view logs, give feedback
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from db import get_db, my_supervisor


# ---------- MY STUDENTS (READ) ----------
# selected students doing internships at the supervisor's company
def students():
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)
    cur.execute("""
        SELECT applications.id AS application_id, users.name AS student_name,
               students.roll_number, internships.title
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN students    ON applications.student_id = students.id
        JOIN users       ON students.user_id = users.id
        WHERE internships.company_id = %s AND applications.status = 'selected'
    """, (me['company_id'],))
    rows = cur.fetchall()
    db.close()
    return render_template('students.html', rows=rows)


# ---------- VIEW LOGS of one student (READ) ----------
def view_logs(application_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)

    # the application must be at the supervisor's company
    cur.execute("""
        SELECT applications.id, users.name AS student_name, internships.title
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN students    ON applications.student_id = students.id
        JOIN users       ON students.user_id = users.id
        WHERE applications.id = %s AND internships.company_id = %s
    """, (application_id, me['company_id']))
    application = cur.fetchone()
    if not application:
        db.close()
        flash('Not found.')
        return redirect(url_for('students'))

    cur.execute("SELECT * FROM progress_logs WHERE application_id = %s ORDER BY week_number",
                (application_id,))
    logs = cur.fetchall()
    db.close()
    return render_template('view_logs.html', application=application, logs=logs)


# ---------- GIVE FEEDBACK on a log (UPDATE) ----------
def give_feedback(log_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)
    # only logs of applications at the supervisor's company
    cur.execute("""
        UPDATE progress_logs
        JOIN applications ON progress_logs.application_id = applications.id
        JOIN internships  ON applications.internship_id = internships.id
        SET progress_logs.feedback = %s, progress_logs.marks = %s,
            progress_logs.supervisor_id = %s
        WHERE progress_logs.id = %s AND internships.company_id = %s
    """, (request.form['feedback'], request.form['marks'] or None,
          me['id'], log_id, me['company_id']))
    db.commit()

    cur.execute("SELECT application_id FROM progress_logs WHERE id = %s", (log_id,))
    row = cur.fetchone()
    db.close()
    flash('Feedback saved.')
    return redirect(url_for('view_logs', application_id=row['application_id']))
