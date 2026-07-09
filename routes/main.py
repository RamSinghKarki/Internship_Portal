# ============================================================
# Main pages: home, dashboard, internship list (all roles)
# ============================================================

from flask import render_template, redirect, url_for, session
from db import get_db, my_student, my_company


# ---------- HOME ----------
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ---------- DASHBOARD (READ - counts from every main table) ----------
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    counts = {}
    for table in ('students', 'companies', 'supervisors', 'internships', 'applications'):
        cur.execute(f"SELECT COUNT(*) AS c FROM {table}")
        counts[table] = cur.fetchone()['c']
    db.close()
    return render_template('dashboard.html', counts=counts)


# ---------- INTERNSHIP LIST (READ with JOIN) ----------
# students see open internships, a company sees its own posts
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    base_query = """
        SELECT internships.*, users.name AS company_name
        FROM internships
        JOIN companies ON internships.company_id = companies.id
        JOIN users     ON companies.user_id = users.id
    """

    applied_ids = []
    if session['role'] == 'company':
        me = my_company(cur)
        cur.execute(base_query + " WHERE internships.company_id = %s "
                    "ORDER BY internships.id DESC", (me['id'],))
    elif session['role'] == 'student':
        me = my_student(cur)
        cur.execute("SELECT internship_id FROM applications WHERE student_id = %s", (me['id'],))
        applied_ids = [r['internship_id'] for r in cur.fetchall()]
        cur.execute(base_query + " WHERE internships.status = 'open' "
                    "ORDER BY internships.id DESC")
    else:   # admin / supervisor see everything
        cur.execute(base_query + " ORDER BY internships.id DESC")

    items = cur.fetchall()
    db.close()
    return render_template('internships.html', internships=items, applied_ids=applied_ids)
