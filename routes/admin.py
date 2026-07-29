# ============================================================
# Admin pages: user management (search + pagination + export),
# audit log, delete user
# ============================================================

import csv
import io
from flask import render_template, redirect, url_for, session, flash, request, Response
from datetime import datetime
from models import db, User, College, Student, AuditLog, audit, notify


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


# ---------- COLLEGES (READ + CREATE) - admin only ----------
def colleges():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        if College.query.filter_by(name=name).first():
            flash('That college is already registered.')
        else:
            db.session.add(College(name=name,
                                   affiliation=request.form['affiliation'],
                                   address=request.form['address']))
            audit(session['user_id'], 'add_college', name)
            db.session.commit()
            flash('College added.')
        return redirect(url_for('colleges'))

    items = College.query.order_by(College.name).all()
    counts = {c.id: Student.query.filter_by(college_id=c.id).count() for c in items}
    return render_template('colleges.html', colleges=items, counts=counts)


# ---------- DELETE COLLEGE ----------
def delete_college(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    college = db.session.get(College, id)
    if college:
        audit(session['user_id'], 'delete_college', college.name)
        db.session.delete(college)      # students keep their record (college set to NULL)
        db.session.commit()
        flash('College removed.')
    return redirect(url_for('colleges'))


# ---------- VERIFICATION QUEUE (READ) - admin only ----------
def verifications():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    status = request.args.get('status', 'pending')
    query = User.query.filter(User.email != session.get('email', ''))
    if status in ('pending', 'verified', 'rejected'):
        query = query.filter_by(verification_status=status)
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
        audit(session['user_id'], 'verify_user', f'{user.name} <{user.email}>')
        db.session.commit()
        flash(f'{user.name} has been approved.')
    return redirect(url_for('verifications'))


# ---------- REJECT AN ACCOUNT (UPDATE) ----------
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
        audit(session['user_id'], 'reject_user',
              f'{user.name} <{user.email}>: {reason or "no reason"}')
        db.session.commit()
        flash(f'{user.name} has been rejected.')
    return redirect(url_for('verifications'))
