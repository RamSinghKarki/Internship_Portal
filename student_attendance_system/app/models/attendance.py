from datetime import datetime

from app.extensions import db

ATTENDANCE_STATUSES = ["Present", "Absent", "Late", "Leave"]
# Late counts as attended for percentage purposes.
PRESENT_LIKE = ("Present", "Late")


class AttendanceSession(db.Model):
    """One attendance-taking event: a subject taught to a section on a date/period."""
    __tablename__ = "attendance"
    __table_args__ = (
        # prevent duplicate attendance for the same subject/section/date/period
        db.UniqueConstraint(
            "subject_id", "section_id", "date", "schedule_id",
            name="uq_attendance_session",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(
        db.Integer, db.ForeignKey("schedules.id", ondelete="SET NULL"), index=True,
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    semester_id = db.Column(
        db.Integer, db.ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False,
    )
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teachers.id", ondelete="SET NULL"), index=True,
    )
    date = db.Column(db.Date, nullable=False, index=True)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule = db.relationship("Schedule", back_populates="sessions")
    subject = db.relationship("Subject")
    section = db.relationship("Section")
    semester = db.relationship("Semester")
    teacher = db.relationship("Teacher", back_populates="sessions")
    records = db.relationship(
        "AttendanceRecord", back_populates="session",
        cascade="all, delete-orphan", lazy="selectin",
    )

    # ------------------------------------------------------------------
    def counts(self):
        c = {s: 0 for s in ATTENDANCE_STATUSES}
        for r in self.records:
            c[r.status] = c.get(r.status, 0) + 1
        return c

    @property
    def present_count(self):
        return sum(1 for r in self.records if r.status in PRESENT_LIKE)

    @property
    def total_count(self):
        return len(self.records)

    def __repr__(self):
        return f"<AttendanceSession {self.date} subject={self.subject_id}>"


class AttendanceRecord(db.Model):
    """Per-student mark inside an attendance session."""
    __tablename__ = "attendance_details"
    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="uq_record_session_student"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("attendance.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    status = db.Column(db.String(10), nullable=False, default="Present")
    remarks = db.Column(db.String(255))

    session = db.relationship("AttendanceSession", back_populates="records")
    student = db.relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<AttendanceRecord student={self.student_id} {self.status}>"
