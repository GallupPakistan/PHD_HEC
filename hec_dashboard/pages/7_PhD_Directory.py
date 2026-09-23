import streamlit as st

from config.settings import APP_NAME, PAGE_ICON
from styles.css import inject_css
from styles.theme import PLOTLY_CONFIG
from components.header import render_header
from data.phd_directory_recipes import (
    total_phds,
    year_table,
    discipline_chart_data,
    subject_wordcloud_data,
)
from charts.phd_directory import discipline_bar_chart, subject_wordcloud_chart, phd_year_area_chart


def fmt_k(n):
    return f"{n / 1000:.1f}K"


st.set_page_config(page_title=f"{APP_NAME} — PhD Directory", page_icon=PAGE_ICON, layout="wide")
inject_css()
render_header(
    "PhD Country Directory",
    "PhD graduates produced by national universities, by year, discipline, and subject.",
    stat={"title": "PhD Graduates Registered", "value": fmt_k(total_phds())},
    stat_icon="🎓",
)

# ---------------------------------------------------------------------------
# Row 1: Year trend chart + Discipline bar chart
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    fig_year = phd_year_area_chart(year_table())
    st.plotly_chart(fig_year, use_container_width=True, config=PLOTLY_CONFIG)
    st.caption("2026 is a partial year still in progress, not a real drop-off.")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    fig_bar = discipline_bar_chart(discipline_chart_data())
    st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)
    st.caption("Excludes the small 'Generic programmes' bucket and records with no discipline recorded.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Row 2: Subject keyword word cloud
# ---------------------------------------------------------------------------
st.markdown('<div class="hec-card">', unsafe_allow_html=True)
fig_cloud = subject_wordcloud_chart(subject_wordcloud_data())
st.plotly_chart(fig_cloud, use_container_width=True, config=PLOTLY_CONFIG)
st.caption(
    "Top 45 subject keywords by PhDs produced; word size reflects popularity. "
    "A gender-wise breakdown isn't available in the provided PhD directory data, so it isn't shown here."
)
st.markdown("</div>", unsafe_allow_html=True)