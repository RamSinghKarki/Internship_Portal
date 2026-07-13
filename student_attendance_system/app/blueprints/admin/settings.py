from flask import render_template, request, redirect, url_for, flash

from app.extensions import db
from app.models import Setting, Notification
from app.utils.decorators import admin_required
from . import admin_bp

EDITABLE_KEYS = [
    ("institute_name", "Institute Name", "text"),
    ("academic_year", "Current Academic Year", "text"),
    ("low_attendance_threshold", "Low Attendance Threshold (%)", "number"),
    ("allow_same_day_edit", "Allow teachers to edit same-day attendance", "checkbox"),
]


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        for key, _label, kind in EDITABLE_KEYS:
            if kind == "checkbox":
                Setting.set(key, "1" if request.form.get(key) else "0")
            else:
                value = (request.form.get(key) or "").strip()
                if key == "low_attendance_threshold":
                    try:
                        value = str(min(max(float(value), 0), 100))
                    except ValueError:
                        value = "75"
                Setting.set(key, value)
        db.session.commit()
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))

    values = {key: Setting.get(key) for key, _l, _k in EDITABLE_KEYS}
    return render_template("admin/settings/index.html",
                           keys=EDITABLE_KEYS, values=values)


@admin_bp.route("/notifications")
@admin_required
def notifications():
    rows = (
        Notification.query.filter(Notification.user_id.is_(None))
        .order_by(Notification.created_at.desc())
        .limit(100).all()
    )
    return render_template("admin/settings/notifications.html", rows=rows)


@admin_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@admin_required
def notification_read(notification_id):
    n = db.get_or_404(Notification, notification_id)
    n.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("admin.notifications"))
