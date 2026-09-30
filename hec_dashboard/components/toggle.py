import streamlit as st

from charts._base import MODES


def value_mode_toggle(page_key: str = None, default: str = None) -> str:
    """'Numbers / Percentage' switch shown at the top of the page, right
    under the header. Returns the chosen mode.

    By default the choice is shared by every page (kept in session_state so
    it carries over on navigation). Pass `page_key` to give a page its own
    independent switch and `default` to choose what it starts on -- used by
    the Enrolment Ratios page, which is a 'ratios' page and so starts on
    Percentage."""
    state_key = f"_value_mode_{page_key}" if page_key else "_value_mode"
    widget_key = f"{state_key}_widget"
    current = st.session_state.get(state_key, default or MODES[0])

    def _remember():
        st.session_state[state_key] = st.session_state[widget_key]

    left, _ = st.columns([2, 3])
    with left:
        mode = st.radio(
            "📊 Show values as",
            MODES,
            index=MODES.index(current),
            horizontal=True,
            key=widget_key,
            on_change=_remember,
            help="Numbers = headcounts. Percentage = share of the total "
                 "(charts that are already percentages don't change).",
        )
    st.session_state[state_key] = mode
    return mode
