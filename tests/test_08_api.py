# ============================================================
# TEST CASE 24 : JSON REST API
# ============================================================

from conftest import setup_all_roles, login, logout


def test_tc24_api_returns_correct_json(client):
    """TC-24: /api/stats and /api/internships return valid JSON."""
    setup_all_roles(client)
    login(client, 'student@test.com')
    client.post('/apply/1', data={'cover_letter': 'Interested'}, follow_redirects=True)
    logout(client)

    # ---- statistics ----
    response = client.get('/api/stats')
    assert response.status_code == 200
    assert response.content_type.startswith('application/json')
    stats = response.get_json()
    assert stats['students'] == 1
    assert stats['companies'] == 1
    assert stats['supervisors'] == 1
    assert stats['internships'] == 1
    assert stats['applications'] == 1

    # ---- open internships ----
    response = client.get('/api/internships')
    assert response.status_code == 200
    internships = response.get_json()
    assert isinstance(internships, list) and len(internships) == 1
    item = internships[0]
    assert item['title'] == 'Python Intern'
    assert item['company'] == 'Test Company'
    assert item['duration_weeks'] == 8

    # ---- a closed internship must not be listed ----
    login(client, 'company@test.com')
    client.post('/internships/edit/1', data={
        'title': 'Python Intern', 'description': 'x', 'required_skills': 'Python',
        'duration_weeks': '8', 'stipend': 'Rs. 10000', 'vacancies': '2',
        'status': 'closed'}, follow_redirects=True)
    assert client.get('/api/internships').get_json() == []
