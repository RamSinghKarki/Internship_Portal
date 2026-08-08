# ============================================================
# TEST CASES 18 - 20 : In-app notifications
#
# Every notification is created in the same transaction as the action
# that caused it, so a stored action always has its message with it.
# ============================================================

from conftest import (setup_all_roles, register_student, register_company,
                      login, logout, approve_all, post_internship)


def _apply(client, cover='I am interested in this internship.'):
    """Log in as the student and apply to internship 1."""
    login(client, 'student@test.com')
    response = client.post('/apply/1', data={'cover_letter': cover},
                           follow_redirects=True)
    logout(client)
    return response


def test_tc18_applying_notifies_the_company(client):
    """TC-18: Applying raises an unread notification for the company."""
    setup_all_roles(client)
    _apply(client)

    from models import Notification, User
    company = User.query.filter_by(email='company@test.com').first()
    note = Notification.query.filter_by(user_id=company.id).first()

    assert note is not None
    assert 'New application' in note.message
    assert note.is_read is False              # unread, so the bell shows a badge
    assert note.link is not None              # clicking it opens the applicants page

    # the company sees the message on its notifications page
    login(client, 'company@test.com')
    response = client.get('/notifications')
    assert b'New application' in response.data


def test_tc19_the_decision_notifies_the_student(client):
    """TC-19: The student is notified when the company decides."""
    setup_all_roles(client)
    _apply(client)

    from models import Application, Notification, User
    application = Application.query.first()

    login(client, 'company@test.com')
    client.post(f'/applications/{application.id}/status',
                data={'status': 'selected'}, follow_redirects=True)
    logout(client)

    student = User.query.filter_by(email='student@test.com').first()
    messages = [n.message for n in Notification.query.filter_by(user_id=student.id).all()]
    assert any('selected' in m for m in messages)


def test_tc20_logs_and_feedback_notify_both_sides(client):
    """TC-20: A submitted log notifies the supervisor; feedback notifies the student."""
    setup_all_roles(client)
    _apply(client)

    from models import Application, Notification, ProgressLog, User
    application = Application.query.first()

    # the company selects the student, which unlocks the log book
    login(client, 'company@test.com')
    client.post(f'/applications/{application.id}/status',
                data={'status': 'selected'}, follow_redirects=True)
    logout(client)

    # the student submits a weekly log
    login(client, 'student@test.com')
    client.post(f'/my_logs/{application.id}',
                data={'week_number': '1', 'description': 'Set up the project.'},
                follow_redirects=True)
    logout(client)

    supervisor = User.query.filter_by(email='supervisor@test.com').first()
    messages = [n.message for n in Notification.query.filter_by(user_id=supervisor.id).all()]
    assert any('weekly log' in m for m in messages)

    # the supervisor replies with feedback and marks
    log = ProgressLog.query.first()
    login(client, 'supervisor@test.com')
    client.post(f'/logs/{log.id}/feedback',
                data={'feedback': 'Good start.', 'marks': '8'},
                follow_redirects=True)
    logout(client)

    student = User.query.filter_by(email='student@test.com').first()
    messages = [n.message for n in Notification.query.filter_by(user_id=student.id).all()]
    assert any('feedback' in m for m in messages)


def test_opening_the_page_clears_the_unread_badge(client):
    """Reading the notification list marks every message as read."""
    setup_all_roles(client)
    _apply(client)

    from models import Notification, User
    company = User.query.filter_by(email='company@test.com').first()
    assert Notification.query.filter_by(user_id=company.id, is_read=False).count() == 1

    login(client, 'company@test.com')
    client.get('/notifications')

    assert Notification.query.filter_by(user_id=company.id, is_read=False).count() == 0
