# ============================================================
# Company pages: post/edit/delete internships, view applicants,
# select or reject applications
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from db import get_db, my_company


# ---------- ADD INTERNSHIP (CREATE) ----------
def add_internship():
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        me = my_company(cur)
        cur.execute(
            "INSERT INTO internships (company_id, title, description, required_skills, "
            "duration_weeks, stipend, vacancies) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (me['id'], request.form['title'], request.form['description'],
             request.form['required_skills'], request.form['duration_weeks'] or None,
             request.form['stipend'], request.form['vacancies'] or None)
        )
        db.commit()
        db.close()
        flash('Internship posted.')
        return redirect(url_for('internships'))

    return render_template('add_internship.html')


# ---------- EDIT INTERNSHIP (UPDATE - own posts only) ----------
def edit_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s", (id, me['id']))
    internship = cur.fetchone()

    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    if request.method == 'POST':
        cur.execute(
            "UPDATE internships SET title = %s, description = %s, required_skills = %s, "
            "duration_weeks = %s, stipend = %s, vacancies = %s, status = %s WHERE id = %s",
            (request.form['title'], request.form['description'],
             request.form['required_skills'], request.form['duration_weeks'] or None,
             request.form['stipend'], request.form['vacancies'] or None,
             request.form['status'], id)
        )
        db.commit()
        db.close()
        flash('Internship updated.')
        return redirect(url_for('internships'))

    db.close()
    return render_template('edit_internship.html', internship=internship)


# ---------- DELETE INTERNSHIP (DELETE - own posts only) ----------
# its applications and logs are removed by ON DELETE CASCADE
def delete_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    cur.execute("DELETE FROM internships WHERE id = %s AND company_id = %s", (id, me['id']))
    db.commit()
    db.close()
    flash('Internship deleted.')
    return redirect(url_for('internships'))


# ---------- VIEW APPLICANTS (READ) ----------
def applicants(internship_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s",
                (internship_id, me['id']))
    internship = cur.fetchone()
    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    cur.execute("""
        SELECT applications.id, applications.status, applications.cover_letter,
               users.name AS student_name, users.email AS student_email,
               students.roll_number, students.department, students.semester, students.skills
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN users    ON students.user_id = users.id
        WHERE applications.internship_id = %s
    """, (internship_id,))
    apps = cur.fetchall()
    db.close()
    return render_template('applicants.html', internship=internship, applications=apps)


# ---------- UPDATE APPLICATION STATUS (UPDATE) ----------
def update_status(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    # only allow changing applications of this company's internships
    cur.execute("""
        UPDATE applications
        JOIN internships ON applications.internship_id = internships.id
        SET applications.status = %s
        WHERE applications.id = %s AND internships.company_id = %s
    """, (request.form['status'], id, me['id']))
    db.commit()

    cur.execute("SELECT internship_id FROM applications WHERE id = %s", (id,))
    row = cur.fetchone()
    db.close()
    flash('Status updated.')
    return redirect(url_for('applicants', internship_id=row['internship_id']))
