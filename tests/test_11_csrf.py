# ============================================================
# TEST CASE 27 : Cross Site Request Forgery (CSRF) protection
# ============================================================

import pytest
from conftest import flask_app, _build_test_database, register_company


@pytest.fixture()
def csrf_client():
    """A client with CSRF protection switched ON (it is off for other tests)."""
    _build_test_database()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = True
    with flask_app.app_context():
        with flask_app.test_client() as c:
            yield c
    flask_app.config['WTF_CSRF_ENABLED'] = False


def test_tc27_post_without_a_token_is_rejected(csrf_client):
    """TC-27: A POST without a valid CSRF token is refused."""
    response = csrf_client.post('/login', data={
        'email': 'admin@portal.com', 'password': 'admin123'})
    assert response.status_code == 400          # rejected by CSRF protection

    # nobody was logged in
    with csrf_client.session_transaction() as session:
        assert 'user_id' not in session


def test_tc27b_forms_contain_a_token(csrf_client):
    """TC-27: Every form served by the system carries a CSRF token."""
    for url in ('/login', '/register/student', '/register/company'):
        page = csrf_client.get(url).data
        assert b'name="csrf_token"' in page, f'{url} has no CSRF token'


def test_tc27c_a_request_with_the_token_succeeds(csrf_client):
    """TC-27: A normal user, whose browser sends the token, is not affected."""
    import re
    page = csrf_client.get('/login').data.decode()
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)

    response = csrf_client.post('/login', data={
        'email': 'admin@portal.com', 'password': 'admin123',
        'csrf_token': token}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data           # login worked normally


def test_tc27d_json_api_is_not_blocked(csrf_client):
    """TC-27: The read-only JSON API remains reachable."""
    assert csrf_client.get('/api/stats').status_code == 200
    assert csrf_client.get('/api/internships').status_code == 200
