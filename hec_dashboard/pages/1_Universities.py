import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from components.cards import chart_card
from components.toggle import value_mode_toggle
from data.recipes import load_province_table, load_sector_summary, load_year_growth, load_city_map
from data.extra_recipes import hei_decades, hei_specialisation
from charts.universities import city_map_chart, year_growth_chart, sector_donut_chart, province_sector_bar_chart
from charts.extra import donut, stacked_hbar, vbar, hbar, PROVINCE_COLORS, PUBLIC, PRIVATE, GOLD

st.set_page_config(page_title=APP_NAME, page_icon=PAGE_ICON, layout="wide")
inject_css()

province_df = load_province_table()
sector_df = load_sector_summary()
year_df = load_year_growth()
city_df = load_city_map()

total_row = province_df[province_df["Province"] == "TOTAL (PAKISTAN)"]
if not total_row.empty:
    total_heis = int(total_row["Total"].iloc[0])
    total_public = int(total_row["Public"].iloc[0])
    total_private = int(total_row["Private"].iloc[0])
else:
    total_heis = int(province_df["Total"].sum())
    total_public = int(province_df["Public"].sum())
    total_private = int(province_df["Private"].sum())
prov_only = province_df[province_df["Province"] != "TOTAL (PAKISTAN)"].reset_index(drop=True)

render_header(
    "Universities",
    "Province, sector, and city-wise distribution of Higher Education Institutions in Pakistan.",
    stat={"title": "Total HEIs", "value": f"{total_heis:,}"},
    stat_icon="🏛️",
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total HEIs", f"{total_heis}", color=COLORS["gold"])
with k2:
    kpi_card("Public", f"{total_public}", color=COLORS["public"])
with k3:
    kpi_card("Private", f"{total_private}", color=COLORS["private"])
with k4:
    top = prov_only.loc[prov_only["Total"].idxmax()]
    kpi_card("Largest Province", f"{top['Province']} ({int(top['Total'])})", color=COLORS["positive"])

mode = value_mode_toggle()
st.write("")

# 1 ── Map
chart_card(city_map_chart(city_df, mode),
           "Bubble size = number of HEIs with their main campus in that city. City-level coordinates (not individual campuses).")

# 2 ── Province & sector
chart_card(stacked_hbar(prov_only["Province"],
                        [("Public", prov_only["Public"], PUBLIC), ("Private", prov_only["Private"], PRIVATE)],
                        "Province & Sector-wise HEIs", xtitle="Number of HEIs", mode=mode))

# 3 ── Growth over the years (labels removed — values are in the hover)
chart_card(year_growth_chart(year_df, mode), "Hover over the lines to see the exact numbers for any year.")

# 4 ── Sector donut + Province donut (two compact charts side by side)
c1, c2 = st.columns(2)
with c1:
    chart_card(sector_donut_chart(sector_df, mode))
with c2:
    chart_card(donut(prov_only["Province"], prov_only["Total"], "Province-wise Share of HEIs",
                     colors=[PROVINCE_COLORS.get(p) for p in prov_only["Province"]], height=420,
                     center=f"{total_heis}<br>Total", mode=mode))

# 5 ── Top cities, split by sector
cities = city_df.sort_values("Total", ascending=False)
chart_card(stacked_hbar(cities["City"], [("Public", cities["Public"], PUBLIC), ("Private", cities["Private"], PRIVATE)],
                        "Top Cities — Public vs Private HEIs", xtitle="Number of HEIs", mode=mode),
           "Top 9 cities by number of HEIs.")

# 6 ── Decade-wise growth
dec = hei_decades(year_df)
chart_card(vbar(dec["Label"], dec["Added"], "HEIs Added per Decade", color=GOLD, ytitle="New HEIs", height=420, mode=mode),
           "Net increase in the running total of HEIs in each decade (adds up to today's total).")

# 7 ── Specialisation (institution directory)
spec, n_dir = hei_specialisation()
chart_card(hbar(spec["Type"], spec["Count"], "HEIs by Specialisation", color=COLORS["accent"], xtitle="Number of HEIs", mode=mode),
           f"Based on the institution directory list ({n_dir} institutions), which is a slightly shorter list than the {total_heis} HEIs counted above.")
