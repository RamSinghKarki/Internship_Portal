# ============================================================
# Main pages: home, dashboard, internship list (all roles)
# ============================================================

from flask import render_template, redirect, url_for, session
from db import get_db, my_student, my_company, my_supervisor


# ---------- LANDING PAGE ----------
# public home page: shows how many students, companies etc. have joined
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    db = get_db()
    cur = db.cursor()
    counts = {}
    for table in ('students', 'companies', 'supervisors', 'internships'):
        cur.execute(f"SELECT COUNT(*) AS c FROM {table}")
        counts[table] = cur.fetchone()['c']
    db.close()
    return render_template('index.html', counts=counts)


# ---------- DASHBOARD (READ - each role sees only its own numbers) ----------
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    def count(sql, params=None):
        cur.execute(sql, params or ())
        return cur.fetchone()['c']

    stats = []   # list of (label, number) shown as cards

    if session['role'] == 'student':
        me = my_student(cur)
        stats.append(('Open Internships', count("SELECT COUNT(*) AS c FROM internships WHERE status = 'open'")))
        stats.append(('Companies', count("SELECT COUNT(*) AS c FROM companies")))
        stats.append(('My Applications', count("SELECT COUNT(*) AS c FROM applications WHERE student_id = %s", (me['id'],))))
        stats.append(('Selected', count("SELECT COUNT(*) AS c FROM applications WHERE student_id = %s AND status = 'selected'", (me['id'],))))

    elif session['role'] == 'company':
        me = my_company(cur)
        stats.append(('My Internships', count("SELECT COUNT(*) AS c FROM internships WHERE company_id = %s", (me['id'],))))
        stats.append(('Applications Received', count(
            "SELECT COUNT(*) AS c FROM applications "
            "JOIN internships ON applications.internship_id = internships.id "
            "WHERE internships.company_id = %s", (me['id'],))))
        stats.append(('Students Registered', count("SELECT COUNT(*) AS c FROM students")))
        stats.append(('My Supervisors', count("SELECT COUNT(*) AS c FROM supervisors WHERE company_id = %s", (me['id'],))))

    elif session['role'] == 'supervisor':
        me = my_supervisor(cur)
        stats.append(('My Students', count(
            "SELECT COUNT(*) AS c FROM applications "
            "JOIN internships ON applications.internship_id = internships.id "
            "WHERE internships.company_id = %s AND applications.status = 'selected'", (me['company_id'],))))
        stats.append(('Logs Submitted', count(
            "SELECT COUNT(*) AS c FROM progress_logs "
            "JOIN applications ON progress_logs.application_id = applications.id "
            "JOIN internships  ON applications.internship_id = internships.id "
            "WHERE internships.company_id = %s", (me['company_id'],))))
        stats.append(('Awaiting My Feedback', count(
            "SELECT COUNT(*) AS c FROM progress_logs "
            "JOIN applications ON progress_logs.application_id = applications.id "
            "JOIN internships  ON applications.internship_id = internships.id "
            "WHERE internships.company_id = %s AND progress_logs.feedback IS NULL", (me['company_id'],))))

    else:   # admin sees the whole system
        for label, table in (('Students', 'students'), ('Companies', 'companies'),
                             ('Supervisors', 'supervisors'), ('Internships', 'internships'),
                             ('Applications', 'applications')):
            stats.append((label, count(f"SELECT COUNT(*) AS c FROM {table}")))

    db.close()
    return render_template('dashboard.html', stats=stats)


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
    elif session['role'] == 'supervisor':
        me = my_supervisor(cur)
        cur.execute(base_query + " WHERE internships.company_id = %s "
                    "ORDER BY internships.id DESC", (me['company_id'],))
    else:   # admin sees everything
        cur.execute(base_query + " ORDER BY internships.id DESC")

    items = cur.fetchall()
    db.close()
    return render_template('internships.html', internships=items, applied_ids=applied_ids)
