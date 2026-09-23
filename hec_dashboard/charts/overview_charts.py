import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE


def _fmt_millions(v):
    return f"{v / 1_000_000:.2f}M"


def hei_growth_mini_chart(year_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=year_df["Cumulative_Total"],
            mode="lines",
            name="Total HEIs",
            line=dict(color=COLORS["gold"], width=3),
            fill="tozeroy",
            fillcolor="rgba(201,168,76,0.15)",
        )
    )
    fig.update_layout(**base_layout("HEIs Established Over the Years (1959–2025)", height=340))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="Total HEIs",
        margin=dict(t=50, b=40, l=50, r=20),
        hovermode="x unified",
    )
    return fig


def province_hei_bar_chart(province_bars):
    fig = go.Figure(
        go.Bar(
            x=province_bars["Province"],
            y=province_bars["Total"],
            marker_color=BOARD_COLOR_SEQUENCE[: len(province_bars)],
            text=province_bars["Total"],
            textposition="outside",
            textfont=dict(size=11, color=COLORS["text_on_light"]),
        )
    )
    fig.update_layout(**base_layout("HEIs by Province", height=340))
    fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Total HEIs",
        margin=dict(t=50, b=60, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(range=[0, province_bars["Total"].max() * 1.2])
    return fig


def enrolment_trend_mini_chart(gender_agg):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=gender_agg["Year"].astype(str),
            y=gender_agg["Total"],
            mode="lines+markers",
            name="Total Enrolment",
            line=dict(color=COLORS["accent"], width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.12)",
        )
    )
    fig.update_layout(**base_layout("Total Enrolment Over the Years", height=340))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="Enrolment",
        margin=dict(t=50, b=60, l=50, r=20),
        hovermode="x unified",
    )
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(tickformat=".1s")
    return fig


def level_stacked_bar_chart(level_agg):
    level_cols = [("Bachelor", BOARD_COLOR_SEQUENCE[0]), ("Master", BOARD_COLOR_SEQUENCE[1]),
                  ("MS_Mphil", BOARD_COLOR_SEQUENCE[2]), ("PGD", BOARD_COLOR_SEQUENCE[3]),
                  ("PhD", BOARD_COLOR_SEQUENCE[4])]
    labels = {"MS_Mphil": "MS/Mphil"}
    fig = go.Figure()
    for col, color in level_cols:
        fig.add_trace(
            go.Bar(
                x=level_agg["Year"].astype(str),
                y=level_agg[col],
                name=labels.get(col, col),
                marker_color=color,
            )
        )
    fig.update_layout(**base_layout("Enrolment by Qualification Level", height=480))
    fig.update_layout(
        barmode="stack",
        xaxis_title="Year",
        yaxis_title="Enrolment",
        legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
        margin=dict(t=50, b=140, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    fig.update_yaxes(tickformat=".1s")
    return fig


def discipline_bar_chart_overview(disc_df):
    max_val = disc_df["Total"].max()
    fig = go.Figure(
        go.Bar(
            x=disc_df["Total"],
            y=disc_df["Discipline"],
            orientation="h",
            marker_color=BOARD_COLOR_SEQUENCE[: len(disc_df)],
            text=[f"{v:,.0f}" for v in disc_df["Total"]],
            textposition="outside",
            textfont=dict(size=11, color=COLORS["text_on_light"]),
            cliponaxis=False,
        )
    )
    fig.update_layout(**base_layout("Enrolment by Discipline (Top 8)", height=420))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Enrolment",
        yaxis_title="",
        margin=dict(t=50, b=40, l=10, r=110),
    )
    fig.update_xaxes(tickformat=".1s", range=[0, max_val * 1.32])
    fig.update_yaxes(automargin=True)
    return fig


def faculty_province_bar_chart(prov_agg):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=prov_agg["Province"], y=prov_agg["PhD"], name="PhD", marker_color=COLORS["gold"]))
    fig.add_trace(go.Bar(x=prov_agg["Province"], y=prov_agg["Non_PhD"], name="Non-PhD", marker_color=COLORS["accent"]))
    fig.update_layout(**base_layout("Faculty by Province (PhD vs Non-PhD)", height=440))
    fig.update_layout(
        barmode="group",
        xaxis_title="",
        yaxis_title="Faculty Count",
        legend=dict(orientation="h", yanchor="top", y=-0.30, xanchor="center", x=0.5),
        margin=dict(t=50, b=130, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-35, automargin=True)
    return fig


def faculty_gender_donut_chart(gender_df):
    total = int(gender_df["Count"].sum())
    fig = px.pie(
        gender_df,
        names="Gender",
        values="Count",
        hole=0.55,
        color="Gender",
        color_discrete_map={"Female": BOARD_COLOR_SEQUENCE[7], "Male": COLORS["public"]},
    )
    fig.update_traces(
        textinfo="value+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=12, color="#FFFFFF"),
        sort=False,
    )
    fig.update_layout(**base_layout("Faculty Gender Split", height=360))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        margin=dict(t=50, b=50, l=30, r=30),
        annotations=[dict(text=f"{total:,}<br>Total", x=0.5, y=0.5, font_size=14, showarrow=False)],
    )
    return fig


def graduates_trend_mini_chart(gender_agg):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=gender_agg["Year"].astype(str),
            y=gender_agg["Total"],
            mode="lines+markers",
            name="Total Graduates",
            line=dict(color=COLORS["positive"], width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.12)",
        )
    )
    fig.update_layout(**base_layout("Graduates (Passout) Over the Years", height=340))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="Graduates",
        margin=dict(t=50, b=60, l=50, r=20),
        hovermode="x unified",
    )
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(tickformat=".1s")
    return fig


def phd_year_bar_chart(phd_df):
    fig = go.Figure(
        go.Bar(
            x=phd_df["Year"],
            y=phd_df["Total PhDs Produced"],
            marker_color=COLORS["gold"],
        )
    )
    fig.update_layout(**base_layout("PhD Graduates Registered, by Year", height=340))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="PhDs Produced",
        margin=dict(t=50, b=60, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-45)
    return fig