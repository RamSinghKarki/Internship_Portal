# Viva Preparation Sheet
## Internship Portal Management System — Final Defense

---

# PART 1 — Your opening (about 60 seconds)

Practise this until it is automatic. It answers "tell us about your project"
and sets the direction of the questions that follow.

> "Our project is an Internship Portal Management System. It solves a real
> problem: in most colleges, internships are arranged informally — students
> hear about openings by word of mouth, apply by email, and once the
> internship starts nobody records what work the student actually does.
>
> Our system brings four roles onto one platform. Students register with
> their college and skills and apply to internships with a cover letter.
> Companies post internships and select or reject applicants. A supervisor
> from the company reviews the student's weekly log book and gives feedback
> with marks. An administrator manages all users and colleges.
>
> It is built with Python Flask, MySQL and the SQLAlchemy ORM, with a
> Bootstrap interface. The database has eleven tables, and we have written
> thirty-five automated tests covering every test case in our report."

---

# PART 2 — Demo order (do not improvise)

Run `python seed_demo.py` **before** the defense so the data looks real.
Have the app already running at `http://127.0.0.1:5000`.

| # | Step | What to say while clicking |
|---|------|----------------------------|
| 1 | Landing page | "These numbers and the company and college cards come live from the database." |
| 2 | Register a student | "Notice the college dropdown and the compulsory PDF upload — citizenship / NID, resume and other documents in one file." |
| 2b | Login as admin, open Verifications | "Every new account waits here. I can see the uploaded document before approving." Approve the new student. |
| 3 | Login as `company1@portal.com` | "The navigation bar changes according to the role." |
| 4 | Post an internship | "This is a CREATE operation." |
| 5 | View applicants | "The company sees the student's college, skills, cover letter and the uploaded PDF with the NID and resume." |
| 6 | Mark one applicant **selected** | "This is an UPDATE, and it notifies the student." |
| 7 | Login as that student | "The bell icon shows the notification." |
| 8 | Open Weekly Logs, submit a log | "Only a selected student can open the log book." |
| 9 | Login as `supervisor1@portal.com` | "The supervisor sees only their own company's students." |
| 10 | Give feedback and marks | "The student can now see this immediately." |
| 11 | Login as `admin@portal.com` | "The admin dashboard shows system wide figures." |
| 12 | Show Users → search, export CSV | "Searchable, paginated, exportable." |
| 13 | Show Audit Log | "Every important action is recorded, including failed logins." |
| 14 | Run `python -m pytest tests/ -v` | "All thirty-five tests pass." |

**Keep a second browser (or incognito window) open** so you can be logged in
as two roles at once and avoid repeated logging in and out.

---

# PART 3 — Questions and answers

## A. Project and requirements

**Q: What problem does your system solve?**
Internship management in colleges is manual and unrecorded. Students do not
know which companies are offering internships, companies lose track of
applications received by email, and there is no record of the work a student
does during the internship or of the supervisor's evaluation. Our system puts
all of that in one place with a permanent database record.

**Q: Who are the users of the system?**
Four roles: student, company, supervisor and administrator. The roles are
stored in a `roles` table and each user's `role_id` decides what they can see.

**Q: What is the difference between a functional and a non-functional requirement?**
A functional requirement is something the system *does* — for example, "a
student can apply to an internship with a cover letter". A non-functional
requirement is a *quality* of how it does it — for example, "passwords are
stored as hashes". We have twenty-four functional requirements and nine
non-functional requirements in Chapter 3.

**Q: What is the scope of the project? What is not included?**
Included: registration and login for all roles, internship posting and
search, applications with cover letters, selection, weekly logs with
supervisor feedback and marks, notifications, audit log, CSV exports,
and college and user administration. Each student uploads one PDF holding
the citizenship / NID, resume and other documents, which the admin checks
before approving and the company reads when the student applies.
Not included: email or SMS delivery, interview scheduling, direct messaging
between users, and separate file attachments on the weekly logs — these are
listed as future scope.

## B. Database

**Q: How many tables do you have and what are they?**
Eleven: `roles`, `users`, `colleges`, `students`, `companies`, `supervisors`,
`internships`, `applications`, `progress_logs`, `notifications`, `audit_logs`.

**Q: Why is `users` separate from `students` and `companies`?**
Everyone who logs in needs the same fields — name, email, password, role — so
those live once in `users`. The details that differ by role go in separate
tables linked by a unique `user_id`. This avoids a wide table full of empty
columns and keeps the design in third normal form.

**Q: Explain your normalization.**
The schema is in 3NF. Every table has a primary key and atomic values (1NF).
Every primary key is a single surrogate `id`, so partial dependency cannot
occur (2NF). No non-key column depends on another non-key column — login data
is only in `users`, role-specific data is in the role tables, and the role
name is factored out into `roles` (3NF).

**Q: What is a primary key and a foreign key in your project?**
A primary key uniquely identifies a row — every table has `id`. A foreign key
points to a primary key in another table — for example
`applications.student_id` references `students.id`, which guarantees an
application can never belong to a student who does not exist.

**Q: What happens when the admin deletes a user?**
The foreign keys use `ON DELETE CASCADE`, so the database automatically
deletes that user's profile row, and anything depending on it — a company's
internships, their applications and progress logs. We do not write those
DELETE statements ourselves; the database enforces it. Test case 15 proves it.

**Q: Why does `progress_logs.supervisor_id` use SET NULL instead of CASCADE?**
Because if a supervisor leaves, the student's weekly log and its marks must
survive. Only the link to that supervisor is cleared. The same idea applies to
`students.college_id`: removing a college must not delete student accounts.

**Q: How do you prevent a student from applying twice?**
Two layers. In the code we check for an existing application first, and in the
database there is a UNIQUE constraint on `(student_id, internship_id)`, so
even a double-click or a direct database insert cannot create a duplicate.

**Q: What indexes do you have?**
Primary keys are indexed automatically, foreign keys are indexed by InnoDB,
and `users.email` and `colleges.name` have unique indexes. Those are the
columns we search and join on most.

## C. Backend and Flask

**Q: Explain the architecture.**
Three tiers. The presentation tier is the browser showing HTML produced from
Jinja templates. The application tier is Flask: `app.py` maps every URL to a
function, the functions live in the `routes/` package, and `models.py`
defines the data model. The data tier is MySQL with eleven tables.

**Q: What does `app.py` do?**
It creates the Flask application, configures the database connection, and
acts as a table of contents: each `app.add_url_rule()` line connects one URL
to one function in `routes/`. We have thirty-two URL rules.

**Q: Why did you split the code into a `routes/` folder?**
So each file has one responsibility — `auth.py` for registration and login,
`student.py` for student pages, and so on. It keeps functions short and means
a change to one role's pages cannot break another's.

**Q: Trace what happens when a student clicks "Apply".**
The browser sends `POST /apply/5`. `app.py` matches the rule and calls
`apply(internship_id=5)` in `routes/student.py`. The function checks
`session['role']` is student, checks there is no existing application, creates
an `Application` object, queues a notification for the company and an audit
entry, and commits. SQLAlchemy generates the INSERT statements. The browser is
then redirected to My Applications, which queries the new row and renders it.

**Q: What is a session and how do you use it?**
After a successful login we store the user's id, name and role in the Flask
session, which is a signed cookie. Every page reads `session['role']` to
decide what to show. Logging out clears it.

**Q: What is Jinja and what is template inheritance?**
Jinja is Flask's template engine — it puts Python values into HTML. All twenty
of our pages start with `{% extends 'base.html' %}`, so the navigation bar and
layout are written once and every page inherits them.

## D. SQLAlchemy and the ORM

**Q: What is an ORM and why did you use it?**
An ORM — Object Relational Mapper — maps database tables to Python classes, so
a row becomes an object. We use SQLAlchemy. It removes repetitive SQL from the
application code, sends every value as a bound parameter, and lets us express
relationships and cascade rules in one place.

**Q: Show the four CRUD operations in your code.**
- CREATE: `db.session.add(application)` then `db.session.commit()`
- READ: `Application.query.filter_by(student_id=me.id).all()`
- UPDATE: `application.status = 'selected'` then `commit()`
- DELETE: `db.session.delete(internship)` then `commit()`

**Q: Where is the SQL then?**
SQLAlchemy generates it from the model classes. The schema itself is
hand-written in `database.sql`, which is the file we run to create the
database. So we control the schema and the ORM handles the statements.

**Q: What is `db.session.commit()`?**
SQLAlchemy collects changes in a session, which is a unit of work. `commit()`
writes them to the database as one transaction. If anything fails, nothing is
half-saved.

**Q: What is a relationship and a backref?**
A relationship lets us move between objects without writing a join. Because
`Application` has `internship = relationship(...)`, we can write
`application.internship.title` in a template. A backref creates the reverse
link automatically, so `internship.applications` gives all applications.

**Q: Why is `models.py` similar to your UML class diagram?**
Because each class in the diagram is literally a class in `models.py` with the
same attributes. That is one benefit of using an ORM — the design and the code
are the same structure.

## E. Security

**Q: How are passwords stored?**
Never in plain text. We call `generate_password_hash()` from Werkzeug at
registration, which produces a salted hash, and `check_password_hash()` at
login. Even we cannot read a user's password — you can see this in the `users`
table.

**Q: How do you prevent SQL injection?**
All database access goes through SQLAlchemy, which sends values as bound
parameters rather than pasting them into the SQL string. So input like
`' OR 1=1--` is treated as text, not as SQL.

**Q: How does account verification work?**
Every new student, company and supervisor account is created with the status
*pending*. Until the administrator approves it, the account can log in and
look around, but its main action is blocked: a student cannot apply, a
company cannot post an internship, and a supervisor cannot give feedback. The
administrator sees a verification queue showing each applicant's details and,
for students, the uploaded document, and approves or rejects with a reason.
The user is notified of the decision, and the whole action is written to the
audit log.

**Q: How does role-based access control work?**
Every route checks `session.get('role')` before doing anything and redirects
if it is wrong. We also check ownership: a company can only edit its own
internships, a supervisor only sees students of their own company, and a
student only their own applications. Test file `test_05_access_control.py`
proves all of this.

**Q: What if I change the URL to another company's applicants?**
You are redirected with "Internship not found". The query filters by both the
internship id and the logged-in company id, so the record simply is not
returned. That is test case 14b.

**Q: How do you know an action was performed by a particular user?**
Every important action writes an entry to `audit_logs` with the user, the
action, details and a timestamp — including failed login attempts, which are
stored with no user id. The admin can review them on the Audit Log page.

**Q: (Honest answer) Do you have CSRF protection?**
No, and we know it. A malicious page could in principle submit a form on
behalf of a user who is already logged in. The standard fix in Flask is
Flask-WTF's `CSRFProtect`, which puts a hidden token in every form and
rejects any POST that arrives without it. We would add that before putting
the system on a public server.

## F. Frontend

**Q: Why Bootstrap and not plain CSS?**
Bootstrap gives a consistent, responsive layout with far less custom CSS —
the navigation bar, cards, tables, badges and forms all come from it. We serve
it from our own `static/` folder rather than a CDN, so the system works
without an internet connection.

**Q: Is it responsive?**
Yes — Bootstrap's grid and the collapsible navbar mean it works on a phone
screen. You can narrow the browser window to see it.

## G. Testing

**Q: How did you test the system?**
Three levels. Unit testing of individual routes with valid and invalid inputs,
integration testing of the complete workflow across roles, and beta testing
where classmates used the system without instructions. All of it is automated
in the `tests/` folder — thirty-five tests, one file per area.

**Q: Show me a test running.**
`python -m pytest tests/ -v` — each test is named after the test case number in
our report, for example `test_tc09_student_cannot_apply_twice`.

**Q: Does running the tests destroy your data?**
No. The tests build a separate database called `internship_db_test` from the
same `database.sql` file, so the schema is identical but the demonstration
data is untouched.

**Q: Give an example of a bug you found and fixed.**
When we moved to the ORM, the date columns were being inserted as NULL because
the defaults were only in the SQL file, not in the model classes. Pages that
formatted dates then crashed. We added `default=datetime.now` to the model
columns and re-tested.

## H. Diagrams

**Q: Explain your ER diagram.**
Eleven entities. `roles` defines the type of every user; `users` is the
central login table; `students`, `companies` and `supervisors` extend it with
role-specific details; `colleges` enrolls students; companies post
`internships`, which receive `applications` from students; each application
contains `progress_logs` which a supervisor evaluates; `notifications` and
`audit_logs` both belong to a user.

**Q: What is the difference between your DFD and your ER diagram?**
The ER diagram shows the *data at rest* — entities and their relationships.
The DFD shows the *data in motion* — the processes, the external entities and
the flows between them. They describe the same system from two angles.

**Q: Is your Level 1 DFD balanced with Level 0?**
Yes. Every flow between an external entity and the system in the context
diagram appears again in Level 1, distributed among the five processes.

**Q: In your UML class diagram, what does the hollow triangle mean?**
Generalization — inheritance. Student, Company, Supervisor and Admin all
extend the abstract `User` class, because they share identity and login
behaviour but add their own attributes and methods.

## I. Harder questions

**Q: What would happen if two students applied at exactly the same moment?**
Both requests would run the duplicate check and then insert. The UNIQUE
constraint on `(student_id, internship_id)` means the database would reject
the second one, so no duplicate can exist. Handling that error gracefully
rather than showing an error page is an improvement we would make.

**Q: How would this scale to a thousand users?**
The reads are indexed and paginated, so listing pages stay fast. The next
steps would be connection pooling, caching the dashboard counts rather than
recalculating them per request, and running the application behind a
production server such as Gunicorn instead of the Flask development server.

**Q: Why not use Django, which has an admin panel built in?**
Django would have given us the admin panel free, but it also hides a lot
behind conventions. With Flask we had to build the routing, the roles and the
admin pages ourselves, which is why we can explain every part of the system.
For a project meant to demonstrate understanding, that was the right trade.

**Q: What was the hardest part?**
Getting the relationships and cascade rules right. Deciding that deleting a
company should remove its internships, but removing a supervisor or a college
must not delete a student's records, took careful thought — and each rule is
now covered by a test.

**Q: If you had two more months, what would you build?**
Email delivery of the notifications we already generate, interview scheduling,
direct messaging between students and companies, automatic completion
certificates, and deployment on a live server with HTTPS and backups.

---

# PART 4 — Be honest about these

Examiners respect a straight answer far more than a bluff. If asked:

- **Email and SMS** — not implemented; notifications are inside the
  application only, because we had no mail server to demonstrate with.
- **Deployment** — runs on the Flask development server; a production
  deployment needs Gunicorn or similar behind a web server, with HTTPS.
- **CSRF protection** — not implemented; the fix is Flask-WTF `CSRFProtect`.
- **The secret key** — it reads from the `SECRET_KEY` environment variable
  when one is set, but the fallback value is still in the source for
  convenience during development.
- **Separate file fields** — the NID, resume and other papers arrive as one
  combined PDF, not as separate uploads that the system can read individually.

If you do not know an answer: *"I am not certain about that — what I do know
is …"* and then say the nearest thing you do know. Never invent a detail.

---

# PART 5 — Quick facts card

| Item | Value |
|------|-------|
| Tables | 11 |
| Model classes | 11 (`models.py`) |
| URL rules | 32 (`app.py`) |
| Route files | 7 (`routes/`) |
| Templates | 20 (all extend `base.html`) |
| Automated tests | 36, all passing |
| Test cases in report | 27 |
| Functional requirements | FR-1 … FR-24 |
| Roles | admin, student, company, supervisor |
| Stack | Python, Flask, SQLAlchemy ORM, PyMySQL, MySQL, Bootstrap 5, Bootstrap Icons |
| Admin login | `admin@portal.com` / `admin123` |
| Demo logins | `student1@portal.com`, `company1@portal.com`, `supervisor1@portal.com` — password `pass123` |

**Commands to remember**

```
python app.py                  start the application
python seed_demo.py            load demonstration data
python -m pytest tests/ -v     run all test cases
mysql -u root -p < database.sql   rebuild the database
```
