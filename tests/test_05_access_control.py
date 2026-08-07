# ============================================================
# TEST CASE 14 : Role based access control (security)
# ============================================================

from conftest import setup_all_roles, login, logout


def test_tc14_pages_are_protected_by_role(client):
    """TC-14: Each role can only reach its own pages."""
    setup_all_roles(client)

    # ---- not logged in: every private page redirects to login ----
    for url in ('/dashboard', '/internships', '/my_applications',
                '/users', '/students'):
        response = client.get(url)
        assert response.status_code == 302, f'{url} should redirect'

    # ---- student cannot reach company, supervisor or admin pages ----
    login(client, 'student@test.com')
    for url in ('/users', '/students', '/internships/add', '/applicants/1'):
        response = client.get(url)
        assert response.status_code == 302, f'student should not open {url}'
    logout(client)

    # ---- company cannot reach admin or supervisor pages ----
    login(client, 'company@test.com')
    for url in ('/users', '/students', '/my_applications'):
        response = client.get(url)
        assert response.status_code == 302, f'company should not open {url}'
    logout(client)

    # ---- supervisor cannot reach admin pages ----
    login(client, 'supervisor@test.com')
    for url in ('/users', '/internships/add'):
        response = client.get(url)
        assert response.status_code == 302, f'supervisor should not open {url}'
    logout(client)

    # ---- admin can reach the admin pages ----
    login(client, 'admin@portal.com', 'admin123')
    for url in ('/users', '/dashboard'):
        assert client.get(url).status_code == 200


def test_tc14b_company_cannot_touch_another_companys_internship(client):
    """TC-14 (ownership): a company can only manage its own internships."""
    setup_all_roles(client)

    # a second company registers and logs in
    from conftest import register_company
    register_company(client, email='other@test.com', name='Other Company')
    login(client, 'other@test.com')

    # internship #1 belongs to the first company
    response = client.get('/applicants/1', follow_redirects=True)
    assert b'Internship not found' in response.data

    response = client.post('/internships/delete/1', follow_redirects=True)
    from models import db, Internship
    assert db.session.get(Internship, 1) is not None      # it was NOT deleted
