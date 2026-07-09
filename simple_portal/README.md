# Internship Portal (Simple Version)

A simple Flask + MySQL web app that demonstrates **database connectivity** and **CRUD operations**.

Three roles:
- **Student** — browse internships, apply, withdraw applications
- **Company** — post / edit / delete internships, view applicants, select or reject them
- **Admin** — view and delete users

## Project Structure

```
simple_portal/
├── app.py              <- all Python code (routes + SQL queries)
├── database.sql        <- creates the database and tables
├── requirements.txt
├── static/
│   └── style.css       <- all styling (plain CSS, no Bootstrap)
└── templates/          <- HTML pages (plain HTML + Jinja)
    ├── base.html       <- layout shared by every page (navbar etc.)
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── internships.html
    ├── add_internship.html
    ├── edit_internship.html
    ├── my_applications.html
    ├── applicants.html
    └── users.html
```

## How to Run

1. Install the two dependencies:
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

| Operation | SQL | Where in app.py |
|-----------|-----|-----------------|
| **C**reate | `INSERT INTO` | `register()`, `add_internship()`, `apply()` |
| **R**ead   | `SELECT`      | `login()`, `internships()`, `my_applications()`, `applicants()`, `users()` |
| **U**pdate | `UPDATE`      | `edit_internship()`, `update_status()` |
| **D**elete | `DELETE FROM` | `delete_internship()`, `withdraw()`, `delete_user()` |

## How It Works (short explanation)

- `get_db()` connects Python to MySQL using **PyMySQL**.
- Every route opens a connection, runs SQL with `cursor.execute()`, and closes it.
- Queries use `%s` placeholders so user input is passed safely (prevents SQL injection).
- Passwords are stored **hashed** using `generate_password_hash()` (never plain text).
- Login stores the user's id, name and role in the Flask **session**;
  each page checks `session['role']` to decide who is allowed in.
- `templates/base.html` holds the navbar and layout; every other page
  `{% extends 'base.html' %}` so you only change the layout in one place.
