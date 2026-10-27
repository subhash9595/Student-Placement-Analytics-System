"""Unit tests for the pure analytics/validation logic (no database needed)."""
import pandas as pd
import pytest

from config import Config
from services import analytics
from services.data import apply_filters, build_master
from services.validation import validate_placement, validate_student


@pytest.fixture()
def frames():
    students = pd.DataFrame([
        dict(id=1, roll_no="A1", name="Asha", email="", department="CSE", cgpa=8.5, backlogs=0,
             aptitude_score=80, skills="Python, SQL, Java, Git", certifications="AWS", internships=1, internship_details=""),
        dict(id=2, roll_no="A2", name="Ben", email="", department="CSE", cgpa=5.9, backlogs=2,
             aptitude_score=40, skills="C", certifications="", internships=0, internship_details=""),
        dict(id=3, roll_no="A3", name="Chitra", email="", department="ECE", cgpa=7.2, backlogs=0,
             aptitude_score=65, skills="Python, VLSI", certifications="", internships=0, internship_details=""),
    ])
    placements = pd.DataFrame([
        dict(id=1, student_id=1, roll_no="A1", name="Asha", department="CSE", cgpa=8.5, status="selected",
             company="TCS", job_role="Engineer", package_lpa=7.0, recruitment_year=2024),
        dict(id=2, student_id=3, roll_no="A3", name="Chitra", department="ECE", cgpa=7.2, status="shortlisted",
             company="Bosch", job_role=None, package_lpa=None, recruitment_year=2024),
    ])
    return students, placements, build_master(students, placements)


def test_master_status(frames):
    _, _, m = frames
    assert m.set_index("id")["status"].to_dict() == {1: "selected", 2: "unplaced", 3: "shortlisted"}


def test_summary(frames):
    _, _, m = frames
    s = analytics.summary(m)
    assert (s["total"], s["placed"], s["unplaced"]) == (3, 1, 2)
    assert s["placement_pct"] == 33.3 and s["avg_package"] == 7.0


def test_department_and_company(frames):
    _, p, m = frames
    dept = {d["department"]: d for d in analytics.department_stats(m)}
    assert dept["CSE"]["placed"] == 1 and dept["ECE"]["placed"] == 0
    assert analytics.top_companies(p)[0]["company"] == "TCS"


def test_empty_data_does_not_crash():
    empty = build_master(pd.DataFrame(columns=["id", "roll_no", "name", "email", "department", "cgpa", "backlogs",
                                               "aptitude_score", "skills", "certifications", "internships",
                                               "internship_details"]), pd.DataFrame())
    assert analytics.summary(empty)["placement_pct"] == 0.0
    assert analytics.department_stats(empty) == [] and analytics.cgpa_ranges(empty)


def test_preparation_flags_weak_student(frames):
    _, _, m = frames
    rows = analytics.preparation_insights(m, Config.PREP_RULES)
    ben = next(r for r in rows if r["name"] == "Ben")
    assert ben["need"] == "High" and any("backlog" in g for g in ben["gaps"])
    assert all(r["name"] != "Asha" for r in rows)  # placed students are not flagged


def test_filters(frames):
    _, _, m = frames
    assert list(apply_filters(m, {"skill": "python"})["name"]) == ["Asha", "Chitra"]
    assert list(apply_filters(m, {"min_cgpa": "8"})["name"]) == ["Asha"]
    assert list(apply_filters(m, {"status": "unplaced"})["name"]) == ["Ben"]


def test_validate_student_errors_and_normalisation():
    data, errors = validate_student({"roll_no": "x1", "name": "N", "department": "cse", "cgpa": "11",
                                     "email": "bad", "skills": "python;sql"})
    fields = {f for f, _ in errors}
    assert {"cgpa", "email"} <= fields
    assert data["department"] == "CSE" and data["skills"] == "Python, SQL"


def test_validate_placement_selected_needs_package():
    _, errors = validate_placement({"status": "selected", "company": "TCS"})
    assert any(f == "package_lpa" for f, _ in errors)
    _, errors = validate_placement({"status": "selected", "company": "TCS", "package_lpa": "5", "recruitment_year": "2024"})
    assert not errors
