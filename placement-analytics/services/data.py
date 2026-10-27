"""Loads data from MySQL into pandas and builds the student-level 'master' frame."""
import pandas as pd
from sqlalchemy import text

from extensions import db
from services.utils import parse_list

RANK = {"selected": 3, "shortlisted": 2, "eligible": 1, "unplaced": 0}

STUDENT_SQL = """SELECT id, roll_no, name, email, department, cgpa, backlogs, aptitude_score,
                        skills, certifications, internships, internship_details FROM students"""
PLACEMENT_SQL = """SELECT p.id, p.student_id, s.roll_no, s.name, s.department, s.cgpa,
                          p.status, p.company, p.job_role, p.package_lpa, p.recruitment_year
                   FROM placements p JOIN students s ON s.id = p.student_id"""


def build_master(students: pd.DataFrame, placements: pd.DataFrame) -> pd.DataFrame:
    """One row per student, enriched with their best placement outcome.

    Best outcome = 'selected' (highest package) > shortlisted > eligible > unplaced.
    A student with no placement record is treated as 'unplaced'.
    """
    m = students.copy()
    for col in ("cgpa", "backlogs", "aptitude_score", "internships"):
        m[col] = pd.to_numeric(m[col], errors="coerce")
    m["skill_list"] = m["skills"].map(parse_list)
    m["num_skills"] = m["skill_list"].map(len)
    m["num_certs"] = m["certifications"].map(lambda s: len(parse_list(s)))

    cols = ["student_id", "status", "company", "job_role", "package_lpa", "recruitment_year"]
    if placements.empty:
        best = pd.DataFrame(columns=cols)
    else:
        p = placements.copy()
        p["package_lpa"] = pd.to_numeric(p["package_lpa"], errors="coerce")
        p["_rank"] = p["status"].map(RANK).fillna(0)
        best = (p.sort_values(["_rank", "package_lpa"], ascending=[False, False])
                 .drop_duplicates("student_id")[cols])
    m = m.merge(best, how="left", left_on="id", right_on="student_id").drop(
        columns=["student_id"], errors="ignore")
    m["status"] = m["status"].fillna("unplaced")
    m["placed"] = m["status"].eq("selected")
    return m


def get_frames():
    """Return (students, placements, master) DataFrames from the database."""
    with db.engine.connect() as conn:
        students = pd.read_sql(text(STUDENT_SQL), conn)
        placements = pd.read_sql(text(PLACEMENT_SQL), conn)
    placements["package_lpa"] = pd.to_numeric(placements["package_lpa"], errors="coerce")
    return students, placements, build_master(students, placements)


def apply_filters(m: pd.DataFrame, args) -> pd.DataFrame:
    """Filter the master frame using request args (department, cgpa, skill, status, ...)."""
    def num(key):
        try:
            return float(args.get(key, ""))
        except (TypeError, ValueError):
            return None

    f = m
    if args.get("q"):
        q = args["q"].strip().lower()
        f = f[f["name"].str.lower().str.contains(q, regex=False, na=False)
              | f["roll_no"].str.lower().str.contains(q, regex=False, na=False)]
    if args.get("department"):
        f = f[f["department"] == args["department"]]
    if args.get("status"):
        f = f[f["status"] == args["status"]]
    if args.get("company"):
        f = f[f["company"] == args["company"]]
    if args.get("skill"):
        wanted = parse_list(args["skill"])
        f = f[f["skill_list"].map(lambda sl: all(w in sl for w in wanted))]
    for key, col, op in (("min_cgpa", "cgpa", ">="), ("max_cgpa", "cgpa", "<="),
                         ("min_salary", "package_lpa", ">="), ("max_salary", "package_lpa", "<=")):
        value = num(key)
        if value is not None:
            f = f[f[col] >= value] if op == ">=" else f[f[col] <= value]
    return f
