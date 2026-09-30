import streamlit as st

from styles.theme import PLOTLY_CONFIG


def chart_card(fig, caption: str = None):
    """White card around a Plotly chart, with an optional small caption."""
    st.markdown('<div class="hec-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    if caption:
        st.caption(caption)
    st.markdown("</div>", unsafe_allow_html=True)
