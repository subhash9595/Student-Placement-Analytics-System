from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from extensions import db
from models import STATUSES, Placement, Student
from services import analytics
from services.data import get_frames
from services.utils import records
from services.validation import validate_placement

bp = Blueprint("placements", __name__, url_prefix="/placements")


@bp.route("/")
def list_placements():
    _, p, _ = get_frames()
    f = p
    for key in ("status", "company"):
        if request.args.get(key):
            f = f[f[key] == request.args[key]]
    if request.args.get("year", type=int):
        f = f[f["recruitment_year"] == request.args.get("year", type=int)]
    f = f.sort_values(["recruitment_year", "id"], ascending=False)
    return render_template(
        "placements/list.html", placements=records(f.head(300)), total=len(f), statuses=STATUSES,
        companies=sorted(p["company"].dropna().unique()),
        years=sorted(p["recruitment_year"].dropna().astype(int).unique(), reverse=True))


@bp.route("/companies")
def companies():
    _, p, _ = get_frames()
    return render_template("placements/companies.html", rows=analytics.company_records(p))


def _handle(placement):
    students = Student.query.order_by(Student.roll_no).all()
    ctx = dict(students=students, statuses=STATUSES, year_now=date.today().year)
    if request.method == "POST":
        data, errors = validate_placement(request.form)
        student_id = request.form.get("student_id", type=int)
        if not student_id or not db.session.get(Student, student_id):
            errors.append(("student", "must be selected"))
        if errors:
            for field, message in errors:
                flash(f"{field.replace('_', ' ').capitalize()} {message}", "danger")
            return render_template("placements/form.html", p=request.form, **ctx)
        obj = placement or Placement()
        obj.student_id = student_id
        for key, value in data.items():
            setattr(obj, key, value)
        db.session.add(obj)
        db.session.commit()
        flash("Placement record saved.", "success")
        return redirect(url_for("placements.list_placements"))
    return render_template("placements/form.html", p=placement or {}, **ctx)


@bp.route("/new", methods=["GET", "POST"])
def create():
    return _handle(None)


@bp.route("/<int:pid>/edit", methods=["GET", "POST"])
def edit(pid):
    return _handle(db.session.get(Placement, pid) or abort(404))


@bp.route("/<int:pid>/delete", methods=["POST"])
def delete(pid):
    db.session.delete(db.session.get(Placement, pid) or abort(404))
    db.session.commit()
    flash("Placement record deleted.", "success")
    return redirect(url_for("placements.list_placements"))
