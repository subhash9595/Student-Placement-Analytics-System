from flask import Blueprint, current_app, render_template, request

from services import analytics
from services.data import get_frames

bp = Blueprint("insights", __name__, url_prefix="/insights")


@bp.route("/")
def index():
    _, _, m = get_frames()
    rules = current_app.config["PREP_RULES"]
    rows = analytics.preparation_insights(m, rules)
    level = request.args.get("need")
    if level in ("High", "Medium", "Low"):
        rows = [r for r in rows if r["need"] == level]
    return render_template("insights.html", rows=rows, rules=rules, level=level or "")
