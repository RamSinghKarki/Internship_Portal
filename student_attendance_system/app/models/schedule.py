from app.extensions import db

DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


class TeacherSubjectAssignment(db.Model):
    """Which teacher teaches which subject to which section."""
    __tablename__ = "teacher_subject_assignments"
    __table_args__ = (
        # one teacher per subject/section/semester/year unless the row is edited
        db.UniqueConstraint(
            "subject_id", "section_id", "semester_id", "academic_year",
            name="uq_assignment_subject_section",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False,
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    academic_year = db.Column(db.String(20), nullable=False)

    teacher = db.relationship("Teacher", back_populates="assignments")
    subject = db.relationship("Subject", back_populates="assignments")
    semester = db.relationship("Semester")
    section = db.relationship("Section")

    def __repr__(self):
        return f"<Assignment t={self.teacher_id} s={self.subject_id}>"


class Schedule(db.Model):
    """A weekly class period (routine entry)."""
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False,
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    room_number = db.Column(db.String(30))
    day_of_week = db.Column(db.String(10), nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    subject = db.relationship("Subject")
    teacher = db.relationship("Teacher", back_populates="schedules")
    semester = db.relationship("Semester")
    section = db.relationship("Section")
    sessions = db.relationship("AttendanceSession", back_populates="schedule", lazy="dynamic")

    @property
    def time_label(self):
        return f"{self.start_time.strftime('%H:%M')} – {self.end_time.strftime('%H:%M')}"

    def __repr__(self):
        return f"<Schedule {self.day_of_week} {self.time_label}>"
