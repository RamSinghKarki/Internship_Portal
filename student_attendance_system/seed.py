"""Demo data seeder.

Creates roles, an administrator, departments, semesters, sections, subjects,
teachers, students, assignments, a weekly routine and ~6 weeks of randomized
attendance so every dashboard, report and chart has data.

Usage:
    python seed.py            (or: flask --app run seed)

Default credentials after seeding:
    admin      admin / admin123
    teacher    emp-001 / teacher123   (any teacher: emp-00X)
    student    reg-2025-0001 / student123
"""
import random
from datetime import date, time, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Role, User, Department, Semester, Section, Subject, Teacher, Student,
    TeacherSubjectAssignment, Schedule, AttendanceSession, AttendanceRecord,
    Notification, Setting,
)
from app.models.schedule import DAYS_OF_WEEK

random.seed(42)

FIRST_NAMES = [
    "Aarav", "Anisha", "Bibek", "Bina", "Dipesh", "Gita", "Hari", "Isha",
    "Kiran", "Laxmi", "Manish", "Nabin", "Nisha", "Prakash", "Pooja", "Rajan",
    "Rita", "Sanjay", "Sita", "Sujan", "Sunita", "Umesh", "Anil", "Mina",
    "Ramesh", "Sarita", "Bikash", "Kabita", "Dinesh", "Muna",
]
LAST_NAMES = [
    "Karki", "Shrestha", "Gurung", "Tamang", "Rai", "Limbu", "Magar",
    "Thapa", "Adhikari", "Poudel", "Sharma", "Koirala", "Bista", "KC",
]


def _name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def run():
    db.drop_all()
    db.create_all()

    # ---------------------------------------------------------------- roles
    roles = {name: Role(name=name) for name in ("admin", "teacher", "student")}
    db.session.add_all(roles.values())

    # ---------------------------------------------------------------- admin
    admin = User(username="admin", email="admin@college.edu", role=roles["admin"])
    admin.set_password("admin123")
    db.session.add(admin)

    # ------------------------------------------------------------- settings
    for key, value in Setting.DEFAULTS.items():
        db.session.add(Setting(key=key, value=value))

    # ---------------------------------------------------------- departments
    dept_specs = [
        ("Computer Science & Engineering", "CSE", "Prof. Ramhari Adhikari"),
        ("Electronics & Communication", "ECE", "Prof. Sabina Shrestha"),
        ("Business Administration", "BBA", "Prof. Kamal Poudel"),
        ("Civil Engineering", "CIV", "Prof. Nirmala Thapa"),
    ]
    departments = []
    for name, code, hod in dept_specs:
        d = Department(name=name, code=code, head_of_department=hod,
                       description=f"Department of {name}.")
        departments.append(d)
        db.session.add(d)

    # ------------------------------------------------------------ semesters
    sem1 = Semester(name="Semester 1", academic_year="2025-2026", status="active")
    sem3 = Semester(name="Semester 3", academic_year="2025-2026", status="active")
    db.session.add_all([sem1, sem3])
    db.session.flush()

    # ------------------------------------------------------------- sections
    sections = []
    for sem in (sem1, sem3):
        for name in ("A", "B"):
            s = Section(name=name, semester_id=sem.id, capacity=48)
            sections.append(s)
            db.session.add(s)
    db.session.flush()

    # -------------------------------------------------------------- subjects
    subject_specs = [
        # (code, name, credits, dept_index, semester)
        ("CS101", "Programming Fundamentals", 4, 0, sem1),
        ("CS102", "Digital Logic", 3, 0, sem1),
        ("MA101", "Engineering Mathematics I", 3, 0, sem1),
        ("EN101", "Communication English", 2, 0, sem1),
        ("CS301", "Data Structures & Algorithms", 4, 0, sem3),
        ("CS302", "Database Management Systems", 3, 0, sem3),
        ("CS303", "Operating Systems", 3, 0, sem3),
        ("EC301", "Microprocessors", 3, 1, sem3),
    ]
    subjects = []
    for code, name, credits, di, sem in subject_specs:
        s = Subject(code=code, name=name, credit_hours=credits,
                    department_id=departments[di].id, semester_id=sem.id)
        subjects.append(s)
        db.session.add(s)

    # -------------------------------------------------------------- teachers
    teacher_specs = [
        ("EMP-001", "Suresh Bhattarai", "Male", "Ph.D. Computer Science", "Professor", 0),
        ("EMP-002", "Anita Maharjan", "Female", "M.Sc. Computer Science", "Assistant Professor", 0),
        ("EMP-003", "Deepak Khadka", "Male", "M.Tech Software Engineering", "Lecturer", 0),
        ("EMP-004", "Sabitri Ghimire", "Female", "M.Sc. Electronics", "Assistant Professor", 1),
        ("EMP-005", "Mohan Basnet", "Male", "MBA", "Lecturer", 2),
        ("EMP-006", "Pratima Dahal", "Female", "M.Sc. Mathematics", "Lecturer", 0),
        ("EMP-007", "Keshav Oli", "Male", "M.A. English", "Lecturer", 0),
        ("EMP-008", "Rachana Joshi", "Female", "M.E. Civil", "Assistant Professor", 3),
    ]
    teachers = []
    for emp_id, name, gender, qual, desig, di in teacher_specs:
        t = Teacher(
            employee_id=emp_id, full_name=name, gender=gender,
            qualification=qual, designation=desig,
            department_id=departments[di].id,
            email=f"{emp_id.lower().replace('-', '')}@college.edu",
            phone=f"98{random.randint(10000000, 99999999)}",
            address="Kathmandu, Nepal",
            joining_date=date(2020 + random.randint(0, 4), random.randint(1, 12), 1),
            employment_status="active",
        )
        user = User(username=emp_id.lower(), email=t.email, role=roles["teacher"])
        user.set_password("teacher123")
        t.user = user
        teachers.append(t)
        db.session.add_all([t, user])
    db.session.flush()

    # -------------------------------------------------------------- students
    students_by_section = {}
    counter = 1
    for section in sections:
        bucket = []
        for _ in range(random.randint(18, 24)):
            reg = f"REG-2025-{counter:04d}"
            st = Student(
                roll_number=f"{section.semester.name[-1]}{section.name}-{counter:03d}",
                registration_number=reg,
                full_name=_name(),
                gender=random.choice(["Male", "Female"]),
                date_of_birth=date(2004 + random.randint(0, 3),
                                   random.randint(1, 12), random.randint(1, 28)),
                department_id=departments[0].id,
                semester_id=section.semester_id,
                section_id=section.id,
                email=f"{reg.lower()}@student.college.edu",
                phone=f"97{random.randint(10000000, 99999999)}",
                guardian_name=_name(),
                guardian_contact=f"98{random.randint(10000000, 99999999)}",
                address="Kathmandu, Nepal",
                admission_year="2025",
                status="active",
            )
            user = User(username=reg.lower(), email=st.email, role=roles["student"])
            user.set_password("student123")
            st.user = user
            bucket.append(st)
            db.session.add_all([st, user])
            counter += 1
        students_by_section[section.id] = bucket
    db.session.flush()

    # ---------------------------------------------- assignments + schedules
    # Map each subject to a teacher, per section of the subject's semester.
    subject_teacher = {
        "CS101": teachers[0], "CS102": teachers[1], "MA101": teachers[5],
        "EN101": teachers[6], "CS301": teachers[2], "CS302": teachers[1],
        "CS303": teachers[0], "EC301": teachers[3],
    }
    assignments = []
    for subject in subjects:
        for section in sections:
            if section.semester_id != subject.semester_id:
                continue
            a = TeacherSubjectAssignment(
                teacher_id=subject_teacher[subject.code].id,
                subject_id=subject.id,
                semester_id=subject.semester_id,
                section_id=section.id,
                academic_year="2025-2026",
            )
            assignments.append(a)
            db.session.add(a)
    db.session.flush()

    # Weekly routine: distribute each assignment over weekdays / periods.
    period_times = [
        (time(7, 0), time(8, 30)), (time(8, 45), time(10, 15)),
        (time(10, 30), time(12, 0)), (time(12, 30), time(14, 0)),
    ]
    teaching_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedules = []
    slot_taken = set()   # (day, period, section) and (day, period, teacher)
    day_idx = 0
    for a in assignments:
        placed = 0
        attempts = 0
        while placed < 2 and attempts < 60:  # two classes per week per subject
            attempts += 1
            day = teaching_days[day_idx % len(teaching_days)]
            period = (day_idx // len(teaching_days)) % len(period_times)
            day_idx += 1
            key_section = (day, period, a.section_id)
            key_teacher = (day, period, "t", a.teacher_id)
            if key_section in slot_taken or key_teacher in slot_taken:
                continue
            slot_taken.add(key_section)
            slot_taken.add(key_teacher)
            start, end = period_times[period]
            sched = Schedule(
                subject_id=a.subject_id, teacher_id=a.teacher_id,
                semester_id=a.semester_id, section_id=a.section_id,
                room_number=f"B-{random.randint(101, 320)}",
                day_of_week=day, start_time=start, end_time=end,
            )
            schedules.append(sched)
            db.session.add(sched)
            placed += 1
    db.session.flush()

    # ------------------------------------------------------------ attendance
    # Simulate the past 6 weeks of classes following the weekly routine.
    today = date.today()
    start_day = today - timedelta(days=42)
    # Give each student a personal attendance tendency for realistic spread.
    tendency = {}
    for bucket in students_by_section.values():
        for st in bucket:
            tendency[st.id] = random.uniform(0.55, 0.98)

    day_lookup = {}
    for sched in schedules:
        day_lookup.setdefault(sched.day_of_week, []).append(sched)

    current = start_day
    while current <= today:
        weekday_name = DAYS_OF_WEEK[(current.weekday() + 1) % 7]
        for sched in day_lookup.get(weekday_name, []):
            # skip today's later periods randomly so the "not taken" widget has data
            if current == today and random.random() < 0.5:
                continue
            session = AttendanceSession(
                schedule_id=sched.id, subject_id=sched.subject_id,
                section_id=sched.section_id, semester_id=sched.semester_id,
                teacher_id=sched.teacher_id, date=current,
            )
            db.session.add(session)
            for st in students_by_section[sched.section_id]:
                r = random.random()
                p = tendency[st.id]
                if r < p:
                    status = "Present"
                elif r < p + 0.05:
                    status = "Late"
                elif r < p + 0.08:
                    status = "Leave"
                else:
                    status = "Absent"
                session.records.append(AttendanceRecord(
                    student_id=st.id, status=status,
                    remarks="Medical leave" if status == "Leave" and random.random() < 0.5 else None,
                ))
        current += timedelta(days=1)

    # --------------------------------------------------------- notifications
    db.session.add_all([
        Notification(title="Welcome to the Attendance System",
                     message="Demo data has been loaded. Explore the dashboard, reports and analytics.",
                     category="info"),
        Notification(title="Low attendance alert",
                     message="Several students are below the 75% attendance threshold. Check the dashboard list.",
                     category="warning"),
    ])

    db.session.commit()

    print("Seed complete.")
    print("  Admin   : admin / admin123")
    print("  Teacher : emp-001 / teacher123 (emp-001 … emp-008)")
    print("  Student : reg-2025-0001 / student123")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run()
