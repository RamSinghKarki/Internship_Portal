# INTERNSHIP PORTAL

## A Web-Based Internship Management System

**Mid-Term Project Report**

Submitted by: **[Your Name]**
Roll No: **[Your Roll Number]**
Program: **[Your Program, e.g. BSc CSIT / BCA]**

Submitted to: **[Department Name]**
**[Your College Name]**

Supervisor: **[Supervisor / Sir's Name]**

Date: **[Month Year]**

\newpage

## Abstract

Internship Portal is a web application that connects students looking for internships with companies offering them. Students can browse open internships and apply with a cover letter. Companies can post internships and select the best applicants. After selection, the student keeps a weekly log book of the work done, and a supervisor from the company reviews each log and gives feedback with marks. An admin manages all the users of the system.

The system is built with **Python (Flask)** for the web application and **MySQL** for the database. The main goal of this phase of the project was to achieve **database connectivity** and implement all four **CRUD operations** (Create, Read, Update, Delete) using raw SQL queries.

\newpage

## Table of Contents

1. Introduction
2. Problem Statement
3. Objectives
4. System Analysis
5. System Design
6. Implementation
7. Testing
8. Progress Status
9. Conclusion and Future Work
10. References

\newpage

## 1. Introduction

Finding an internship is an important step for every student, but the process is often unorganized. Students ask around personally, companies collect applications by email, and colleges have no easy way to follow what their students are doing during the internship.

Internship Portal solves this by bringing everyone to one website:

- **Students** create a profile with their skills, browse internships and apply online.
- **Companies** post internship openings and review all applicants in one place.
- **Supervisors** (company staff) follow the weekly progress of selected students.
- **Admin** looks after the whole system and its users.

## 2. Problem Statement

At present, there is no single system where students, companies and supervisors can work together during an internship. This causes problems such as:

- Students do not know which companies are offering internships.
- Companies receive applications through many different channels and lose track of them.
- There is no record of what work the student actually did every week.
- Supervisor feedback is informal and never stored anywhere.

## 3. Objectives

The main objectives of this project are:

1. To build a web application connected to a MySQL database.
2. To implement all CRUD operations (Create, Read, Update, Delete) using SQL.
3. To provide role-based login for four types of users (admin, student, company, supervisor).
4. To let students apply for internships and companies select applicants.
5. To keep a weekly progress log of every selected student with supervisor feedback and marks.

## 4. System Analysis

### 4.1 Functional Requirements

| Role | Requirements |
|------|--------------|
| Student | Register with details (roll no, department, semester, skills), login, browse open internships, apply with a cover letter, withdraw an application, submit weekly logs after selection |
| Company | Register, login, post internships (title, skills, duration, stipend, vacancies), edit or delete own posts, view applicants with details, mark applicants as selected or rejected |
| Supervisor | Register under a company, login, view selected students of that company, read their weekly logs, give feedback and marks |
| Admin | Login, view all users of the system, delete a user |

### 4.2 Non-Functional Requirements

- **Security:** Passwords are stored as hashes, never in plain text. SQL queries use placeholders (`%s`) so user input cannot break the query (prevents SQL injection). Every page checks the logged-in user's role before showing anything.
- **Usability:** Simple and clean interface built with plain HTML and CSS, easy to use without training.
- **Maintainability:** The code is separated into small files (one file per user type), so changes are easy to make.

### 4.3 Tools and Technologies

| Tool | Use |
|------|-----|
| Python 3 | Programming language |
| Flask | Web framework (routes, templates, sessions) |
| MySQL | Database |
| PyMySQL | Library that connects Python to MySQL |
| HTML + Jinja | Web pages (templates) |
| CSS | Styling (no framework, plain CSS) |
| Git / GitHub | Version control |

## 5. System Design

### 5.1 System Architecture

The system uses a simple three-layer architecture:

```
Browser (HTML/CSS)  <-->  Flask (Python, routes/)  <-->  MySQL (database)
```

1. The user opens a page in the browser and submits a form.
2. Flask receives the request, runs the matching function from the `routes/` folder.
3. The function executes SQL queries on MySQL through PyMySQL and renders an HTML template with the result.

### 5.2 ER Diagram

**[ Insert your ER diagram image here ]**

### 5.3 Database Design

The database `internship_db` has **8 tables**:

**Table: roles** — the four types of users

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| role_name | VARCHAR(20), UNIQUE | admin / student / company / supervisor |

**Table: users** — central login table

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| role_id | INT | Foreign Key -> roles(id) |
| name | VARCHAR(100) | |
| email | VARCHAR(100), UNIQUE | |
| password | VARCHAR(255) | stored as hash |
| created_at | TIMESTAMP | |

**Table: students** — extra details of a student user

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| user_id | INT, UNIQUE | Foreign Key -> users(id) |
| roll_number | VARCHAR(50) | |
| department | VARCHAR(100) | |
| semester | INT | |
| skills | VARCHAR(255) | |

**Table: companies** — extra details of a company user

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| user_id | INT, UNIQUE | Foreign Key -> users(id) |
| industry | VARCHAR(100) | |
| location | VARCHAR(100) | |
| description | TEXT | |

**Table: supervisors** — company staff who guide students

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| user_id | INT, UNIQUE | Foreign Key -> users(id) |
| company_id | INT | Foreign Key -> companies(id) |
| designation | VARCHAR(100) | |
| department | VARCHAR(100) | |

**Table: internships** — posted by companies

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| company_id | INT | Foreign Key -> companies(id) |
| title | VARCHAR(200) | |
| description | TEXT | |
| required_skills | VARCHAR(255) | |
| duration_weeks | INT | |
| stipend | VARCHAR(50) | |
| vacancies | INT | |
| status | VARCHAR(20) | open / closed |
| posted_date | TIMESTAMP | |

**Table: applications** — a student applies to an internship

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| student_id | INT | Foreign Key -> students(id) |
| internship_id | INT | Foreign Key -> internships(id) |
| cover_letter | TEXT | |
| status | VARCHAR(20) | applied / selected / rejected |
| applied_date | TIMESTAMP | |

A student cannot apply twice to the same internship (UNIQUE constraint on student_id + internship_id).

**Table: progress_logs** — weekly work reports

| Column | Type | Key |
|--------|------|-----|
| id | INT, AUTO_INCREMENT | Primary Key |
| application_id | INT | Foreign Key -> applications(id) |
| supervisor_id | INT | Foreign Key -> supervisors(id) |
| week_number | INT | |
| description | TEXT | work done by the student |
| feedback | TEXT | written by the supervisor |
| marks | INT | out of 10 |
| submitted_date | TIMESTAMP | |

All foreign keys use **ON DELETE CASCADE**, so when the admin deletes a user, all of that user's data (profile, internships, applications, logs) is removed automatically by the database.

### 5.4 UML Class Diagram

**[ Insert your UML class diagram image here ]**

## 6. Implementation

### 6.1 Project Structure

```
Internship_Portal/
|-- app.py              main file: connects every URL to its function
|-- db.py               database connection + shared helper functions
|-- routes/             page functions, one file per part of the site
|   |-- auth.py         register (3 types), login, logout
|   |-- main.py         landing page, dashboard, internship list
|   |-- student.py      apply, my applications, weekly logs
|   |-- company.py      post/edit/delete internships, applicants
|   |-- supervisor.py   my students, view logs, give feedback
|   |-- admin.py        manage users
|-- database.sql        creates the database, 8 tables and admin account
|-- static/style.css    all styling
|-- templates/          HTML pages (all extend base.html)
```

### 6.2 Database Connectivity

The function `get_db()` in `db.py` connects Python to MySQL using PyMySQL:

```python
def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='......',
        database='internship_db',
        cursorclass=pymysql.cursors.DictCursor
    )
```

Every page function opens a connection, runs its SQL with `cursor.execute()`, commits if data was changed, and closes the connection.

### 6.3 CRUD Operations

| Operation | SQL | Where it is used |
|-----------|-----|------------------|
| Create | INSERT INTO | registration (users + role table), post internship, apply, submit weekly log |
| Read | SELECT (with JOIN) | login, landing page counts, internship list, applications, applicants, logs, users list |
| Update | UPDATE | edit internship, select/reject an application, supervisor feedback and marks |
| Delete | DELETE FROM | delete internship, withdraw application, delete user |

Example of a CREATE operation (student applies to an internship):

```python
cur.execute(
    "INSERT INTO applications (student_id, internship_id, cover_letter) "
    "VALUES (%s, %s, %s)",
    (me['id'], internship_id, request.form['cover_letter'])
)
db.commit()
```

Example of a READ operation with JOIN (student's applications with company name):

```sql
SELECT applications.id, applications.status,
       internships.title, users.name AS company_name
FROM applications
JOIN internships ON applications.internship_id = internships.id
JOIN companies   ON internships.company_id = companies.id
JOIN users       ON companies.user_id = users.id
WHERE applications.student_id = %s
```

### 6.4 Login and Sessions

When a user logs in, the system joins the `users` and `roles` tables, checks the password hash, and saves the user's id, name and role in the Flask session. Every page first checks `session['role']` — for example, only a user with role `company` can post an internship.

### 6.5 Security Measures

1. **Password hashing** — `generate_password_hash()` is used at registration and `check_password_hash()` at login. Plain passwords are never stored.
2. **SQL injection prevention** — every query uses `%s` placeholders; user input is never joined into the SQL string directly.
3. **Role checking** — every page verifies the session role before doing anything.
4. **Ownership checking** — a company can only edit/delete its own internships; a student can only withdraw their own applications; a supervisor can only see logs of students at their own company.

### 6.6 Screenshots

**[ Insert screenshots here: landing page, login, register, student internship list, company applicants page, weekly log book, supervisor feedback, admin users page ]**

## 7. Testing

The system was tested manually by going through every user journey. Some of the test cases:

| # | Test Case | Steps | Expected Result | Result |
|---|-----------|-------|-----------------|--------|
| 1 | Student registration | Fill the student form and submit | Row created in users and students tables, redirected to login | Pass |
| 2 | Duplicate email | Register again with the same email | "Email is already registered" message | Pass |
| 3 | Wrong password | Login with wrong password | "Invalid email or password" message | Pass |
| 4 | Post internship | Login as company, fill the post form | Internship appears in the list | Pass |
| 5 | Apply | Login as student, apply with cover letter | Application saved with status "applied" | Pass |
| 6 | Apply twice | Apply again to the same internship | "You already applied" message | Pass |
| 7 | Select applicant | Company changes status to selected | Status badge changes to "selected" | Pass |
| 8 | Weekly log | Selected student submits week 1 log | Log appears in the log book | Pass |
| 9 | Feedback | Supervisor writes feedback and marks | Feedback and marks visible to the student | Pass |
| 10 | Delete user | Admin deletes a company | Company, its internships and applications are all removed (cascade) | Pass |
| 11 | Access control | Student opens a company-only page | Redirected away | Pass |

## 8. Progress Status (Mid-Term)

### Completed

- Database design with 8 tables and relationships (foreign keys, cascade delete)
- Database connectivity from Python using PyMySQL
- All CRUD operations with raw SQL
- Role-based registration and login (4 roles)
- Full workflow: post -> apply -> select -> weekly logs -> feedback and marks
- Landing page with live counts from the database

### Remaining (planned for final defense)

- Resume/file upload for students
- Search and filter for internships
- Email notification when an applicant is selected
- Reports for admin (e.g. internships per company)
- Deployment on a live server

## 9. Conclusion and Future Work

This phase of the project successfully achieved its main objective: a working web application with full database connectivity and all four CRUD operations implemented through raw SQL queries. The complete internship workflow — from a company posting an internship to a supervisor marking a student's weekly log — works end to end.

In the next phase, the system can be extended with file uploads, search, notifications and reports, and finally deployed to a live server so real users can access it.

## 10. References

1. Flask Documentation — https://flask.palletsprojects.com/
2. MySQL Documentation — https://dev.mysql.com/doc/
3. PyMySQL Documentation — https://pymysql.readthedocs.io/
4. Jinja Template Documentation — https://jinja.palletsprojects.com/
