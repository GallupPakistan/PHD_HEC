import pandas as pd

from styles.theme import COLORS, FONTS

# Display modes for the sidebar toggle (see components/toggle.py)
MODES = ["Numbers", "Percentage"]


def is_pct(mode) -> bool:
    return mode == "Percentage"


def share(values, total=None):
    """Return `values` as a % of `total` (defaults to the sum of `values`).
    Zero / missing totals give 0 instead of NaN/inf so charts never break."""
    v = pd.Series(values).astype(float).reset_index(drop=True)
    if total is None:
        total = v.sum()
    if isinstance(total, pd.Series):
        t = total.astype(float).reset_index(drop=True).replace(0, float("nan"))
        return (v / t * 100).fillna(0)
    if not total:
        return v * 0
    return v / float(total) * 100


def fmt_compact(v) -> str:
    """12,345 -> 12.3K, 1,234,567 -> 1.23M — short enough for data labels."""
    v = float(v)
    a = abs(v)
    if a >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if a >= 1_000:
        return f"{v / 1_000:.1f}K"
    return f"{v:,.0f}"


def fmt_pct(v, decimals: int = 1) -> str:
    return f"{float(v):.{decimals}f}%"


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


def legend_below(y: float = -0.25, title: str = None) -> dict:
    """Horizontal, centred legend under the plot — one place to keep every chart's legend consistent."""
    legend = dict(orientation="h", yanchor="top", y=y, xanchor="center", x=0.5)
    if title:
        legend["title"] = dict(text=title)
    return legend


def headroom_range(*series, pad=0.18, floor_pad=0.0):
    """[0, max * (1+pad)] across one or more value series, so a data-point
    label positioned above/outside the highest bar or marker has room to
    render without being clipped by the plot area edge. floor_pad adds a
    small negative buffer at 0 for charts whose 'below' labels (e.g. a
    two-sided line chart) also need breathing room."""
    peak = max(float(s.max()) for s in series if len(s))
    return [-peak * floor_pad, peak * (1 + pad)]
