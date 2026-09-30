import plotly.graph_objects as go
from charts._base import apply_finalize, base_layout, legend_below, is_pct, fmt_compact
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE

# Same Bachelor/Master/MS-Mphil/PGD/PhD -> color mapping used by
# level_stacked_bar_chart on the Enrolment Summary page, so a level keeps
# the same color wherever it appears across the dashboard.
LEVEL_COLS = [("Bachelor", BOARD_COLOR_SEQUENCE[0]), ("Master", BOARD_COLOR_SEQUENCE[1]),
              ("MS_Mphil", BOARD_COLOR_SEQUENCE[2]), ("PGD", BOARD_COLOR_SEQUENCE[3]),
              ("PhD", BOARD_COLOR_SEQUENCE[4])]
LEVEL_LABELS = {"MS_Mphil": "MS/Mphil"}


def level_ratio_area_chart(level_table, mode="Percentage"):
    """Percentage: 100%-stacked area, each level's share of enrolment year
    over year (a composition *shifting* over time). Numbers: the same stack
    but of raw headcounts, so the height of the stack is total enrolment.
    No per-point value labels -- 5 stacked series x 12 years would crowd the
    plot -- hover shows the exact figure instead."""
    pct = is_pct(mode)
    x = level_table["Year"].astype(str)
    fig = go.Figure()
    for col, color in LEVEL_COLS:
        fig.add_trace(
            go.Scatter(
                x=x, y=level_table[col], name=LEVEL_LABELS.get(col, col),
                mode="lines", stackgroup="one",
                **({"groupnorm": "percent"} if pct else {}),
                line=dict(width=0.5, color=color),
                fillcolor=color,
                hovertemplate=("%{fullData.name}: %{y:.1f}%<extra></extra>" if pct
                               else "%{fullData.name}: %{y:,.0f}<extra></extra>"),
            )
        )
    fig.update_layout(**base_layout("Year & Level-wise Enrolment" + (" (Share)" if pct else ""), height=460))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.28, "Qualification"),
        xaxis_title="Year",
        yaxis_title="Share of Enrolment (%)" if pct else "Enrolment",
        hovermode="x unified",
        margin=dict(t=50, b=110, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    if pct:
        fig.update_yaxes(ticksuffix="%", range=[0, 100])
    else:
        fig.update_yaxes(tickformat=".2s")
    return fig


def discipline_gender_diverging_chart(discipline_table, mode="Percentage"):
    """Diverging ('population pyramid' style) horizontal bar: Female bars
    extend left of a zero axis, Male bars extend right -- the standard way
    to compare two groups across many categories. Percentage mode uses the
    Female_Pct / Male_Pct columns; Numbers mode uses estimated Female / Male
    headcounts (see load_discipline_count_table_for_ratios)."""
    pct = is_pct(mode)
    df = discipline_table
    labels = df["Discipline"].astype(str)
    female = df["Female_Pct"] if pct else df["Female"]
    male = df["Male_Pct"] if pct else df["Male"]
    fmt = (lambda v: f"{v:.1f}%") if pct else (lambda v: fmt_compact(v))
    max_val = max(female.max(), male.max())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=-female, name="Female", orientation="h",
        marker=dict(color=BOARD_COLOR_SEQUENCE[7]),
        text=[fmt(v) for v in female], textposition="outside",
        textfont=dict(size=10, color=BOARD_COLOR_SEQUENCE[7]),
        hovertemplate="%{y}<br>Female: %{text}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=labels, x=male, name="Male", orientation="h",
        marker=dict(color=COLORS["public"]),
        text=[fmt(v) for v in male], textposition="outside",
        textfont=dict(size=10, color=COLORS["public"]),
        hovertemplate="%{y}<br>Male: %{text}<extra></extra>",
    ))
    fig.update_layout(barmode="overlay")
    fig.update_layout(**base_layout(
        "Discipline & Gender-wise Enrolment" + (" (Share)" if pct else " (Estimated Headcount)"), height=560))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.10, "Gender"),
        xaxis_title="Share of Enrolment" if pct else "Estimated Enrolment",
        bargap=0.35,
        margin=dict(t=50, b=70, l=280, r=60),
    )
    pad = max_val * 1.30
    ticks = [-max_val, -max_val / 2, 0, max_val / 2, max_val]
    tick_fmt = (lambda v: f"{v:.0f}%") if pct else (lambda v: fmt_compact(v))
    fig.update_xaxes(
        range=[-pad, pad],
        tickvals=ticks,
        ticktext=[tick_fmt(abs(t)) for t in ticks],
        zeroline=True, zerolinewidth=2, zerolinecolor=COLORS["primary"],
    )
    fig.update_yaxes(automargin=True, tickfont=dict(size=11))
    return fig


def _sector_count_chart(sector_table):
    """Numbers-mode counterpart: Private vs Public enrolment headcount per year."""
    x = sector_table["Year"].astype(str)
    fig = go.Figure()
    for name, color, pos in (("Private", COLORS["private"], "top center"),
                             ("Public", COLORS["public"], "bottom center")):
        y = sector_table[name]
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines+markers+text", name=name,
            line=dict(color=color, width=3), marker=dict(size=6),
            text=[fmt_compact(v) for v in y], textposition=pos,
            textfont=dict(size=9, color=color),
            hovertemplate="%{y:,.0f}<extra>" + name + "</extra>",
        ))
    fig.update_layout(**base_layout("Year and Sector-wise Enrolment", height=460))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.30, "Sector"),
        xaxis_title="Year",
        yaxis_title="Enrolment",
        hovermode="x unified",
        margin=dict(t=50, b=130, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(tickformat=".2s", rangemode="tozero")
    return fig


def sector_share_trend_chart(sector_table, mode="Percentage"):
    """Numbers mode plots headcounts instead (see _sector_count_chart).
    Private-sector share of enrolment over time, plotted against a 50%
    reference line so the story is 'who's ahead, and when did it flip' --
    fill color switches at the crossover instead of using two full-height
    series, which keeps a 2-category, sums-to-100 table from just repeating
    the stacked-area or two-line trend patterns used elsewhere on this
    dashboard. No per-point labels; hover carries the exact split."""
    if not is_pct(mode):
        return _sector_count_chart(sector_table)
    x = sector_table["Year"].astype(str)
    private = sector_table["Private"]
    public = sector_table["Public"]

    above = private.where(private >= 50)
    below = private.where(private < 50)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=above, mode="none", fill="tozeroy", fillcolor="rgba(11,30,77,0.18)",
        name="Private-led (above 50%)", showlegend=True, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=below, mode="none", fill="tozeroy", fillcolor="rgba(59,130,246,0.18)",
        name="Public-led (below 50%)", showlegend=True, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=private, mode="lines+markers+text", name="Private Share",
        line=dict(color=COLORS["private"], width=3), marker=dict(size=6),
        text=[f"{v:.0f}%" for v in private], textposition="top center",
        textfont=dict(size=9, color=COLORS["private"]),
        customdata=public,
        hovertemplate="Private: %{y:.1f}%<br>Public: %{customdata:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=[50] * len(x), mode="lines", name="50% split",
        line=dict(color=COLORS["neutral"], width=1.5, dash="dash"), hoverinfo="skip",
    ))
    fig.update_layout(**base_layout("Year and Sector-wise Enrolment (Share)", height=460))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.30),
        xaxis_title="Year",
        yaxis_title="Private Sector Share",
        hovermode="x unified",
        margin=dict(t=50, b=130, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return fig


apply_finalize(globals())
