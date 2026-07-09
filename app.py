# ============================================================
# Internship Portal - Simple Flask + MySQL app
#
# CRUD operations used in this project:
#   CREATE -> INSERT INTO ...   (register, post internship, apply)
#   READ   -> SELECT ...        (login, list internships, list applications)
#   UPDATE -> UPDATE ...        (edit internship, change application status)
#   DELETE -> DELETE FROM ...   (delete internship, withdraw application)
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = 'my-secret-key'   # needed for sessions and flash messages


# ---------- Database connection ----------
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='password',          # <-- change to your MySQL password
        database='internship_db',
        cursorclass=pymysql.cursors.DictCursor  # rows come back as dictionaries
    )


# ============================================================
# HOME
# ============================================================
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ============================================================
# REGISTER  (CREATE - insert a new user)
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']            # 'student' or 'company'

        db = get_db()
        cur = db.cursor()

        # check if email already exists (READ)
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            db.close()
            flash('Email is already registered.')
            return redirect(url_for('register'))

        # insert the new user (CREATE)
        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, role)
        )
        db.commit()
        db.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')


# ============================================================
# LOGIN  (READ - select user and check password)
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            # save user info in the session
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.')

    return render_template('login.html')


# ============================================================
# LOGOUT
# ============================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# DASHBOARD  (shows different info for each role)
# ============================================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM internships")
    total_internships = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'student'")
    total_students = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'company'")
    total_companies = cur.fetchone()['total']
    db.close()

    return render_template('dashboard.html',
                           total_internships=total_internships,
                           total_students=total_students,
                           total_companies=total_companies)


# ============================================================
# INTERNSHIPS - list all  (READ with JOIN)
# ============================================================
@app.route('/internships')
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    # join with users table to also get the company name
    cur.execute("""
        SELECT internships.*, users.name AS company_name
        FROM internships
        JOIN users ON internships.company_id = users.id
        ORDER BY internships.id DESC
    """)
    items = cur.fetchall()

    # which internships has this student already applied to?
    applied_ids = []
    if session['role'] == 'student':
        cur.execute("SELECT internship_id FROM applications WHERE student_id = %s",
                    (session['user_id'],))
        applied_ids = [row['internship_id'] for row in cur.fetchall()]
    db.close()

    return render_template('internships.html', internships=items, applied_ids=applied_ids)


# ============================================================
# ADD INTERNSHIP  (CREATE) - company only
# ============================================================
@app.route('/internships/add', methods=['GET', 'POST'])
def add_internship():
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO internships (company_id, title, description, skills, deadline) "
            "VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], request.form['title'], request.form['description'],
             request.form['skills'], request.form['deadline'] or None)
        )
        db.commit()
        db.close()
        flash('Internship posted.')
        return redirect(url_for('internships'))

    return render_template('add_internship.html')


# ============================================================
# EDIT INTERNSHIP  (UPDATE) - company only, own posts only
# ============================================================
@app.route('/internships/edit/<int:id>', methods=['GET', 'POST'])
def edit_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s",
                (id, session['user_id']))
    internship = cur.fetchone()

    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    if request.method == 'POST':
        cur.execute(
            "UPDATE internships SET title = %s, description = %s, skills = %s, deadline = %s "
            "WHERE id = %s",
            (request.form['title'], request.form['description'],
             request.form['skills'], request.form['deadline'] or None, id)
        )
        db.commit()
        db.close()
        flash('Internship updated.')
        return redirect(url_for('internships'))

    db.close()
    return render_template('edit_internship.html', internship=internship)


# ============================================================
# DELETE INTERNSHIP  (DELETE) - company only, own posts only
# ============================================================
@app.route('/internships/delete/<int:id>', methods=['POST'])
def delete_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    # delete applications of this internship first (foreign key)
    cur.execute("DELETE FROM applications WHERE internship_id = %s", (id,))
    cur.execute("DELETE FROM internships WHERE id = %s AND company_id = %s",
                (id, session['user_id']))
    db.commit()
    db.close()
    flash('Internship deleted.')
    return redirect(url_for('internships'))


# ============================================================
# APPLY  (CREATE) - student only
# ============================================================
@app.route('/apply/<int:internship_id>', methods=['POST'])
def apply(internship_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    # do not allow applying twice
    cur.execute("SELECT id FROM applications WHERE student_id = %s AND internship_id = %s",
                (session['user_id'], internship_id))
    if cur.fetchone():
        flash('You already applied to this internship.')
    else:
        cur.execute("INSERT INTO applications (student_id, internship_id) VALUES (%s, %s)",
                    (session['user_id'], internship_id))
        db.commit()
        flash('Application submitted!')
    db.close()
    return redirect(url_for('my_applications'))


# ============================================================
# MY APPLICATIONS  (READ) - student only
# ============================================================
@app.route('/my_applications')
def my_applications():
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT applications.id, applications.status,
               internships.title, users.name AS company_name
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN users       ON internships.company_id = users.id
        WHERE applications.student_id = %s
    """, (session['user_id'],))
    apps = cur.fetchall()
    db.close()
    return render_template('my_applications.html', applications=apps)


# ============================================================
# WITHDRAW APPLICATION  (DELETE) - student only
# ============================================================
@app.route('/withdraw/<int:id>', methods=['POST'])
def withdraw(id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM applications WHERE id = %s AND student_id = %s",
                (id, session['user_id']))
    db.commit()
    db.close()
    flash('Application withdrawn.')
    return redirect(url_for('my_applications'))


# ============================================================
# VIEW APPLICANTS  (READ) - company only
# ============================================================
@app.route('/applicants/<int:internship_id>')
def applicants(internship_id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s",
                (internship_id, session['user_id']))
    internship = cur.fetchone()
    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    cur.execute("""
        SELECT applications.id, applications.status,
               users.name AS student_name, users.email AS student_email
        FROM applications
        JOIN users ON applications.student_id = users.id
        WHERE applications.internship_id = %s
    """, (internship_id,))
    apps = cur.fetchall()
    db.close()
    return render_template('applicants.html', internship=internship, applications=apps)


# ============================================================
# UPDATE APPLICATION STATUS  (UPDATE) - company only
# ============================================================
@app.route('/applications/<int:id>/status', methods=['POST'])
def update_status(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    new_status = request.form['status']
    db = get_db()
    cur = db.cursor()
    # make sure the application belongs to this company's internship
    cur.execute("""
        UPDATE applications
        JOIN internships ON applications.internship_id = internships.id
        SET applications.status = %s
        WHERE applications.id = %s AND internships.company_id = %s
    """, (new_status, id, session['user_id']))
    db.commit()

    cur.execute("SELECT internship_id FROM applications WHERE id = %s", (id,))
    row = cur.fetchone()
    db.close()
    flash('Status updated.')
    return redirect(url_for('applicants', internship_id=row['internship_id']))


# ============================================================
# ALL USERS  (READ) - admin only
# ============================================================
@app.route('/users')
def users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, email, role FROM users ORDER BY id")
    all_users = cur.fetchall()
    db.close()
    return render_template('users.html', users=all_users)


# ============================================================
# DELETE USER  (DELETE) - admin only
# ============================================================
@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if id == session['user_id']:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))

    db = get_db()
    cur = db.cursor()
    # remove the user's related records first (foreign keys)
    cur.execute("DELETE FROM applications WHERE student_id = %s", (id,))
    cur.execute("DELETE FROM applications WHERE internship_id IN "
                "(SELECT id FROM internships WHERE company_id = %s)", (id,))
    cur.execute("DELETE FROM internships WHERE company_id = %s", (id,))
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    db.commit()
    db.close()
    flash('User deleted.')
    return redirect(url_for('users'))


if __name__ == '__main__':
    app.run(debug=True)
