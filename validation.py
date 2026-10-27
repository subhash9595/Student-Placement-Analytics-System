"""Row/field validation shared by the web forms and the CSV importer."""
import math
import re
from datetime import date

from constants import STATUSES
from services.utils import normalize_list_text

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _number(raw, field, errors, integer=False, lo=None, hi=None, required=False):
    value = str(raw.get(field, "") or "").strip()
    if not value:
        if required:
            errors.append((field, "is required"))
        return None
    try:
        number = float(value)
    except ValueError:
        errors.append((field, f"'{value}' is not a number"))
        return None
    if math.isnan(number) or math.isinf(number):
        errors.append((field, f"'{value}' is not a valid number"))
        return None
    if integer and number != int(number):
        errors.append((field, f"'{value}' must be a whole number"))
        return None
    if (lo is not None and number < lo) or (hi is not None and number > hi):
        bounds = f"between {lo} and {hi}" if hi is not None and lo is not None else (
            f"at least {lo}" if lo is not None else f"at most {hi}")
        errors.append((field, f"must be {bounds} (got {value})"))
        return None
    return int(number) if integer else number


def _text(raw, field):
    return str(raw.get(field, "") or "").strip()


def validate_student(raw):
    """Return (clean_dict, errors) where errors is a list of (field, message)."""
    errors = []
    data = {
        "roll_no": _text(raw, "roll_no"),
        "name": _text(raw, "name"),
        "email": _text(raw, "email"),
        "department": _text(raw, "department").upper(),
        "skills": normalize_list_text(raw.get("skills", "")),
        "certifications": normalize_list_text(raw.get("certifications", "")),
        "internship_details": _text(raw, "internship_details"),
    }
    for field in ("roll_no", "name", "department"):
        if not data[field]:
            errors.append((field, "is required"))
    if data["email"] and not EMAIL_RE.match(data["email"]):
        errors.append(("email", f"'{data['email']}' is not a valid email address"))
    data["cgpa"] = _number(raw, "cgpa", errors, lo=0, hi=10, required=True)
    data["backlogs"] = _number(raw, "backlogs", errors, integer=True, lo=0) or 0
    data["aptitude_score"] = _number(raw, "aptitude_score", errors, lo=0, hi=100)
    data["internships"] = _number(raw, "internships", errors, integer=True, lo=0) or 0
    return data, errors


def validate_placement(raw):
    """Validate a placement record. Returns (clean_dict, errors)."""
    errors = []
    status = _text(raw, "status").lower()
    data = {
        "status": status,
        "company": _text(raw, "company"),
        "job_role": _text(raw, "job_role"),
    }
    if status not in STATUSES:
        errors.append(("status", f"must be one of {', '.join(STATUSES)} (got '{status}')"))
    if status in ("shortlisted", "selected") and not data["company"]:
        errors.append(("company", f"is required when status is {status}"))
    data["package_lpa"] = _number(raw, "package_lpa", errors, lo=0, hi=500)
    if status == "selected" and not data["package_lpa"]:
        errors.append(("package_lpa", "is required (and must be above 0) when status is selected"))
    year = _number(raw, "recruitment_year", errors, integer=True, lo=2000, hi=2100)
    data["recruitment_year"] = year or date.today().year
    return data, errors
