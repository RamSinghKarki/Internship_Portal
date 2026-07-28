# ============================================================
# EXTRA CHECKS : Landing page and role specific dashboards
# ============================================================

from conftest import setup_all_roles, login, logout


def test_landing_page_shows_live_counts(client):
    """The public landing page shows counts taken from the database."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Find Your Internship' in response.data

    setup_all_roles(client)
    response = client.get('/')
    assert b'Students Joined' in response.data
    assert b'Internships Posted' in response.data


def test_each_role_sees_only_its_own_dashboard_figures(client):
    """Every role gets a dashboard with figures relevant to that role."""
    setup_all_roles(client)

    login(client, 'student@test.com')
    response = client.get('/dashboard')
    assert b'Open Internships' in response.data
    assert b'My Applications' in response.data
    assert b'Supervisors' not in response.data          # admin figure
    logout(client)

    login(client, 'company@test.com')
    response = client.get('/dashboard')
    assert b'My Internships' in response.data
    assert b'Applications Received' in response.data
    logout(client)

    login(client, 'supervisor@test.com')
    response = client.get('/dashboard')
    assert b'My Students' in response.data
    assert b'Awaiting My Feedback' in response.data
    logout(client)

    login(client, 'admin@portal.com', 'admin123')
    response = client.get('/dashboard')
    for label in (b'Students', b'Companies', b'Supervisors',
                  b'Internships', b'Applications'):
        assert label in response.data
    assert b'chart_' in response.data                   # charts are rendered
