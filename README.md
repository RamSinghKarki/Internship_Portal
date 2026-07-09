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
├── db.py               <- database connection + shared helper functions
├── routes/             <- the page functions, one file per part of the site
│   ├── auth.py         <- register (3 types), login, logout
│   ├── main.py         <- home, dashboard, internship list
│   ├── student.py      <- apply, my applications, weekly logs
│   ├── company.py      <- post/edit/delete internships, applicants
│   ├── supervisor.py   <- my students, view logs, give feedback
│   └── admin.py        <- manage users
├── database.sql        <- creates the database, 8 tables and admin account
├── requirements.txt
├── static/style.css    <- all styling (plain CSS, colors set in :root variables)
└── templates/          <- plain HTML + Jinja pages (all extend base.html)
```

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create the database (enter your MySQL password when asked):
   ```
   mysql -u root -p < database.sql
   ```

3. Open `app.py` and set your MySQL password in the `get_db()` function.

4. Start the app:
   ```
   python app.py
   ```

5. Open http://127.0.0.1:5000 in the browser.

Default admin login: `admin@portal.com` / `admin123`

## Where Each CRUD Operation Is (for the viva)

| Operation | SQL | Where in routes/ |
|-----------|-----|-----------------|
| **C**reate | `INSERT INTO` | `auth.py`: register student/company/supervisor · `company.py`: `add_internship()` · `student.py`: `apply()`, `my_logs()` |
| **R**ead   | `SELECT` (+ `JOIN`) | `auth.py`: `login()` · `main.py`: `dashboard()`, `internships()` · `student.py`: `my_applications()` · `company.py`: `applicants()` · `supervisor.py`: `students()`, `view_logs()` · `admin.py`: `users()` |
| **U**pdate | `UPDATE`      | `company.py`: `edit_internship()`, `update_status()` · `supervisor.py`: `give_feedback()` |
| **D**elete | `DELETE FROM` | `company.py`: `delete_internship()` · `student.py`: `withdraw()` · `admin.py`: `delete_user()` |

## How It Works (short explanation)

- `app.py` is a "table of contents": `app.add_url_rule()` connects each URL
  to a function written in the `routes/` folder.
- `db.py` has `get_db()`, which connects Python to MySQL using **PyMySQL**.
- Every route opens a connection, runs SQL with `cursor.execute()`, and closes it.
- Queries use `%s` placeholders so user input is passed safely (prevents SQL injection).
- Passwords are stored **hashed** using `generate_password_hash()` (never plain text).
- Registration inserts into **two tables**: first `users`, then the role table
  (`students` / `companies` / `supervisors`) using `cursor.lastrowid` as the foreign key.
- Login joins `users` with `roles` and stores id, name and role in the Flask **session**;
  each page checks `session['role']` to decide who is allowed in.
- Lists use `JOIN` to combine tables (e.g. applications + internships + users).
- Foreign keys use `ON DELETE CASCADE`, so deleting a user automatically removes
  their student/company/supervisor row, internships, applications and logs.
- `templates/base.html` holds the navbar and layout; every other page
  `{% extends 'base.html' %}` so you only change the layout in one place.
