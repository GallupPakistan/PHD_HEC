from styles.theme import COLORS, FONTS


def base_layout(title: str = "", height: int = 420) -> dict:
    return dict(
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(family=FONTS["heading"], size=16, color=COLORS["text_on_light"]),
        ),
        height=height,
        margin=dict(t=50, b=40, l=40, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONTS["body"], color=COLORS["text_on_light"]),
        hoverlabel=dict(bgcolor=COLORS["primary"], font_color="#FFFFFF"),
    )


def headroom_range(*series, pad=0.18, floor_pad=0.0):
    """[0, max * (1+pad)] across one or more value series, so a data-point
    label positioned above/outside the highest bar or marker has room to
    render without being clipped by the plot area edge. floor_pad adds a
    small negative buffer at 0 for charts whose 'below' labels (e.g. a
    two-sided line chart) also need breathing room."""
    peak = max(float(s.max()) for s in series if len(s))
    return [-peak * floor_pad, peak * (1 + pad)]