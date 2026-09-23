import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout, headroom_range
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE

LEVEL_COLS = ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD"]
LEVEL_LABELS = {"MS_Mphil": "MS/Mphil"}


def _spread_positions(series_a, series_b):
    """Per-point text positions for a two-line comparison chart: whichever
    series is higher at a given x gets its label pushed further up, the
    lower one further down -- so the two labels track their own line and
    move apart instead of colliding when the lines sit close together or
    cross over (a fixed top/bottom split gets this backwards at a crossover
    and makes the labels overlap the *other* line instead)."""
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
            text=[f"{v:,.0f}" for v in gender_agg["Female"]],
            textposition=female_pos,
            textfont=dict(size=9, color=BOARD_COLOR_SEQUENCE[7]),
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
            text=[f"{v:,.0f}" for v in gender_agg["Male"]],
            textposition=male_pos,
            textfont=dict(size=9, color=COLORS["public"]),
        )
    )
    fig.update_layout(**base_layout("Year & Gender-wise Passout", height=500))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.42, xanchor="center", x=0.5),
        xaxis_title="HEI Provided Year",
        yaxis_title="Student Passout",
        hovermode="x unified",
        margin=dict(t=50, b=150, l=60, r=30),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(
        tickformat=",",
        range=headroom_range(gender_agg["Female"], gender_agg["Male"], pad=0.16, floor_pad=0.14),
    )
    return fig


def gender_donut_chart(gender_totals_df):
    fig = px.pie(
        gender_totals_df,
        names="Gender",
        values="Count",
        hole=0,
        color="Gender",
        color_discrete_map={"Female": BOARD_COLOR_SEQUENCE[7], "Male": COLORS["public"]},
    )
    fig.update_traces(
        textinfo="label+value+percent",
        textposition="outside",
        texttemplate="%{label}<br>%{value:,} (%{percent})",
        textfont=dict(size=12, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Gender Wise Student Passout", height=420))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=50, b=30, l=60, r=60),
    )
    return fig


def level_heatmap_chart(level_agg):
    """Year x Level matrix. Levels differ in scale by two orders of
    magnitude (Bachelor is ~100x PGD/PhD), so a single linear color scale
    across the whole matrix would leave the smaller levels looking blank.
    Colors are therefore normalised per level (row-wise min-max) so each
    level's own year-to-year trend is visible; the text/hover always show
    the real headcount, never the normalised color value."""
    years = level_agg["Year"].astype(str).tolist()
    y_labels = [LEVEL_LABELS.get(c, c) for c in LEVEL_COLS]

    z_actual = [level_agg[col].tolist() for col in LEVEL_COLS]
    z_norm = []
    for row in z_actual:
        lo, hi = min(row), max(row)
        span = (hi - lo) or 1
        z_norm.append([(v - lo) / span for v in row])
    text = [[f"{v:,}" for v in row] for row in z_actual]

    fig = go.Figure(
        go.Heatmap(
            x=years, y=y_labels, z=z_norm,
            text=text, texttemplate="%{text}",
            textfont=dict(size=10, color=COLORS["text_on_light"]),
            hovertemplate="%{y}, %{x}<br>%{text} graduates<extra></extra>",
            colorscale=[[0, "#EAF1FF"], [0.5, COLORS["accent_light"]], [1, COLORS["accent"]]],
            showscale=False,
            xgap=4, ygap=4,
        )
    )
    fig.update_layout(**base_layout("Year, Gender & Level-wise Passout", height=420))
    fig.update_layout(margin=dict(t=50, b=70, l=100, r=30))
    fig.update_xaxes(tickangle=-25, automargin=True, side="bottom")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12))
    return fig