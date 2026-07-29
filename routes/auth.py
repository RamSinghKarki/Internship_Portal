# ============================================================
# Auth pages: register (3 types), login, logout
# ============================================================

import os
import time
from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Role, User, Student, Company, Supervisor, College, audit

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}


def save_document(file):
    """Save an uploaded file into static/uploads and return its
    relative path, or None if no valid file was given."""
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return None
    fname = f"{int(time.time())}_{secure_filename(file.filename)}"
    file.save(os.path.join(current_app.root_path, 'static', 'uploads', fname))
    return f"uploads/{fname}"


def _email_taken(email):
    return User.query.filter_by(email=email).first() is not None


# ---------- REGISTER - choose account type ----------
def register():
    return render_template('register.html')


# ---------- REGISTER STUDENT (CREATE - users + students rows) ----------
def register_student():
    colleges = College.query.order_by(College.name).all()
    if request.method == 'POST':
        if _email_taken(request.form['email']):
            flash('Email is already registered.')
            return redirect(url_for('register_student'))

        # a valid document upload is required to create a student account
        document = save_document(request.files.get('document'))
        if not document:
            flash('Please upload a valid document (pdf, png, jpg, doc or docx).')
            return redirect(url_for('register_student'))

        role = Role.query.filter_by(role_name='student').first()
        user = User(role_id=role.id, name=request.form['name'], email=request.form['email'])
        user.set_password(request.form['password'])

        # student profile linked to the new user through the relationship
        student = Student(user=user,
                          college_id=request.form.get('college_id') or None,
                          roll_number=request.form['roll_number'],
                          department=request.form['department'],
                          semester=request.form['semester'] or None,
                          skills=request.form['skills'],
                          document_url=document)
        db.session.add(student)     # adds the user too (relationship)
        db.session.commit()
        audit(user.id, 'register', f'student {user.email}')
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_student.html', colleges=colleges)


# ---------- REGISTER COMPANY (CREATE - users + companies rows) ----------
def register_company():
    if request.method == 'POST':
        if _email_taken(request.form['email']):
            flash('Email is already registered.')
            return redirect(url_for('register_company'))

        role = Role.query.filter_by(role_name='company').first()
        user = User(role_id=role.id, name=request.form['name'], email=request.form['email'])
        user.set_password(request.form['password'])

        company = Company(user=user,
                          industry=request.form['industry'],
                          location=request.form['location'],
                          description=request.form['description'])
        db.session.add(company)
        db.session.commit()
        audit(user.id, 'register', f'company {user.email}')
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_company.html')


# ---------- REGISTER SUPERVISOR (CREATE - users + supervisors rows) ----------
def register_supervisor():
    if request.method == 'POST':
        if _email_taken(request.form['email']):
            flash('Email is already registered.')
            return redirect(url_for('register_supervisor'))

        role = Role.query.filter_by(role_name='supervisor').first()
        user = User(role_id=role.id, name=request.form['name'], email=request.form['email'])
        user.set_password(request.form['password'])

        sup = Supervisor(user=user,
                         company_id=request.form['company_id'],
                         designation=request.form['designation'],
                         department=request.form['department'])
        db.session.add(sup)
        db.session.commit()
        audit(user.id, 'register', f'supervisor {user.email}')
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    # for the company dropdown in the form
    companies = Company.query.all()
    return render_template('register_supervisor.html', companies=companies)


# ---------- LOGIN (READ - find user, check password hash) ----------
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role.role_name   # via the Role relationship
            audit(user.id, 'login', user.email)
            db.session.commit()
            return redirect(url_for('dashboard'))

        audit(None, 'login_failed', request.form['email'])
        db.session.commit()
        flash('Invalid email or password.')

    return render_template('login.html')


# ---------- LOGOUT ----------
def logout():
    session.clear()
    return redirect(url_for('login'))
