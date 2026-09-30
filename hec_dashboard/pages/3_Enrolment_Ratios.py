import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from components.toggle import value_mode_toggle
from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.ratios_recipes import (
    load_level_ratio_summary, load_level_count_table, load_sector_count_table,
    load_discipline_count_table_for_ratios,
)
from data.extra_recipes import enrol_by_province, LEVEL_COLS, LEVEL_LABELS
from charts.enrolment import level_pie_chart
from charts.ratios import level_ratio_area_chart, discipline_gender_diverging_chart, sector_share_trend_chart
from charts.extra import donut, stacked_hbar, LEVEL_COLORS, PUBLIC, PRIVATE

st.set_page_config(page_title=f"{APP_NAME} — Enrolment Ratios", page_icon=PAGE_ICON, layout="wide")
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

level_counts = load_level_count_table(sel_provinces, sel_years)
sector_counts = load_sector_count_table(sel_provinces, sel_years)
level_summary = load_level_ratio_summary(sel_provinces, sel_years)
discipline_counts = load_discipline_count_table_for_ratios(sel_provinces)
by_level = enrol_by_province(sel_provinces, sel_years, "level")
by_sector = enrol_by_province(sel_provinces, sel_years, "sector")

bachelor_share = level_summary.loc[level_summary["Level"] == "Bachelor", "Percentage"]
bachelor_share = float(bachelor_share.iloc[0]) if not bachelor_share.empty else 0.0
render_header(
    "Enrolment Ratios",
    "How enrolment divides by qualification level, sector, discipline and province.",
    stat={"title": "Bachelor Share of Enrolment", "value": f"{bachelor_share:.1f}%"},
    stat_icon="📊",
)

sector_tot = {"Public": int(sector_counts["Public"].sum()), "Private": int(sector_counts["Private"].sum())}
k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Bachelor Share", f"{bachelor_share:.1f}%", color=COLORS["accent"])
with k2:
    kpi_card("Public Enrolment", f"{sector_tot['Public']:,}", color=PUBLIC)
with k3:
    kpi_card("Private Enrolment", f"{sector_tot['Private']:,}", color=PRIVATE)
mode = value_mode_toggle()
st.write("")

# 1 ── Level by year
chart_card(level_ratio_area_chart(level_counts, mode))

# 2 ── Level pie + sector donut (two compact charts side by side)
c1, c2 = st.columns(2)
with c1:
    chart_card(donut(level_summary["Level"], level_summary["Count"], "Level-wise Enrolment",
                     colors=[LEVEL_COLORS[l] for l in level_summary["Level"]], height=460, mode=mode))
with c2:
    chart_card(donut(["Public", "Private"], [sector_tot["Public"], sector_tot["Private"]],
                     "Sector-wise Enrolment", colors=[PUBLIC, PRIVATE], height=460, mode=mode))

# 3 ── Discipline x gender
chart_card(discipline_gender_diverging_chart(discipline_counts, mode),
           "Discipline data is province-wise only (no year breakdown in the source data). "
           "Headcounts are estimates: each province's % × its all-years enrolment.")

# 4 ── Sector trend
chart_card(sector_share_trend_chart(sector_counts, mode))

# 5 ── Province x level
chart_card(stacked_hbar(by_level["Province"],
                        [(LEVEL_LABELS.get(c, c), by_level[c], LEVEL_COLORS[LEVEL_LABELS.get(c, c)]) for c in LEVEL_COLS],
                        "Province-wise Enrolment by Qualification Level", xtitle="Enrolment (selected years combined)", mode=mode))

# 6 ── Province x sector
chart_card(stacked_hbar(by_sector["Province"], [("Public", by_sector["Public"], PUBLIC), ("Private", by_sector["Private"], PRIVATE)],
                        "Province-wise Enrolment by Sector", xtitle="Enrolment (selected years combined)", mode=mode))
