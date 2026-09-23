import plotly.graph_objects as go
from charts._base import base_layout
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE

# Same Bachelor/Master/MS-Mphil/PGD/PhD -> color mapping used by
# level_stacked_bar_chart on the Enrolment Summary page, so a level keeps
# the same color wherever it appears across the dashboard.
LEVEL_COLS = [("Bachelor", BOARD_COLOR_SEQUENCE[0]), ("Master", BOARD_COLOR_SEQUENCE[1]),
              ("MS_Mphil", BOARD_COLOR_SEQUENCE[2]), ("PGD", BOARD_COLOR_SEQUENCE[3]),
              ("PhD", BOARD_COLOR_SEQUENCE[4])]
LEVEL_LABELS = {"MS_Mphil": "MS/Mphil"}


def level_ratio_area_chart(level_table):
    """100%-stacked area: each level's share of enrolment, year over year.
    A smooth filled area (rather than a bar or heatmap, both already used
    elsewhere in this dashboard) reads naturally as a composition *shifting*
    over time. No per-point value labels -- with 5 stacked series across 12
    years that would crowd the plot -- hover shows the exact split instead."""
    x = level_table["Year"].astype(str)
    fig = go.Figure()
    for col, color in LEVEL_COLS:
        fig.add_trace(
            go.Scatter(
                x=x, y=level_table[col], name=LEVEL_LABELS.get(col, col),
                mode="lines", stackgroup="one", groupnorm="percent",
                line=dict(width=0.5, color=color),
                fillcolor=color,
                hovertemplate="%{fullData.name}: %{y:.1f}%<extra></extra>",
            )
        )
    fig.update_layout(**base_layout("Year & Level-wise Enrolment (Share)", height=460))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5),
        xaxis_title="Year",
        yaxis_title="Share of Enrolment",
        hovermode="x unified",
        margin=dict(t=50, b=100, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return fig


def discipline_gender_diverging_chart(discipline_table):
    """Diverging ('population pyramid' style) horizontal bar: Female% bars
    extend left of a zero axis, Male% bars extend right -- the standard way
    to compare two groups' share across many categories, and a different
    chart family from the stacked bars used for discipline elsewhere."""
    df = discipline_table
    labels = df["Discipline"].astype(str)
    female = df["Female_Pct"]
    male = df["Male_Pct"]
    max_val = max(female.max(), male.max())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=-female, name="Female", orientation="h",
        marker=dict(color=BOARD_COLOR_SEQUENCE[7]),
        text=[f"{v:.1f}%" for v in female], textposition="outside",
        textfont=dict(size=10, color=BOARD_COLOR_SEQUENCE[7]),
        hovertemplate="%{y}<br>Female: %{text}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=labels, x=male, name="Male", orientation="h",
        marker=dict(color=COLORS["public"]),
        text=[f"{v:.1f}%" for v in male], textposition="outside",
        textfont=dict(size=10, color=COLORS["public"]),
        hovertemplate="%{y}<br>Male: %{text}<extra></extra>",
    ))
    fig.update_layout(barmode="overlay")
    fig.update_layout(**base_layout("Discipline & Gender-wise Enrolment (Share)", height=560))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="center", x=0.5),
        xaxis_title="Share of Enrolment",
        bargap=0.35,
        margin=dict(t=50, b=70, l=280, r=60),
    )
    pad = max_val * 1.30
    fig.update_xaxes(
        range=[-pad, pad],
        tickvals=[-max_val, -max_val / 2, 0, max_val / 2, max_val],
        ticktext=[f"{max_val:.0f}%", f"{max_val / 2:.0f}%", "0%", f"{max_val / 2:.0f}%", f"{max_val:.0f}%"],
        zeroline=True, zerolinewidth=2, zerolinecolor=COLORS["primary"],
    )
    fig.update_yaxes(automargin=True, tickfont=dict(size=11))
    return fig


def sector_share_trend_chart(sector_table):
    """Private-sector share of enrolment over time, plotted against a 50%
    reference line so the story is 'who's ahead, and when did it flip' --
    fill color switches at the crossover instead of using two full-height
    series, which keeps a 2-category, sums-to-100 table from just repeating
    the stacked-area or two-line trend patterns used elsewhere on this
    dashboard. No per-point labels; hover carries the exact split."""
    x = sector_table["Year"].astype(str)
    private = sector_table["Private"]
    public = sector_table["Public"]

    above = private.where(private >= 50)
    below = private.where(private < 50)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=above, mode="none", fill="tozeroy", fillcolor="rgba(11,30,77,0.18)",
        name="Private-led", showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=below, mode="none", fill="tozeroy", fillcolor="rgba(59,130,246,0.18)",
        name="Public-led", showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=private, mode="lines+markers", name="Private Share",
        line=dict(color=COLORS["private"], width=3), marker=dict(size=6),
        customdata=public,
        hovertemplate="Private: %{y:.1f}%<br>Public: %{customdata:.1f}%<extra></extra>",
    ))
    fig.add_hline(
        y=50, line=dict(color=COLORS["neutral"], width=1.5, dash="dash"),
        annotation_text="50% split", annotation_position="top left",
        annotation_font=dict(size=10, color=COLORS["text_on_light_muted"]),
    )
    fig.update_layout(**base_layout("Year and Sector-wise Enrolment (Share)", height=460))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="Private Sector Share",
        hovermode="x unified",
        margin=dict(t=50, b=90, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return fig
