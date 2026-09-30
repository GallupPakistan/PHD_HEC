import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG, BOARD_COLOR_SEQUENCE, COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.toggle import value_mode_toggle
from components.cards import chart_card

from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.extra_recipes import (
    enrol_by_province, passout_by_province, phd_by_province, clean_discipline,
)
from data.passout_recipes import YEAR_ORDER as PASSOUT_YEARS
from data.overview_recipes import _years_for
from data.overview_recipes import (
    overview_universities,
    overview_enrolment,
    overview_discipline,
    overview_faculty,
    overview_graduates,
    overview_phd,
)
from charts.universities import city_map_chart, sector_donut_chart
from charts.extra import hbar, stacked_hbar, PROVINCE_COLORS, GOLD, PUBLIC, PRIVATE
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
enrol_prov = enrol_by_province(sel_provinces, sel_years, "gender")
grad_prov = passout_by_province(sel_provinces, _years_for(sel_years, PASSOUT_YEARS) or None, "gender")
phd_prov = phd_by_province()

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

mode = value_mode_toggle()
st.write("")


# ---------------------------------------------------------------------------
# Universities
# ---------------------------------------------------------------------------
st.caption("Universities and PhD Directory charts are not affected by the sidebar filters.")
chart_card(city_map_chart(city_df, mode))
chart_card(hei_growth_mini_chart(year_df, mode))

c1, c2 = st.columns(2)
with c1:
    chart_card(hbar(province_bars["Province"], province_bars["Total"], "HEIs by Province",
                    colors=[PROVINCE_COLORS.get(p) for p in province_bars["Province"]], xtitle="Total HEIs", mode=mode))
with c2:
    chart_card(sector_donut_chart(sector_df, mode))

# ---------------------------------------------------------------------------
# Enrolment
# ---------------------------------------------------------------------------
chart_card(enrolment_trend_mini_chart(gender_agg, mode))
chart_card(level_stacked_bar_chart(level_agg, mode))

c3, c4 = st.columns(2)
with c3:
    chart_card(gender_pie_chart(gender_summary, mode))
with c4:
    chart_card(hbar(enrol_prov["Province"], enrol_prov["Total"], "Enrolment by Province",
                    colors=[PROVINCE_COLORS.get(p) for p in enrol_prov["Province"]],
                    xtitle="Enrolment (selected years combined)", mode=mode))

disc_top = discipline_top.copy()
disc_top["Label"] = disc_top["Discipline"].apply(clean_discipline)
# share of ALL disciplines (not just the 8 shown): total = shown sum / shown share
_disc_all = float(disc_top["Total"].sum()) / (float(disc_top["Share"].sum()) / 100) if disc_top["Share"].sum() else None
chart_card(hbar(disc_top["Label"], disc_top["Total"], "Enrolment by Discipline (Top 8)", color=COLORS["accent"],
                xtitle="Enrolment (estimated)", mode=mode, total=_disc_all))

# ---------------------------------------------------------------------------
# Faculty
# ---------------------------------------------------------------------------
chart_card(stacked_hbar(faculty_prov_agg["Province"],
                        [("PhD", faculty_prov_agg["PhD"], GOLD), ("Non-PhD", faculty_prov_agg["Non_PhD"], COLORS["accent"])],
                        "Faculty by Province (PhD vs Non-PhD)", xtitle="Faculty Count", mode=mode))
c5, c6 = st.columns(2)
with c5:
    chart_card(faculty_gender_donut_chart(faculty_gender_df, mode))
with c6:
    chart_card(hbar(grad_prov["Province"], grad_prov["Total"], "Graduates by Province",
                    colors=[PROVINCE_COLORS.get(p) for p in grad_prov["Province"]],
                    xtitle="Graduates (selected years combined)", mode=mode))

# ---------------------------------------------------------------------------
# Graduates & PhDs
# ---------------------------------------------------------------------------
chart_card(graduates_trend_mini_chart(graduates_agg, mode))
chart_card(phd_year_bar_chart(phd_by_year, mode))
chart_card(hbar(phd_prov["Province"], phd_prov["PhDs"], "PhDs Produced by Province",
                colors=[PROVINCE_COLORS.get(p) for p in phd_prov["Province"]], xtitle="PhDs Produced", mode=mode))
