import plotly.express as px
import plotly.graph_objects as go
from charts._base import apply_finalize, base_layout, headroom_range, is_pct, share, legend_below
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE


def _fmt_millions(v):
    return f"{v / 1_000_000:.2f}M"


def _spread_positions(series_a, series_b):
    """Per-point text positions for a two-line comparison chart: whichever
    series is higher at a given x gets its label pushed further up, the
    lower one further down -- so the two labels move apart instead of
    colliding when the lines sit close together."""
    pos_a, pos_b = [], []
    for a, b in zip(series_a, series_b):
        if a >= b:
            pos_a.append("top center")
            pos_b.append("bottom center")
        else:
            pos_a.append("bottom center")
            pos_b.append("top center")
    return pos_a, pos_b


def _two_line_chart(df, a, b, a_color, b_color, title, mode, y_title):
    """Shared builder for the Female/Male and Public/Private trend charts.
    Numbers mode plots headcounts; Percentage mode plots each series as its
    share of (a + b) for that year, so the two lines always sum to 100%."""
    pct = is_pct(mode)
    if pct:
        both = df[a].reset_index(drop=True) + df[b].reset_index(drop=True)
        ya, yb = share(df[a], both), share(df[b], both)
    else:
        ya, yb = df[a].reset_index(drop=True), df[b].reset_index(drop=True)

    fmt = (lambda v: f"{v:.1f}%") if pct else _fmt_millions
    hover = "%{y:.1f}%" if pct else "%{y:,.0f}"
    pos_a, pos_b = _spread_positions(ya, yb)
    x = df["Year"].astype(str).reset_index(drop=True)

    fig = go.Figure()
    for name, y, color, pos in ((a, ya, a_color, pos_a), (b, yb, b_color, pos_b)):
        fig.add_trace(
            go.Scatter(
                x=x, y=y, mode="lines+markers+text", name=name,
                line=dict(color=color, width=3), marker=dict(size=6),
                text=[fmt(v) for v in y], textposition=pos,
                textfont=dict(size=8, color=color),
                hovertemplate=f"{hover}<extra>{name}</extra>",
            )
        )
    fig.update_layout(**base_layout(title, height=500))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.38),
        xaxis_title="Year",
        yaxis_title=("Share of Enrolment (%)" if pct else y_title),
        hovermode="x unified",
        margin=dict(t=60, b=130, l=50, r=30),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(range=headroom_range(ya, yb, pad=0.18, floor_pad=0.12))
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    else:
        fig.update_yaxes(tickformat=".1s")
    return fig


def gender_line_chart(gender_agg, mode="Numbers"):
    return _two_line_chart(
        gender_agg, "Female", "Male", BOARD_COLOR_SEQUENCE[7], COLORS["public"],
        "Gender-wise Enrolment Over the Years", mode, "Enrolment",
    )


def sector_trend_chart(sector_agg, mode="Numbers"):
    return _two_line_chart(
        sector_agg, "Public", "Private", COLORS["public"], COLORS["private"],
        "Sector-wise Enrolment Over the Years", mode, "Enrolment",
    )


def discipline_gender_bar_chart(disc_df, mode="Numbers"):
    """Horizontal stacked bar: Female/Male enrolment per discipline, sorted
    ascending by Total so the largest discipline renders at the top.
    Percentage mode shows every segment as a share of overall enrolment
    (all segments together add up to 100%)."""
    pct = is_pct(mode)
    df = disc_df.sort_values("Total", ascending=True).reset_index(drop=True)
    labels = df["Discipline"].astype(str)
    grand = float(df["Total"].sum())

    if pct:
        female, male, totals = share(df["Female"], grand), share(df["Male"], grand), share(df["Total"], grand)
        fmt = lambda v: f"{v:.1f}%"
        seg_text = lambda s: [f"{v:.1f}%" if v >= 1.5 else "" for v in s]
    else:
        female, male, totals = df["Female"], df["Male"], df["Total"]
        fmt = lambda v: f"{int(v):,}"
        seg_text = lambda s: [""] * len(s)

    fig = go.Figure()
    for name, vals, color in (("Female", female, BOARD_COLOR_SEQUENCE[7]), ("Male", male, COLORS["public"])):
        fig.add_trace(
            go.Bar(
                y=labels, x=vals, name=name, orientation="h",
                marker=dict(color=color),
                text=seg_text(vals), textposition="inside",
                textfont=dict(size=9, color="#FFFFFF"),
                hovertemplate=("%{y}<br>" + name + ": %{x:.2f}%<extra></extra>") if pct
                else ("%{y}<br>" + name + ": %{x:,.0f}<extra></extra>"),
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_layout(**base_layout("Discipline & Gender-wise Enrolment", height=560))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.10),
        xaxis_title="Share of Enrolment (%)" if pct else "Enrolment",
        bargap=0.35,
        margin=dict(t=50, b=70, l=280, r=90),
        annotations=[
            dict(
                x=total, y=label, text=fmt(total),
                xanchor="left", yanchor="middle", showarrow=False,
                font=dict(size=10, color=COLORS["text_on_light"]), xshift=10,
            )
            for total, label in zip(totals, labels)
        ],
    )
    fig.update_xaxes(range=[0, float(totals.max()) * 1.20])
    if pct:
        fig.update_xaxes(ticksuffix="%", tickformat=".0f")
    else:
        fig.update_xaxes(tickformat=".2s")
    fig.update_yaxes(automargin=True, tickfont=dict(size=11))
    return fig


def level_pie_chart(level_summary_df, mode="Percentage"):
    """Numbers mode sizes/labels slices by headcount (needs a 'Count' column
    from load_level_ratio_summary); Percentage mode by share."""
    pct = is_pct(mode) or "Count" not in level_summary_df.columns
    fig = px.pie(
        level_summary_df,
        names="Level",
        values="Percentage" if pct else "Count",
        hole=0,
        color="Level",
        color_discrete_sequence=BOARD_COLOR_SEQUENCE,
    )
    fig.update_traces(
        textinfo="percent" if pct else "value+percent",
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Level-wise Enrolment", height=460))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.22, "Qualification"),
        margin=dict(t=50, b=90, l=40, r=40),
    )
    return fig


def gender_pie_chart(gender_summary_df, mode="Numbers"):
    pct = is_pct(mode)
    fig = px.pie(
        gender_summary_df,
        names="Gender",
        values="Count",
        color="Gender",
        color_discrete_map={"Female": BOARD_COLOR_SEQUENCE[7], "Male": COLORS["public"]},
    )
    fig.update_traces(
        textinfo="percent" if pct else "value+percent",
        textposition="outside",
        textfont=dict(size=13, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Gender-wise Enrolment", height=460))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.20, "Gender"),
        margin=dict(t=50, b=80, l=40, r=40),
    )
    return fig


apply_finalize(globals())
