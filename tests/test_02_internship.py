# ============================================================
# TEST CASES 6, 7, 17 : Internship management and search
# ============================================================

from conftest import register_company, login, post_internship, approve_all


def test_tc06_company_can_post_internship(client):
    """TC-06: A company can post an internship and it appears in the list."""
    register_company(client)
    approve_all()                      # the admin approves the account
    login(client, 'company@test.com')

    response = post_internship(client, title='Python Backend Intern')
    assert b'Internship posted' in response.data
    assert b'Python Backend Intern' in response.data

    from models import db, Internship
    internship = Internship.query.first()
    assert internship.title == 'Python Backend Intern'
    assert internship.status == 'open'          # open by default
    assert internship.vacancies == 2


def test_tc07_company_can_edit_and_close_internship(client):
    """TC-07: Editing saves the changes; a closed internship is hidden from students."""
    register_company(client)
    approve_all()                      # the admin approves the account
    login(client, 'company@test.com')
    post_internship(client)

    response = client.post('/internships/edit/1', data={
        'title': 'Updated Title', 'description': 'Updated description',
        'required_skills': 'Python, MySQL', 'duration_weeks': '12',
        'stipend': 'Rs. 15000', 'vacancies': '3', 'status': 'closed'},
        follow_redirects=True)
    assert b'Internship updated' in response.data

    from models import db, Internship
    internship = db.session.get(Internship, 1)
    assert internship.title == 'Updated Title'
    assert internship.duration_weeks == 12
    assert internship.status == 'closed'

    # a student must not see a closed internship
    from conftest import register_student, logout
    logout(client)
    register_student(client)
    approve_all()
    login(client, 'student@test.com')
    response = client.get('/internships')
    assert b'Updated Title' not in response.data


def test_tc17_search_internships_by_keyword_and_skill(client):
    """TC-17: Search returns only the internships that match."""
    register_company(client)
    approve_all()                      # the admin approves the account
    login(client, 'company@test.com')
    post_internship(client, title='Python Backend Intern', skills='Python, Flask')
    post_internship(client, title='Graphic Designer Intern', skills='Photoshop')
    post_internship(client, title='Data Entry Intern', skills='Excel, Python')

    from conftest import register_student, logout
    logout(client)
    register_student(client)
    approve_all()
    login(client, 'student@test.com')

    # keyword search matches the two internships mentioning Python
    response = client.get('/internships?q=python')
    assert b'Python Backend Intern' in response.data
    assert b'Data Entry Intern' in response.data
    assert b'Graphic Designer Intern' not in response.data

    # skill filter matches only the design internship
    response = client.get('/internships?skill=Photoshop')
    assert b'Graphic Designer Intern' in response.data
    assert b'Python Backend Intern' not in response.data

    # without a search every open internship is listed
    response = client.get('/internships')
    for title in (b'Python Backend Intern', b'Graphic Designer Intern',
                  b'Data Entry Intern'):
        assert title in response.data
