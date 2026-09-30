import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from components.toggle import value_mode_toggle
from data.phd_directory_recipes import total_phds, discipline_chart_data, subject_wordcloud_data
from data.extra_recipes import (
    phd_year_series, phd_by_province, phd_top_universities, phd_top_subjects,
)
from charts.phd_directory import discipline_bar_chart, subject_wordcloud_chart, phd_year_area_chart, _clean_discipline
from charts.extra import hbar, multi_line, PROVINCE_COLORS, GOLD


def fmt_k(n):
    return f"{n / 1000:.1f}K"


st.set_page_config(page_title=f"{APP_NAME} — PhD Directory", page_icon=PAGE_ICON, layout="wide")
inject_css()

total = total_phds()
years_df, early_total = phd_year_series()
disc_df = discipline_chart_data()
prov_df = phd_by_province()
top_year = years_df.loc[years_df["Numbers"].idxmax()]
top_disc = disc_df.iloc[0]

render_header(
    "PhD Country Directory",
    "PhD graduates produced by national universities, by year, discipline, province, university and subject.",
    stat={"title": "PhD Graduates Registered", "value": fmt_k(total)},
    stat_icon="🎓",
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total PhDs Registered", f"{total:,}", color=COLORS["gold"])
with k2:
    kpi_card("Peak Year", f"{int(top_year['Year'])} ({int(top_year['Numbers']):,})", color=COLORS["accent"])
with k3:
    kpi_card("Largest Discipline", _clean_discipline(top_disc["Discipline"]).split(",")[0], color=COLORS["positive"])
with k4:
    kpi_card("Top Province", str(prov_df.iloc[0]["Province"]), color=COLORS["private"])

mode = value_mode_toggle()
st.write("")

# All charts are full width and stacked one after another (nothing side by side)
# so long labels always have room.

# 1 ── Year-wise
chart_card(
    phd_year_area_chart(years_df, mode, total),
    f"Shows 2001 onward. {early_total:,} PhDs registered up to 2000 are one lumped row in the source data, "
    "so they are left out of the trend line. The last year is still in progress — its dashed segment is not a real drop-off.",
)

# 2 ── Discipline
chart_card(
    discipline_bar_chart(disc_df, mode, total),
    "Excludes the small 'Generic programmes' bucket and records with no discipline recorded.",
)

# 3 ── Cumulative
x = [2000] + years_df["Year"].tolist()
cum, run = [], 0
run = early_total
cum.append(run)
for n in years_df["Numbers"]:
    run += int(n)
    cum.append(run)
chart_card(
    multi_line(x, [("Cumulative PhDs", cum, GOLD)], "Cumulative PhDs Produced", ytitle="PhDs (running total)",
               xtitle="Year", dtick=2, area=True, mode=mode, pct_kind="of_last"),
    "The first point (2000) includes all PhDs registered up to and including 2000.",
)

# 4 ── Province-wise
chart_card(
    hbar(prov_df["Province"], prov_df["PhDs"], "Province-wise PhDs Produced",
         colors=[PROVINCE_COLORS.get(p, COLORS["accent"]) for p in prov_df["Province"]], xtitle="PhDs Produced", mode=mode),
    "The PhD directory has no province column, so each university is placed in a province using the city / region "
    "in its name (e.g. “…, Lahore” → Punjab; Islamabad is shown as Federal).",
)

# 5 ── Top universities
chart_card(
    hbar(*(lambda d: (d["University"], d["Numbers"]))(phd_top_universities(15)),
         "Top 15 Universities by PhDs Produced", color=COLORS["accent"], xtitle="PhDs Produced", per=34, mode=mode, total=total),
)

# 6 ── Top subjects
subj = phd_top_subjects(10)
chart_card(
    hbar(subj["Subject"], subj["Numbers"], "Top 10 Subjects by PhDs Produced", color=COLORS["positive"],
         xtitle="PhDs Produced", mode=mode, total=total),
)

# 7 ── Word cloud
chart_card(
    subject_wordcloud_chart(subject_wordcloud_data(), mode, total),
    "Top 45 subject keywords by PhDs produced; word size reflects popularity. "
    "A gender-wise breakdown isn't available in the provided PhD directory data, so it isn't shown here.",
)
