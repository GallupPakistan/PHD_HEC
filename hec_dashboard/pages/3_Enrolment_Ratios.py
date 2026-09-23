import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG
from components.header import render_header
from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.ratios_recipes import (
    load_level_ratio_table,
    load_sector_ratio_table,
    load_level_ratio_summary,
    load_discipline_ratio_table,
)
from charts.enrolment import level_pie_chart
from charts.ratios import (
    level_ratio_area_chart,
    discipline_gender_diverging_chart,
    sector_share_trend_chart,
)

st.set_page_config(page_title=f"{APP_NAME} — Enrolment Ratios", page_icon=PAGE_ICON, layout="wide")
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

level_table = load_level_ratio_table(sel_provinces, sel_years)
sector_table = load_sector_ratio_table(sel_provinces, sel_years)
level_summary = load_level_ratio_summary(sel_provinces, sel_years)
discipline_table = load_discipline_ratio_table(sel_provinces)

bachelor_share = level_summary.loc[level_summary["Level"] == "Bachelor", "Percentage"]
bachelor_share = float(bachelor_share.iloc[0]) if not bachelor_share.empty else 0.0
render_header(
    "Enrolment Ratios",
    "Share of enrolment by qualification level, sector, and discipline, by gender.",
    stat={"title": "Bachelor Share of Enrolment", "value": f"{bachelor_share:.1f}%"},
    stat_icon="📊",
)


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1: Year & Level-wise share (100% stacked area) + Level-wise pie
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1.4, 1])

with col1:
    chart_card(level_ratio_area_chart(level_table))

with col2:
    chart_card(level_pie_chart(level_summary))

# ---------------------------------------------------------------------------
# Row 2: Discipline & Gender share (diverging bar) + Sector share trend
# ---------------------------------------------------------------------------
col3, col4 = st.columns([1.4, 1])

with col3:
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(discipline_gender_diverging_chart(discipline_table), use_container_width=True, config=PLOTLY_CONFIG)
    st.caption("Discipline data is province-wise only (no year breakdown available in source data).")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    chart_card(sector_share_trend_chart(sector_table))