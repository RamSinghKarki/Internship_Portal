# ============================================================
# REST API - JSON endpoints (for reports or a future mobile app)
# ============================================================

from flask import jsonify
from models import Student, Company, Supervisor, Internship, Application


def api_stats():
    """GET /api/stats - system statistics as JSON."""
    return jsonify({
        'students':     Student.query.count(),
        'companies':    Company.query.count(),
        'supervisors':  Supervisor.query.count(),
        'internships':  Internship.query.count(),
        'applications': Application.query.count(),
    })


def api_internships():
    """GET /api/internships - all open internships as JSON."""
    items = Internship.query.filter_by(status='open').order_by(Internship.id.desc()).all()
    return jsonify([{
        'id': i.id,
        'title': i.title,
        'company': i.company.user.name,
        'required_skills': i.required_skills,
        'duration_weeks': i.duration_weeks,
        'stipend': i.stipend,
        'vacancies': i.vacancies,
    } for i in items])
