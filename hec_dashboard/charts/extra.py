"""Clean, reusable chart builders.

Design rules (why the charts here don't look messy):
  * long category names go on a HORIZONTAL bar's y-axis, never rotated on x
  * time axes carry no per-point text labels -- exact values are in the hover
  * legends sit ABOVE the plot, so they can never collide with tick labels
  * every chart is meant to be drawn full width, one after the other
"""
import math
import plotly.graph_objects as go

from charts._base import base_layout, fmt_compact, is_pct
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


def _shares(values, total=None):
    """values as % of `total` (default: their own sum). Zero total -> zeros."""
    vals = [float(v) for v in values]
    denom = float(total) if total else sum(vals)
    return [(v / denom * 100 if denom else 0.0) for v in vals]


def _pct_ticks(fig, axis, peak):
    """Percent axis: '%' suffix, decimals only when the values are small."""
    fmt = ".0f" if peak >= 5 else ".1f"
    (fig.update_xaxes if axis == "x" else fig.update_yaxes)(ticksuffix="%", tickformat=fmt)


# ---------------------------------------------------------------------------
# Bars   (every builder takes mode="Percentage" | "Numbers"; default = %)
# ---------------------------------------------------------------------------
def hbar(labels, values, title, color=None, colors=None, xtitle="", fmt=None, per=38,
         mode="Percentage", total=None):
    """Single-series horizontal bar, biggest on top, value at the bar end.
    Percentage mode = share of `total` (defaults to the sum of the bars)."""
    pct = is_pct(mode)
    fmt = fmt or (lambda v: f"{v:,.0f}")
    pairs = sorted(zip(labels, values), key=lambda p: p[1])          # ascending -> largest on top
    labels_s = [str(p[0]) for p in pairs]
    raw = [float(p[1]) for p in pairs]
    vals = _shares(raw, total) if pct else raw
    if colors:
        cmap = dict(zip([str(l) for l in labels], colors))
        marker = [cmap[l] for l in labels_s]
    else:
        marker = color or COLORS["accent"]
    fig = go.Figure(go.Bar(
        y=labels_s, x=vals, orientation="h", marker_color=marker,
        text=[f"{v:.1f}%" for v in vals] if pct else [fmt(v) for v in vals],
        textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        hovertemplate="%{y}<br>%{x:.1f}%<extra></extra>" if pct else "%{y}<br>%{x:,.0f}<extra></extra>",
    ))
    _frame(fig, title, _hbar_height(len(labels_s), per), l=10, r=70)
    peak = max(vals) if vals else 1
    fig.update_xaxes(title="Share of total (%)" if pct else xtitle, range=[0, peak * 1.15 or 1],
                     showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    if pct:
        _pct_ticks(fig, "x", peak)
    else:
        fig.update_xaxes(tickformat="~s")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


def stacked_hbar(cats, series, title, xtitle="", min_label_share=0.09, per=42, mode="Percentage"):
    """series = [(name, values, color), ...]. Segment labels only when the
    segment is wide enough to hold them.
    Numbers mode: absolute stacks, total written past the end.
    Percentage mode: every bar is 100% -- the mix *within* each category."""
    pct = is_pct(mode)
    cats = [str(c) for c in cats]
    totals = [sum(float(s[1][i]) for s in series) for i in range(len(cats))]
    order = sorted(range(len(cats)), key=lambda i: totals[i])              # ascending (by size)
    cats_o = [cats[i] for i in order]
    peak = max(totals) if totals else 1
    fig = go.Figure()
    for name, vals, color in series:
        v = [float(vals[i]) for i in order]
        if pct:
            v = [(x / totals[i] * 100 if totals[i] else 0.0) for x, i in zip(v, order)]
            text = [f"{x:.0f}%" if x >= 6 else "" for x in v]
            hover = "%{y}<br>" + name + ": %{x:.1f}%<extra></extra>"
        else:
            text = [fmt_compact(x) if x >= peak * min_label_share else "" for x in v]
            hover = "%{y}<br>" + name + ": %{x:,.0f}<extra></extra>"
        fig.add_trace(go.Bar(
            y=cats_o, x=v, name=name, orientation="h",
            marker=dict(color=color, line=dict(color="#FFFFFF", width=1)),
            text=text, textposition="inside", insidetextanchor="middle",
            textfont=dict(size=11, color="#FFFFFF"), hovertemplate=hover,
        ))
    fig.update_layout(barmode="stack")
    _frame(fig, title, _hbar_height(len(cats_o), per, base=130), legend=True, l=10, r=90)
    if pct:
        fig.update_xaxes(title="Share within each row (%)", range=[0, 100],
                         tickvals=[0, 20, 40, 60, 80, 100], ticksuffix="%", tickformat=".0f",
                         showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    else:
        fig.update_layout(annotations=[
            dict(x=totals[i], y=cats[i], text=f"<b>{totals[i]:,.0f}</b>", showarrow=False,
                 xanchor="left", xshift=8, font=dict(size=11, color=COLORS["text_on_light"]))
            for i in order
        ])
        fig.update_xaxes(title=xtitle, range=[0, peak * 1.16 or 1], tickformat="~s",
                         showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


def vbar(labels, values, title, color=None, ytitle="", xtitle="", height=420, fmt=None,
         mode="Percentage", total=None):
    """Vertical bars for SHORT labels only (decades, years)."""
    pct = is_pct(mode)
    fmt = fmt or (lambda v: f"{v:,.0f}")
    vals = _shares(values, total) if pct else [float(v) for v in values]
    fig = go.Figure(go.Bar(
        x=[str(l) for l in labels], y=vals, marker_color=color or COLORS["accent"],
        text=[f"{v:.1f}%" for v in vals] if pct else [fmt(v) for v in vals],
        textposition="outside", cliponaxis=False,
        textfont=dict(size=12, color=COLORS["text_on_light"]),
        hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>" if pct else "%{x}<br>%{y:,.0f}<extra></extra>",
    ))
    _frame(fig, title, height, b=70)
    peak = max(vals) if vals else 1
    fig.update_yaxes(title="Share of total (%)" if pct else ytitle, range=[0, peak * 1.18 or 1],
                     gridcolor="rgba(0,0,0,0.06)")
    if pct:
        _pct_ticks(fig, "y", peak)
    else:
        fig.update_yaxes(tickformat="~s")
    fig.update_xaxes(title=xtitle, type="category")
    return fig


def gap_bar(labels, female, male, title, per=38, mode="Percentage"):
    """Female minus Male per category: right of zero = more women, left = more men.
    Percentage mode = the gap in percentage points of that category's Female+Male
    (e.g. +20 pts means women are 60% and men 40%)."""
    pct = is_pct(mode)
    if pct:
        diff = [((float(f) - float(m)) / (float(f) + float(m)) * 100 if (float(f) + float(m)) else 0.0)
                for f, m in zip(female, male)]
    else:
        diff = [float(f) - float(m) for f, m in zip(female, male)]
    pairs = sorted(zip([str(l) for l in labels], diff), key=lambda p: p[1])
    ls, ds = [p[0] for p in pairs], [p[1] for p in pairs]
    fig = go.Figure(go.Bar(
        y=ls, x=ds, orientation="h",
        marker_color=[FEMALE if d >= 0 else MALE for d in ds], showlegend=False,
        text=[f"{d:+.1f} pts" if pct else f"{d:+,.0f}" for d in ds], textposition="outside", cliponaxis=False,
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        hovertemplate=("%{y}<br>Female − Male: %{x:+.1f} pts<extra></extra>" if pct
                       else "%{y}<br>Female − Male: %{x:+,.0f}<extra></extra>"),
    ))
    # legend proxies
    for name, color in (("More women (Female > Male)", FEMALE), ("More men (Male > Female)", MALE)):
        fig.add_trace(go.Bar(y=[None], x=[None], name=name, marker_color=color, orientation="h"))
    _frame(fig, title, _hbar_height(len(ls), per, base=130), legend=True, l=10, r=80)
    span = max(abs(min(ds)), abs(max(ds))) * 1.25 or 1
    fig.update_xaxes(range=[-span, span], zeroline=True, zerolinewidth=2,
                     zerolinecolor=COLORS["primary"], gridcolor="rgba(0,0,0,0.06)",
                     title="Gap in percentage points (Female % − Male %)" if pct else "")
    if pct:
        fig.update_xaxes(tickformat=".0f", ticksuffix=" pts")
    else:
        fig.update_xaxes(tickformat="~s")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12), ticksuffix="  ")
    return fig


# ---------------------------------------------------------------------------
# Lines / areas  (no per-point text -- hover carries the numbers)
# ---------------------------------------------------------------------------
def multi_line(x, series, title, ytitle="", xtitle="", height=440, dtick=None, area=False,
               mode="Percentage", pct_kind="share"):
    """series = [(name, values, color), ...]
    Percentage mode, by `pct_kind`:
      "share"   -> each series as % of all series at that x (lines add up to 100%)
      "growth"  -> year-over-year % change (for a single total series)
      "of_last" -> % of the final value (for a running total)."""
    pct = is_pct(mode)
    x = list(x)
    data = [(n, [float(v) for v in vals], c) for n, vals, c in series]
    if pct:
        if pct_kind == "growth":
            data = [(n, [None] + [((v[i] / v[i - 1] - 1) * 100 if v[i - 1] else None) for i in range(1, len(v))], c)
                    for n, v, c in data]
            ytitle = "Growth vs previous year (%)"
        elif pct_kind == "of_last":
            data = [(n, [(a / v[-1] * 100 if v[-1] else 0.0) for a in v], c) for n, v, c in data]
            ytitle = "Share of latest total (%)"
        else:
            col_tot = [sum(v[i] for _, v, _ in data) for i in range(len(x))]
            data = [(n, [(v[i] / col_tot[i] * 100 if col_tot[i] else 0.0) for i in range(len(x))], c)
                    for n, v, c in data]
            ytitle = "Share of total (%)"
    fig = go.Figure()
    for name, vals, color in data:
        fig.add_trace(go.Scatter(
            x=x, y=vals, name=name, mode="lines+markers",
            line=dict(color=color, width=3), marker=dict(size=6),
            **({"fill": "tozeroy", "fillcolor": _rgba(color, 0.12)} if area else {}),
            hovertemplate=("%{y:+.1f}%" if (pct and pct_kind == "growth") else "%{y:.1f}%") + "<extra>" + name + "</extra>"
            if pct else "%{y:,.0f}<extra>" + name + "</extra>",
        ))
    _frame(fig, title, height, legend=len(series) > 1, l=70, b=70)
    fig.update_layout(hovermode="x unified")
    if pct:
        fig.update_yaxes(title=ytitle, ticksuffix="%", tickformat=".0f", gridcolor="rgba(0,0,0,0.06)",
                         **({} if pct_kind == "growth" else {"rangemode": "tozero"}))
    else:
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
def donut(labels, values, title, colors=None, height=440, hole=0.55, center=None, mode="Percentage"):
    pct = is_pct(mode)
    fig = go.Figure(go.Pie(
        labels=[str(l) for l in labels], values=[float(v) for v in values], hole=hole, sort=False,
        marker=dict(colors=colors or BOARD_COLOR_SEQUENCE[:len(labels)], line=dict(color="#FFFFFF", width=2)),
        texttemplate="%{percent}" if pct else "%{value:,.0f}<br>(%{percent})", textposition="inside",
        insidetextorientation="horizontal", textfont=dict(size=12, color="#FFFFFF"),
        hovertemplate="%{label}<br>%{percent}<extra></extra>" if pct else "%{label}<br>%{value:,.0f} (%{percent})<extra></extra>",
    ))
    _frame(fig, title, height, legend=False, l=20, r=20, b=70)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, title=dict(text="")),
        uniformtext_minsize=10, uniformtext_mode="hide",
    )
    if pct:
        center = ""                                   # no headcount in the middle in % view
    elif center is None:
        center = f"{sum(float(v) for v in values):,.0f}<br>Total"
    if center:
        fig.add_annotation(text=center, x=0.5, y=0.5, showarrow=False, font=dict(size=15, color=COLORS["text_on_light"]))
    return fig


def treemap(labels, values, title, height=520, colors=None, mode="Percentage"):
    pct = is_pct(mode)
    colors = colors or [BOARD_COLOR_SEQUENCE[i % len(BOARD_COLOR_SEQUENCE)] for i in range(len(labels))]
    fig = go.Figure(go.Treemap(
        labels=[str(l) for l in labels], values=[float(v) for v in values], parents=[""] * len(labels),
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
        texttemplate="<b>%{label}</b><br>%{percentRoot:.1%}" if pct else "<b>%{label}</b><br>%{value:,.0f}",
        textfont=dict(size=12, color="#FFFFFF"),
        hovertemplate=("%{label}<br>%{percentRoot:.1%}<extra></extra>" if pct
                       else "%{label}<br>%{value:,.0f} (%{percentRoot:.1%})<extra></extra>"),
        tiling=dict(pad=3),
    ))
    _frame(fig, title, height, l=10, r=10, b=10)
    return fig


def heatmap(z, x_labels, y_labels, title, colorbar_title="", height=None, cell_fmt=None, mode="Percentage"):
    """z = list of rows (one per y label).
    Percentage mode: every cell is shown as a share of its column total
    (e.g. a province's share of that year, or a discipline's share of that province)."""
    pct = is_pct(mode)
    if pct:
        cols = list(zip(*z)) if len(z) else []
        col_tot = [sum(float(v) for v in c) for c in cols]
        z = [[(float(v) / col_tot[j] * 100 if col_tot[j] else 0.0) for j, v in enumerate(row)] for row in z]
        cell_fmt = lambda v: f"{v:.1f}%"
        colorbar_title = "% of column total"
    cell_fmt = cell_fmt or fmt_compact
    text = [[cell_fmt(v) for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=list(x_labels), y=list(y_labels), text=text, texttemplate="%{text}",
        textfont=dict(size=11),
        colorscale=[[0, "#EAF1FF"], [0.5, COLORS["accent_light"]], [1, COLORS["primary"]]],
        xgap=3, ygap=3,
        colorbar=dict(title=dict(text=colorbar_title, side="right"), thickness=14, len=0.9,
                      **({"tickformat": ".0f", "ticksuffix": "%"} if pct else {"tickformat": "~s"})),
        hovertemplate="%{y}<br>%{x}<br>%{z:.1f}%<extra></extra>" if pct else "%{y}<br>%{x}<br>%{z:,.0f}<extra></extra>",
    ))
    _frame(fig, title, height or _hbar_height(len(y_labels), 52, base=130, minimum=340), l=10, r=20, b=70)
    fig.update_yaxes(automargin=True, autorange="reversed", tickfont=dict(size=12))
    fig.update_xaxes(side="bottom", tickfont=dict(size=11))
    return fig
