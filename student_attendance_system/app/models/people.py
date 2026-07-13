from app.extensions import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    photo = db.Column(db.String(255))
    full_name = db.Column(db.String(120), nullable=False, index=True)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    qualification = db.Column(db.String(150))
    designation = db.Column(db.String(100))
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"), index=True,
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    joining_date = db.Column(db.Date)
    employment_status = db.Column(db.String(20), default="active", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), unique=True)

    department = db.relationship("Department", back_populates="teachers")
    user = db.relationship("User", back_populates="teacher")
    assignments = db.relationship(
        "TeacherSubjectAssignment", back_populates="teacher", lazy="dynamic",
        cascade="all, delete-orphan",
    )
    schedules = db.relationship("Schedule", back_populates="teacher", lazy="dynamic")
    sessions = db.relationship("AttendanceSession", back_populates="teacher", lazy="dynamic")

    def __repr__(self):
        return f"<Teacher {self.employee_id}>"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(30), nullable=False, index=True)
    registration_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    photo = db.Column(db.String(255))
    full_name = db.Column(db.String(120), nullable=False, index=True)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"), index=True,
    )
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="SET NULL"), index=True,
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey("sections.id", ondelete="SET NULL"), index=True,
    )
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    guardian_name = db.Column(db.String(120))
    guardian_contact = db.Column(db.String(20))
    address = db.Column(db.String(255))
    admission_year = db.Column(db.String(10))
    status = db.Column(db.String(20), default="active", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), unique=True)

    department = db.relationship("Department", back_populates="students")
    semester = db.relationship("Semester", back_populates="students")
    section = db.relationship("Section", back_populates="students")
    user = db.relationship("User", back_populates="student")
    attendance_records = db.relationship(
        "AttendanceRecord", back_populates="student", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Student {self.roll_number}>"
