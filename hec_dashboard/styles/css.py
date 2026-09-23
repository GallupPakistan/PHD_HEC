import streamlit as st
from styles.theme import COLORS, FONTS


def inject_css():
    custom_css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: {FONTS['body']};
    }}

    .stApp {{
        background-color: {COLORS['bg_page']};
    }}

    /* ---- Unified header (badge row + big page title, one navy block) ---- */
    .hec-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        padding: 26px 36px 30px 36px;
        border-bottom: 3px solid {COLORS['accent']};
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(11, 30, 77, 0.25);
        box-sizing: border-box;
        position: relative;
        overflow: hidden;
    }}
    .hec-header::after {{
        content: "";
        position: absolute;
        top: 0; right: 0;
        width: 220px; height: 100%;
        background-image: radial-gradient(rgba(255,255,255,0.10) 1.5px, transparent 1.5px);
        background-size: 16px 16px;
        -webkit-mask-image: linear-gradient(to left, black, transparent);
        mask-image: linear-gradient(to left, black, transparent);
        pointer-events: none;
    }}
    .hec-header-top {{
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
        margin-bottom: 22px;
        position: relative;
        z-index: 1;
    }}
    .hec-header-badge {{
        background: rgba(255,255,255,0.06);
        border: 2px solid {COLORS['stat_icon_border']};
        border-radius: 6px;
        padding: 8px 16px;
        color: {COLORS['text_primary']};
        font-size: 0.85rem;
        white-space: nowrap;
        font-weight: 500;
    }}
    .hec-header-badge b {{
        font-weight: 700;
    }}
    .hec-header-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .hec-header-icon {{
        width: 44px;
        height: 44px;
        background: {COLORS['stat_icon_bg']};
        border: 2px solid {COLORS['stat_icon_border']};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }}
    .hec-header-app-title {{
        color: {COLORS['text_primary']};
        font-family: {FONTS['heading']};
        font-size: 1.15rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.3px;
        line-height: 1.2;
    }}
    .hec-header-app-subtitle {{
        color: {COLORS['accent_light']};
        font-size: 0.8rem;
        margin: 1px 0 0 0;
    }}
    .hec-header-stat {{
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255,255,255,0.06);
        border: 2px solid {COLORS['stat_icon_border']};
        border-radius: 10px;
        padding: 10px 22px;
    }}
    .hec-header-stat-icon {{
        width: 40px;
        height: 40px;
        background: {COLORS['stat_icon_bg']};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }}
    .hec-header-stat-value {{
        color: {COLORS['text_primary']};
        font-family: {FONTS['heading']};
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }}
    .hec-header-stat-title {{
        color: {COLORS['text_secondary']};
        font-size: 0.72rem;
        margin: 2px 0 0 0;
        white-space: nowrap;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .hec-header-page {{
        border-left: 4px solid {COLORS['accent']};
        padding-left: 18px;
        position: relative;
        z-index: 1;
    }}
    .hec-header-page h1 {{
        font-family: {FONTS['heading']};
        color: {COLORS['text_primary']};
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    .hec-header-page p {{
        color: {COLORS['text_secondary']};
        font-size: 0.95rem;
        margin: 6px 0 0 0;
    }}

    /* ---- Sidebar ---- */
    [data-testid='stSidebar'] {{
        background: {COLORS['primary']};
    }}
    [data-testid='stSidebar'] * {{
        color: {COLORS['text_primary']} !important;
    }}
    [data-testid='stSidebar'] h4 {{
        font-family: {FONTS['heading']};
        color: {COLORS['gold']} !important;
        font-size: 1rem;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }}

    /* Filter widgets must show DARK text on their white input surface */
    [data-testid='stSidebar'] [data-baseweb="select"] {{
        background: #FFFFFF;
        border-radius: 6px;
    }}
    [data-testid='stSidebar'] [data-baseweb="select"] * {{
        color: {COLORS['text_on_light']} !important;
    }}
    [data-testid='stSidebar'] [data-baseweb="select"] svg {{
        fill: {COLORS['text_on_light']} !important;
    }}
    [data-testid='stSidebar'] [data-baseweb="tag"] {{
        background: {COLORS['accent']} !important;
    }}
    [data-testid='stSidebar'] [data-baseweb="tag"] * {{
        color: #FFFFFF !important;
    }}
    [data-testid='stSidebar'] [data-baseweb="popover"] * {{
        color: {COLORS['text_on_light']} !important;
    }}
    [data-testid='stSidebar'] input::placeholder {{
        color: {COLORS['text_on_light_muted']} !important;
        opacity: 1;
    }}

    /* ---- Card container ---- */
    .hec-card {{
        background: {COLORS['card_bg_light']};
        border: 1px solid {COLORS['card_border_light']};
        box-shadow: 0 2px 4px {COLORS['card_shadow_light']};
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 18px;
    }}
    .hec-card h3 {{
        font-family: {FONTS['heading']};
        color: {COLORS['text_on_light']};
        font-size: 1.05rem;
        margin: 0 0 10px 0;
    }}

    /* ---- KPI card ---- */
    .hec-kpi-card {{
        background: {COLORS['card_bg_light']};
        border: 1px solid {COLORS['card_border_light']};
        box-shadow: 0 2px 4px {COLORS['card_shadow_light']};
        border-radius: 8px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        transition: box-shadow 0.15s ease, transform 0.15s ease;
    }}
    .hec-kpi-card:hover {{
        box-shadow: 0 4px 10px rgba(16, 24, 64, 0.14);
        transform: translateY(-1px);
    }}
    .hec-kpi-title {{
        color: {COLORS['text_on_light']};
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0;
    }}
    .hec-kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
        font-family: {FONTS['heading']};
        margin: 0;
    }}

    /* Hide default streamlit chrome that can cause visual clutter */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        display: none;
    }}
    .main .block-container {{
        padding-top: 1.5rem;
    }}
    """
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)