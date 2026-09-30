import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from data.enrolment_recipes import (
    load_gender_wise, load_level_wise, load_sector_wise, apply_filters, aggregate_by_year, PROVINCES, YEAR_ORDER,
)
from data.details_recipes import load_gender_summary
from data.extra_recipes import enrol_by_province, enrol_province_year
from charts.enrolment import gender_line_chart, gender_pie_chart, sector_trend_chart
from charts.overview_charts import level_stacked_bar_chart
from charts.extra import stacked_hbar, multi_line, short_year, FEMALE, MALE, PROVINCE_COLORS

st.set_page_config(page_title=f"{APP_NAME} — Enrolment", page_icon=PAGE_ICON, layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.markdown("#### Province")
sel_provinces = st.sidebar.multiselect(
    "Province", PROVINCES, default=[], label_visibility="collapsed", placeholder="All provinces",
)
st.sidebar.markdown("#### Year")
sel_years = st.sidebar.multiselect(
    "Year", YEAR_ORDER, default=[], label_visibility="collapsed", placeholder="All years",
)

gender_df = apply_filters(load_gender_wise(), sel_provinces, sel_years)
level_df = apply_filters(load_level_wise(), sel_provinces, sel_years)
sector_df = apply_filters(load_sector_wise(), sel_provinces, sel_years)

gender_agg = aggregate_by_year(gender_df, ["Female", "Male", "Total"])
level_agg = aggregate_by_year(level_df, ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD", "Total"])
sector_agg = aggregate_by_year(sector_df, ["Private", "Public", "Total"])
gender_summary = load_gender_summary(sel_provinces, sel_years)
by_prov = enrol_by_province(sel_provinces, sel_years, "gender")
prov_year = enrol_province_year(sel_provinces, sel_years)

latest_total = int(gender_agg["Total"].iloc[-1])
render_header(
    "Enrolment (Summary)",
    "Gender, level, sector and province-wise student enrolment trends.",
    stat={"title": "Latest Year Enrolment", "value": f"{latest_total / 1_000_000:.2f}M"},
    stat_icon="🎓",
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Latest Year Enrolment", f"{latest_total:,}", color=COLORS["accent"])
with k2:
    kpi_card("Female (selected years)", f"{int(gender_summary.loc[0, 'Count']):,}", color=FEMALE)
with k3:
    kpi_card("Male (selected years)", f"{int(gender_summary.loc[1, 'Count']):,}", color=MALE)
with k4:
    lead = by_prov.loc[by_prov["Total"].idxmax(), "Province"] if not by_prov.empty else "-"
    kpi_card("Largest Province", str(lead), color=COLORS["gold"])
st.write("")

# All charts are full width, one after another, except the two small donut/pie pair.

# 1 ── Gender trend
chart_card(gender_line_chart(gender_agg, "Numbers"), "Hover over the lines to see exact values.")

# 2 ── Total enrolment trend
chart_card(multi_line([short_year(y) for y in gender_agg["Year"]],
                      [("Total enrolment", gender_agg["Total"], COLORS["accent"])],
                      "Total Enrolment Over the Years", ytitle="Enrolment", xtitle="Year", area=True),
           "* = provisional year.")

# 3 ── Level-wise by year
chart_card(level_stacked_bar_chart(level_agg, "Numbers"))

# 4 ── Sector trend
chart_card(sector_trend_chart(sector_agg, "Numbers"))

# 5 ── Gender split (one compact chart, beside the province-wise gender chart is too cramped -> stacked below)
chart_card(gender_pie_chart(gender_summary, "Numbers"))

# 6 ── Province-wise enrolment by gender
chart_card(stacked_hbar(by_prov["Province"], [("Female", by_prov["Female"], FEMALE), ("Male", by_prov["Male"], MALE)],
                        "Province-wise Enrolment by Gender", xtitle="Enrolment (selected years combined)"))

# 7 ── Province trend
years_shown = list(prov_year.columns)
chart_card(multi_line([short_year(y) for y in years_shown],
                      [(p, prov_year.loc[p].values, PROVINCE_COLORS.get(p)) for p in prov_year.index],
                      "Province-wise Enrolment Over the Years", ytitle="Enrolment", xtitle="Year", height=480),
           "* = provisional year. Click a province in the legend to hide or show it.")
