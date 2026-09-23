import streamlit as st
from config.settings import APP_NAME, APP_SUBTITLE, LAST_UPDATED


def render_topbar():
    st.markdown(
        f"""
        <div class="hec-topbar">
            <div>
                <p class="hec-topbar-title">{APP_NAME}</p>
                <p class="hec-topbar-subtitle">{APP_SUBTITLE}</p>
            </div>
            <div class="hec-topbar-badge">Last updated: {LAST_UPDATED}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
