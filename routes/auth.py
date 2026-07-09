# ============================================================
# Auth pages: register (3 types), login, logout
# ============================================================

from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, role_id_of


# ---------- REGISTER - choose account type ----------
def register():
    return render_template('register.html')


# ---------- REGISTER STUDENT (CREATE - insert into users + students) ----------
def register_student():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()

        # email must not be taken already (READ)
        cur.execute("SELECT id FROM users WHERE email = %s", (request.form['email'],))
        if cur.fetchone():
            db.close()
            flash('Email is already registered.')
            return redirect(url_for('register_student'))

        # 1) insert into users (CREATE)
        cur.execute(
            "INSERT INTO users (role_id, name, email, password) VALUES (%s, %s, %s, %s)",
            (role_id_of(cur, 'student'), request.form['name'], request.form['email'],
             generate_password_hash(request.form['password']))
        )
        new_user_id = cur.lastrowid   # id of the user we just inserted

        # 2) insert into students (CREATE)
        cur.execute(
            "INSERT INTO students (user_id, roll_number, department, semester, skills) "
            "VALUES (%s, %s, %s, %s, %s)",
            (new_user_id, request.form['roll_number'], request.form['department'],
             request.form['semester'] or None, request.form['skills'])
        )
        db.commit()
        db.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_student.html')


# ---------- REGISTER COMPANY (CREATE - insert into users + companies) ----------
def register_company():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (request.form['email'],))
        if cur.fetchone():
            db.close()
            flash('Email is already registered.')
            return redirect(url_for('register_company'))

        cur.execute(
            "INSERT INTO users (role_id, name, email, password) VALUES (%s, %s, %s, %s)",
            (role_id_of(cur, 'company'), request.form['name'], request.form['email'],
             generate_password_hash(request.form['password']))
        )
        new_user_id = cur.lastrowid

        cur.execute(
            "INSERT INTO companies (user_id, industry, location, description) "
            "VALUES (%s, %s, %s, %s)",
            (new_user_id, request.form['industry'], request.form['location'],
             request.form['description'])
        )
        db.commit()
        db.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_company.html')


# ---------- REGISTER SUPERVISOR (CREATE - insert into users + supervisors) ----------
def register_supervisor():
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        cur.execute("SELECT id FROM users WHERE email = %s", (request.form['email'],))
        if cur.fetchone():
            db.close()
            flash('Email is already registered.')
            return redirect(url_for('register_supervisor'))

        cur.execute(
            "INSERT INTO users (role_id, name, email, password) VALUES (%s, %s, %s, %s)",
            (role_id_of(cur, 'supervisor'), request.form['name'], request.form['email'],
             generate_password_hash(request.form['password']))
        )
        new_user_id = cur.lastrowid

        cur.execute(
            "INSERT INTO supervisors (user_id, company_id, designation, department) "
            "VALUES (%s, %s, %s, %s)",
            (new_user_id, request.form['company_id'],
             request.form['designation'], request.form['department'])
        )
        db.commit()
        db.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    # for the company dropdown in the form
    cur.execute("""
        SELECT companies.id, users.name
        FROM companies JOIN users ON companies.user_id = users.id
    """)
    companies = cur.fetchall()
    db.close()
    return render_template('register_supervisor.html', companies=companies)


# ---------- LOGIN (READ - join users with roles, check password) ----------
def login():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT users.*, roles.role_name
            FROM users JOIN roles ON users.role_id = roles.id
            WHERE users.email = %s
        """, (request.form['email'],))
        user = cur.fetchone()
        db.close()

        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role_name']
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')


# ---------- LOGOUT ----------
def logout():
    session.clear()
    return redirect(url_for('login'))
