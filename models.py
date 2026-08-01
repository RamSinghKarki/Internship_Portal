# ============================================================
# Database models (SQLAlchemy ORM)
#
# Each class below is one table of the database. SQLAlchemy
# maps the class to the table, so rows become Python objects:
#   CREATE -> db.session.add(object) + commit
#   READ   -> Model.query.filter_by(...) / .all() / .first()
#   UPDATE -> change object attributes + commit
#   DELETE -> db.session.delete(object) + commit
# ============================================================

from flask import session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True, nullable=False)

    users = db.relationship('User', backref='role')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)   # stored as a hash
    # the admin checks every new account before it can be used
    verification_status = db.Column(db.String(20), default='pending')
    verification_remarks = db.Column(db.String(255))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # one user has at most one of these profiles (depends on the role);
    # deleting the user also deletes the profile (cascade)
    student = db.relationship('Student', backref='user', uselist=False,
                              cascade='all, delete-orphan', passive_deletes=True)
    company = db.relationship('Company', backref='user', uselist=False,
                              cascade='all, delete-orphan', passive_deletes=True)
    supervisor = db.relationship('Supervisor', backref='user', uselist=False,
                                 cascade='all, delete-orphan', passive_deletes=True)

    @property
    def is_verified(self):
        return self.verification_status == 'verified'

    def set_password(self, pw):
        self.password = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password, pw)


class College(db.Model):
    __tablename__ = 'colleges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    affiliation = db.Column(db.String(100))
    address = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.now)

    students = db.relationship('Student', backref='college')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        unique=True, nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id', ondelete='SET NULL'))
    roll_number = db.Column(db.String(50))
    department = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    skills = db.Column(db.String(255))
    # one PDF holding the citizenship / NID, resume and other documents
    document_url = db.Column(db.String(255))

    applications = db.relationship('Application', backref='student',
                                   cascade='all, delete-orphan', passive_deletes=True)


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        unique=True, nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)

    internships = db.relationship('Internship', backref='company',
                                  cascade='all, delete-orphan', passive_deletes=True)
    supervisors = db.relationship('Supervisor', backref='company',
                                  cascade='all, delete-orphan', passive_deletes=True)


class Supervisor(db.Model):
    __tablename__ = 'supervisors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'),
                           nullable=False)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))


class Internship(db.Model):
    __tablename__ = 'internships'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'),
                           nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.String(255))
    duration_weeks = db.Column(db.Integer)
    stipend = db.Column(db.String(50))
    vacancies = db.Column(db.Integer)
    status = db.Column(db.String(20), default='open')     # open / closed
    posted_date = db.Column(db.DateTime, default=datetime.now)

    applications = db.relationship('Application', backref='internship',
                                   cascade='all, delete-orphan', passive_deletes=True)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'),
                           nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id', ondelete='CASCADE'),
                              nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='applied')  # applied / selected / rejected
    applied_date = db.Column(db.DateTime, default=datetime.now)

    logs = db.relationship('ProgressLog', backref='application',
                           cascade='all, delete-orphan', passive_deletes=True)


class ProgressLog(db.Model):
    __tablename__ = 'progress_logs'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer,
                               db.ForeignKey('applications.id', ondelete='CASCADE'),
                               nullable=False)
    supervisor_id = db.Column(db.Integer,
                              db.ForeignKey('supervisors.id', ondelete='SET NULL'))
    week_number = db.Column(db.Integer)
    description = db.Column(db.Text)      # work done by the student
    feedback = db.Column(db.Text)         # written by the supervisor
    marks = db.Column(db.Integer)
    submitted_date = db.Column(db.DateTime, default=datetime.now)

    supervisor = db.relationship('Supervisor')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User')


# ---------- account verification ----------
def verified_only(action='use this feature'):
    """Return an error message if the logged-in user is not verified yet,
    otherwise None. Used by the routes that change data."""
    from flask import session
    user = db.session.get(User, session.get('user_id'))
    if user is None:
        return 'Please login again.'
    if user.verification_status == 'verified':
        return None
    if user.verification_status == 'rejected':
        return (f'Your account was not approved, so you cannot {action}. '
                f'Reason: {user.verification_remarks or "no reason given"}.')
    return f'Your account is waiting for admin approval, so you cannot {action} yet.'


# ---------- notifications and audit trail ----------
def notify(user_id, message, link=None):
    """Queue an in-app notification (saved on the next commit)."""
    db.session.add(Notification(user_id=user_id, message=message, link=link))


def audit(user_id, action, details=''):
    """Record who did what (saved on the next commit)."""
    db.session.add(AuditLog(user_id=user_id, action=action, details=details))


# ---------- helpers: profile row of the logged-in user ----------
def current_student():
    return Student.query.filter_by(user_id=session['user_id']).first()


def current_company():
    return Company.query.filter_by(user_id=session['user_id']).first()


def current_supervisor():
    return Supervisor.query.filter_by(user_id=session['user_id']).first()
