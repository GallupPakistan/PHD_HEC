"""Clean, reusable chart builders.

Design rules (why the charts here don't look messy):
  * long category names go on a HORIZONTAL bar's y-axis, never rotated on x
  * time axes carry no per-point text labels -- exact values are in the hover
  * legends sit ABOVE the plot, so they can never collide with tick labels
  * every chart is meant to be drawn full width, one after the other
"""
import math
import plotly.graph_objects as go

from charts._base import base_layout, fmt_compact
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE

FEMALE = BOARD_COLOR_SEQUENCE[7]
MALE = COLORS["public"]
PUBLIC = COLORS["public"]
PRIVATE = COLORS["private"]
GOLD = COLORS["gold"]

PROVINCE_COLORS = {
    "Punjab": "#3B82F6", "Sindh": "#C9A84C", "Khyber Pakhtunkhwa": "#22C55E",
    "Balochistan": "#EF4444", "Federal": "#A855F7", "AJ&K": "#F97316",
    "Gilgit-Baltistan": "#14B8A6",
}
LEVEL_COLORS = {
    "Bachelor": BOARD_COLOR_SEQUENCE[0], "Master": BOARD_COLOR_SEQUENCE[1],
    "MS/Mphil": BOARD_COLOR_SEQUENCE[2], "PGD": BOARD_COLOR_SEQUENCE[3],
    "PhD": BOARD_COLOR_SEQUENCE[4],
}


def short_year(y):
    return str(y).replace(" (Provisional)", "*")


def _frame(fig, title, height, legend=False, l=60, r=30, b=60, t=None):
    fig.update_layout(**base_layout(title, height=height))
    top = t if t is not None else (105 if legend else 60)
    fig.update_layout(
        showlegend=legend,
        margin=dict(t=top, b=b, l=l, r=r),
        title=dict(text=title, x=0.02, xanchor="left", y=0.97, yanchor="top",
                   font=dict(family="'Cinzel', serif", size=16, color=COLORS["text_on_light"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0.0,
                    font=dict(size=12), title=dict(text="")),
        bargap=0.3,
    )
    return fig


def _hbar_height(n, per=38, base=110, minimum=300):
    return max(minimum, int(n * per + base))


# ---------------------------------------------------------------------------
# Bars
# ---------------------------------------------------------------------------
def hbar(labels, values, title, color=None, colors=None, xtitle="", fmt=None, per=38):
    """Single-series horizontal bar, biggest on top, value at the bar end."""
    fmt = fmt or (lambda v: f"{v:,.0f}")
    pairs = sorted(zip(labels, values), key=lambda p: p[1])          # ascending -> largest on top
    labels_s = [str(p[0]) for p in pairs]
    vals = [float(p[1]) for p in pairs]
    if colors:
        cmap = dict(zip([str(l) for l in labels], colors))
        marker = [cmap[l] for l in labels_s]
    else:
        marker = color or COLORS["accent"]
    fig = go.Figure(go.Bar(
        y=labels_s, x=vals, orientation="h", marker_color=marker,
        text=[fmt(v) for v in vals], textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>",
    ))
    _frame(fig, title, _hbar_height(len(labels_s), per), l=10, r=70)
    fig.update_xaxes(title=xtitle, range=[0, (max(vals) if vals else 1) * 1.15 or 1], tickformat="~s", showgrid=True,
                     gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


def stacked_hbar(cats, series, title, xtitle="", min_label_share=0.09, per=42):
    """series = [(name, values, color), ...]. Segment labels only when the
    segment is wide enough to hold them; the total is written past the end."""
    cats = [str(c) for c in cats]
    totals = [sum(float(s[1][i]) for s in series) for i in range(len(cats))]
    order = sorted(range(len(cats)), key=lambda i: totals[i])              # ascending
    cats_o = [cats[i] for i in order]
    peak = max(totals) if totals else 1
    fig = go.Figure()
    for name, vals, color in series:
        v = [float(vals[i]) for i in order]
        fig.add_trace(go.Bar(
            y=cats_o, x=v, name=name, orientation="h",
            marker=dict(color=color, line=dict(color="#FFFFFF", width=1)),
            text=[fmt_compact(x) if x >= peak * min_label_share else "" for x in v],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(size=11, color="#FFFFFF"),
            hovertemplate="%{y}<br>" + name + ": %{x:,.0f}<extra></extra>",
        ))
    fig.update_layout(barmode="stack")
    _frame(fig, title, _hbar_height(len(cats_o), per, base=130), legend=True, l=10, r=90)
    fig.update_layout(annotations=[
        dict(x=totals[i], y=cats[i], text=f"<b>{totals[i]:,.0f}</b>", showarrow=False,
             xanchor="left", xshift=8, font=dict(size=11, color=COLORS["text_on_light"]))
        for i in order
    ])
    fig.update_xaxes(title=xtitle, range=[0, peak * 1.16 or 1], tickformat="~s",
                     showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


def vbar(labels, values, title, color=None, ytitle="", xtitle="", height=420, fmt=None):
    """Vertical bars for SHORT labels only (decades, years)."""
    fmt = fmt or (lambda v: f"{v:,.0f}")
    fig = go.Figure(go.Bar(
        x=[str(l) for l in labels], y=[float(v) for v in values], marker_color=color or COLORS["accent"],
        text=[fmt(v) for v in values], textposition="outside", cliponaxis=False,
        textfont=dict(size=12, color=COLORS["text_on_light"]),
        hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>",
    ))
    _frame(fig, title, height, b=70)
    peak = max(float(v) for v in values) if len(values) else 1
    fig.update_yaxes(title=ytitle, range=[0, peak * 1.18 or 1], tickformat="~s", gridcolor="rgba(0,0,0,0.06)")
    fig.update_xaxes(title=xtitle, type="category")
    return fig


def gap_bar(labels, female, male, title, per=38):
    """Female minus Male per category: right of zero = more women, left = more men."""
    diff = [float(f) - float(m) for f, m in zip(female, male)]
    pairs = sorted(zip([str(l) for l in labels], diff), key=lambda p: p[1])
    ls, ds = [p[0] for p in pairs], [p[1] for p in pairs]
    fig = go.Figure(go.Bar(
        y=ls, x=ds, orientation="h",
        marker_color=[FEMALE if d >= 0 else MALE for d in ds], showlegend=False,
        text=[f"{d:+,.0f}" for d in ds], textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        hovertemplate="%{y}<br>Female − Male: %{x:+,.0f}<extra></extra>",
    ))
    # legend proxies
    for name, color in (("More women (Female > Male)", FEMALE), ("More men (Male > Female)", MALE)):
        fig.add_trace(go.Bar(y=[None], x=[None], name=name, marker_color=color, orientation="h"))
    _frame(fig, title, _hbar_height(len(ls), per, base=130), legend=True, l=10, r=80)
    span = max(abs(min(ds)), abs(max(ds))) * 1.25 or 1
    fig.update_xaxes(range=[-span, span], tickformat="~s", zeroline=True, zerolinewidth=2,
                     zerolinecolor=COLORS["primary"], gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


# ---------------------------------------------------------------------------
# Lines / areas  (no per-point text -- hover carries the numbers)
# ---------------------------------------------------------------------------
def multi_line(x, series, title, ytitle="", xtitle="", height=440, dtick=None, area=False):
    """series = [(name, values, color), ...]"""
    fig = go.Figure()
    for name, vals, color in series:
        fig.add_trace(go.Scatter(
            x=list(x), y=list(vals), name=name, mode="lines+markers",
            line=dict(color=color, width=3), marker=dict(size=6),
            **({"fill": "tozeroy", "fillcolor": _rgba(color, 0.12)} if area else {}),
            hovertemplate="%{y:,.0f}<extra>" + name + "</extra>",
        ))
    _frame(fig, title, height, legend=len(series) > 1, l=70, b=70)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title=ytitle, tickformat="~s", rangemode="tozero", gridcolor="rgba(0,0,0,0.06)")
    fig.update_xaxes(title=xtitle, **({"dtick": dtick} if dtick else {}))
    return fig


def _rgba(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


# ---------------------------------------------------------------------------
# Pies, tree-maps, heat-maps
# ---------------------------------------------------------------------------
def donut(labels, values, title, colors=None, height=440, hole=0.55, center=None):
    fig = go.Figure(go.Pie(
        labels=[str(l) for l in labels], values=[float(v) for v in values], hole=hole, sort=False,
        marker=dict(colors=colors or BOARD_COLOR_SEQUENCE[:len(labels)], line=dict(color="#FFFFFF", width=2)),
        texttemplate="%{value:,.0f}<br>(%{percent})", textposition="inside",
        insidetextorientation="horizontal", textfont=dict(size=12, color="#FFFFFF"),
        hovertemplate="%{label}<br>%{value:,.0f} (%{percent})<extra></extra>",
    ))
    _frame(fig, title, height, legend=False, l=20, r=20, b=70)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, title=dict(text="")),
        uniformtext_minsize=10, uniformtext_mode="hide",
    )
    if center is None:
        center = f"{sum(float(v) for v in values):,.0f}<br>Total"
    if center:
        fig.add_annotation(text=center, x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=COLORS["text_on_light"]))
    return fig


def treemap(labels, values, title, height=520, colors=None):
    colors = colors or [BOARD_COLOR_SEQUENCE[i % len(BOARD_COLOR_SEQUENCE)] for i in range(len(labels))]
    fig = go.Figure(go.Treemap(
        labels=[str(l) for l in labels], values=[float(v) for v in values], parents=[""] * len(labels),
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        texttemplate="<b>%{label}</b><br>%{value:,.0f}", textfont=dict(size=12, color="#FFFFFF"),
        hovertemplate="%{label}<br>%{value:,.0f} (%{percentRoot:.1%})<extra></extra>",
        tiling=dict(pad=3),
    ))
    _frame(fig, title, height, l=10, r=10, b=10)
    return fig


def heatmap(z, x_labels, y_labels, title, colorbar_title="", height=None, cell_fmt=None):
    """z = list of rows (one per y label)."""
    cell_fmt = cell_fmt or fmt_compact
    text = [[cell_fmt(v) for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=list(x_labels), y=list(y_labels), text=text, texttemplate="%{text}",
        textfont=dict(size=11),
        colorscale=[[0, "#EAF1FF"], [0.5, COLORS["accent_light"]], [1, COLORS["primary"]]],
        xgap=3, ygap=3,
        colorbar=dict(title=dict(text=colorbar_title, side="right"), thickness=14, len=0.9, tickformat="~s"),
        hovertemplate="%{y}<br>%{x}<br>%{z:,.0f}<extra></extra>",
    ))
    _frame(fig, title, height or _hbar_height(len(y_labels), 52, base=130, minimum=340), l=10, r=20, b=70)
    fig.update_yaxes(automargin=True, autorange="reversed", tickfont=dict(size=12))
    fig.update_xaxes(side="bottom", tickfont=dict(size=11))
    return fig
