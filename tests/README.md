# Test Cases

Automated tests for the Internship Portal Management System. Each test
corresponds to a numbered test case in Table 5.2 of the project report.

## Safety

The tests run against a **separate database** called `internship_db_test`,
which is created and rebuilt automatically before every test. The real
`internship_db` database and its data are never touched.

## How to run

Install pytest once:

```
pip install pytest
```

Run every test case:

```
python -m pytest tests/ -v
```

Run one file (for example only the login tests):

```
python -m pytest tests/test_01_authentication.py -v
```

Run one single test case:

```
python -m pytest tests/test_01_authentication.py::test_tc01_student_registration -v
```

If your MySQL password is not `password`, set it once before running:

```
set TEST_DB_PASS=your_password        (Windows)
export TEST_DB_PASS=your_password     (Linux / macOS)
```

## What each file covers

| File | Test cases | Covers |
|------|-----------|--------|
| `test_01_authentication.py` | TC-01 … TC-05, TC-16 | Student / company / supervisor registration, duplicate email, wrong password, registration without a document |
| `test_02_internship.py` | TC-06, TC-07, TC-17 | Posting an internship, editing and closing it, search by keyword and skill |
| `test_03_application.py` | TC-08 … TC-11 | Applying with a cover letter, duplicate application, withdrawal, selection and rejection |
| `test_04_progress_log.py` | TC-12, TC-13 | Weekly log submission, supervisor feedback and marks |
| `test_05_access_control.py` | TC-14 | Role based access control and record ownership |
| `test_06_notifications.py` | TC-18 … TC-20 | Notifications for applications, decisions, logs and feedback |
| `test_07_admin.py` | TC-15, TC-21 … TC-23 | Cascade deletion, audit log, user search and pagination, CSV exports |
| `test_08_api.py` | TC-24 | JSON REST API endpoints |
| `test_09_dashboard.py` | extra | Landing page counts and role specific dashboards |

## Structure

`conftest.py` contains the shared setup: it builds the test database from
`database.sql` (so the schema is always the same as the real system) and
provides helper functions used by the tests, such as `register_student()`,
`login()` and `post_internship()`.
