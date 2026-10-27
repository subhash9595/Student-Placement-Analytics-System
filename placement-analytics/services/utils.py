"""Small helpers shared across the services and templates."""
import math
import re

import numpy as np

_ACRONYMS = {
    "sql": "SQL", "html": "HTML", "css": "CSS", "aws": "AWS", "gcp": "GCP", "ml": "ML",
    "ai": "AI", "c++": "C++", "c": "C", "php": "PHP", "api": "API", "ui": "UI", "ux": "UX",
    "devops": "DevOps", "javascript": "JavaScript", "nodejs": "Node.js", "node.js": "Node.js",
    "mysql": "MySQL", "mongodb": "MongoDB", "powerbi": "Power BI", "power bi": "Power BI",
    "autocad": "AutoCAD", "matlab": "MATLAB", "vlsi": "VLSI", "iot": "IoT", "git": "Git",
    "numpy": "NumPy", "pandas": "Pandas", "tableau": "Tableau", "excel": "Excel",
}


def parse_list(value) -> list:
    """'Python, SQL ; java' -> ['python', 'sql', 'java'] (lower-cased, de-duplicated)."""
    if not isinstance(value, str):
        return []
    seen, out = set(), []
    for item in re.split(r"[,;|]", value):
        item = item.strip().lower()
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def pretty_skill(skill: str) -> str:
    skill = skill.strip()
    return _ACRONYMS.get(skill.lower(), skill.title() if skill.islower() else skill)


def normalize_list_text(value) -> str:
    """Store lists consistently: 'python;SQL' -> 'Python, SQL'."""
    return ", ".join(pretty_skill(s) for s in parse_list(value))


def clean(obj):
    """Recursively convert numpy/pandas values to JSON-safe Python values (NaN -> None)."""
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [clean(v) for v in obj]
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    try:  # pandas NA / NaT
        import pandas as pd
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return str(obj)


def records(df) -> list:
    return clean(df.to_dict("records"))
