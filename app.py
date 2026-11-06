import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import DBManager
from data.generate_data import generate_data

st.set_page_config(
    page_title="Student Placement Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_database():
    db = DBManager()
    if db.is_empty():
        generate_data()
    return db

db = init_database()

@st.cache_data
def load_data():
    return db.get_all_students()

df = load_data()
stats = db.get_summary_stats()

with st.sidebar:
    st.markdown("## 🎓 Placement Analytics")
    st.markdown("**College Dashboard System**")
    st.divider()
    st.markdown(f"✅ **DB Status:** {stats['total']} students loaded")
    st.divider()
    st.markdown("### 🔍 Global Filters")
    years = ["All"] + sorted(df["year"].unique().tolist())
    branches = ["All"] + sorted(df["branch"].unique().tolist())
    sel_year = st.selectbox("Academic Year", years)
    sel_branch = st.selectbox("Branch", branches)
    st.session_state["sel_year"] = sel_year
    st.session_state["sel_branch"] = sel_branch
    st.divider()
    st.caption("Built with Streamlit + Plotly + Scikit-learn")

filtered_df = db.get_students_by_filter(
    year=sel_year if sel_year != "All" else None,
    branch=sel_branch if sel_branch != "All" else None
)

st.title("🎓 Student Placement Data Analysis System")
st.markdown("#### Welcome! Use the sidebar to navigate between pages.")
st.divider()

total = len(filtered_df)
placed = (filtered_df["placement_status"] == "Placed").sum()
placement_pct = round(placed / total * 100, 1) if total > 0 else 0
avg_pkg = round(filtered_df[filtered_df["placement_status"] == "Placed"]["package_lpa"].mean(), 2) if placed > 0 else 0
max_pkg = round(filtered_df[filtered_df["placement_status"] == "Placed"]["package_lpa"].max(), 2) if placed > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👨‍🎓 Total Students", f"{total:,}")
col2.metric("✅ Placement Rate", f"{placement_pct}%")
col3.metric("💰 Avg Package", f"{avg_pkg} LPA")
col4.metric("🚀 Highest Package", f"{max_pkg} LPA")

st.divider()

import plotly.express as px
grp = filtered_df.groupby(["year", "placement_status"]).size().reset_index(name="Count")
fig = px.bar(grp, x="year", y="Count", color="placement_status",
             barmode="group",
             color_discrete_map={"Placed": "#22c55e", "Not Placed": "#ef4444"},
             title="📊 Placement Overview by Year",
             labels={"year": "Year", "placement_status": "Status"})
fig.update_layout(template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.info("👈 Use the **sidebar** to explore all pages!")
