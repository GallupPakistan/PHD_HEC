import streamlit as st

from charts._base import MODES  # ["Numbers", "Percentage"]

_KEY = "hec_show_numbers"


def value_mode_toggle(label: str = "Show Numbers") -> str:
    """Numbers switch, placed right under the KPI cards on every page.

    Charts show PERCENTAGES by default. Turning the switch on returns
    "Numbers" so every chart below it is drawn with actual counts.
    The choice is shared by all pages (it is remembered while you navigate).
    """
    # Streamlit drops a widget's state when the widget isn't drawn on a page;
    # re-assigning it here keeps the choice alive across page changes.
    if _KEY in st.session_state:
        st.session_state[_KEY] = st.session_state[_KEY]

    st.toggle(
        f"🔢 {label}",
        key=_KEY,
        value=False,
        help="Charts show percentages by default. Switch on to see actual numbers instead.",
    )
    return MODES[0] if st.session_state.get(_KEY) else MODES[1]
