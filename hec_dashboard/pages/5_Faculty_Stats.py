import pandas as pd
import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from components.toggle import value_mode_toggle
from data.faculty_recipes import (
    PROVINCES, YEAR_ORDER, FACULTY_TYPES, QUALIFICATIONS,
    load_province_table, load_pct_by_year_table, load_sector_table, load_gender_by_year_table,
)
from data.extra_recipes import faculty_type_by_province, faculty_gender_by_province
from charts.faculty import province_qualification_bar_chart, qualification_share_donut, sector_qualification_bar_chart
from charts.overview_charts import faculty_gender_donut_chart
from charts.extra import donut, stacked_hbar, hbar, FEMALE, MALE, GOLD

st.set_page_config(page_title=f"{APP_NAME} — Faculty Stats", page_icon=PAGE_ICON, layout="wide")
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
if len(YEAR_ORDER) == 1:
    st.sidebar.caption("Only one year of faculty data is currently available.")

st.sidebar.markdown("#### PhD / Non-PhD")
sel_qualifications = st.sidebar.multiselect(
    "PhD / Non-PhD", QUALIFICATIONS, default=[], label_visibility="collapsed", placeholder="All (PhD, Non-PhD)",
)
st.sidebar.markdown("#### Faculty Type")
sel_faculty_types = st.sidebar.multiselect(
    "Faculty Type", FACULTY_TYPES, default=[], label_visibility="collapsed", placeholder="All (Full Time, Part Time)",
)

province_table = load_province_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
pct_by_year = load_pct_by_year_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
sector_table = load_sector_table(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
gender_by_year = load_gender_by_year_table(sel_provinces, sel_years, sel_faculty_types)
type_by_prov = faculty_type_by_province(sel_provinces, sel_years, sel_faculty_types, sel_qualifications)
gender_by_prov = faculty_gender_by_province(sel_provinces, sel_years, sel_faculty_types)

total_row = province_table.loc[province_table["Province"] == "Total"].iloc[0]
total_faculty = int(total_row["Total"])
render_header(
    "Faculty Stats",
    "PhD / Non-PhD faculty by province, sector, faculty type and gender.",
    stat={"title": "Total Faculty", "value": f"{total_faculty:,}"},
    stat_icon="🧑‍🏫",
)

province_chart_df = province_table[province_table["Province"] != "Total"]
gender_row = gender_by_year.iloc[0]
gender_long = pd.DataFrame({"Gender": ["Female", "Male"], "Count": [gender_row["Female"], gender_row["Male"]]})

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total Faculty", f"{total_faculty:,}", color=COLORS["accent"])
with k2:
    kpi_card("PhD Faculty", f"{int(total_row['PhD']):,}", color=GOLD)
with k3:
    kpi_card("Non-PhD Faculty", f"{int(total_row['Non_PhD']):,}", color=COLORS["private"])
with k4:
    kpi_card("Female Faculty", f"{int(gender_row['Female']):,}", color=FEMALE)
mode = value_mode_toggle()
st.write("")

# 1 ── PhD / Non-PhD by province
chart_card(province_qualification_bar_chart(province_chart_df, mode))

# 2 ── Gender donut + PhD share donut (two compact charts side by side)
c1, c2 = st.columns(2)
with c1:
    chart_card(faculty_gender_donut_chart(gender_long, mode),
               "Not split by PhD/Non-PhD in the source data, so the PhD/Non-PhD filter doesn't affect this chart.")
with c2:
    chart_card(qualification_share_donut(pct_by_year.iloc[0], total_row, mode))

# 3 ── Full time / part time by province
chart_card(stacked_hbar(type_by_prov["Province"],
                        [("Full Time", type_by_prov["Full Time"], COLORS["accent"]),
                         ("Part Time", type_by_prov["Part Time"], COLORS["gold"])],
                        "Province-wise Faculty by Type (Full Time vs Part Time)", xtitle="Faculty Count", mode=mode))

# 4 ── Gender by province
chart_card(stacked_hbar(gender_by_prov["Province"],
                        [("Female", gender_by_prov["Female"], FEMALE), ("Male", gender_by_prov["Male"], MALE)],
                        "Province-wise Faculty by Gender", xtitle="Faculty Count", mode=mode),
           "Not split by PhD/Non-PhD in the source data, so that filter doesn't affect this chart.")

# 5 ── PhD faculty by province
phd_df = province_chart_df[province_chart_df["PhD"] > 0]
chart_card(hbar(phd_df["Province"], phd_df["PhD"], "PhD Faculty by Province", color=GOLD, xtitle="PhD Faculty", mode=mode))

# 6 ── Sector qualification mix + Faculty type donut
c3, c4 = st.columns(2)
with c3:
    chart_card(sector_qualification_bar_chart(sector_table),
               "Always shown as shares: sector shares are averaged across Full Time and Part Time faculty (no raw sector headcounts in source data).")
with c4:
    type_tot = type_by_prov[["Full Time", "Part Time"]].sum()
    chart_card(donut(["Full Time", "Part Time"], [type_tot["Full Time"], type_tot["Part Time"]],
                     "Full Time vs Part Time Faculty", colors=[COLORS["accent"], COLORS["gold"]], height=420, mode=mode))
