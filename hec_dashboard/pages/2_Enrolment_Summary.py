import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG
from components.header import render_header
from data.enrolment_recipes import (
    load_gender_wise,
    load_level_wise,
    load_sector_wise,
    apply_filters,
    aggregate_by_year,
    PROVINCES,
    YEAR_ORDER,
)
from data.details_recipes import load_gender_summary
from charts.enrolment import gender_line_chart, gender_pie_chart, sector_trend_chart
from charts.overview_charts import level_stacked_bar_chart

st.set_page_config(page_title=f"{APP_NAME} — Enrolment", page_icon=PAGE_ICON, layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown("#### Province")
sel_provinces = st.sidebar.multiselect(
    "Province", PROVINCES, default=[], label_visibility="collapsed",
    placeholder="All provinces",
)
st.sidebar.markdown("#### Year")
sel_years = st.sidebar.multiselect(
    "Year", YEAR_ORDER, default=[], label_visibility="collapsed",
    placeholder="All years",
)

gender_df = apply_filters(load_gender_wise(), sel_provinces, sel_years)
level_df = apply_filters(load_level_wise(), sel_provinces, sel_years)
sector_df = apply_filters(load_sector_wise(), sel_provinces, sel_years)

gender_agg = aggregate_by_year(gender_df, ["Female", "Male", "Total"])
level_agg = aggregate_by_year(level_df, ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD", "Total"])
sector_agg = aggregate_by_year(sector_df, ["Private", "Public", "Total"])
gender_summary = load_gender_summary(sel_provinces, sel_years)

latest_total = int(gender_agg["Total"].iloc[-1])
render_header(
    "Enrolment (Summary)",
    "Gender, level, and sector-wise student enrolment trends across all provinces.",
    stat={"title": "Latest Year Enrolment", "value": f"{latest_total / 1_000_000:.2f}M"},
    stat_icon="🎓",
)


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1: Gender-wise trend + Gender share donut
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])

with col1:
    chart_card(gender_line_chart(gender_agg))

with col2:
    chart_card(gender_pie_chart(gender_summary))

# ---------------------------------------------------------------------------
# Row 2: Level-wise stacked bar + Sector-wise two-line trend
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    chart_card(level_stacked_bar_chart(level_agg))

with col4:
    chart_card(sector_trend_chart(sector_agg))