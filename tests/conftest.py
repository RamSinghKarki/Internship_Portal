# ============================================================
# Shared setup for all test cases (pytest fixtures)
#
# The tests run against a SEPARATE database (internship_db_test)
# so running them never touches the real internship_db data.
#
# The test database is built from the same database.sql file used
# by the real system, so the schema is always identical.
# ============================================================

import io
import os
import re
import sys

import pymysql
import pytest

# ---- database settings for the tests (change the password if yours differs) ----
DB_HOST = os.environ.get('TEST_DB_HOST', 'localhost')
DB_USER = os.environ.get('TEST_DB_USER', 'root')
DB_PASS = os.environ.get('TEST_DB_PASS', 'password')
DB_NAME = os.environ.get('TEST_DB_NAME', 'internship_db_test')

# point the application at the test database BEFORE it is imported
os.environ['DATABASE_URL'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import app as flask_app          # noqa: E402
from models import db                     # noqa: E402


def _build_test_database():
    """Create the test database from database.sql (same schema as the real one)."""
    with open(os.path.join(ROOT, 'database.sql'), encoding='utf-8') as f:
        script = f.read()
    # run everything against the test database instead of the real one
    script = script.replace('internship_db', DB_NAME)

    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    try:
        with conn.cursor() as cur:
            for statement in [s.strip() for s in script.split(';')]:
                # skip comments and empty fragments
                body = re.sub(r'--.*', '', statement).strip()
                if body:
                    cur.execute(body)
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def client():
    """A fresh application and empty database for every test case."""
    _build_test_database()
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.session.remove()
        db.engine.dispose()
        with flask_app.test_client() as c:
            yield c


# ------------------------------------------------------------
# helpers used by the test cases
# ------------------------------------------------------------
def a_document(name='nid_resume.pdf'):
    """A small file to use for the student document upload.
    In the portal this is one PDF holding the NID, resume and other papers."""
    return (io.BytesIO(b'test document content'), name)


def register_student(client, email='student@test.com', name='Test Student',
                     skills='Python, MySQL', document=True,
                     document_name='nid_resume.pdf'):
    data = {'name': name, 'email': email, 'password': 'pass123',
            'roll_number': 'CS-101',
            'department': 'Computer Engineering',
            'semester': '6', 'skills': skills}
    if document:
        data['document'] = a_document(document_name)
    return client.post('/register/student', data=data,
                       content_type='multipart/form-data', follow_redirects=True)


def register_company(client, email='company@test.com', name='Test Company'):
    return client.post('/register/company', data={
        'name': name, 'email': email, 'password': 'pass123',
        'industry': 'Software', 'location': 'Kathmandu',
        'description': 'A test company'}, follow_redirects=True)


def register_supervisor(client, email='supervisor@test.com', name='Test Supervisor',
                        company_id=1):
    return client.post('/register/supervisor', data={
        'name': name, 'email': email, 'password': 'pass123',
        'company_id': str(company_id), 'designation': 'Senior Developer',
        'department': 'IT'}, follow_redirects=True)


def approve_all(client=None):
    """Approve every account, as the admin would, so the workflow can run."""
    from models import db, User
    from datetime import datetime
    for user in User.query.all():
        user.verification_status = 'verified'
        user.verified_at = datetime.now()
    db.session.commit()


def login(client, email, password='pass123'):
    return client.post('/login', data={'email': email, 'password': password},
                       follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def post_internship(client, title='Python Intern', skills='Python, Flask'):
    return client.post('/internships/add', data={
        'title': title, 'description': 'Work on web applications',
        'required_skills': skills, 'duration_weeks': '8',
        'stipend': 'Rs. 10000', 'vacancies': '2'}, follow_redirects=True)


def setup_all_roles(client):
    """Register a company, a supervisor and a student, and post one internship.

    This is the starting point used by most of the workflow test cases.
    """
    register_company(client)
    register_supervisor(client)
    register_student(client)
    approve_all()               # the admin approves the new accounts
    login(client, 'company@test.com')
    post_internship(client)
    logout(client)
