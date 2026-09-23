import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG
from components.header import render_header
from data.passout_recipes import (
    load_gender_wise,
    load_level_wise,
    apply_filters,
    aggregate_by_year,
    gender_totals,
    PROVINCES,
    YEAR_ORDER,
)
from charts.passout import gender_line_chart, gender_donut_chart, level_heatmap_chart

st.set_page_config(page_title=f"{APP_NAME} — Graduate Stats", page_icon=PAGE_ICON, layout="wide")
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

gender_agg = aggregate_by_year(gender_df, ["Female", "Male", "Total"])
level_agg = aggregate_by_year(level_df, ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD", "Total"])

total_graduates = int(gender_agg["Total"].sum())
render_header(
    "Graduate Stats",
    "Year, gender, and level-wise breakdown of graduating students (passout) across all provinces.",
    stat={"title": "Total Graduates (Selected Years)", "value": f"{total_graduates:,}"},
    stat_icon="🎓",
)


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1: Year, Gender & Level-wise Passout -- heatmap (full width)
# ---------------------------------------------------------------------------
st.markdown('<div class="hec-card">', unsafe_allow_html=True)
st.plotly_chart(level_heatmap_chart(level_agg), use_container_width=True, config=PLOTLY_CONFIG)
st.caption("Source data doesn't split this table by gender, only by qualification level. Color is scaled per level (row-wise) since Bachelor volumes run ~100x PGD/PhD -- the number in each cell is always the real headcount.")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Year & Gender-wise Passout -- line trend + donut
# (this is the same gender_agg the table above used to duplicate, so the
# table was dropped rather than charted a second time)
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])

with col1:
    chart_card(gender_line_chart(gender_agg))

with col2:
    chart_card(gender_donut_chart(gender_totals(gender_agg)))