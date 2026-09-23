import streamlit as st
from config.settings import APP_NAME, APP_SUBTITLE, LAST_UPDATED, PAGE_ICON


def render_header(page_title: str, page_subtitle: str = None, stat: dict = None, stat_icon: str = "🏛️"):
    """Renders the single big navy header block: a top row (last-updated
    badge, app brand, optional headline stat) plus the current page's
    title and subtitle underneath — all inside one card.

    Pass `stat={"title": ..., "value": ...}` to show a headline number
    on the right (e.g. Total HEIs, Total Faculty).

    NOTE: HTML built as one flat, unindented string — Streamlit's markdown
    renderer treats 4+ leading spaces as a literal code block (a Markdown
    rule), so multi-line/indented f-strings must never be passed to
    st.markdown(unsafe_allow_html=True).
    """
    stat_html = ""
    if stat:
        stat_html = (
            '<div class="hec-header-stat">'
            f'<div class="hec-header-stat-icon">{stat_icon}</div>'
            "<div>"
            f'<p class="hec-header-stat-value">{stat["value"]}</p>'
            f'<p class="hec-header-stat-title">{stat["title"]}</p>'
            "</div>"
            "</div>"
        )

    subtitle_html = f"<p>{page_subtitle}</p>" if page_subtitle else ""

    html = (
        '<div class="hec-header">'
        '<div class="hec-header-top">'
        f'<div class="hec-header-badge">📅 Last updated: <b>{LAST_UPDATED}</b></div>'
        '<div class="hec-header-brand">'
        f'<div class="hec-header-icon">{PAGE_ICON}</div>'
        "<div>"
        f'<p class="hec-header-app-title">{APP_NAME}</p>'
        f'<p class="hec-header-app-subtitle">{APP_SUBTITLE}</p>'
        "</div>"
        "</div>"
        f"{stat_html}"
        "</div>"
        '<div class="hec-header-page">'
        f"<h1>{page_title}</h1>"
        f"{subtitle_html}"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
