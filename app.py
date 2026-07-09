# ============================================================
# Internship Portal - Simple Flask + MySQL app (full ER design)
#
# Tables : roles, users, students, companies, supervisors,
#          internships, applications, progress_logs
#
# CRUD operations used in this project:
#   CREATE -> INSERT INTO  (register, post internship, apply, submit log)
#   READ   -> SELECT       (login, lists, joins for reports)
#   UPDATE -> UPDATE       (edit internship, select/reject, give feedback)
#   DELETE -> DELETE FROM  (delete internship, withdraw, delete user)
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


# ---------- Small helpers ----------
def role_id_of(cur, role_name):
    """Look up the id of a role from the roles table."""
    cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
    return cur.fetchone()['id']


def my_student(cur):
    """Return the students row of the logged-in user."""
    cur.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()


def my_company(cur):
    """Return the companies row of the logged-in user."""
    cur.execute("SELECT * FROM companies WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()


def my_supervisor(cur):
    """Return the supervisors row of the logged-in user."""
    cur.execute("SELECT * FROM supervisors WHERE user_id = %s", (session['user_id'],))
    return cur.fetchone()


# ============================================================
# HOME
# ============================================================
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# ============================================================
# REGISTER - choose account type
# ============================================================
@app.route('/register')
def register():
    return render_template('register.html')


# ============================================================
# REGISTER STUDENT  (CREATE - insert into users + students)
# ============================================================
@app.route('/register/student', methods=['GET', 'POST'])
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


# ============================================================
# REGISTER COMPANY  (CREATE - insert into users + companies)
# ============================================================
@app.route('/register/company', methods=['GET', 'POST'])
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


# ============================================================
# REGISTER SUPERVISOR  (CREATE - insert into users + supervisors)
# ============================================================
@app.route('/register/supervisor', methods=['GET', 'POST'])
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


# ============================================================
# LOGIN  (READ - join users with roles, check password)
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# DASHBOARD  (READ - counts from every main table)
# ============================================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    counts = {}
    for table in ('students', 'companies', 'supervisors', 'internships', 'applications'):
        cur.execute(f"SELECT COUNT(*) AS c FROM {table}")
        counts[table] = cur.fetchone()['c']
    db.close()
    return render_template('dashboard.html', counts=counts)


# ============================================================
# INTERNSHIPS - list  (READ with JOIN)
# students see open internships, a company sees its own posts
# ============================================================
@app.route('/internships')
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    base_query = """
        SELECT internships.*, users.name AS company_name
        FROM internships
        JOIN companies ON internships.company_id = companies.id
        JOIN users     ON companies.user_id = users.id
    """

    applied_ids = []
    if session['role'] == 'company':
        me = my_company(cur)
        cur.execute(base_query + " WHERE internships.company_id = %s "
                    "ORDER BY internships.id DESC", (me['id'],))
    elif session['role'] == 'student':
        cur.execute(base_query + " WHERE internships.status = 'open' "
                    "ORDER BY internships.id DESC")
        me = my_student(cur)
        cur.execute("SELECT internship_id FROM applications WHERE student_id = %s", (me['id'],))
        applied_ids = [r['internship_id'] for r in cur.fetchall()]
        cur.execute(base_query + " WHERE internships.status = 'open' "
                    "ORDER BY internships.id DESC")
    else:   # admin / supervisor see everything
        cur.execute(base_query + " ORDER BY internships.id DESC")

    items = cur.fetchall()
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
        me = my_company(cur)
        cur.execute(
            "INSERT INTO internships (company_id, title, description, required_skills, "
            "duration_weeks, stipend, vacancies) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (me['id'], request.form['title'], request.form['description'],
             request.form['required_skills'], request.form['duration_weeks'] or None,
             request.form['stipend'], request.form['vacancies'] or None)
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
    me = my_company(cur)
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s", (id, me['id']))
    internship = cur.fetchone()

    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    if request.method == 'POST':
        cur.execute(
            "UPDATE internships SET title = %s, description = %s, required_skills = %s, "
            "duration_weeks = %s, stipend = %s, vacancies = %s, status = %s WHERE id = %s",
            (request.form['title'], request.form['description'],
             request.form['required_skills'], request.form['duration_weeks'] or None,
             request.form['stipend'], request.form['vacancies'] or None,
             request.form['status'], id)
        )
        db.commit()
        db.close()
        flash('Internship updated.')
        return redirect(url_for('internships'))

    db.close()
    return render_template('edit_internship.html', internship=internship)


# ============================================================
# DELETE INTERNSHIP  (DELETE) - company only, own posts only
# (its applications and logs are removed by ON DELETE CASCADE)
# ============================================================
@app.route('/internships/delete/<int:id>', methods=['POST'])
def delete_internship(id):
    if session.get('role') != 'company':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    cur.execute("DELETE FROM internships WHERE id = %s AND company_id = %s", (id, me['id']))
    db.commit()
    db.close()
    flash('Internship deleted.')
    return redirect(url_for('internships'))


# ============================================================
# APPLY  (CREATE) - student only, with cover letter
# ============================================================
@app.route('/apply/<int:internship_id>', methods=['POST'])
def apply(internship_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)

    cur.execute("SELECT id FROM applications WHERE student_id = %s AND internship_id = %s",
                (me['id'], internship_id))
    if cur.fetchone():
        flash('You already applied to this internship.')
    else:
        cur.execute(
            "INSERT INTO applications (student_id, internship_id, cover_letter) "
            "VALUES (%s, %s, %s)",
            (me['id'], internship_id, request.form['cover_letter'])
        )
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
    me = my_student(cur)
    cur.execute("""
        SELECT applications.id, applications.status, applications.applied_date,
               internships.title, users.name AS company_name
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN companies   ON internships.company_id = companies.id
        JOIN users       ON companies.user_id = users.id
        WHERE applications.student_id = %s
    """, (me['id'],))
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
    me = my_student(cur)
    cur.execute("DELETE FROM applications WHERE id = %s AND student_id = %s", (id, me['id']))
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
    me = my_company(cur)
    cur.execute("SELECT * FROM internships WHERE id = %s AND company_id = %s",
                (internship_id, me['id']))
    internship = cur.fetchone()
    if not internship:
        db.close()
        flash('Internship not found.')
        return redirect(url_for('internships'))

    cur.execute("""
        SELECT applications.id, applications.status, applications.cover_letter,
               users.name AS student_name, users.email AS student_email,
               students.roll_number, students.department, students.semester, students.skills
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN users    ON students.user_id = users.id
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

    db = get_db()
    cur = db.cursor()
    me = my_company(cur)
    # only allow changing applications of this company's internships
    cur.execute("""
        UPDATE applications
        JOIN internships ON applications.internship_id = internships.id
        SET applications.status = %s
        WHERE applications.id = %s AND internships.company_id = %s
    """, (request.form['status'], id, me['id']))
    db.commit()

    cur.execute("SELECT internship_id FROM applications WHERE id = %s", (id,))
    row = cur.fetchone()
    db.close()
    flash('Status updated.')
    return redirect(url_for('applicants', internship_id=row['internship_id']))


# ============================================================
# WEEKLY LOGS of a student  (CREATE + READ) - student only
# a student can write logs only for a 'selected' application
# ============================================================
@app.route('/my_logs/<int:application_id>', methods=['GET', 'POST'])
def my_logs(application_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_student(cur)

    # the application must belong to this student and be selected
    cur.execute("""
        SELECT applications.*, internships.title
        FROM applications JOIN internships ON applications.internship_id = internships.id
        WHERE applications.id = %s AND applications.student_id = %s
              AND applications.status = 'selected'
    """, (application_id, me['id']))
    application = cur.fetchone()
    if not application:
        db.close()
        flash('Log book is only available for selected applications.')
        return redirect(url_for('my_applications'))

    if request.method == 'POST':
        cur.execute(
            "INSERT INTO progress_logs (application_id, week_number, description) "
            "VALUES (%s, %s, %s)",
            (application_id, request.form['week_number'] or None, request.form['description'])
        )
        db.commit()
        db.close()
        flash('Weekly log submitted.')
        return redirect(url_for('my_logs', application_id=application_id))

    cur.execute("SELECT * FROM progress_logs WHERE application_id = %s ORDER BY week_number",
                (application_id,))
    logs = cur.fetchall()
    db.close()
    return render_template('my_logs.html', application=application, logs=logs)


# ============================================================
# MY STUDENTS  (READ) - supervisor only
# selected students doing internships at the supervisor's company
# ============================================================
@app.route('/students')
def students():
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)
    cur.execute("""
        SELECT applications.id AS application_id, users.name AS student_name,
               students.roll_number, internships.title
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN students    ON applications.student_id = students.id
        JOIN users       ON students.user_id = users.id
        WHERE internships.company_id = %s AND applications.status = 'selected'
    """, (me['company_id'],))
    rows = cur.fetchall()
    db.close()
    return render_template('students.html', rows=rows)


# ============================================================
# VIEW LOGS + GIVE FEEDBACK  - supervisor only
# ============================================================
@app.route('/logs/<int:application_id>')
def view_logs(application_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)

    # the application must be at the supervisor's company
    cur.execute("""
        SELECT applications.id, users.name AS student_name, internships.title
        FROM applications
        JOIN internships ON applications.internship_id = internships.id
        JOIN students    ON applications.student_id = students.id
        JOIN users       ON students.user_id = users.id
        WHERE applications.id = %s AND internships.company_id = %s
    """, (application_id, me['company_id']))
    application = cur.fetchone()
    if not application:
        db.close()
        flash('Not found.')
        return redirect(url_for('students'))

    cur.execute("SELECT * FROM progress_logs WHERE application_id = %s ORDER BY week_number",
                (application_id,))
    logs = cur.fetchall()
    db.close()
    return render_template('view_logs.html', application=application, logs=logs)


# ============================================================
# FEEDBACK on a log  (UPDATE) - supervisor only
# ============================================================
@app.route('/logs/<int:log_id>/feedback', methods=['POST'])
def give_feedback(log_id):
    if session.get('role') != 'supervisor':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    me = my_supervisor(cur)
    # only logs of applications at the supervisor's company
    cur.execute("""
        UPDATE progress_logs
        JOIN applications ON progress_logs.application_id = applications.id
        JOIN internships  ON applications.internship_id = internships.id
        SET progress_logs.feedback = %s, progress_logs.marks = %s,
            progress_logs.supervisor_id = %s
        WHERE progress_logs.id = %s AND internships.company_id = %s
    """, (request.form['feedback'], request.form['marks'] or None,
          me['id'], log_id, me['company_id']))
    db.commit()

    cur.execute("SELECT application_id FROM progress_logs WHERE id = %s", (log_id,))
    row = cur.fetchone()
    db.close()
    flash('Feedback saved.')
    return redirect(url_for('view_logs', application_id=row['application_id']))


# ============================================================
# ALL USERS  (READ) - admin only
# ============================================================
@app.route('/users')
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


# ============================================================
# DELETE USER  (DELETE) - admin only
# (student/company/supervisor rows and their data are removed
#  automatically because of ON DELETE CASCADE)
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
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    db.commit()
    db.close()
    flash('User deleted.')
    return redirect(url_for('users'))


if __name__ == '__main__':
    app.run(debug=True)
