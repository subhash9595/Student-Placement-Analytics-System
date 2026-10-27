"""Pure pandas/NumPy analytics. Every function takes DataFrames and returns plain data."""
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd

from constants import STATUSES
from services.utils import clean, pretty_skill, records


def _r(x, digits=2):
    return None if x is None or pd.isna(x) else round(float(x), digits)


def summary(m: pd.DataFrame) -> dict:
    placed = m[m["placed"]]
    pk = placed["package_lpa"].dropna()
    total, n = len(m), len(placed)
    return clean({
        "total": total,
        "placed": n,
        "unplaced": total - n,
        "placement_pct": round(100 * n / total, 1) if total else 0.0,
        "avg_package": _r(pk.mean()),
        "median_package": _r(np.median(pk)) if len(pk) else None,
        "min_package": _r(pk.min()),
        "max_package": _r(pk.max()),
        "status_counts": {s: int((m["status"] == s).sum()) for s in STATUSES},
    })


def department_stats(m: pd.DataFrame) -> list:
    if m.empty:
        return []
    total = m.groupby("department").size().rename("total")
    placed = m[m["placed"]].groupby("department").agg(
        placed=("id", "count"), avg_package=("package_lpa", "mean"))
    d = pd.concat([total, placed], axis=1)
    d["placed"] = d["placed"].fillna(0).astype(int)
    d["placement_pct"] = (100 * d["placed"] / d["total"]).round(1)
    d["avg_package"] = d["avg_package"].round(2)
    d.index.name = "department"
    return records(d.reset_index())


def year_stats(p: pd.DataFrame) -> list:
    if p.empty:
        return []
    rows = []
    for year, g in p.groupby("recruitment_year"):
        sel = g[g["status"] == "selected"]
        n_all, n_sel = g["student_id"].nunique(), sel["student_id"].nunique()
        rows.append({
            "year": int(year),
            "students": n_all,
            "placed": n_sel,
            "placement_pct": round(100 * n_sel / n_all, 1) if n_all else 0.0,
            "avg_package": _r(sel["package_lpa"].mean()),
            "max_package": _r(sel["package_lpa"].max()),
        })
    return clean(sorted(rows, key=lambda r: r["year"]))


def top_companies(p: pd.DataFrame, n=10) -> list:
    sel = p[(p["status"] == "selected") & p["company"].notna()]
    if sel.empty:
        return []
    g = sel.groupby("company").agg(hires=("id", "count"), avg_package=("package_lpa", "mean"),
                                   max_package=("package_lpa", "max"))
    g = g.sort_values(["hires", "avg_package"], ascending=False).head(n).round(2)
    return records(g.reset_index())


def company_records(p: pd.DataFrame) -> list:
    """Company-wise recruitment table: count of records per status."""
    c = p[p["company"].notna() & (p["company"] != "")]
    if c.empty:
        return []
    pivot = c.pivot_table(index="company", columns="status", values="id",
                          aggfunc="count", fill_value=0).reindex(columns=STATUSES, fill_value=0)
    pivot["total"] = pivot.sum(axis=1)
    avg = c[c["status"] == "selected"].groupby("company")["package_lpa"].mean().round(2)
    pivot["avg_package"] = avg
    return records(pivot.sort_values("total", ascending=False).reset_index())


def salary_distribution(m: pd.DataFrame) -> dict:
    labels = ["Below 3", "3 - 5", "5 - 8", "8 - 12", "12 - 20", "20+"]
    bins = [0, 3, 5, 8, 12, 20, np.inf]
    pk = m.loc[m["placed"], "package_lpa"].dropna()
    counts = pd.cut(pk, bins=bins, labels=labels, right=False).value_counts(sort=False)
    return {"labels": labels, "counts": [int(counts.get(l, 0)) for l in labels]}


def role_stats(p: pd.DataFrame) -> list:
    sel = p[(p["status"] == "selected") & p["job_role"].notna() & (p["job_role"] != "")]
    if sel.empty:
        return []
    g = sel.groupby("job_role").agg(hires=("id", "count"), avg_package=("package_lpa", "mean"))
    return records(g.sort_values("avg_package", ascending=False).round(2).reset_index())


def skill_demand(m: pd.DataFrame, top=12) -> list:
    placed_c, all_c = Counter(), Counter()
    for skills, placed in zip(m["skill_list"], m["placed"]):
        for s in set(skills):
            all_c[s] += 1
            if placed:
                placed_c[s] += 1
    rows = [{"skill": pretty_skill(s), "placed": placed_c[s], "total": all_c[s],
             "placement_rate": round(100 * placed_c[s] / all_c[s], 1)} for s in all_c]
    rows.sort(key=lambda r: (r["placed"], r["total"]), reverse=True)
    return rows[:top]


def skill_combinations(m: pd.DataFrame, min_count=3, top=10) -> list:
    all_c, placed_c = Counter(), Counter()
    for skills, placed in zip(m["skill_list"], m["placed"]):
        for pair in combinations(sorted(set(skills)), 2):
            all_c[pair] += 1
            if placed:
                placed_c[pair] += 1
    rows = [{"combo": f"{pretty_skill(a)} + {pretty_skill(b)}", "students": n,
             "placed": placed_c[(a, b)], "placement_rate": round(100 * placed_c[(a, b)] / n, 1)}
            for (a, b), n in all_c.items() if n >= min_count]
    rows.sort(key=lambda r: (r["placement_rate"], r["students"]), reverse=True)
    return rows[:top]


def skill_gaps(m: pd.DataFrame, top=8) -> list:
    """Skills held by many placed students but few unplaced students."""
    placed, unplaced = m[m["placed"]], m[~m["placed"]]
    if placed.empty or unplaced.empty:
        return []
    pc = Counter(s for sl in placed["skill_list"] for s in set(sl))
    uc = Counter(s for sl in unplaced["skill_list"] for s in set(sl))
    rows = []
    for skill, count in pc.items():
        p_share = 100 * count / len(placed)
        u_share = 100 * uc.get(skill, 0) / len(unplaced)
        rows.append({"skill": pretty_skill(skill), "placed_share": round(p_share, 1),
                     "unplaced_share": round(u_share, 1), "gap": round(p_share - u_share, 1)})
    rows = [r for r in rows if r["gap"] > 0]
    rows.sort(key=lambda r: r["gap"], reverse=True)
    return rows[:top]


def cgpa_ranges(m: pd.DataFrame) -> list:
    labels = ["Below 6", "6 - 7", "7 - 8", "8 - 9", "9 - 10"]
    band = pd.cut(m["cgpa"], bins=[0, 6, 7, 8, 9, 10.01], labels=labels, right=False)
    rows = []
    for label in labels:
        g = m[band == label]
        n, placed = len(g), int(g["placed"].sum())
        rows.append({"range": label, "students": n, "placed": placed,
                     "placement_pct": round(100 * placed / n, 1) if n else 0.0})
    return rows


def _strength(r):
    if r is None:
        return "n/a"
    a = abs(r)
    return "strong" if a >= 0.5 else "moderate" if a >= 0.3 else "weak" if a >= 0.1 else "negligible"


def correlations(m: pd.DataFrame) -> list:
    """Pearson correlation of each attribute with being placed (point-biserial)."""
    y = m["placed"].astype(float)
    rows = []
    for col, label in [("cgpa", "CGPA"), ("aptitude_score", "Aptitude score"),
                       ("internships", "Internships"), ("num_skills", "Number of skills"),
                       ("num_certs", "Certifications"), ("backlogs", "Backlogs")]:
        x = pd.to_numeric(m[col], errors="coerce")
        ok = x.notna()
        if ok.sum() < 3 or x[ok].std() == 0 or y[ok].std() == 0:
            r = None
        else:
            r = round(float(np.corrcoef(x[ok], y[ok])[0, 1]), 3)
        rows.append({"attribute": label, "r": r, "strength": _strength(r),
                     "direction": "" if r is None else ("positive" if r > 0 else "negative")})
    return clean(rows)


def attribute_comparison(m: pd.DataFrame) -> list:
    rows = []
    for col, label in [("cgpa", "CGPA"), ("aptitude_score", "Aptitude score"),
                       ("internships", "Internships"), ("num_skills", "Skills"),
                       ("num_certs", "Certifications"), ("backlogs", "Backlogs")]:
        rows.append({"attribute": label,
                     "placed": _r(m.loc[m["placed"], col].mean()),
                     "not_placed": _r(m.loc[~m["placed"], col].mean())})
    return clean(rows)


# ---------------------------------------------------------------- preparation insights
def evaluate_student(row, rules: dict) -> dict:
    """Check one student against the configurable criteria."""
    gaps, recs = [], []
    cgpa, apt = row["cgpa"], row["aptitude_score"]
    skills = set(row["skill_list"])

    if pd.isna(cgpa) or cgpa < rules["min_cgpa"]:
        gaps.append(f"CGPA below {rules['min_cgpa']}")
        recs.append("Focus on raising CGPA in the remaining semesters.")
    if (row["backlogs"] or 0) > rules["max_backlogs"]:
        gaps.append(f"{int(row['backlogs'])} active backlog(s)")
        recs.append("Clear all backlogs - many companies filter on them.")
    if pd.isna(apt) or apt < rules["min_aptitude"]:
        gaps.append(f"Aptitude score below {rules['min_aptitude']}")
        recs.append("Practise quantitative, logical and verbal aptitude tests weekly.")
    if row["num_skills"] < rules["min_skills"]:
        gaps.append(f"Only {int(row['num_skills'])} technical skill(s) listed")
        recs.append(f"Build at least {rules['min_skills']} job-relevant technical skills.")
    if (row["internships"] or 0) < rules["min_internships"]:
        gaps.append("No internship experience")
        recs.append("Apply for an internship or complete a real-world project.")
    if row["num_certs"] < rules["min_certifications"]:
        gaps.append("No certifications")
        recs.append("Complete an industry-recognised certification in your core skills.")
    missing = [s for s in rules["required_skills"] if s.lower() not in skills]
    if missing:
        names = ", ".join(pretty_skill(s) for s in missing)
        gaps.append(f"Missing required skills: {names}")
        recs.append(f"Learn {names} - these are expected for most roles.")

    total_checks = 7
    score = round(100 * (total_checks - len(gaps)) / total_checks)
    level = "High" if score < 50 else "Medium" if score < 80 else "Low"
    return {"gaps": gaps, "recommendations": recs, "readiness": score, "need": level}


def preparation_insights(m: pd.DataFrame, rules: dict) -> list:
    """Students not yet placed who fail one or more criteria, most in need first."""
    out = []
    for _, row in m[~m["placed"]].iterrows():
        result = evaluate_student(row, rules)
        if result["gaps"]:
            out.append({"id": row["id"], "roll_no": row["roll_no"], "name": row["name"],
                        "department": row["department"], "cgpa": row["cgpa"],
                        "status": row["status"], **result})
    out.sort(key=lambda r: r["readiness"])
    return clean(out)
