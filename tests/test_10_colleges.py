# ============================================================
# TEST CASES 24, 25 : College management
# ============================================================

from conftest import register_student, login, logout


def test_tc24_student_is_linked_to_a_college(client):
    """TC-24: A student chooses a college at registration and it is stored."""
    response = register_student(client)
    assert b'Registration successful' in response.data

    from models import db, Student, College
    student = Student.query.first()
    assert student.college_id == 1
    assert student.college.name == db.session.get(College, 1).name

    # the college appears on the public landing page
    response = client.get('/')
    assert b'Colleges Working With Us' in response.data
    assert student.college.name.encode() in response.data


def test_tc25_admin_can_add_and_remove_colleges(client):
    """TC-25: The administrator manages the list of colleges."""
    login(client, 'admin@portal.com', 'admin123')

    from models import College
    before = College.query.count()

    response = client.post('/colleges', data={
        'name': 'Test Engineering College', 'affiliation': 'Pokhara University',
        'address': 'Butwal'}, follow_redirects=True)
    assert b'College added' in response.data
    assert College.query.count() == before + 1

    # the same college cannot be added twice
    response = client.post('/colleges', data={
        'name': 'Test Engineering College', 'affiliation': 'X', 'address': 'Y'},
        follow_redirects=True)
    assert b'already registered' in response.data
    assert College.query.count() == before + 1

    new_college = College.query.filter_by(name='Test Engineering College').first()
    response = client.post(f'/colleges/delete/{new_college.id}', follow_redirects=True)
    assert b'College removed' in response.data
    assert College.query.count() == before


def test_tc25b_removing_a_college_keeps_its_students(client):
    """TC-25 (safety): removing a college must not delete student accounts."""
    register_student(client)
    from models import Student, College

    login(client, 'admin@portal.com', 'admin123')
    client.post('/colleges/delete/1', follow_redirects=True)

    student = Student.query.first()
    assert student is not None            # the student still exists
    assert student.college_id is None     # the link is simply cleared
