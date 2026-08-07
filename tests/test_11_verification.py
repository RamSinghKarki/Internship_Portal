# ============================================================
# TEST CASE 26 : Admin verification of new accounts
# ============================================================

from conftest import (register_student, register_company, register_supervisor,
                      login, logout, post_internship, approve_all)


def test_tc26_new_accounts_start_as_pending(client):
    """TC-26: Every new account waits for admin approval; the admin is approved."""
    register_student(client)
    register_company(client)

    from models import User
    student = User.query.filter_by(email='student@test.com').first()
    company = User.query.filter_by(email='company@test.com').first()
    admin = User.query.filter_by(email='admin@portal.com').first()

    assert student.verification_status == 'pending'
    assert company.verification_status == 'pending'
    assert admin.verification_status == 'verified'      # seeded as approved


def test_tc26b_unverified_users_cannot_act(client):
    """TC-26: A pending company cannot post, and a pending student cannot apply."""
    register_company(client)
    register_student(client)

    # the company is still pending, so posting is refused
    login(client, 'company@test.com')
    response = client.get('/internships/add', follow_redirects=True)
    assert b'waiting for admin approval' in response.data

    from models import Internship
    post_internship(client)
    assert Internship.query.count() == 0                # nothing was created
    logout(client)

    # approve only the company, then it can post
    approve_all()
    login(client, 'company@test.com')
    post_internship(client)
    assert Internship.query.count() == 1


def test_tc26c_admin_can_approve_an_account(client):
    """TC-26: The admin approves an account and the status changes."""
    register_student(client)
    from models import User
    student = User.query.filter_by(email='student@test.com').first()

    login(client, 'admin@portal.com', 'admin123')
    response = client.get('/verifications')
    assert b'Test Student' in response.data              # appears in the queue

    response = client.post(f'/verify/{student.id}', follow_redirects=True)
    assert b'has been approved' in response.data

    student = User.query.filter_by(email='student@test.com').first()
    assert student.verification_status == 'verified'
    assert student.verified_at is not None


def test_tc26d_admin_can_reject_with_a_reason(client):
    """TC-26: A rejected account is told why, and still cannot act."""
    register_student(client)
    from models import User
    student = User.query.filter_by(email='student@test.com').first()

    login(client, 'admin@portal.com', 'admin123')
    client.post(f'/reject/{student.id}',
                data={'remarks': 'The document was not readable'},
                follow_redirects=True)
    logout(client)

    student = User.query.filter_by(email='student@test.com').first()
    assert student.verification_status == 'rejected'
    assert student.verification_remarks == 'The document was not readable'

    # the reason is shown to the student
    login(client, 'student@test.com')
    response = client.get('/dashboard')
    assert b'was not approved' in response.data
    assert b'The document was not readable' in response.data


def test_tc26e_only_the_admin_can_verify(client):
    """TC-26: Other roles cannot reach the verification pages."""
    register_student(client)
    register_company(client)
    approve_all()

    from models import User
    student = User.query.filter_by(email='student@test.com').first()

    login(client, 'company@test.com')
    assert client.get('/verifications').status_code == 302
    client.post(f'/verify/{student.id}')
    logout(client)

    # the company could not change anything
    assert User.query.filter_by(email='student@test.com').first().verification_status == 'verified'
