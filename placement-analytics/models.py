from datetime import datetime

from extensions import db

from constants import STATUSES  # noqa: F401  (re-exported)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    department = db.Column(db.String(50), nullable=False, index=True)
    cgpa = db.Column(db.Float, nullable=False)
    backlogs = db.Column(db.Integer, nullable=False, default=0)
    aptitude_score = db.Column(db.Float)
    skills = db.Column(db.Text, default="")
    certifications = db.Column(db.Text, default="")
    internships = db.Column(db.Integer, nullable=False, default=0)
    internship_details = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    placements = db.relationship(
        "Placement", backref="student", cascade="all, delete-orphan", lazy=True
    )


class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = db.Column(db.String(20), nullable=False, default="eligible", index=True)
    company = db.Column(db.String(120), index=True)
    job_role = db.Column(db.String(120))
    package_lpa = db.Column(db.Float)  # package in lakhs per annum
    recruitment_year = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
