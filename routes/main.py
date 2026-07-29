# ============================================================
# Main pages: landing page, dashboard (key figures),
# internship list with search, notifications
# ============================================================

from datetime import datetime
from flask import render_template, redirect, url_for, session, request
from models import (db, User, Student, Company, Supervisor, Internship, College,
                    Application, ProgressLog, Notification,
                    current_student, current_company, current_supervisor)


# ---------- LANDING PAGE (public - live counts) ----------
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    counts = {
        'students':    Student.query.count(),
        'companies':   Company.query.count(),
        'supervisors': Supervisor.query.count(),
        'internships': Internship.query.count(),
    }

    # companies working with the portal, newest first, with their number
    # of open internships (shown as cards on the landing page)
    partners = []
    for company in Company.query.order_by(Company.id.desc()).limit(12).all():
        open_count = Internship.query.filter_by(company_id=company.id,
                                                status='open').count()
        partners.append({'name': company.user.name,
                         'industry': company.industry,
                         'location': company.location,
                         'initials': ''.join(w[0] for w in company.user.name.split()[:2]).upper(),
                         'open_internships': open_count})

    # colleges taking part, with how many of their students have joined
    campuses = []
    for college in College.query.order_by(College.name).limit(12).all():
        campuses.append({'name': college.name,
                         'affiliation': college.affiliation,
                         'address': college.address,
                         'initials': ''.join(w[0] for w in college.name.split()[:3]).upper(),
                         'students': Student.query.filter_by(college_id=college.id).count()})

    return render_template('index.html', counts=counts, partners=partners,
                           campuses=campuses)


# ---------- DASHBOARD (role-specific key figures) ----------
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    stats = []    # list of (label, number, small sub-text)

    if session['role'] == 'student':
        me = current_student()
        my_apps = Application.query.filter_by(student_id=me.id)
        stats.append(('Open Internships', Internship.query.filter_by(status='open').count(), ''))
        stats.append(('Companies', Company.query.count(), ''))
        stats.append(('My Applications', my_apps.count(), ''))
        stats.append(('Selected', my_apps.filter_by(status='selected').count(), ''))

    elif session['role'] == 'company':
        me = current_company()
        received = Application.query.join(Internship).filter(Internship.company_id == me.id)
        stats.append(('My Internships', Internship.query.filter_by(company_id=me.id).count(), ''))
        stats.append(('Applications Received', received.count(),
                      f'+{received.filter(Application.applied_date >= month_start).count()} this month'))
        stats.append(('Selected', received.filter(Application.status == 'selected').count(), ''))
        stats.append(('My Supervisors', Supervisor.query.filter_by(company_id=me.id).count(), ''))

    elif session['role'] == 'supervisor':
        me = current_supervisor()
        selected = (Application.query.join(Internship)
                    .filter(Internship.company_id == me.company_id,
                            Application.status == 'selected'))
        my_logs = (ProgressLog.query.join(Application).join(Internship)
                   .filter(Internship.company_id == me.company_id))
        stats.append(('My Students', selected.count(), ''))
        stats.append(('Logs Submitted', my_logs.count(),
                      f'+{my_logs.filter(ProgressLog.submitted_date >= month_start).count()} this month'))
        stats.append(('Awaiting My Feedback', my_logs.filter(ProgressLog.feedback.is_(None)).count(), ''))

    else:   # admin - whole system
        for label, model, datecol in (
                ('Students', Student, None), ('Companies', Company, None),
                ('Supervisors', Supervisor, None),
                ('Internships', Internship, Internship.posted_date),
                ('Applications', Application, Application.applied_date)):
            sub = ''
            if datecol is not None:
                sub = f'+{model.query.filter(datecol >= month_start).count()} this month'
            stats.append((label, model.query.count(), sub))

    return render_template('dashboard.html', stats=stats)


# ---------- INTERNSHIP LIST (READ + search) ----------
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    skill = request.args.get('skill', '').strip()

    query = Internship.query
    if q:
        like = f'%{q}%'
        query = query.filter(Internship.title.like(like) |
                             Internship.description.like(like) |
                             Internship.required_skills.like(like))
    if skill:
        query = query.filter(Internship.required_skills.like(f'%{skill}%'))

    applied_ids = []
    if session['role'] == 'company':
        me = current_company()
        query = query.filter_by(company_id=me.id)
    elif session['role'] == 'student':
        me = current_student()
        applied_ids = [a.internship_id for a in me.applications]
        query = query.filter_by(status='open')
    elif session['role'] == 'supervisor':
        me = current_supervisor()
        query = query.filter_by(company_id=me.company_id)

    items = query.order_by(Internship.id.desc()).all()
    return render_template('internships.html', internships=items,
                           applied_ids=applied_ids, q=q, skill=skill)


# ---------- NOTIFICATIONS (bell icon page) ----------
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    items = (Notification.query.filter_by(user_id=session['user_id'])
             .order_by(Notification.id.desc()).limit(50).all())
    # mark everything as read once the page is opened
    (Notification.query.filter_by(user_id=session['user_id'], is_read=False)
     .update({'is_read': True}))
    db.session.commit()
    return render_template('notifications.html', items=items)
