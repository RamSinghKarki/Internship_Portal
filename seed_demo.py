# ============================================================
# Demo data generator for the Internship Portal
#
# Fills the database with realistic sample data so that the
# dashboards, charts and tables can be demonstrated properly.
#
#   python seed_demo.py
#
# WARNING: this clears the existing data first.
# Every demo account uses the password:  pass123
# The administrator stays as:            admin@portal.com / admin123
# ============================================================

import random
from datetime import datetime, timedelta

from app import app
from models import (db, Role, User, Student, Company, Supervisor, Internship,
                    Application, ProgressLog, Notification, AuditLog)

random.seed(7)          # same data every time the script is run

NOW = datetime.now()

STUDENTS = [
    ('Aashish Thapa', 'CE-201', 'Computer Engineering', 6, 'Python, MySQL, Flask'),
    ('Sneha Adhikari', 'CE-202', 'Computer Engineering', 6, 'Java, Spring, MySQL'),
    ('Bishal Karki', 'CE-203', 'Computer Engineering', 7, 'Python, Django, REST API'),
    ('Prakriti Sharma', 'SE-104', 'Software Engineering', 5, 'JavaScript, React, CSS'),
    ('Nabin Bhandari', 'CE-204', 'Computer Engineering', 7, 'C++, Data Structures'),
    ('Anjali Rai', 'IT-301', 'Information Technology', 6, 'Python, Machine Learning'),
    ('Sujan Gurung', 'CE-205', 'Computer Engineering', 8, 'PHP, Laravel, MySQL'),
    ('Manisha Poudel', 'SE-105', 'Software Engineering', 6, 'Figma, Photoshop, CSS'),
    ('Rohit Shrestha', 'CE-206', 'Computer Engineering', 5, 'Python, Flask, Git'),
    ('Sabina Magar', 'IT-302', 'Information Technology', 7, 'Networking, Linux'),
    ('Deepak Joshi', 'CE-207', 'Computer Engineering', 6, 'Java, Android, Kotlin'),
    ('Pooja Bhatta', 'SE-106', 'Software Engineering', 8, 'Testing, Selenium, Python'),
    ('Kiran Tamang', 'CE-208', 'Computer Engineering', 6, 'Python, MySQL, Excel'),
    ('Sarita Chaudhary', 'IT-303', 'Information Technology', 5, 'HTML, CSS, JavaScript'),
    ('Milan Bista', 'CE-209', 'Computer Engineering', 7, 'Node.js, MongoDB, React'),
    ('Rekha Khadka', 'SE-107', 'Software Engineering', 6, 'Python, Data Analysis'),
    ('Suman Lama', 'CE-210', 'Computer Engineering', 8, 'DevOps, Docker, Linux'),
    ('Nisha Basnet', 'IT-304', 'Information Technology', 6, 'Cyber Security, Python'),
]

COMPANIES = [
    ('Himalayan Tech Solutions', 'Software Development', 'Kathmandu',
     'A software house building web and mobile applications for local and international clients.'),
    ('Everest Data Systems', 'Data and Analytics', 'Lalitpur',
     'Data engineering and business intelligence services for banks and insurance companies.'),
    ('Kathmandu Web Works', 'Web Development', 'Kathmandu',
     'Web design and development studio working with startups and NGOs.'),
    ('Nepal Cloud Services', 'Cloud and Infrastructure', 'Bhaktapur',
     'Cloud hosting, DevOps consulting and infrastructure management.'),
    ('Sagarmatha Softworks', 'Enterprise Software', 'Pokhara',
     'Enterprise resource planning and accounting software for Nepali businesses.'),
]

SUPERVISORS = [
    ('Ramesh Adhikari', 'Senior Software Engineer', 'Development', 0),
    ('Sunita Maharjan', 'Team Lead', 'Engineering', 0),
    ('Bikash Rana', 'Data Engineering Manager', 'Data', 1),
    ('Anita Shrestha', 'Project Manager', 'Delivery', 2),
    ('Deepak Sapkota', 'DevOps Lead', 'Infrastructure', 3),
    ('Kabita Neupane', 'Principal Engineer', 'Product', 4),
]

INTERNSHIPS = [
    (0, 'Python Backend Intern', 'Work with our backend team on Flask APIs, database design and integration with the front end.', 'Python, Flask, MySQL', 12, 'Rs. 15000/month', 3),
    (0, 'Frontend Developer Intern', 'Build responsive user interfaces with modern HTML, CSS and JavaScript for client projects.', 'JavaScript, React, CSS', 10, 'Rs. 12000/month', 2),
    (1, 'Data Analyst Intern', 'Assist the analytics team in cleaning datasets, writing SQL queries and preparing reports.', 'Python, MySQL, Data Analysis', 12, 'Rs. 14000/month', 2),
    (1, 'Machine Learning Intern', 'Support model development and evaluation for forecasting projects.', 'Python, Machine Learning', 16, 'Rs. 18000/month', 1),
    (2, 'Web Development Intern', 'Develop and maintain websites for our clients using PHP and MySQL.', 'PHP, MySQL, CSS', 8, 'Rs. 10000/month', 4),
    (2, 'UI/UX Design Intern', 'Design interfaces and prototypes, and prepare assets for the development team.', 'Figma, Photoshop, CSS', 8, 'Rs. 10000/month', 2),
    (3, 'DevOps Intern', 'Learn deployment pipelines, containers and server monitoring with our infrastructure team.', 'Linux, Docker, Git', 12, 'Rs. 16000/month', 2),
    (3, 'Network Support Intern', 'Assist in network configuration, monitoring and technical support tasks.', 'Networking, Linux', 10, 'Rs. 11000/month', 2),
    (4, 'Java Developer Intern', 'Contribute to our enterprise accounting product built with Java and Spring.', 'Java, Spring, MySQL', 16, 'Rs. 17000/month', 3),
    (4, 'Quality Assurance Intern', 'Write and execute test cases, and report defects for our software products.', 'Testing, Selenium, Python', 10, 'Rs. 12000/month', 2),
    (0, 'Mobile App Intern', 'Build Android features for our client applications.', 'Java, Android, Kotlin', 12, 'Rs. 15000/month', 2),
    (1, 'Business Intelligence Intern', 'Prepare dashboards and reports for banking clients.', 'MySQL, Excel, Python', 8, 'Rs. 13000/month', 1),
]

WORK_DONE = [
    'Set up the development environment and studied the existing codebase.',
    'Implemented the user registration and login pages with input validation.',
    'Designed the database tables and wrote the required queries.',
    'Built the listing page and added search and filter options.',
    'Fixed reported defects and improved error handling across the module.',
    'Wrote unit tests for the module and documented the API endpoints.',
    'Integrated the front end with the backend API and handled edge cases.',
    'Prepared the weekly report and presented progress to the team.',
]

FEEDBACK = [
    ('Good work this week. The code is clean and well organised.', 9),
    ('Satisfactory progress. Try to add more comments to your code.', 8),
    ('Excellent effort, especially on the database design.', 10),
    ('Work completed as planned. Improve the commit messages.', 8),
    ('Very good understanding shown during the review session.', 9),
    ('Acceptable, but the testing could be more thorough.', 7),
]


# a fixed pattern so roughly half are pending, a third selected, the rest rejected
STATUS_CYCLE = ['applied', 'selected', 'applied', 'rejected',
                'applied', 'selected', 'applied', 'rejected',
                'selected', 'applied']


def make_user(role_name, name, email, created_at):
    role = Role.query.filter_by(role_name=role_name).first()
    user = User(role_id=role.id, name=name, email=email, created_at=created_at)
    user.set_password('pass123')
    return user


def seed():
    print('Clearing existing data...')
    for model in (AuditLog, Notification, ProgressLog, Application,
                  Internship, Supervisor, Student, Company):
        model.query.delete()
    User.query.filter(User.email != 'admin@portal.com').delete()
    db.session.commit()

    admin = User.query.filter_by(email='admin@portal.com').first()

    # ---------------- companies ----------------
    print('Creating companies...')
    company_rows = []
    for i, (name, industry, location, desc) in enumerate(COMPANIES):
        created = NOW - timedelta(days=120 - i * 7)
        user = make_user('company', name, f'company{i + 1}@portal.com', created)
        company = Company(user=user, industry=industry, location=location,
                          description=desc)
        db.session.add(company)
        company_rows.append(company)
    db.session.commit()

    # ---------------- supervisors ----------------
    print('Creating supervisors...')
    for i, (name, designation, dept, company_index) in enumerate(SUPERVISORS):
        created = NOW - timedelta(days=100 - i * 5)
        user = make_user('supervisor', name, f'supervisor{i + 1}@portal.com', created)
        db.session.add(Supervisor(user=user, company_id=company_rows[company_index].id,
                                  designation=designation, department=dept))
    db.session.commit()

    # ---------------- students ----------------
    print('Creating students...')
    student_rows = []
    for i, (name, roll, dept, sem, skills) in enumerate(STUDENTS):
        # spread joining dates over the last three months, several this month
        created = NOW - timedelta(days=random.randint(1, 90))
        user = make_user('student', name, f'student{i + 1}@portal.com', created)
        student = Student(user=user, roll_number=roll, department=dept,
                          semester=sem, skills=skills,
                          document_url='uploads/sample_document.pdf')
        db.session.add(student)
        student_rows.append(student)
    db.session.commit()

    # ---------------- internships ----------------
    print('Creating internships...')
    internship_rows = []
    for i, (company_index, title, desc, skills, weeks, stipend, vac) in enumerate(INTERNSHIPS):
        posted = NOW - timedelta(days=random.randint(2, 75))
        internship = Internship(company_id=company_rows[company_index].id,
                                title=title, description=desc,
                                required_skills=skills, duration_weeks=weeks,
                                stipend=stipend, vacancies=vac,
                                status='closed' if i in (5, 11) else 'open',
                                posted_date=posted)
        db.session.add(internship)
        internship_rows.append(internship)
    db.session.commit()

    # ---------------- applications ----------------
    print('Creating applications...')
    applications = []
    for student in student_rows:
        for internship in random.sample(internship_rows, random.randint(1, 3)):
            if any(a.student_id == student.id and a.internship_id == internship.id
                   for a in applications):
                continue
            # cycle through the statuses so the demo shows a realistic mix
            status = STATUS_CYCLE[len(applications) % len(STATUS_CYCLE)]
            applied = internship.posted_date + timedelta(days=random.randint(1, 20))
            application = Application(
                student_id=student.id, internship_id=internship.id,
                cover_letter=(
                    f'Dear Sir/Madam,\n\n'
                    f'I am {student.user.name}, a semester {student.semester} student of '
                    f'{student.department}. I am very interested in the {internship.title} '
                    f'position at your organisation.\n\n'
                    f'My skills include {student.skills}, which match the requirements of '
                    f'this internship. I am eager to apply my knowledge in a professional '
                    f'environment and learn from your team.\n\n'
                    f'Thank you for considering my application.\n\n'
                    f'Sincerely,\n{student.user.name}'),
                status=status,
                applied_date=min(applied, NOW - timedelta(days=1)))
            db.session.add(application)
            applications.append(application)
    db.session.commit()

    # ---------------- progress logs ----------------
    print('Creating progress logs...')
    selected = [a for a in applications if a.status == 'selected']
    supervisors = Supervisor.query.all()
    for application in selected:
        company_supervisors = [s for s in supervisors
                               if s.company_id == application.internship.company_id]
        weeks = random.randint(2, 6)
        for week in range(1, weeks + 1):
            submitted = application.applied_date + timedelta(days=7 * week + 3)
            if submitted > NOW:
                break
            log = ProgressLog(application_id=application.id, week_number=week,
                              description=random.choice(WORK_DONE),
                              submitted_date=submitted)
            # most weeks are already evaluated, the newest one may still be pending
            if company_supervisors and week < weeks:
                text, marks = random.choice(FEEDBACK)
                log.feedback = text
                log.marks = marks
                log.supervisor_id = random.choice(company_supervisors).id
            db.session.add(log)
    db.session.commit()

    # ---------------- notifications ----------------
    print('Creating notifications...')
    for application in random.sample(applications, min(12, len(applications))):
        company_user_id = application.internship.company.user_id
        db.session.add(Notification(
            user_id=company_user_id,
            message=f'New application for "{application.internship.title}" '
                    f'from {application.student.user.name}',
            link=f'/applicants/{application.internship_id}',
            is_read=random.choice([True, False]),
            created_at=application.applied_date))
    for application in selected[:8]:
        db.session.add(Notification(
            user_id=application.student.user_id,
            message=f'Your application for "{application.internship.title}" '
                    f'was marked selected',
            link='/my_applications', is_read=random.choice([True, False]),
            created_at=application.applied_date + timedelta(days=3)))
    db.session.commit()

    # ---------------- audit log ----------------
    print('Creating audit entries...')
    entries = []
    for user in User.query.all():
        entries.append(AuditLog(user_id=user.id, action='register',
                                details=f'{user.role.role_name} {user.email}',
                                created_at=user.created_at))
        for _ in range(random.randint(1, 4)):
            entries.append(AuditLog(
                user_id=user.id, action='login', details=user.email,
                created_at=NOW - timedelta(days=random.randint(0, 30),
                                           hours=random.randint(0, 23))))
    for internship in internship_rows:
        entries.append(AuditLog(user_id=internship.company.user_id,
                                action='post_internship', details=internship.title,
                                created_at=internship.posted_date))
    for application in applications:
        entries.append(AuditLog(user_id=application.student.user_id, action='apply',
                                details=f'internship #{application.internship_id}',
                                created_at=application.applied_date))
        if application.status != 'applied':
            entries.append(AuditLog(
                user_id=application.internship.company.user_id,
                action='update_status',
                details=f'application #{application.id} -> {application.status}',
                created_at=application.applied_date + timedelta(days=3)))
    entries.append(AuditLog(user_id=None, action='login_failed',
                            details='student3@portal.com',
                            created_at=NOW - timedelta(days=2)))
    entries.append(AuditLog(user_id=admin.id, action='login',
                            details='admin@portal.com', created_at=NOW))
    for e in entries:
        db.session.add(e)
    db.session.commit()

    # ---------------- summary ----------------
    print('\nDemo data created:')
    print(f'  Students      : {Student.query.count()}')
    print(f'  Companies     : {Company.query.count()}')
    print(f'  Supervisors   : {Supervisor.query.count()}')
    print(f'  Internships   : {Internship.query.count()}')
    print(f'  Applications  : {Application.query.count()}'
          f'  (selected: {Application.query.filter_by(status="selected").count()},'
          f' rejected: {Application.query.filter_by(status="rejected").count()})')
    print(f'  Progress logs : {ProgressLog.query.count()}')
    print(f'  Notifications : {Notification.query.count()}')
    print(f'  Audit entries : {AuditLog.query.count()}')
    print('\nLogin accounts (password: pass123)')
    print('  Student    : student1@portal.com')
    print('  Company    : company1@portal.com')
    print('  Supervisor : supervisor1@portal.com')
    print('  Admin      : admin@portal.com  (password: admin123)')


if __name__ == '__main__':
    with app.app_context():
        seed()
