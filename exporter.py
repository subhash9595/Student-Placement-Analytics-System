"""CSV export helpers."""
import csv
import io

from flask import Response

STUDENT_COLUMNS = ["roll_no", "name", "email", "department", "cgpa", "backlogs", "aptitude_score",
                   "skills", "certifications", "internships", "status", "company", "job_role",
                   "package_lpa", "recruitment_year"]


def _safe(value):
    """Neutralise spreadsheet formula injection and blank out NaN."""
    if value is None or (isinstance(value, float) and value != value):
        return ""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") and not _is_number(text) else text


def _is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def csv_response(rows, header, filename) -> Response:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    for row in rows:
        writer.writerow([_safe(v) for v in row])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


def dataframe_response(df, columns, filename) -> Response:
    return csv_response(df[columns].itertuples(index=False, name=None), columns, filename)
