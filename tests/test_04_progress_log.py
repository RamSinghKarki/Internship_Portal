# ============================================================
# TEST CASES 12, 13 : Weekly progress logs and supervisor feedback
# ============================================================

from conftest import setup_all_roles, login, logout


def _select_a_student(client):
    """Helper: student applies and the company selects them."""
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)
    login(client, 'company@test.com')
    client.post('/applications/1/status', data={'status': 'selected'},
                follow_redirects=True)
    logout(client)


def test_tc12_selected_student_can_submit_weekly_log(client):
    """TC-12: A selected student can submit a weekly log; others cannot."""
    setup_all_roles(client)

    # before selection the log book is not available
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    response = client.get('/my_logs/1', follow_redirects=True)
    assert b'only available for selected applications' in response.data
    logout(client)

    _select_a_student(client)

    login(client, 'student@test.com')
    response = client.post('/my_logs/1', data={
        'week_number': '1',
        'description': 'Learned Flask basics.\nBuilt the login page.'},
        follow_redirects=True)
    assert b'Weekly log submitted' in response.data

    from models import db, ProgressLog
    log = ProgressLog.query.first()
    assert log.week_number == 1
    assert 'Built the login page.' in log.description
    assert log.feedback is None                 # no feedback yet


def test_tc13_supervisor_can_give_feedback_and_marks(client):
    """TC-13: A supervisor records feedback and marks; the student can see them."""
    setup_all_roles(client)
    _select_a_student(client)

    login(client, 'student@test.com')
    client.post('/my_logs/1', data={'week_number': '1',
                                    'description': 'Worked on the database'},
                follow_redirects=True)
    logout(client)

    # the supervisor sees the student and their log
    login(client, 'supervisor@test.com')
    response = client.get('/students')
    assert b'Test Student' in response.data

    response = client.post('/logs/1/feedback', data={
        'feedback': 'Good progress, keep it up', 'marks': '9'},
        follow_redirects=True)
    assert b'Feedback saved' in response.data
    logout(client)

    from models import db, ProgressLog
    log = db.session.get(ProgressLog, 1)
    assert log.feedback == 'Good progress, keep it up'
    assert log.marks == 9
    assert log.supervisor_id == 1               # recorded who evaluated

    # the student can read the feedback
    login(client, 'student@test.com')
    response = client.get('/my_logs/1')
    assert b'Good progress, keep it up' in response.data
    assert b'9' in response.data
