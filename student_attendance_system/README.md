# Student Attendance Management System

A production-style attendance management system for colleges and universities,
built with **Python Flask**, **SQLAlchemy**, **MySQL**, **Bootstrap 5** and
**Chart.js**. It digitizes students, teachers, departments, academic
structures, class routines and daily attendance, and provides reports and
analytics with PDF/Excel export.

![Stack](https://img.shields.io/badge/Flask-3.x-blue) ![DB](https://img.shields.io/badge/MySQL-8-orange) ![UI](https://img.shields.io/badge/Bootstrap-5.3-purple)

## Features

**Administrator**
- Dashboard with summary cards (students, teachers, subjects, departments,
  today's classes, present/absent today, students below 75%, attendance %)
  and Chart.js charts (monthly trend, department/subject/semester comparison,
  present-vs-absent, teacher sessions)
- Full CRUD with search, filters and pagination for departments, semesters,
  sections, subjects, teachers, students
- Teacher–subject assignment (one teacher per subject/section/year enforced)
- Class routine with weekly timetable view and clash detection
  (section and teacher double-booking prevented)
- Attendance monitoring and history with rich filters
- Reports centre: student / teacher / subject / department reports with
  printable view, PDF export (ReportLab) and Excel export (openpyxl)
- Analytics: monthly, weekly-heatmap, daily charts, subject and department
  comparison, teacher sessions, top/bottom student rankings
- User account management (enable/disable, password reset) and system settings
- Notifications (low session attendance, attendance-not-taken widget)

**Teacher**
- Personal dashboard: today's classes with "taken / take now" state,
  session stats, low-attendance students in own subjects
- Take attendance: semester → section → subject → date → class period flow,
  auto-loaded roster, Present/Absent/Late/Leave per student, remarks,
  mark-all/reset shortcuts, duplicate-session prevention
- Same-day attendance editing (admin-configurable)
- Attendance history and per-subject reports

**Student**
- Personal dashboard: overall %, subject-wise breakdown with progress bars,
  monthly chart, low-attendance warning
- Attendance history with subject / month filters
- Downloadable personal report (PDF / Excel)

## Project Structure

```
student_attendance_system/
├── app.py                  # application entry point (dev server)
├── config.py               # env-driven configuration
├── init_db.py              # clean database setup (roles + admin, no demo data)
├── seed.py                 # optional demo data seeder
├── requirements.txt
└── app/
    ├── __init__.py         # app factory, blueprint registration
    ├── extensions.py       # db / login / csrf singletons
    ├── models/             # SQLAlchemy models (normalized schema)
    ├── blueprints/
    │   ├── auth/           # login, logout, profile
    │   ├── admin/          # all management modules + reports + analytics
    │   ├── teacher/        # teacher portal + attendance flow
    │   ├── student/        # student portal
    │   └── api/            # JSON endpoints for charts & cascading dropdowns
    ├── utils/              # decorators, helpers, stats queries, PDF/Excel
    ├── templates/          # Jinja2 templates (Bootstrap 5)
    └── static/             # css, js, uploaded photos
```

## Database Schema

Normalized tables with FKs, unique constraints and indexes:
`roles`, `users`, `departments`, `semesters`, `sections`, `subjects`,
`teachers`, `students`, `teacher_subject_assignments`, `schedules`,
`attendance` (sessions), `attendance_details` (per-student marks),
`notifications`, `settings`.

Key integrity rules:
- `attendance` is unique on (subject, section, date, schedule) — no duplicate sessions
- `attendance_details` is unique on (session, student)
- `teacher_subject_assignments` is unique on (subject, section, semester, year)
- cascading deletes from sessions to their detail rows

## Quick Start (SQLite demo — zero setup)

```bash
cd student_attendance_system
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python init_db.py       # creates tables + admin account (clean, no demo data)
python app.py           # http://127.0.0.1:5000
```

Log in as `admin / admin123` and add departments, semesters, sections,
subjects, teachers and students from the admin panel. To try the system
with pre-filled demo data instead, run `python seed.py` in place of
`init_db.py` (warning: it wipes existing data first).

## MySQL Setup (production)

```sql
CREATE DATABASE attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'attendance_user'@'localhost' IDENTIFIED BY 'strong-password';
GRANT ALL PRIVILEGES ON attendance_db.* TO 'attendance_user'@'localhost';
```

```bash
export DATABASE_URL="mysql+pymysql://attendance_user:strong-password@localhost:3306/attendance_db?charset=utf8mb4"
export SECRET_KEY="a-long-random-string"
python init_db.py && python app.py
```

## Default Credentials

| Setup | Role | Username | Password |
|-------|------|----------|----------|
| `init_db.py` (clean) | Admin | `admin` | `admin123` |
| `seed.py` (demo, optional) | Teacher | `emp-001` … `emp-008` | `teacher123` |
| `seed.py` (demo, optional) | Student | `reg-2025-0001` … | `student123` |

Change the admin password from **My Profile** after first login.
Teacher/student accounts are created automatically when you add their
profiles (username = employee ID / registration number).

## Security

- Passwords hashed with Werkzeug (PBKDF2)
- Role-based access control via decorators (`admin_required`, `role_required`)
- CSRF protection on every form (Flask-WTF `CSRFProtect`)
- SQLAlchemy ORM everywhere — no raw SQL string building
- Server-side validation + uniqueness checks on all forms
- Session cookies: HttpOnly, SameSite=Lax (Secure in production config)
- Teachers can only take/edit attendance for their own assignments;
  students only see their own records

## Tech Stack

Flask 3 · Flask-SQLAlchemy · Flask-Login · Flask-WTF · PyMySQL ·
Bootstrap 5.3 · Bootstrap Icons · Chart.js 4 · ReportLab · openpyxl
