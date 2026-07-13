from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from . import (  # noqa: E402,F401
    dashboard, departments, semesters, sections, subjects,
    teachers, students, assignments, schedules,
    attendance, reports, users, settings,
)
