import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG, BOARD_COLOR_SEQUENCE
from components.header import render_header
from components.kpi_card import kpi_card

from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.overview_recipes import (
    overview_universities,
    overview_enrolment,
    overview_discipline,
    overview_faculty,
    overview_graduates,
    overview_phd,
)
from charts.universities import city_map_chart, sector_donut_chart
from charts.enrolment import gender_pie_chart
from charts.overview_charts import (
    hei_growth_mini_chart,
    province_hei_bar_chart,
    enrolment_trend_mini_chart,
    level_stacked_bar_chart,
    discipline_bar_chart_overview,
    faculty_province_bar_chart,
    faculty_gender_donut_chart,
    graduates_trend_mini_chart,
    phd_year_bar_chart,
)

st.set_page_config(page_title=f"{APP_NAME} — Overview", page_icon=PAGE_ICON, layout="wide")
inject_css()

# ---------------------------------------------------------------------------
# Sidebar filters — apply to Enrolment, Discipline, Faculty and Graduates
# charts. Universities and PhD Directory charts are unaffected: their source
# data has no per-record Province/Year to filter on.
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
st.sidebar.caption(
    "Filters apply to Enrolment, Faculty, Graduates and Discipline charts. "
    "Universities and PhD Directory charts always show all data."
)

# ---------------------------------------------------------------------------
# Pull every page's numbers in one pass
# ---------------------------------------------------------------------------
province_bars, sector_df, year_df, city_df, total_heis = overview_universities()
gender_agg, level_agg, gender_summary, latest_enrolment = overview_enrolment(sel_provinces, sel_years)
discipline_top = overview_discipline(top_n=8, provinces=sel_provinces)
faculty_prov_agg, faculty_gender_df, total_faculty = overview_faculty(sel_provinces, sel_years)
graduates_agg, latest_graduates = overview_graduates(sel_provinces, sel_years)
phd_by_year, total_phds_count = overview_phd()

female_pct = gender_summary.loc[gender_summary["Gender"] == "Female", "Percentage"]
female_pct = float(female_pct.iloc[0]) if not female_pct.empty else 0.0

render_header(
    "Overview",
    "The complete picture — every page's headline numbers and best visual, in one place.",
    stat={"title": "Total HEIs", "value": f"{total_heis:,}"},
    stat_icon="🏛️",
)

# ---------------------------------------------------------------------------
# KPI strip
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    kpi_card("Total HEIs", f"{total_heis:,}", color=BOARD_COLOR_SEQUENCE[1])
with k2:
    kpi_card("Latest Enrolment", f"{latest_enrolment / 1_000_000:.2f}M", color=BOARD_COLOR_SEQUENCE[0])
with k3:
    kpi_card("Total Faculty", f"{total_faculty:,}", color=BOARD_COLOR_SEQUENCE[2])
with k4:
    kpi_card("Latest Graduates", f"{latest_graduates:,}", color=BOARD_COLOR_SEQUENCE[4])
with k5:
    kpi_card("PhDs Registered", f"{total_phds_count / 1000:.1f}K", color=BOARD_COLOR_SEQUENCE[5])
with k6:
    kpi_card("Female Enrolment Share", f"{female_pct:.1f}%", color=BOARD_COLOR_SEQUENCE[7])

st.write("")


def chart_card(fig):
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Row 1 — Universities: map + growth trend
# ---------------------------------------------------------------------------
st.caption("Universities charts below are not affected by the sidebar filters.")
c1, c2 = st.columns(2)
with c1:
    chart_card(city_map_chart(city_df))
with c2:
    chart_card(hei_growth_mini_chart(year_df))

# ---------------------------------------------------------------------------
# Row 2 — Universities: province split + sector split
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)
with c3:
    chart_card(province_hei_bar_chart(province_bars))
with c4:
    chart_card(sector_donut_chart(sector_df))

# ---------------------------------------------------------------------------
# Row 3 — Enrolment: trend + gender split
# ---------------------------------------------------------------------------
c5, c6 = st.columns(2)
with c5:
    chart_card(enrolment_trend_mini_chart(gender_agg))
with c6:
    chart_card(gender_pie_chart(gender_summary))

# ---------------------------------------------------------------------------
# Row 4 — Enrolment: level split + discipline (full width, stacked)
# ---------------------------------------------------------------------------
chart_card(level_stacked_bar_chart(level_agg))
chart_card(discipline_bar_chart_overview(discipline_top))

# ---------------------------------------------------------------------------
# Row 5 — Faculty: province split + gender split
# ---------------------------------------------------------------------------
c9, c10 = st.columns(2)
with c9:
    chart_card(faculty_province_bar_chart(faculty_prov_agg))
with c10:
    chart_card(faculty_gender_donut_chart(faculty_gender_df))

# ---------------------------------------------------------------------------
# Row 6 — Graduates trend + PhD registrations by year
# (PhD Directory chart on the right is not affected by the sidebar filters —
# its source data has no Province column.)
# ---------------------------------------------------------------------------
c11, c12 = st.columns(2)
with c11:
    chart_card(graduates_trend_mini_chart(graduates_agg))
with c12:
    chart_card(phd_year_bar_chart(phd_by_year))