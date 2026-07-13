from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    head_of_department = db.Column(db.String(120))
    description = db.Column(db.Text)

    teachers = db.relationship("Teacher", back_populates="department", lazy="dynamic")
    students = db.relationship("Student", back_populates="department", lazy="dynamic")
    subjects = db.relationship("Subject", back_populates="department", lazy="dynamic")

    def __repr__(self):
        return f"<Department {self.code}>"


class Semester(db.Model):
    __tablename__ = "semesters"
    __table_args__ = (
        db.UniqueConstraint("name", "academic_year", name="uq_semester_name_year"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)          # e.g. "Semester 1"
    academic_year = db.Column(db.String(20), nullable=False)  # e.g. "2025-2026"
    status = db.Column(db.String(20), default="active", nullable=False)  # active / inactive

    sections = db.relationship("Section", back_populates="semester", lazy="dynamic")
    subjects = db.relationship("Subject", back_populates="semester", lazy="dynamic")
    students = db.relationship("Student", back_populates="semester", lazy="dynamic")

    @property
    def label(self):
        return f"{self.name} ({self.academic_year})"

    def __repr__(self):
        return f"<Semester {self.label}>"


class Section(db.Model):
    __tablename__ = "sections"
    __table_args__ = (
        db.UniqueConstraint("name", "semester_id", name="uq_section_name_semester"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)  # e.g. "A"
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    capacity = db.Column(db.Integer, default=60, nullable=False)

    semester = db.relationship("Semester", back_populates="sections")
    students = db.relationship("Student", back_populates="section", lazy="dynamic")

    @property
    def label(self):
        return f"{self.name} — {self.semester.label}" if self.semester else self.name

    def __repr__(self):
        return f"<Section {self.name}>"


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    credit_hours = db.Column(db.Integer, default=3, nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    department = db.relationship("Department", back_populates="subjects")
    semester = db.relationship("Semester", back_populates="subjects")
    assignments = db.relationship(
        "TeacherSubjectAssignment", back_populates="subject", lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def label(self):
        return f"{self.code} — {self.name}"

    def __repr__(self):
        return f"<Subject {self.code}>"
