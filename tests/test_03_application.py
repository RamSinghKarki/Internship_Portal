# ============================================================
# TEST CASES 8, 9, 10, 11 : Applying and selection
# ============================================================

from conftest import setup_all_roles, login, logout


def test_tc08_student_can_apply_with_cover_letter(client):
    """TC-08: A student can apply and the application is stored as 'applied'."""
    setup_all_roles(client)
    login(client, 'student@test.com')

    response = client.post('/apply/1', data={
        'cover_letter': 'Dear Sir,\nI am interested.\nThank you.'},
        follow_redirects=True)
    assert b'Application submitted' in response.data

    from models import db, Application
    application = Application.query.first()
    assert application.status == 'applied'
    assert 'I am interested.' in application.cover_letter
    assert '\n' in application.cover_letter      # line breaks are preserved


def test_tc09_student_cannot_apply_twice(client):
    """TC-09: The same student cannot apply twice to the same internship."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'First'}, follow_redirects=True)

    response = client.post('/apply/1', data={'cover_letter': 'Second'},
                           follow_redirects=True)
    assert b'already applied' in response.data

    from models import db, Application
    assert Application.query.count() == 1


def test_tc10_student_can_withdraw_application(client):
    """TC-10: A pending application can be withdrawn."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Please consider me'},
                follow_redirects=True)

    from models import db, Application
    assert Application.query.count() == 1

    response = client.post('/withdraw/1', follow_redirects=True)
    assert b'Application withdrawn' in response.data
    assert Application.query.count() == 0


def test_tc11_company_can_select_and_reject_applicant(client):
    """TC-11: The company can change an application status to selected or rejected."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'I am a good fit'},
                follow_redirects=True)
    logout(client)

    login(client, 'company@test.com')
    response = client.get('/applicants/1')
    assert b'Test Student' in response.data        # applicant is visible
    assert b'I am a good fit' in response.data     # cover letter is visible

    response = client.post('/applications/1/status', data={'status': 'selected'},
                           follow_redirects=True)
    assert b'Status updated' in response.data

    from models import db, Application
    assert db.session.get(Application, 1).status == 'selected'

    client.post('/applications/1/status', data={'status': 'rejected'},
                follow_redirects=True)
    assert db.session.get(Application, 1).status == 'rejected'
