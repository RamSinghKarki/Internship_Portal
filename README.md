# Internship Portal

A Flask + MySQL web app that connects **Students**, **Companies**, **Supervisors** and an **Admin** — built to demonstrate **database connectivity** and **CRUD operations** with plain, easy-to-read code.

## Roles and what they can do

| Role | Actions |
|------|---------|
| **Student** | Register with details (roll no, department, semester, skills), browse open internships, apply with a cover letter, withdraw, and keep a **weekly log book** after being selected |
| **Company** | Register, post / edit / delete internships (skills, duration, stipend, vacancies), view applicants with their details, mark them selected / rejected |
| **Supervisor** | Register under a company, see the selected students of that company, read their weekly logs and give **feedback + marks** |
| **Admin** | View all users, delete users (related data is removed automatically by `ON DELETE CASCADE`) |

## Database (8 tables — matches the ER diagram)

```
roles ──< users ──< students ──────< applications >────── internships >── companies
                └─< companies                │                                │
                └─< supervisors ──┐          └──< progress_logs >──┘          │
                        │         └────────────── (feedback+marks)           │
                        └── belongs to a company ─────────────────────────────┘
```

- `roles` — admin / student / company / supervisor
- `users` — central login table (name, email, hashed password, role_id)
- `students`, `companies`, `supervisors` — extra details of each user type
- `internships` — posted by a company (title, skills, duration, stipend, vacancies, status)
- `applications` — student applies to internship (cover letter, status: applied/selected/rejected)
- `progress_logs` — weekly work of a selected student + supervisor feedback and marks

## Project Structure

```
Internship_Portal/
├── app.py              <- main file: connects every URL to its function
├── models.py           <- database tables as SQLAlchemy model classes
├── routes/             <- the page functions, one file per part of the site
│   ├── auth.py         <- register (3 types), login, logout
│   ├── main.py         <- home, dashboard, internship list
│   ├── student.py      <- apply, my applications, weekly logs
│   ├── company.py      <- post/edit/delete internships, applicants
│   ├── supervisor.py   <- my students, view logs, give feedback
│   └── admin.py        <- manage users, audit log, CSV export
├── database.sql        <- creates the database, 8 tables and admin account
├── requirements.txt
├── static/
│   ├── bootstrap.min.css   <- Bootstrap 5 (served locally, works offline)
│   ├── bootstrap.bundle.min.js
│   ├── style.css           <- small custom additions
│   └── uploads/            <- student documents
└── templates/          <- plain HTML + Jinja pages (all extend base.html)
```

## Enterprise Features

- **Admin verification of accounts** — every new student, company and
  supervisor starts as *pending*. The admin sees them in a verification queue
  (with the student's uploaded document) and approves or rejects each one,
  giving a reason. Until approved, a student cannot apply, a company cannot
  post internships, and a supervisor cannot give feedback.

- **Partner directory on the landing page** — cards showing the companies
  working with the portal (with their open internship count) and the
  participating colleges (with their student count).
- **College management** — colleges are stored in their own table, students
  choose their college at registration, and the admin can add or remove
  colleges.

- **Role-specific dashboards** — each role sees key figures relevant to it,
  with monthly growth, read live from the database.
- **In-app notifications** — bell icon with unread count; users are notified
  when an application arrives, a decision is made, a log is submitted, or
  feedback is given.
- **Audit log** — every important action (logins, failed logins, registrations,
  postings, decisions, deletions) is recorded and browsable by the admin.
- **Search + pagination** — internship search by keyword and skill; the admin
  user table is searchable and paginated.
- **CSV exports** — the admin can export all users; a company can export the
  applicants of an internship.

## Demo Data

To fill the database with realistic sample data for a demonstration
(18 students, 5 companies, 6 supervisors, 12 internships, applications in
every status, weekly logs with feedback, notifications and audit entries):

```
python seed_demo.py
```

All demo accounts use the password `pass123`:

| Role | Example login |
|------|---------------|
| Student | `student1@portal.com` |
| Company | `company1@portal.com` |
| Supervisor | `supervisor1@portal.com` |
| Admin | `admin@portal.com` (password `admin123`) |

Note: the script clears existing data before inserting the demo records.

## Running the Test Cases

All test cases from the project report are automated in the `tests/` folder
and run against a **separate** database (`internship_db_test`), so the real
data is never affected.

```
pip install pytest
python -m pytest tests/ -v
```

On Windows you can also double-click `run_tests.bat`. See `tests/README.md`
for the mapping between test files and the numbered test cases of the report.

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create the database (enter your MySQL password when asked):
   ```
   mysql -u root -p < database.sql
   ```

3. Open `app.py` and set your MySQL password in the `SQLALCHEMY_DATABASE_URI` line.

4. Start the app:
   ```
   python app.py
   ```

5. Open http://127.0.0.1:5000 in the browser.

Default admin login: `admin@portal.com` / `admin123`

## Where Each CRUD Operation Is (for the viva)

| Operation | SQL | Where in routes/ |
|-----------|-----|-----------------|
| **C**reate | `db.session.add()` | `auth.py`: register student/company/supervisor · `company.py`: `add_internship()` · `student.py`: `apply()`, `my_logs()` |
| **R**ead   | `Model.query` | `auth.py`: `login()` · `main.py`: `dashboard()`, `internships()` · `student.py`: `my_applications()` · `company.py`: `applicants()` · `supervisor.py`: `students()`, `view_logs()` · `admin.py`: `users()` |
| **U**pdate | change attribute + `commit()` | `company.py`: `edit_internship()`, `update_status()` · `supervisor.py`: `give_feedback()` |
| **D**elete | `db.session.delete()` | `company.py`: `delete_internship()` · `student.py`: `withdraw()` · `admin.py`: `delete_user()` |

## How It Works (short explanation)

- `app.py` is a "table of contents": `app.add_url_rule()` connects each URL
  to a function written in the `routes/` folder.
- `models.py` defines every database table as a **SQLAlchemy model class**
  (`User`, `Student`, `Internship`, ...); SQLAlchemy connects to MySQL through
  PyMySQL using the URI configured in `app.py`.
- CRUD through the ORM: **Create** = `db.session.add(object)` + `commit()`,
  **Read** = `Model.query.filter_by(...)`, **Update** = change the object's
  attributes + `commit()`, **Delete** = `db.session.delete(object)` + `commit()`.
- The ORM sends all values as bound parameters, which prevents SQL injection.
- Passwords are stored **hashed** using `generate_password_hash()` (never plain text).
- Registration creates a `User` and its profile object together through the
  relationship (e.g. `Student(user=user, ...)`) — one commit inserts both rows.
- Login finds the user, checks the password hash, and stores id, name and role
  (via `user.role.role_name`) in the Flask **session**; each page checks
  `session['role']` to decide who is allowed in.
- Related data is read through **relationships** (e.g. `application.internship.title`,
  `internship.company.user.name`) instead of manual joins.
- Foreign keys use `ON DELETE CASCADE`, so deleting a user automatically removes
  their student/company/supervisor row, internships, applications and logs.
- `templates/base.html` holds the navbar and layout; every other page
  `{% extends 'base.html' %}` so you only change the layout in one place.
