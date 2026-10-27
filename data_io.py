"""CSV import (with validation) and CSV report exports."""
from flask import Blueprint, current_app, flash, render_template, request

from services import analytics
from services.data import apply_filters, get_frames
from services.exporter import STUDENT_COLUMNS, csv_response, dataframe_response
from services.importer import ImportFileError, import_dataframe, read_csv

bp = Blueprint("data_io", __name__)


@bp.route("/import", methods=["GET", "POST"])
def import_csv():
    result = None
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Choose a CSV file to upload.", "danger")
        elif not file.filename.lower().endswith(".csv"):
            flash("Only .csv files are supported.", "danger")
        else:
            try:
                result = import_dataframe(read_csv(file))
                if result["imported"]:
                    flash(f"Imported {result['imported']} student record(s).", "success")
                if result["skipped"]:
                    flash(f"Skipped {result['skipped']} row(s) with problems - see the list below.", "warning")
            except ImportFileError as exc:
                flash(str(exc), "danger")
    return render_template("import.html", result=result)


@bp.route("/reports")
def reports():
    _, _, m = get_frames()
    return render_template("reports.html", total=len(m))


@bp.route("/reports/students.csv")
def students_csv():
    _, _, m = get_frames()
    return dataframe_response(apply_filters(m, request.args), STUDENT_COLUMNS, "students_report.csv")


@bp.route("/reports/unplaced.csv")
def unplaced_csv():
    _, _, m = get_frames()
    rows = analytics.preparation_insights(m, current_app.config["PREP_RULES"])
    data = [(r["roll_no"], r["name"], r["department"], r["cgpa"], r["readiness"], r["need"],
             "; ".join(r["gaps"]), "; ".join(r["recommendations"])) for r in rows]
    header = ["roll_no", "name", "department", "cgpa", "readiness_pct", "need", "gaps", "recommendations"]
    return csv_response(data, header, "preparation_insights.csv")


@bp.route("/reports/summary.csv")
def summary_csv():
    _, p, m = get_frames()
    s = analytics.summary(m)
    rows = [("Overall", k, v) for k, v in s.items() if k != "status_counts"]
    rows += [("Status", k, v) for k, v in s["status_counts"].items()]
    for d in analytics.department_stats(m):
        rows += [(f"Department {d['department']}", "students", d["total"]),
                 (f"Department {d['department']}", "placed", d["placed"]),
                 (f"Department {d['department']}", "placement_pct", d["placement_pct"]),
                 (f"Department {d['department']}", "avg_package_lpa", d["avg_package"])]
    for y in analytics.year_stats(p):
        rows += [(f"Year {y['year']}", "placed", y["placed"]),
                 (f"Year {y['year']}", "placement_pct", y["placement_pct"]),
                 (f"Year {y['year']}", "avg_package_lpa", y["avg_package"])]
    for c in analytics.top_companies(p, 10):
        rows += [(f"Company {c['company']}", "hires", c["hires"]),
                 (f"Company {c['company']}", "avg_package_lpa", c["avg_package"])]
    return csv_response(rows, ["section", "metric", "value"], "placement_summary.csv")
