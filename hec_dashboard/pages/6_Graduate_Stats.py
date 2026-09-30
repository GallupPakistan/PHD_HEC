import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from data.passout_recipes import (
    load_gender_wise, load_level_wise, apply_filters, aggregate_by_year, gender_totals, PROVINCES, YEAR_ORDER,
)
from data.extra_recipes import passout_by_province, passout_province_year, level_totals, LEVEL_COLS, LEVEL_LABELS
from charts.passout import gender_line_chart, gender_donut_chart, level_heatmap_chart
from charts.overview_charts import level_stacked_bar_chart
from charts.extra import donut, stacked_hbar, multi_line, short_year, LEVEL_COLORS, FEMALE, MALE, PROVINCE_COLORS

st.set_page_config(page_title=f"{APP_NAME} — Graduate Stats", page_icon=PAGE_ICON, layout="wide")
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
gender_agg = aggregate_by_year(gender_df, ["Female", "Male", "Total"])
level_agg = aggregate_by_year(level_df, ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD", "Total"])
by_gender = passout_by_province(sel_provinces, sel_years, "gender")
by_level = passout_by_province(sel_provinces, sel_years, "level")
prov_year = passout_province_year(sel_provinces, sel_years)
lvl_tot = level_totals(level_agg)

total_graduates = int(gender_agg["Total"].sum())
render_header(
    "Graduate Stats",
    "Year, gender, level and province-wise breakdown of graduating students (passout).",
    stat={"title": "Total Graduates (Selected Years)", "value": f"{total_graduates:,}"},
    stat_icon="🎓",
)

g = gender_totals(gender_agg)
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total Graduates", f"{total_graduates:,}", color=COLORS["accent"])
with k2:
    kpi_card("Female Graduates", f"{int(g.loc[0, 'Count']):,}", color=FEMALE)
with k3:
    kpi_card("Male Graduates", f"{int(g.loc[1, 'Count']):,}", color=MALE)
with k4:
    kpi_card("PhD Graduates", f"{int(level_agg['PhD'].sum()):,}", color=COLORS["gold"])
st.write("")

# 1 ── Year x level heat-map
chart_card(level_heatmap_chart(level_agg, "Numbers"),
           "Source data doesn't split this table by gender, only by qualification level. Colour is scaled per level "
           "(row-wise) since Bachelor volumes run ~100x PGD/PhD — the number in each cell is the real headcount.")

# 2 ── Gender trend
chart_card(gender_line_chart(gender_agg, "Numbers"), "Hover over the lines to see exact values.")

# 3 ── Level-wise by year
chart_card(level_stacked_bar_chart(level_agg, "Numbers").update_layout(
    title_text="Graduates by Qualification Level", yaxis_title="Graduates"))

# 4 ── Gender donut + level donut (two compact charts side by side)
c1, c2 = st.columns(2)
with c1:
    chart_card(gender_donut_chart(g, "Numbers"))
with c2:
    chart_card(donut(lvl_tot["Level"], lvl_tot["Count"], "Level-wise Graduates",
                     colors=[LEVEL_COLORS[l] for l in lvl_tot["Level"]], height=420))

# 5 ── Province x gender
chart_card(stacked_hbar(by_gender["Province"], [("Female", by_gender["Female"], FEMALE), ("Male", by_gender["Male"], MALE)],
                        "Province-wise Graduates by Gender", xtitle="Graduates (selected years combined)"))

# 6 ── Province x level
chart_card(stacked_hbar(by_level["Province"],
                        [(LEVEL_LABELS.get(c, c), by_level[c], LEVEL_COLORS[LEVEL_LABELS.get(c, c)]) for c in LEVEL_COLS],
                        "Province-wise Graduates by Qualification Level", xtitle="Graduates (selected years combined)"))

# 7 ── Province trend
chart_card(multi_line([short_year(y) for y in prov_year.columns],
                      [(p, prov_year.loc[p].values, PROVINCE_COLORS.get(p)) for p in prov_year.index],
                      "Province-wise Graduates Over the Years", ytitle="Graduates", xtitle="Year", height=480),
           "* = provisional year. Click a province in the legend to hide or show it.")
