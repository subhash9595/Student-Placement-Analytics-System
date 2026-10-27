from math import ceil

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from extensions import db
from models import STATUSES, Placement, Student
from services import analytics
from services.data import apply_filters, get_frames
from services.utils import records
from services.validation import validate_student

bp = Blueprint("students", __name__, url_prefix="/students")
PER_PAGE = 15


@bp.route("/")
def list_students():
    _, p, m = get_frames()
    filtered = apply_filters(m, request.args)
    total = len(filtered)
    pages = max(1, ceil(total / PER_PAGE))
    page = min(max(request.args.get("page", 1, type=int), 1), pages)
    rows = filtered.iloc[(page - 1) * PER_PAGE: page * PER_PAGE]

    def page_url(n):
        args = request.args.to_dict()
        args["page"] = n
        return url_for("students.list_students", **args)

    return render_template(
        "students/list.html", students=records(rows), total=total, page=page, pages=pages,
        page_url=page_url, statuses=STATUSES,
        departments=sorted(m["department"].dropna().unique()),
        companies=sorted(p["company"].dropna().unique()))


@bp.route("/<int:student_id>")
def detail(student_id):
    student = db.session.get(Student, student_id) or abort(404)
    _, _, m = get_frames()
    row = m[m["id"] == student_id].iloc[0]
    check = analytics.evaluate_student(row, current_app.config["PREP_RULES"])
    placements = sorted(student.placements, key=lambda x: (x.recruitment_year, x.id), reverse=True)
    return render_template("students/detail.html", s=student, placements=placements, check=check,
                           skills=[s.strip() for s in (student.skills or "").split(",") if s.strip()])


def _save(student, raw):
    data, errors = validate_student(raw)
    if not errors:
        clash = Student.query.filter(db.func.lower(Student.roll_no) == data["roll_no"].lower())
        if student:
            clash = clash.filter(Student.id != student.id)
        if clash.first():
            errors.append(("roll_no", f"{data['roll_no']} already exists"))
    if errors:
        for field, message in errors:
            flash(f"{field.replace('_', ' ').capitalize()} {message}", "danger")
        return None, raw
    student = student or Student()
    for key, value in data.items():
        setattr(student, key, value)
    db.session.add(student)
    db.session.commit()
    return student, data


@bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        student, data = _save(None, request.form)
        if student:
            flash(f"Added {student.name}.", "success")
            return redirect(url_for("students.detail", student_id=student.id))
        return render_template("students/form.html", s=data, title="Add student")
    return render_template("students/form.html", s={}, title="Add student")


@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
def edit(student_id):
    student = db.session.get(Student, student_id) or abort(404)
    if request.method == "POST":
        saved, data = _save(student, request.form)
        if saved:
            flash("Student updated.", "success")
            return redirect(url_for("students.detail", student_id=student_id))
        return render_template("students/form.html", s=data, title="Edit student", editing=True)
    return render_template("students/form.html", s=student, title="Edit student", editing=True)


@bp.route("/<int:student_id>/delete", methods=["POST"])
def delete(student_id):
    student = db.session.get(Student, student_id) or abort(404)
    db.session.delete(student)
    db.session.commit()
    flash(f"Deleted {student.name} and their placement records.", "success")
    return redirect(url_for("students.list_students"))
