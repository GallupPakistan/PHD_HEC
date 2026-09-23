import streamlit as st

from config.settings import APP_NAME, APP_SUBTITLE, PAGE_ICON
from styles.css import inject_css
from components.topbar import render_topbar

st.set_page_config(page_title=APP_NAME, page_icon=PAGE_ICON, layout="wide")
inject_css()
render_topbar()

st.markdown('<div class="hec-card">', unsafe_allow_html=True)
st.markdown(f"### Welcome to {APP_NAME}")
st.write(APP_SUBTITLE)
st.write("Use the sidebar to navigate between pages:")
st.markdown(
    """
    - **Universities** — HEIs by province, sector, city map, and growth over the years
    - **Enrolment (Summary)** — Gender, level, and sector-wise enrolment trends
    """
)
st.markdown("</div>", unsafe_allow_html=True)
