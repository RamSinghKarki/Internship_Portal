# ============================================================
# Admin pages: user management (search + pagination + export),
# audit log, delete user
# ============================================================

import csv
import io
from flask import render_template, redirect, url_for, session, flash, request, Response
from models import db, User, AuditLog, audit


# ---------- ALL USERS (READ - with search and pagination) ----------
def users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = User.query
    if q:
        like = f'%{q}%'
        query = query.filter(User.name.like(like) | User.email.like(like))

    pagination = query.order_by(User.id).paginate(page=page, per_page=10, error_out=False)
    return render_template('users.html', users=pagination.items,
                           pagination=pagination, q=q)


# ---------- EXPORT USERS AS CSV ----------
def users_export():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(['ID', 'Name', 'Email', 'Role', 'Joined'])
    for u in User.query.order_by(User.id).all():
        writer.writerow([u.id, u.name, u.email, u.role.role_name,
                         u.created_at.strftime('%Y-%m-%d') if u.created_at else ''])
    return Response(out.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=users.csv'})


# ---------- AUDIT LOG (who did what and when) ----------
def audit_log():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    pagination = (AuditLog.query.order_by(AuditLog.id.desc())
                  .paginate(page=page, per_page=20, error_out=False))
    return render_template('audit.html', logs=pagination.items, pagination=pagination)


# ---------- DELETE USER (DELETE - cascade removes related data) ----------
def delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if id == session['user_id']:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))

    user = db.session.get(User, id)
    if user:
        audit(session['user_id'], 'delete_user', f'{user.name} <{user.email}>')
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.')
    return redirect(url_for('users'))
