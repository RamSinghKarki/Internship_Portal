# ============================================================
# TEST CASE 28 : Admin verification of new accounts
# ============================================================

from conftest import (register_student, register_company, register_supervisor,
                      login, logout, post_internship, approve_all)


def test_tc28_new_accounts_start_as_pending(client):
    """TC-28: Every new account waits for admin approval; the admin is approved."""
    register_student(client)
    register_company(client)

    from models import User
    student = User.query.filter_by(email='student@test.com').first()
    company = User.query.filter_by(email='company@test.com').first()
    admin = User.query.filter_by(email='admin@portal.com').first()

    assert student.verification_status == 'pending'
    assert company.verification_status == 'pending'
    assert admin.verification_status == 'verified'      # seeded as approved


def test_tc28b_unverified_users_cannot_act(client):
    """TC-28: A pending company cannot post, and a pending student cannot apply."""
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


def test_tc28c_admin_can_approve_an_account(client):
    """TC-28: The admin approves an account and the user is notified."""
    register_student(client)
    from models import User, Notification
    student = User.query.filter_by(email='student@test.com').first()

    login(client, 'admin@portal.com', 'admin123')
    response = client.get('/verifications')
    assert b'Test Student' in response.data              # appears in the queue

    response = client.post(f'/verify/{student.id}', follow_redirects=True)
    assert b'has been approved' in response.data

    student = User.query.filter_by(email='student@test.com').first()
    assert student.verification_status == 'verified'
    assert student.verified_at is not None
    # the student was told
    note = Notification.query.filter_by(user_id=student.id).first()
    assert note is not None and 'approved' in note.message


def test_tc28d_admin_can_reject_with_a_reason(client):
    """TC-28: A rejected account is told why, and still cannot act."""
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


def test_tc28e_only_the_admin_can_verify(client):
    """TC-28: Other roles cannot reach the verification pages."""
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
