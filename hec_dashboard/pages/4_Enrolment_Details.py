import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from data.enrolment_recipes import PROVINCES, YEAR_ORDER
from data.details_recipes import load_gender_year_table, load_gender_summary, load_discipline_count_table
from data.extra_recipes import enrol_by_province, enrol_province_year, discipline_by_province, clean_discipline
from charts.enrolment import gender_pie_chart, gender_line_chart, discipline_gender_bar_chart
from charts.extra import treemap, gap_bar, hbar, heatmap, short_year, PROVINCE_COLORS

st.set_page_config(page_title=f"{APP_NAME} — Enrolment Details", page_icon=PAGE_ICON, layout="wide")
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

discipline_table = load_discipline_count_table(sel_provinces)
gender_year_table = load_gender_year_table(sel_provinces, sel_years)
gender_summary = load_gender_summary(sel_provinces, sel_years)
by_prov = enrol_by_province(sel_provinces, sel_years, "gender")
prov_year = enrol_province_year(sel_provinces, sel_years)
disc_by_prov = discipline_by_province(sel_provinces)

female_pct = gender_summary.loc[gender_summary["Gender"] == "Female", "Percentage"]
female_pct = float(female_pct.iloc[0]) if not female_pct.empty else 0.0
render_header(
    "Enrolment Details",
    "Discipline, year, province and gender-wise breakdown of student enrolment.",
    stat={"title": "Female Share of Enrolment", "value": f"{female_pct:.1f}%"},
    stat_icon="👩‍🎓",
)

disc_chart_df = discipline_table[discipline_table["Discipline"] != "Total"].copy()
disc_chart_df["Label"] = disc_chart_df["Discipline"].apply(clean_discipline)
total_row = discipline_table.loc[discipline_table["Discipline"] == "Total"].iloc[0]

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Total Enrolment (selected provinces)", f"{int(total_row['Total']):,}", color=COLORS["accent"])
with k2:
    top_d = disc_chart_df.loc[disc_chart_df["Total"].idxmax()]
    kpi_card("Largest Discipline", top_d["Label"].split(",")[0], color=COLORS["gold"])
with k3:
    kpi_card("Female Share", f"{female_pct:.1f}%", color="#EC4899")
st.write("")

# 1 ── Discipline x gender
chart_card(discipline_gender_bar_chart(disc_chart_df.drop(columns="Label"), "Numbers"),
           "Discipline breakdown is province-wise only (no year breakdown available in source data); headcounts are estimates.")

# 2 ── Discipline tree-map
tm = disc_chart_df[~disc_chart_df["Discipline"].str.startswith("00")]
chart_card(treemap(tm["Label"], tm["Total"], "Discipline Share of Enrolment (Tree-map)", height=520),
           "Bigger tile = more students. Hover for the exact number and share. The small 'Generic programmes' bucket is left out.")

# 3 ── Gender gap by discipline
chart_card(gap_bar(disc_chart_df["Label"], disc_chart_df["Female"], disc_chart_df["Male"],
                   "Gender Gap by Discipline (Female − Male)"),
           "Right of the centre line = more women enrolled; left = more men.")

# 4 ── Gender trend
chart_card(gender_line_chart(gender_year_table, "Numbers"), "Hover over the lines to see exact values.")

# 5 ── Gender pie + province total (compact pair)
c1, c2 = st.columns(2)
with c1:
    chart_card(gender_pie_chart(gender_summary, "Numbers"))
with c2:
    chart_card(hbar(by_prov["Province"], by_prov["Total"], "Enrolment by Province",
                    colors=[PROVINCE_COLORS.get(p) for p in by_prov["Province"]], xtitle="Enrolment (selected years combined)"))

# 6 ── Province x Year heat-map
chart_card(heatmap(prov_year.values.tolist(), [short_year(y) for y in prov_year.columns], list(prov_year.index),
                   "Province × Year Enrolment (Heat-map)", colorbar_title="Enrolment"),
           "Darker = higher enrolment. * = provisional year.")

# 7 ── Discipline x Province heat-map
labels_x = [p.replace("Khyber Pakhtunkhwa", "Khyber<br>Pakhtunkhwa").replace("Gilgit-Baltistan", "Gilgit-<br>Baltistan")
            for p in disc_by_prov.columns]
chart_card(heatmap(disc_by_prov.values.tolist(), labels_x, list(disc_by_prov.index),
                   "Discipline × Province Enrolment (Heat-map)", colorbar_title="Est. enrolment"),
           "Estimated headcount (each province's discipline % × its all-years enrolment). The small 'Generic programmes' bucket is left out.")
