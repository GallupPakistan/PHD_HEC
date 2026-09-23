import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout, headroom_range
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


def gender_line_chart(gender_agg):
    female_pos, male_pos = _spread_positions(gender_agg["Female"], gender_agg["Male"])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=gender_agg["Year"].astype(str),
            y=gender_agg["Female"],
            mode="lines+markers+text",
            name="Female",
            line=dict(color=BOARD_COLOR_SEQUENCE[7], width=3),  # pink
            marker=dict(size=6),
            text=[_fmt_millions(v) for v in gender_agg["Female"]],
            textposition=female_pos,
            textfont=dict(size=8, color=BOARD_COLOR_SEQUENCE[7]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=gender_agg["Year"].astype(str),
            y=gender_agg["Male"],
            mode="lines+markers+text",
            name="Male",
            line=dict(color=COLORS["public"], width=3),
            marker=dict(size=6),
            text=[_fmt_millions(v) for v in gender_agg["Male"]],
            textposition=male_pos,
            textfont=dict(size=8, color=COLORS["public"]),
        )
    )
    fig.update_layout(**base_layout("Gender-wise Enrolment Over the Years", height=500))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
        xaxis_title="Year",
        yaxis_title="Enrolment",
        hovermode="x unified",
        margin=dict(t=60, b=130, l=50, r=30),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(tickformat=".1s", range=headroom_range(gender_agg["Female"], gender_agg["Male"], pad=0.18, floor_pad=0.12))
    return fig


def discipline_gender_bar_chart(disc_df):
    """Horizontal stacked bar: Female/Male enrolment per discipline, sorted
    ascending by Total so the largest discipline renders at the top. Bars
    get a wide bargap and a padded value-label so long discipline names
    (left) and the total labels (right of each bar) never crowd the plot."""
    df = disc_df.sort_values("Total", ascending=True).reset_index(drop=True)
    labels = df["Discipline"].astype(str)
    totals = df["Total"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=labels, x=df["Female"], name="Female", orientation="h",
            marker=dict(color=BOARD_COLOR_SEQUENCE[7]),
        )
    )
    fig.add_trace(
        go.Bar(
            y=labels, x=df["Male"], name="Male", orientation="h",
            marker=dict(color=COLORS["public"]),
        )
    )
    fig.update_layout(barmode="stack")
    fig.update_layout(**base_layout("Discipline & Gender-wise Enrolment", height=560))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="center", x=0.5),
        xaxis_title="Enrolment",
        bargap=0.35,
        margin=dict(t=50, b=70, l=280, r=90),
        annotations=[
            dict(
                x=total, y=label, text=f"{int(total):,}",
                xanchor="left", yanchor="middle", showarrow=False,
                font=dict(size=10, color=COLORS["text_on_light"]), xshift=10,
            )
            for total, label in zip(totals, labels)
        ],
    )
    fig.update_xaxes(tickformat=".2s", range=[0, float(totals.max()) * 1.20])
    fig.update_yaxes(automargin=True, tickfont=dict(size=11))
    return fig


def level_pie_chart(level_summary_df):
    fig = px.pie(
        level_summary_df,
        names="Level",
        values="Percentage",
        hole=0,
        color="Level",
        color_discrete_sequence=BOARD_COLOR_SEQUENCE,
    )
    fig.update_traces(
        textinfo="percent",
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Level-wise Enrolment", height=460))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5,
            title=dict(text="Qualification"),
        ),
        margin=dict(t=50, b=90, l=40, r=40),
    )
    return fig


def gender_pie_chart(gender_summary_df):
    fig = px.pie(
        gender_summary_df,
        names="Gender",
        values="Count",
        color="Gender",
        color_discrete_map={"Female": BOARD_COLOR_SEQUENCE[7], "Male": COLORS["public"]},
    )
    fig.update_traces(
        textinfo="percent",
        textposition="outside",
        textfont=dict(size=13, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Gender-wise Enrolment", height=460))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5,
            title=dict(text="Gender"),
        ),
        margin=dict(t=50, b=80, l=40, r=40),
    )
    return fig


def sector_trend_chart(sector_agg):
    public_pos, private_pos = _spread_positions(sector_agg["Public"], sector_agg["Private"])
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sector_agg["Year"].astype(str),
            y=sector_agg["Public"],
            mode="lines+markers+text",
            name="Public",
            line=dict(color=COLORS["public"], width=3),
            marker=dict(size=6),
            text=[_fmt_millions(v) for v in sector_agg["Public"]],
            textposition=public_pos,
            textfont=dict(size=8, color=COLORS["public"]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sector_agg["Year"].astype(str),
            y=sector_agg["Private"],
            mode="lines+markers+text",
            name="Private",
            line=dict(color=COLORS["private"], width=3),
            marker=dict(size=6),
            text=[_fmt_millions(v) for v in sector_agg["Private"]],
            textposition=private_pos,
            textfont=dict(size=8, color=COLORS["private"]),
        )
    )
    fig.update_layout(**base_layout("Sector-wise Enrolment Over the Years", height=500))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
        xaxis_title="Year",
        yaxis_title="Enrolment",
        hovermode="x unified",
        margin=dict(t=60, b=130, l=50, r=30),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(tickformat=".1s", range=headroom_range(sector_agg["Public"], sector_agg["Private"], pad=0.18, floor_pad=0.12))
    return fig