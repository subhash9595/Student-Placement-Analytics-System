from flask import Blueprint, Response, render_template

from services import analytics, charts
from services.data import get_frames

bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@bp.route("/companies")
def companies():
    _, p, m = get_frames()
    return render_template(
        "analytics/companies.html", companies=analytics.top_companies(p, 10),
        salary=analytics.salary_distribution(m), roles=analytics.role_stats(p),
        departments=analytics.department_stats(m), summary=analytics.summary(m))


@bp.route("/skills")
def skills():
    _, _, m = get_frames()
    return render_template(
        "analytics/skills.html", demand=analytics.skill_demand(m, 12),
        combos=analytics.skill_combinations(m), gaps=analytics.skill_gaps(m))


@bp.route("/academics")
def academics():
    _, _, m = get_frames()
    return render_template(
        "analytics/academics.html", ranges=analytics.cgpa_ranges(m),
        corr=analytics.correlations(m), comparison=analytics.attribute_comparison(m))


@bp.route("/matplotlib/<name>.png")
def matplotlib_chart(name):
    _, _, m = get_frames()
    makers = {
        "salary": lambda: charts.salary_histogram(m),
        "departments": lambda: charts.department_chart(analytics.department_stats(m)),
        "cgpa": lambda: charts.cgpa_scatter(m),
    }
    if name not in makers:
        return Response("Unknown chart", status=404)
    return Response(makers[name](), mimetype="image/png")
