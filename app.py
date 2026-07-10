# ============================================================
# Internship Portal - main file
#
# The database models (tables) are in models.py.
# The code for the pages lives in the routes/ folder:
#   routes/auth.py       -> register + login + logout
#   routes/main.py       -> landing page + dashboard + internship list
#   routes/student.py    -> apply, my applications, weekly logs
#   routes/company.py    -> post/edit/delete internships, applicants
#   routes/supervisor.py -> my students, view logs, give feedback
#   routes/admin.py      -> manage users
#
# Below, app.add_url_rule() connects every URL of the site
# to its function - like a table of contents of the whole app.
# ============================================================

from flask import Flask
from models import db

app = Flask(__name__)
app.secret_key = 'my-secret-key'   # needed for sessions and flash messages

# ---------- database connection (SQLAlchemy + PyMySQL) ----------
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:password@localhost/internship_db'   # <-- change 'password' to your MySQL password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from routes import main, auth, student, company, supervisor, admin

# ---------- home + dashboard + internship list ----------
app.add_url_rule('/',            view_func=main.home)
app.add_url_rule('/dashboard',   view_func=main.dashboard)
app.add_url_rule('/internships', view_func=main.internships)

# ---------- register + login + logout ----------
app.add_url_rule('/register',            view_func=auth.register)
app.add_url_rule('/register/student',    view_func=auth.register_student,    methods=['GET', 'POST'])
app.add_url_rule('/register/company',    view_func=auth.register_company,    methods=['GET', 'POST'])
app.add_url_rule('/register/supervisor', view_func=auth.register_supervisor, methods=['GET', 'POST'])
app.add_url_rule('/login',  view_func=auth.login, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=auth.logout)

# ---------- student pages ----------
app.add_url_rule('/apply/<int:internship_id>',    view_func=student.apply,    methods=['POST'])
app.add_url_rule('/my_applications',              view_func=student.my_applications)
app.add_url_rule('/withdraw/<int:id>',            view_func=student.withdraw, methods=['POST'])
app.add_url_rule('/my_logs/<int:application_id>', view_func=student.my_logs,  methods=['GET', 'POST'])

# ---------- company pages ----------
app.add_url_rule('/internships/add',             view_func=company.add_internship,    methods=['GET', 'POST'])
app.add_url_rule('/internships/edit/<int:id>',   view_func=company.edit_internship,   methods=['GET', 'POST'])
app.add_url_rule('/internships/delete/<int:id>', view_func=company.delete_internship, methods=['POST'])
app.add_url_rule('/applicants/<int:internship_id>', view_func=company.applicants)
app.add_url_rule('/applications/<int:id>/status',   view_func=company.update_status, methods=['POST'])

# ---------- supervisor pages ----------
app.add_url_rule('/students',                   view_func=supervisor.students)
app.add_url_rule('/logs/<int:application_id>',  view_func=supervisor.view_logs)
app.add_url_rule('/logs/<int:log_id>/feedback', view_func=supervisor.give_feedback, methods=['POST'])

# ---------- admin pages ----------
app.add_url_rule('/users',                 view_func=admin.users)
app.add_url_rule('/users/delete/<int:id>', view_func=admin.delete_user, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
