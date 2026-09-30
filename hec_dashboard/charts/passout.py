import plotly.express as px
import plotly.graph_objects as go
from charts._base import apply_finalize, base_layout, headroom_range, is_pct, share, legend_below
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


def gender_line_chart(gender_agg, mode="Numbers"):
    """Percentage mode plots Female / Male as a share of that year's passout."""
    pct = is_pct(mode)
    f_raw = gender_agg["Female"].reset_index(drop=True)
    m_raw = gender_agg["Male"].reset_index(drop=True)
    if pct:
        both = f_raw + m_raw
        female, male = share(f_raw, both), share(m_raw, both)
        fmt = lambda v: f"{v:.1f}%"
        hover = "%{y:.1f}%"
    else:
        female, male = f_raw, m_raw
        fmt = lambda v: f"{v:,.0f}"
        hover = "%{y:,.0f}"
    female_pos, male_pos = _spread_positions(female, male)
    x = gender_agg["Year"].astype(str).reset_index(drop=True)
    fig = go.Figure()
    for name, y, color, pos in (("Female", female, BOARD_COLOR_SEQUENCE[7], female_pos),
                                ("Male", male, COLORS["public"], male_pos)):
        fig.add_trace(
            go.Scatter(
                x=x, y=y, mode="lines+markers+text", name=name,
                line=dict(color=color, width=3), marker=dict(size=6),
                text=[fmt(v) for v in y], textposition=pos,
                textfont=dict(size=9, color=color),
                hovertemplate=f"{hover}<extra>{name}</extra>",
            )
        )
    fig.update_layout(**base_layout("Year & Gender-wise Passout", height=500))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.42, "Gender"),
        xaxis_title="HEI Provided Year",
        yaxis_title="Share of Passout (%)" if pct else "Student Passout",
        hovermode="x unified",
        margin=dict(t=50, b=150, l=60, r=30),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(range=headroom_range(female, male, pad=0.16, floor_pad=0.14))
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    else:
        fig.update_yaxes(tickformat=",")
    return fig


def gender_donut_chart(gender_totals_df, mode="Numbers"):
    pct = is_pct(mode)
    fig = px.pie(
        gender_totals_df,
        names="Gender",
        values="Count",
        hole=0,
        color="Gender",
        color_discrete_map={"Female": BOARD_COLOR_SEQUENCE[7], "Male": COLORS["public"]},
    )
    fig.update_traces(
        textposition="outside",
        texttemplate="%{percent}" if pct else "%{value:,} (%{percent})",
        textfont=dict(size=12, color=COLORS["text_on_light"]),
        sort=False,
    )
    fig.update_layout(**base_layout("Gender Wise Student Passout", height=420))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.05, "Gender"),
        margin=dict(t=50, b=60, l=60, r=60),
    )
    return fig


def level_heatmap_chart(level_agg, mode="Numbers"):
    """Year x Level matrix. Levels differ in scale by two orders of
    magnitude (Bachelor is ~100x PGD/PhD), so colours are normalised per
    level (row-wise min-max) so each level's own year-to-year trend is
    visible; the text/hover always show the real value, never the
    normalised colour value. Percentage mode shows each cell as a share of
    that year's total passout instead of a headcount."""
    pct = is_pct(mode)
    years = level_agg["Year"].astype(str).tolist()
    y_labels = [LEVEL_LABELS.get(c, c) for c in LEVEL_COLS]

    year_total = level_agg[LEVEL_COLS].sum(axis=1).reset_index(drop=True)
    if pct:
        z_actual = [share(level_agg[col], year_total).tolist() for col in LEVEL_COLS]
        text = [[f"{v:.1f}%" for v in row] for row in z_actual]
        unit = "of that year's graduates"
    else:
        z_actual = [level_agg[col].tolist() for col in LEVEL_COLS]
        text = [[f"{v:,}" for v in row] for row in z_actual]
        unit = "graduates"
    z_norm = []
    for row in z_actual:
        lo, hi = min(row), max(row)
        span = (hi - lo) or 1
        z_norm.append([(v - lo) / span for v in row])

    fig = go.Figure(
        go.Heatmap(
            x=years, y=y_labels, z=z_norm,
            text=text, texttemplate="%{text}",
            textfont=dict(size=10, color=COLORS["text_on_light"]),
            hovertemplate="%{y}, %{x}<br>%{text} " + unit + "<extra></extra>",
            colorscale=[[0, "#EAF1FF"], [0.5, COLORS["accent_light"]], [1, COLORS["accent"]]],
            showscale=True,
            colorbar=dict(
                title=dict(text="Within each level", side="right"),
                tickvals=[0, 1], ticktext=["Lowest year", "Highest year"],
                len=0.8, thickness=14,
            ),
            xgap=4, ygap=4,
        )
    )
    fig.update_layout(**base_layout("Year, Gender & Level-wise Passout" + (" (% of year)" if pct else ""), height=420))
    fig.update_layout(margin=dict(t=50, b=70, l=100, r=30))
    fig.update_xaxes(tickangle=-25, automargin=True, side="bottom")
    fig.update_yaxes(automargin=True, tickfont=dict(size=12))
    return fig


apply_finalize(globals())
