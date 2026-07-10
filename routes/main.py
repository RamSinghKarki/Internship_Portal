# ============================================================
# Main pages: landing page, dashboard, internship list
# ============================================================

from flask import render_template, redirect, url_for, session
from models import (db, User, Student, Company, Supervisor, Internship,
                    Application, ProgressLog,
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
    return render_template('index.html', counts=counts)


# ---------- DASHBOARD (each role sees only its own numbers) ----------
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    stats = []   # list of (label, number) shown as cards

    if session['role'] == 'student':
        me = current_student()
        stats.append(('Open Internships', Internship.query.filter_by(status='open').count()))
        stats.append(('Companies', Company.query.count()))
        stats.append(('My Applications', Application.query.filter_by(student_id=me.id).count()))
        stats.append(('Selected', Application.query.filter_by(student_id=me.id, status='selected').count()))

    elif session['role'] == 'company':
        me = current_company()
        stats.append(('My Internships', Internship.query.filter_by(company_id=me.id).count()))
        stats.append(('Applications Received',
                      Application.query.join(Internship)
                      .filter(Internship.company_id == me.id).count()))
        stats.append(('Students Registered', Student.query.count()))
        stats.append(('My Supervisors', Supervisor.query.filter_by(company_id=me.id).count()))

    elif session['role'] == 'supervisor':
        me = current_supervisor()
        my_logs = (ProgressLog.query.join(Application).join(Internship)
                   .filter(Internship.company_id == me.company_id))
        stats.append(('My Students',
                      Application.query.join(Internship)
                      .filter(Internship.company_id == me.company_id,
                              Application.status == 'selected').count()))
        stats.append(('Logs Submitted', my_logs.count()))
        stats.append(('Awaiting My Feedback', my_logs.filter(ProgressLog.feedback.is_(None)).count()))

    else:   # admin sees the whole system
        stats.append(('Students', Student.query.count()))
        stats.append(('Companies', Company.query.count()))
        stats.append(('Supervisors', Supervisor.query.count()))
        stats.append(('Internships', Internship.query.count()))
        stats.append(('Applications', Application.query.count()))

    return render_template('dashboard.html', stats=stats)


# ---------- INTERNSHIP LIST (READ) ----------
# students see open internships, a company sees its own posts
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    applied_ids = []
    if session['role'] == 'company':
        me = current_company()
        items = (Internship.query.filter_by(company_id=me.id)
                 .order_by(Internship.id.desc()).all())
    elif session['role'] == 'student':
        me = current_student()
        applied_ids = [a.internship_id for a in me.applications]
        items = (Internship.query.filter_by(status='open')
                 .order_by(Internship.id.desc()).all())
    elif session['role'] == 'supervisor':
        me = current_supervisor()
        items = (Internship.query.filter_by(company_id=me.company_id)
                 .order_by(Internship.id.desc()).all())
    else:   # admin sees everything
        items = Internship.query.order_by(Internship.id.desc()).all()

    return render_template('internships.html', internships=items, applied_ids=applied_ids)
