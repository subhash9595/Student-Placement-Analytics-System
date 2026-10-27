"""CSV import with validation. One row per student; placement columns are optional."""
import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from extensions import db
from models import Placement, Student
from services.validation import validate_placement, validate_student

REQUIRED_COLUMNS = ["roll_no", "name", "department", "cgpa"]
KNOWN_COLUMNS = REQUIRED_COLUMNS + [
    "email", "backlogs", "aptitude_score", "skills", "certifications", "internships",
    "internship_details", "status", "company", "job_role", "package_lpa", "recruitment_year"]


class ImportFileError(Exception):
    """The file itself cannot be processed (wrong format, missing columns, ...)."""


def read_csv(fileobj) -> pd.DataFrame:
    try:
        df = pd.read_csv(fileobj, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except EmptyDataError:
        raise ImportFileError("The file is empty.")
    except (ParserError, UnicodeDecodeError) as exc:
        raise ImportFileError(f"Could not read the file as UTF-8 CSV: {exc}")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ImportFileError(
            f"Missing required column(s): {', '.join(missing)}. "
            f"Expected columns: {', '.join(KNOWN_COLUMNS)}.")
    if df.empty:
        raise ImportFileError("The file has a header but no data rows.")
    return df


def import_dataframe(df: pd.DataFrame) -> dict:
    existing = {r[0].lower() for r in db.session.query(Student.roll_no).all()}
    seen, errors, imported = set(), [], 0

    for idx, row in df.iterrows():
        line = idx + 2  # header is line 1
        raw = row.to_dict()
        if not any(str(v).strip() for v in raw.values()):
            continue  # blank line
        student, errs = validate_student(raw)
        placement, perrs = None, []
        if str(raw.get("status", "")).strip():
            placement, perrs = validate_placement(raw)
        row_errors = [(f, m) for f, m in errs + perrs]

        key = student["roll_no"].lower()
        if key and key in seen:
            row_errors.append(("roll_no", f"duplicate of an earlier row in this file ({student['roll_no']})"))
        elif key and key in existing:
            row_errors.append(("roll_no", f"{student['roll_no']} already exists in the database"))

        if row_errors:
            errors.extend({"row": line, "field": f, "message": m} for f, m in row_errors)
            continue
        seen.add(key)
        obj = Student(**student)
        if placement:
            obj.placements.append(Placement(**placement))
        db.session.add(obj)
        imported += 1

    try:
        db.session.commit()
    except Exception as exc:  # database-level failure: nothing is saved
        db.session.rollback()
        raise ImportFileError(f"Database error while saving: {exc}")

    skipped_rows = len({e["row"] for e in errors})
    return {"imported": imported, "skipped": skipped_rows, "errors": errors}
