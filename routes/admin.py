# ============================================================
# Admin pages: view all users, delete a user
# ============================================================

from flask import render_template, redirect, url_for, session, flash
from models import db, User


# ---------- ALL USERS (READ) ----------
def users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_users = User.query.order_by(User.id).all()
    return render_template('users.html', users=all_users)


# ---------- DELETE USER (DELETE) ----------
# profile, internships, applications and logs of the user are
# removed automatically by the cascade rules
def delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if id == session['user_id']:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))

    user = db.session.get(User, id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.')
    return redirect(url_for('users'))
