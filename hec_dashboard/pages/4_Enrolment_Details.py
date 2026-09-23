import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG, COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.details_recipes import (
    load_gender_year_table,
    load_gender_summary,
    load_discipline_count_table,
)
from charts.enrolment import gender_pie_chart, gender_line_chart, discipline_gender_bar_chart

st.set_page_config(page_title=f"{APP_NAME} — Enrolment Details", page_icon=PAGE_ICON, layout="wide")
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

discipline_table = load_discipline_count_table(sel_provinces)
gender_year_table = load_gender_year_table(sel_provinces, sel_years)
gender_summary = load_gender_summary(sel_provinces, sel_years)

female_pct = gender_summary.loc[gender_summary["Gender"] == "Female", "Percentage"]
female_pct = float(female_pct.iloc[0]) if not female_pct.empty else 0.0
render_header(
    "Enrolment Details",
    "Discipline, year, and gender-wise breakdown of student enrolment.",
    stat={"title": "Female Share of Enrolment", "value": f"{female_pct:.1f}%"},
    stat_icon="👩‍🎓",
)


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1: Discipline & Gender-wise bar chart (full width)
# ---------------------------------------------------------------------------
disc_chart_df = discipline_table[discipline_table["Discipline"] != "Total"]
total_row = discipline_table.loc[discipline_table["Discipline"] == "Total"].iloc[0]

st.markdown('<div class="hec-card">', unsafe_allow_html=True)
kpi_card("Total Enrolment (selected provinces)", f"{int(total_row['Total']):,}", color=COLORS["accent"])
st.plotly_chart(discipline_gender_bar_chart(disc_chart_df), use_container_width=True, config=PLOTLY_CONFIG)
st.caption("Discipline breakdown is province-wise only (no year breakdown available in source data).")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Year-wise Gender trend + Gender pie
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1.4, 1])

with col1:
    chart_card(gender_line_chart(gender_year_table))

with col2:
    chart_card(gender_pie_chart(gender_summary))