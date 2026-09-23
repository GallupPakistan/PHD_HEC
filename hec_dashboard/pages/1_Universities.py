import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG, COLORS
from components.header import render_header
from components.kpi_card import kpi_card
from data.recipes import (
    load_province_table,
    load_sector_summary,
    load_year_growth,
    load_city_map,
)
from charts.universities import city_map_chart, year_growth_chart, sector_donut_chart, province_sector_bar_chart

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

render_header(
    "Universities",
    "Province, sector, and city-wise distribution of Higher Education Institutions in Pakistan.",
    stat={"title": "Total HEIs", "value": f"{total_heis:,}"},
    stat_icon="🏛️",
)

k1, k2, k3 = st.columns(3)
with k1:
    kpi_card("Total HEIs", f"{total_heis}", color=COLORS["gold"])
with k2:
    kpi_card("Public", f"{total_public}", color=COLORS["public"])
with k3:
    kpi_card("Private", f"{total_private}", color=COLORS["private"])

st.write("")

# ---------------------------------------------------------------------------
# Row 1: Map (full width)
# ---------------------------------------------------------------------------
st.markdown('<div class="hec-card">', unsafe_allow_html=True)
fig_map = city_map_chart(city_df)
st.plotly_chart(fig_map, use_container_width=True, config=PLOTLY_CONFIG)
st.caption("Bubble size/city = number of HEIs with main campus there. City-level coordinates (not individual campuses).")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Province & Sector-wise HEIs (full width)
# ---------------------------------------------------------------------------
st.markdown('<div class="hec-card">', unsafe_allow_html=True)
fig_province = province_sector_bar_chart(province_df)
st.plotly_chart(fig_province, use_container_width=True, config=PLOTLY_CONFIG)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 3: Line chart + Donut
# ---------------------------------------------------------------------------
col3, col4 = st.columns([1.4, 1])

with col3:
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    fig_line = year_growth_chart(year_df)
    st.plotly_chart(fig_line, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    fig_donut = sector_donut_chart(sector_df)
    st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)
    st.markdown("</div>", unsafe_allow_html=True)