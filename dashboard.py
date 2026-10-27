from flask import Blueprint, jsonify, render_template

from services import analytics
from services.data import get_frames

bp = Blueprint("dashboard", __name__)


def _dashboard_data():
    _, p, m = get_frames()
    return {
        "summary": analytics.summary(m),
        "departments": analytics.department_stats(m),
        "years": analytics.year_stats(p),
        "companies": analytics.top_companies(p, 8),
        "salary": analytics.salary_distribution(m),
        "skills": analytics.skill_demand(m, 10),
    }


@bp.route("/")
def index():
    return render_template("dashboard.html", **_dashboard_data())


@bp.route("/api/dashboard")
def api_dashboard():
    return jsonify(_dashboard_data())
