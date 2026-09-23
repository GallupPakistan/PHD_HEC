import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout
from styles.theme import COLORS


def city_map_chart(city_df):
    map_view = city_df.melt(
        id_vars=["City", "lon", "lat", "Total"],
        value_vars=["Public", "Private"],
        var_name="Sector",
        value_name="Count",
    )
    map_view = map_view[map_view["Count"] > 0]

    fig = px.scatter_map(
        map_view,
        lat="lat",
        lon="lon",
        size="Count",
        color="Sector",
        hover_name="City",
        hover_data={"Count": True, "lat": False, "lon": False},
        color_discrete_map={"Public": COLORS["public"], "Private": COLORS["private"]},
        size_max=38,
        zoom=4.2,
        center={"lat": 30.3, "lon": 69.5},
    )
    fig.update_layout(**base_layout("Map Location — City-wise HEIs", height=460))
    fig.update_layout(
        map_style="open-street-map",
        margin=dict(t=90, b=10, l=0, r=0),
        legend=dict(
            orientation="h", yanchor="top", y=0.97, xanchor="left", x=0.01,
            title=dict(text="Sector"),
            bgcolor="rgba(255,255,255,0.85)",
        ),
    )
    return fig


def year_growth_chart(year_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=year_df["Cumulative_Total"],
            mode="lines+markers+text",
            name="Total HEIs Established Over the Years",
            line=dict(color=COLORS["positive"], width=3),
            marker=dict(size=5),
            text=year_df["Cumulative_Total"],
            textposition="top center",
            textfont=dict(size=8, color=COLORS["positive"]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=year_df["New_Added"],
            mode="lines+markers+text",
            name="New HEIs Established Within a Year",
            line=dict(color=COLORS["private"], width=2),
            marker=dict(size=5),
            text=year_df["New_Added"],
            textposition="bottom center",
            textfont=dict(size=8, color=COLORS["private"]),
        )
    )
    fig.update_layout(**base_layout("Increase in HEIs over the years (1959–2025)", height=480))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        xaxis_title="Year",
        yaxis_title="Number of HEIs",
        hovermode="x unified",
        margin=dict(t=50, b=80, l=40, r=20),
    )
    fig.update_yaxes(range=[-15, year_df["Cumulative_Total"].max() * 1.15])
    return fig


def province_sector_bar_chart(province_df):
    df = province_df[province_df["Province"] != "TOTAL (PAKISTAN)"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Province"], y=df["Private"], name="Private", marker_color=COLORS["private"]))
    fig.add_trace(go.Bar(x=df["Province"], y=df["Public"], name="Public", marker_color=COLORS["public"]))
    fig.update_layout(**base_layout("Province & Sector-wise HEIs", height=460))
    fig.update_layout(
        barmode="group",
        xaxis_title="",
        yaxis_title="Number of HEIs",
        legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
        margin=dict(t=50, b=130, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25)
    return fig


def sector_donut_chart(sector_df):
    total = int(sector_df["Count"].sum())
    fig = px.pie(
        sector_df,
        names="Sector",
        values="Count",
        hole=0.6,
        color="Sector",
        color_discrete_map={"Public": COLORS["public"], "Private": COLORS["private"]},
    )
    fig.update_traces(
        textinfo="value+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=13, color="#FFFFFF"),
        sort=False,
    )
    fig.update_layout(**base_layout("Sector-wise Number of HEIs", height=420))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        margin=dict(t=50, b=50, l=40, r=40),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        annotations=[
            dict(text=f"{total}<br>Total", x=0.5, y=0.5, font_size=16, showarrow=False)
        ],
    )
    return fig