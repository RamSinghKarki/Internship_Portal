# ============================================================
# TEST CASES 15, 21, 22, 23 : Administration, audit log and exports
# ============================================================

from conftest import setup_all_roles, register_student, login, logout


def test_tc15_deleting_a_user_removes_related_data(client):
    """TC-15: Deleting a company removes its internships and applications (cascade)."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)

    from models import User, Company, Internship, Application, Supervisor
    assert Internship.query.count() == 1
    assert Application.query.count() == 1

    company_user = User.query.filter_by(email='company@test.com').first()
    login(client, 'admin@portal.com', 'admin123')
    response = client.post(f'/users/delete/{company_user.id}', follow_redirects=True)
    assert b'User deleted' in response.data

    # the company and everything that depended on it is gone
    assert User.query.filter_by(email='company@test.com').first() is None
    assert Company.query.count() == 0
    assert Internship.query.count() == 0
    assert Application.query.count() == 0
    assert Supervisor.query.count() == 0


def test_tc15b_admin_cannot_delete_own_account(client):
    """TC-15 (safety): the administrator cannot delete their own account."""
    setup_all_roles(client)
    login(client, 'admin@portal.com', 'admin123')

    from models import User
    admin = User.query.filter_by(email='admin@portal.com').first()
    response = client.post(f'/users/delete/{admin.id}', follow_redirects=True)
    assert b'cannot delete your own account' in response.data
    assert User.query.filter_by(email='admin@portal.com').first() is not None


def test_tc21_important_actions_are_written_to_the_audit_log(client):
    """TC-21: Logins, failed logins and changes are recorded in the audit log."""
    setup_all_roles(client)

    # a failed login attempt
    login(client, 'student@test.com', 'WRONG-PASSWORD')

    from models import AuditLog
    actions = {log.action for log in AuditLog.query.all()}
    for expected in ('register', 'login', 'login_failed', 'post_internship'):
        assert expected in actions, f'{expected} missing from the audit log'

    # the failed login stored the email that was tried
    failed = AuditLog.query.filter_by(action='login_failed').first()
    assert failed.details == 'student@test.com'
    assert failed.user_id is None            # nobody was logged in

    # the admin can read the audit page
    login(client, 'admin@portal.com', 'admin123')
    response = client.get('/audit')
    assert response.status_code == 200
    assert b'login_failed' in response.data


def test_tc22_user_list_can_be_searched_and_paged(client):
    """TC-22: The user list supports search and pagination (ten per page)."""
    setup_all_roles(client)
    # add enough students to need a second page
    for i in range(12):
        register_student(client, email=f'bulk{i}@test.com', name=f'Bulk Student {i}')

    login(client, 'admin@portal.com', 'admin123')

    # search by name
    response = client.get('/users?q=Bulk Student 3')
    assert b'Bulk Student 3' in response.data
    assert b'Test Company' not in response.data

    # search by email
    response = client.get('/users?q=company@test.com')
    assert b'Test Company' in response.data

    # pagination: page 1 shows ten rows, page 2 shows the rest
    page1 = client.get('/users?page=1').data
    page2 = client.get('/users?page=2').data
    assert page1.count(b'<tr>') - 1 == 10        # minus the header row
    assert page1 != page2


def test_tc23_csv_exports_contain_the_right_data(client):
    """TC-23: The admin can export users and a company can export applicants."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)

    # ---- users export (admin) ----
    login(client, 'admin@portal.com', 'admin123')
    response = client.get('/users/export')
    assert response.status_code == 200
    assert 'attachment' in response.headers['Content-Disposition']
    csv_text = response.data.decode()
    assert csv_text.startswith('ID,Name,Email,Role,Joined')
    assert 'student@test.com' in csv_text
    logout(client)

    # ---- applicants export (company) ----
    login(client, 'company@test.com')
    response = client.get('/applicants/1/export')
    assert response.status_code == 200
    csv_text = response.data.decode()
    assert 'Student,Email,Roll No' in csv_text
    assert 'Test Student' in csv_text
    assert 'CS-101' in csv_text
