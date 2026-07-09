# ============================================================
# Database connection + small helpers shared by all route files
# ============================================================

from flask import session
import pymysql


def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='password',          # <-- change to your MySQL password
        database='internship_db',
        cursorclass=pymysql.cursors.DictCursor  # rows come back as dictionaries
    )


def role_id_of(cur, role_name):
    """Look up the id of a role from the roles table."""
    cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
    return cur.fetchone()['id']


def my_student(cur):
    """Return the students row of the logged-in user."""
    cur.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()


def my_company(cur):
    """Return the companies row of the logged-in user."""
    cur.execute("SELECT * FROM companies WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()


def my_supervisor(cur):
    """Return the supervisors row of the logged-in user."""
    cur.execute("SELECT * FROM supervisors WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()
