from functools import wraps

from flask import abort
from flask_login import current_user

from app.extensions import login_manager


def role_required(*roles):
    """Restrict a view to the given role names. Anonymous users are sent to
    the login page; authenticated users with the wrong role get a 403."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role_name not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


admin_required = role_required("admin")
teacher_required = role_required("teacher", "admin")
student_required = role_required("student")
