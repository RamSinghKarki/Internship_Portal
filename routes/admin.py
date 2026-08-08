# ============================================================
# Admin pages: user management (search + pagination + export),
# account verification, delete user
# ============================================================

import csv
import io
from flask import render_template, redirect, url_for, session, flash, request, Response
from datetime import datetime
from models import db, User, notify


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


# ---------- DELETE USER (DELETE - cascade removes related data) ----------
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


# ---------- VERIFICATION QUEUE (READ) - admin only ----------
def verifications():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    status = request.args.get('status', 'pending')
    query = User.query
    if status in ('pending', 'verified', 'rejected'):
        query = query.filter_by(verification_status=status)
    # role_id 1 is the admin, who does not need approving
    users = query.filter(User.role_id != 1).order_by(User.id.desc()).all()

    counts = {s: User.query.filter_by(verification_status=s)
              .filter(User.role_id != 1).count()
              for s in ('pending', 'verified', 'rejected')}
    return render_template('verifications.html', users=users,
                           status=status, counts=counts)


# ---------- APPROVE AN ACCOUNT (UPDATE) ----------
def verify_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = db.session.get(User, id)
    if user and user.role.role_name != 'admin':
        user.verification_status = 'verified'
        user.verification_remarks = None
        user.verified_at = datetime.now()
        notify(user.id, 'Your account has been approved. You can now use the portal.',
               url_for('dashboard'))
        db.session.commit()
        flash(f'{user.name} has been approved.')
    return redirect(url_for('verifications'))


# ---------- REJECT AN ACCOUNT (UPDATE) ----------
# the reason is stored on the user and shown to them on every page
def reject_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    user = db.session.get(User, id)
    if user and user.role.role_name != 'admin':
        reason = request.form.get('remarks', '').strip()
        user.verification_status = 'rejected'
        user.verification_remarks = reason or None
        notify(user.id,
               f'Your account was not approved. Reason: {reason or "no reason given"}',
               url_for('dashboard'))
        db.session.commit()
        flash(f'{user.name} has been rejected.')
    return redirect(url_for('verifications'))
