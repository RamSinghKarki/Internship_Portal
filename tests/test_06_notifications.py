# ============================================================
# TEST CASES 18, 19, 20 : In-application notifications
# ============================================================

from conftest import setup_all_roles, login, logout


def test_tc18_company_is_notified_of_a_new_application(client):
    """TC-18: Applying raises an unread notification for the company."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)

    login(client, 'company@test.com')
    response = client.get('/dashboard')
    assert b'bg-danger' in response.data              # unread badge is shown

    response = client.get('/notifications')
    assert b'New application' in response.data
    assert b'Test Student' in response.data

    # opening the page marks the notifications as read
    from models import Notification
    assert Notification.query.filter_by(is_read=False).count() == 0


def test_tc19_student_is_notified_of_the_decision(client):
    """TC-19: The student is notified when the company decides."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)

    login(client, 'company@test.com')
    client.post('/applications/1/status', data={'status': 'selected'},
                follow_redirects=True)
    logout(client)

    login(client, 'student@test.com')
    response = client.get('/notifications')
    assert b'selected' in response.data


def test_tc20_notifications_for_logs_and_feedback(client):
    """TC-20: A submitted log notifies the supervisor; feedback notifies the student."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)
    login(client, 'company@test.com')
    client.post('/applications/1/status', data={'status': 'selected'},
                follow_redirects=True)
    logout(client)

    # student submits a log -> supervisor is notified
    login(client, 'student@test.com')
    client.post('/my_logs/1', data={'week_number': '1', 'description': 'Week one work'},
                follow_redirects=True)
    logout(client)

    login(client, 'supervisor@test.com')
    response = client.get('/notifications')
    assert b'submitted a weekly log' in response.data

    # supervisor gives feedback -> student is notified
    client.post('/logs/1/feedback', data={'feedback': 'Well done', 'marks': '8'},
                follow_redirects=True)
    logout(client)

    login(client, 'student@test.com')
    response = client.get('/notifications')
    assert b'New feedback' in response.data
