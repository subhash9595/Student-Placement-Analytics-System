"""Server-side Matplotlib charts returned as PNG bytes."""
import io

import numpy as np
from matplotlib.figure import Figure

INK, TEAL, SAFFRON, ROSE = "#14323b", "#2a7f86", "#e8a93a", "#c4455a"


def _png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    return buf.getvalue()


def _empty(title):
    fig = Figure(figsize=(6, 3.4))
    ax = fig.subplots()
    ax.text(0.5, 0.5, "No data yet", ha="center", va="center", color="#888")
    ax.set_title(title)
    ax.axis("off")
    return _png(fig)


def salary_histogram(m) -> bytes:
    pk = m.loc[m["placed"], "package_lpa"].dropna()
    if pk.empty:
        return _empty("Salary distribution")
    fig = Figure(figsize=(6, 3.4))
    ax = fig.subplots()
    ax.hist(pk, bins=min(12, max(4, len(pk) // 4)), color=TEAL, edgecolor="white")
    ax.axvline(pk.mean(), color=SAFFRON, linewidth=2, label=f"Mean {pk.mean():.1f} LPA")
    ax.axvline(float(np.median(pk)), color=ROSE, linestyle="--", label=f"Median {np.median(pk):.1f} LPA")
    ax.set(title="Salary distribution of placed students", xlabel="Package (LPA)", ylabel="Students")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)


def department_chart(dept_rows) -> bytes:
    if not dept_rows:
        return _empty("Department-wise placement")
    labels = [d["department"] for d in dept_rows]
    x = np.arange(len(labels))
    fig = Figure(figsize=(6, 3.4))
    ax = fig.subplots()
    ax.bar(x - 0.2, [d["total"] for d in dept_rows], 0.4, label="Students", color="#b9c7c9")
    ax.bar(x + 0.2, [d["placed"] for d in dept_rows], 0.4, label="Placed", color=TEAL)
    ax.set_xticks(x, labels)
    ax.set(title="Department-wise placements", ylabel="Students")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)


def cgpa_scatter(m) -> bytes:
    d = m.dropna(subset=["cgpa", "aptitude_score"])
    if d.empty:
        return _empty("CGPA vs aptitude")
    fig = Figure(figsize=(6, 3.4))
    ax = fig.subplots()
    for placed, color, label in ((False, ROSE, "Not placed"), (True, TEAL, "Placed")):
        g = d[d["placed"] == placed]
        ax.scatter(g["cgpa"], g["aptitude_score"], s=22, alpha=0.75, color=color, label=label)
    ax.set(title="CGPA vs aptitude score", xlabel="CGPA", ylabel="Aptitude score")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return _png(fig)
