import streamlit as st
from styles.theme import COLORS


def kpi_card(title: str, value: str, color: str = None):
    """NOTE: HTML built as a single line with no leading whitespace — see
    the comment in components/header.py for why that matters.

    `color` sets a left accent stripe + the value's text color, so KPI
    cards can each carry a distinct theme color instead of being plain
    white. Defaults to the dashboard's main accent blue if not given.
    """
    color = color or COLORS["accent"]
    html = (
        f'<div class="hec-kpi-card" style="border-left: 5px solid {color};">'
        "<div>"
        f'<p class="hec-kpi-title">{title}</p>'
        f'<p class="hec-kpi-value" style="color: {color};">{value}</p>'
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)