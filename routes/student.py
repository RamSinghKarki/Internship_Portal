# ============================================================
# Student pages: apply, my applications, withdraw, weekly logs
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from db import get_db, my_student


# ---------- APPLY (CREATE - with cover letter) ----------
def apply(internship_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)

    cur.execute("SELECT id FROM applications WHERE student_id = %s AND internship_id = %s",
                (me['id'], internship_id))
    if cur.fetchone():
        flash('You already applied to this internship.')
    else:
        cur.execute(
            "INSERT INTO applications (student_id, internship_id, cover_letter) "
            "VALUES (%s, %s, %s)",
            (me['id'], internship_id, request.form['cover_letter'])
        )
        db.commit()
        flash('Application submitted!')
    db.close()
    return redirect(url_for('my_applications'))


# ---------- MY APPLICATIONS (READ) ----------
def my_applications():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)
    cur.execute("""
        SELECT applications.id, applications.status, applications.applied_date,
               internships.title, users.name AS company_name
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN companies   ON internships.company_id = companies.id
        JOIN users       ON companies.user_id = users.id
        WHERE applications.student_id = %s
    """, (me['id'],))
    apps = cur.fetchall()
    db.close()
    return render_template('my_applications.html', applications=apps)


# ---------- WITHDRAW (DELETE) ----------
def withdraw(id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)
    cur.execute("DELETE FROM applications WHERE id = %s AND student_id = %s", (id, me['id']))
    db.commit()
    db.close()
    flash('Application withdrawn.')
    return redirect(url_for('my_applications'))


# ---------- WEEKLY LOG BOOK (CREATE + READ) ----------
# a student can write logs only for a 'selected' application
def my_logs(application_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)

    # the application must belong to this student and be selected
    cur.execute("""
        SELECT applications.*, internships.title
        FROM applications JOIN internships ON applications.internship_id = internships.id
        WHERE applications.id = %s AND applications.student_id = %s
              AND applications.status = 'selected'
    """, (application_id, me['id']))
    application = cur.fetchone()
    if not application:
        db.close()
        flash('Log book is only available for selected applications.')
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        cur.execute(
            "INSERT INTO progress_logs (application_id, week_number, description) "
            "VALUES (%s, %s, %s)",
            (application_id, request.form['week_number'] or None, request.form['description'])
        )
        db.commit()
        db.close()
        flash('Weekly log submitted.')
        return redirect(url_for('my_logs', application_id=application_id))

    cur.execute("SELECT * FROM progress_logs WHERE application_id = %s ORDER BY week_number",
                (application_id,))
    logs = cur.fetchall()
    db.close()
    return render_template('my_logs.html', application=application, logs=logs)
