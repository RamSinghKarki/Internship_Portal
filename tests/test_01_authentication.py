# ============================================================
# TEST CASES 1 - 5, 16 : Registration and Login
# ============================================================

from conftest import (register_student, register_company, register_supervisor,
                      login, a_document)


def test_tc01_student_registration(client):
    """TC-01: A student can register with all details and a document."""
    response = register_student(client)
    assert b'Registration successful' in response.data

    from models import User, Student
    user = User.query.filter_by(email='student@test.com').first()
    assert user is not None                    # row created in users
    assert user.role.role_name == 'student'
    student = Student.query.filter_by(user_id=user.id).first()
    assert student is not None                 # row created in students
    assert student.roll_number == 'CS-101'
    assert student.document_url is not None    # document was saved


def test_tc02_company_registration(client):
    """TC-02: A company can register with its organisation details."""
    response = register_company(client)
    assert b'Registration successful' in response.data

    from models import User, Company
    user = User.query.filter_by(email='company@test.com').first()
    assert user is not None and user.role.role_name == 'company'
    assert Company.query.filter_by(user_id=user.id).first() is not None


def test_tc03_supervisor_registration(client):
    """TC-03: A supervisor can register under an existing company."""
    register_company(client)
    response = register_supervisor(client)
    assert b'Registration successful' in response.data

    from models import User, Supervisor
    user = User.query.filter_by(email='supervisor@test.com').first()
    assert user is not None and user.role.role_name == 'supervisor'
    supervisor = Supervisor.query.filter_by(user_id=user.id).first()
    assert supervisor is not None
    assert supervisor.company_id == 1          # linked to the company


def test_tc04_duplicate_email_is_rejected(client):
    """TC-04: The same email address cannot be registered twice."""
    register_student(client, email='same@test.com')
    response = register_student(client, email='same@test.com')
    assert b'Email is already registered' in response.data

    from models import User
    assert User.query.filter_by(email='same@test.com').count() == 1


def test_tc05_login_with_wrong_password_fails(client):
    """TC-05: Login fails when the password is wrong, succeeds when correct."""
    register_student(client)

    response = login(client, 'student@test.com', 'WRONG-PASSWORD')
    assert b'Invalid email or password' in response.data

    response = login(client, 'student@test.com', 'pass123')
    assert b'Invalid email or password' not in response.data
    assert b'Welcome' in response.data          # reached the dashboard


def test_tc16_registration_without_document_is_rejected(client):
    """TC-16: A student cannot register without uploading a document."""
    response = register_student(client, email='nodoc@test.com', document=False)
    assert b'Please upload a valid document' in response.data

    from models import User
    assert User.query.filter_by(email='nodoc@test.com').first() is None


def test_tc27_document_must_be_a_pdf(client):
    """TC-27: The NID, resume and other papers must come as one PDF file,
    so a file of any other type is refused."""
    response = register_student(client, email='notpdf@test.com',
                                document_name='citizenship.jpg')
    assert b'Please upload a valid document' in response.data

    from models import User
    assert User.query.filter_by(email='notpdf@test.com').first() is None
