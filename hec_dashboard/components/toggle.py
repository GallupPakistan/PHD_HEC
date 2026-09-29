import streamlit as st

from charts._base import MODES


def _remember():
    st.session_state["_value_mode"] = st.session_state["_value_mode_widget"]


def value_mode_toggle() -> str:
    """Sidebar 'Numbers / Percentage' switch. Returns the chosen mode.

    The choice is kept in session_state so it carries over when the user
    moves between pages (Streamlit drops a widget's own state when the
    widget isn't rendered on the page being left)."""
    current = st.session_state.get("_value_mode", MODES[0])
    st.sidebar.markdown("#### Show values as")
    mode = st.sidebar.radio(
        "Show values as", MODES,
        index=MODES.index(current), horizontal=True,
        key="_value_mode_widget", on_change=_remember,
        label_visibility="collapsed",
    )
    st.session_state["_value_mode"] = mode
    st.sidebar.caption(
        "Switches count charts between headcounts and % shares. "
        "Charts that are already percentages are unchanged."
    )
    return mode
