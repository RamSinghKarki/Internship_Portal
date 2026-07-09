# ============================================================
# Admin pages: view all users, delete a user
# ============================================================

from flask import render_template, redirect, url_for, session, flash
from db import get_db


# ---------- ALL USERS (READ) ----------
def users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT users.id, users.name, users.email, users.created_at, roles.role_name
        FROM users JOIN roles ON users.role_id = roles.id
        ORDER BY users.id
    """)
    all_users = cur.fetchall()
    db.close()
    return render_template('users.html', users=all_users)


# ---------- DELETE USER (DELETE) ----------
# student/company/supervisor rows and their data are removed
# automatically because of ON DELETE CASCADE
def delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if id == session['user_id']:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    db.commit()
    db.close()
    flash('User deleted.')
    return redirect(url_for('users'))
