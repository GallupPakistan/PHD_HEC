import pandas as pd
import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG
from components.header import render_header
from data.faculty_recipes import (
    PROVINCES,
    YEAR_ORDER,
    FACULTY_TYPES,
    QUALIFICATIONS,
    load_province_table,
    load_pct_by_year_table,
    load_sector_table,
    load_gender_by_year_table,
)
from charts.faculty import (
    province_qualification_bar_chart,
    qualification_share_donut,
    sector_qualification_bar_chart,
)
from charts.overview_charts import faculty_gender_donut_chart

st.set_page_config(page_title=f"{APP_NAME} — Faculty Stats", page_icon=PAGE_ICON, layout="wide")
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
if len(YEAR_ORDER) == 1:
    st.sidebar.caption("Only one year of faculty data is currently available.")

st.sidebar.markdown("#### PhD / Non-PhD")
sel_qualifications = st.sidebar.multiselect(
    "PhD / Non-PhD", QUALIFICATIONS, default=[], label_visibility="collapsed",
    placeholder="All (PhD, Non-PhD)",
)

st.sidebar.markdown("#### Faculty Type")
sel_faculty_types = st.sidebar.multiselect(
    "Faculty Type", FACULTY_TYPES, default=[], label_visibility="collapsed",
    placeholder="All (Full Time, Part Time)",
)

province_table = load_province_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
pct_by_year = load_pct_by_year_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
sector_table = load_sector_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
gender_by_year = load_gender_by_year_table(sel_provinces, sel_years, sel_faculty_types)

total_faculty = int(province_table.loc[province_table["Province"] == "Total", "Total"].iloc[0])
render_header(
    "Faculty Stats",
    "PhD / Non-PhD faculty by province, sector, and gender.",
    stat={"title": "Total Faculty", "value": f"{total_faculty:,}"},
    stat_icon="🧑‍🏫",
)


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1: PhD/Non-PhD by Province (stacked bar) + Gender split (donut)
# ---------------------------------------------------------------------------
province_chart_df = province_table[province_table["Province"] != "Total"]
gender_row = gender_by_year.iloc[0]
gender_long = pd.DataFrame({
    "Gender": ["Female", "Male"],
    "Count": [gender_row["Female"], gender_row["Male"]],
})

col1, col2 = st.columns([1.4, 1])

with col1:
    chart_card(province_qualification_bar_chart(province_chart_df))

with col2:
    chart_card(faculty_gender_donut_chart(gender_long))
    st.caption("Not split by PhD/Non-PhD in source data, so the PhD/Non-PhD filter doesn't affect this chart.")

# ---------------------------------------------------------------------------
# Row 2: PhD share (donut) + PhD/Non-PhD by Sector (100% stacked bar)
# ---------------------------------------------------------------------------
col3, col4 = st.columns([1, 1.2])

with col3:
    chart_card(qualification_share_donut(pct_by_year.iloc[0]))

with col4:
    chart_card(sector_qualification_bar_chart(sector_table))
    st.caption("Sector shares are averaged across Full Time and Part Time faculty (no raw sector headcounts in source data).")