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


# ---------------------------------------------------------------------------
# Bottom-of-chart layout: keep legends from colliding with x-axis labels
# ---------------------------------------------------------------------------
# A legend placed relative to the plot area (paper y < 0) can't know how tall
# the x tick labels will be -- long year labels such as
# "2024-25 (Provisional)" rotated in a narrow column need 60-90px, and the
# legend simply landed on top of them. finalize_fig() fixes that in one place:
#   * pins the legend to the bottom edge of the whole figure (yref="container")
#   * estimates the space the tick labels / axis title need and reserves
#     exactly that much bottom margin *above* the legend
#   * shortens "(Provisional)" to "*" (footnoted in the axis title)
# Every chart module calls apply_finalize(globals()) once at the bottom, so
# every public chart function gets this automatically.
import functools
import math

_CHAR_W = 6.8      # px per character of an axis tick label (12px font)
_LINE_H = 14       # px per line of tick label text


def _legend_entries(fig):
    names = []
    for t in fig.data:
        if getattr(t, "type", None) == "pie":
            names.extend(str(l) for l in (t.labels if t.labels is not None else []))
        elif t.showlegend is not False and t.name:
            names.append(str(t.name))
    return names


def _legend_height(fig, entries, avail=380):
    """Greedy-pack legend entries into rows of `avail` px; return pixel height."""
    size = (fig.layout.legend.font.size if fig.layout.legend.font.size else 12)
    cw = size * 0.58
    title = fig.layout.legend.title.text if fig.layout.legend.title else None
    used = (len(title) * cw + 14) if title else 0
    rows, row_w = 1, used
    for n in entries:
        w = len(n) * cw + 40
        if row_w + w > avail and row_w > 0:
            rows += 1
            row_w = 0
        row_w += w
    return rows * (size + 9) + 8


def _x_labels(fig):
    labels = []
    for t in fig.data:
        if getattr(t, "orientation", None) == "h":
            continue
        x = getattr(t, "x", None)
        if x is None:
            continue
        for v in list(x):
            if isinstance(v, str) and v not in labels:
                labels.append(v)
    return labels


def _tick_height(labels, angle):
    if not labels:
        return 22                                       # numeric ticks, horizontal
    lines = max(l.count("<br>") + 1 for l in labels)
    longest = max(max(len(p) for p in l.split("<br>")) for l in labels)
    a = math.radians(abs(angle))
    return int(longest * _CHAR_W * math.sin(a) + lines * _LINE_H * math.cos(a) + 10)


def _pick_angle(labels, explicit, plot_w=320):
    """Smallest tick rotation at which neighbouring labels don't overlap.
    Adjacent rotated labels are `spacing * sin(angle)` apart (perpendicular),
    and need about one text line (16px). `plot_w` is a deliberately narrow
    plot width (half-width columns), so wide layouts just get a slightly
    steeper angle than strictly needed -- never an overlap."""
    if not labels:
        return explicit or 0
    spacing = plot_w / len(labels)
    longest = max(max(len(p) for p in l.split("<br>")) for l in labels)
    if longest * _CHAR_W <= spacing * 0.9:
        return 0                                        # everything fits flat
    need = math.degrees(math.asin(min(1.0, 16.0 / spacing)))
    angle = next((a for a in (25, 35, 45, 60, 90) if a >= need), 90)
    if explicit is not None and abs(explicit) >= angle:
        return explicit                                 # chart already asked for steeper
    return -angle


def finalize_fig(fig):
    """Idempotent. Handles (a) figures with a horizontal legend below the plot
    and (b) heatmaps, whose year labels have the same overlap problem."""
    lay = fig.layout
    if isinstance(lay.meta, dict) and lay.meta.get("finalized"):
        return fig
    legend = lay.legend
    has_legend = bool(
        lay.showlegend is not False and legend is not None and legend.orientation == "h"
        and legend.y is not None and legend.y < 0
    )
    has_heat = any(getattr(t, "type", None) == "heatmap" for t in fig.data)
    if not (has_legend or has_heat):
        return fig

    entries = _legend_entries(fig) if has_legend else []
    legend_px = _legend_height(fig, entries) if has_legend else 0

    has_x_axis = any(getattr(t, "type", None) in ("bar", "scatter", "heatmap") for t in fig.data)
    t_margin = lay.margin.t if lay.margin.t is not None else 50
    b_old = lay.margin.b if lay.margin.b is not None else 40
    h_old = lay.height or 420
    plot_h = max(h_old - t_margin - b_old, 200)

    axis_px = 0
    if has_x_axis:
        labels = _x_labels(fig)
        # shorten "(Provisional)" -> "*" so year labels stop colliding with each other
        short = [l.replace(" (Provisional)", "*") for l in labels]
        provisional = short != labels
        angle = _pick_angle(short, lay.xaxis.tickangle)
        if labels:
            fig.update_xaxes(tickmode="array", tickvals=labels, ticktext=short, tickangle=angle)
            labels = short
        else:
            fig.update_xaxes(tickangle=angle)
        title = lay.xaxis.title.text if lay.xaxis.title else None
        if provisional:
            title = f"{title} (* provisional)" if title else "* provisional"
            fig.update_xaxes(title_text=title)
        axis_px = _tick_height(labels, angle) + (26 if title else 0)

    if has_x_axis:
        b_new = axis_px + legend_px + 16
    else:                                 # pies / donuts: only need room for the legend
        b_new = max(b_old, legend_px + 24)
    upd = dict(
        margin=dict(b=b_new),
        height=int(t_margin + plot_h + b_new) if has_x_axis else int(h_old + max(b_new - b_old, 0)),
        meta={"finalized": True},
    )
    if has_legend:
        upd["legend"] = dict(
            yref="container", y=0.0, yanchor="bottom", xanchor="center", x=0.5,
            **({"title": dict(side="left")} if (legend.title and legend.title.text) else {}),
        )
    fig.update_layout(**upd)
    return fig


def apply_finalize(ns):
    """Wrap every public chart function defined in module namespace `ns` so
    the Figure it returns goes through finalize_fig()."""
    import plotly.graph_objects as go
    for name, fn in list(ns.items()):
        if (name.startswith("_") or not callable(fn) or not hasattr(fn, "__module__")
                or fn.__module__ != ns["__name__"] or not hasattr(fn, "__code__")):
            continue

        def make(f):
            @functools.wraps(f)
            def wrapper(*a, **k):
                out = f(*a, **k)
                return finalize_fig(out) if isinstance(out, go.Figure) else out
            return wrapper

        ns[name] = make(fn)
