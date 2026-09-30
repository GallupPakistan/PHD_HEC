import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout, is_pct, share, legend_below
from styles.theme import COLORS


def city_map_chart(city_df, mode="Numbers"):
    """Bubble map of HEIs per city. Percentage mode sizes bubbles and shows
    hover values as a share of all HEIs in the country."""
    pct = is_pct(mode)
    map_view = city_df.melt(
        id_vars=["City", "lon", "lat", "Total"],
        value_vars=["Public", "Private"],
        var_name="Sector",
        value_name="Count",
    )
    map_view = map_view[map_view["Count"] > 0].copy()
    grand = float(city_df["Total"].sum()) or 1.0
    map_view["Share"] = map_view["Count"] / grand * 100

    fig = px.scatter_map(
        map_view,
        lat="lat",
        lon="lon",
        size="Share" if pct else "Count",
        color="Sector",
        hover_name="City",
        hover_data=(
            {"Share": ":.1f", "Count": False, "lat": False, "lon": False} if pct
            else {"Count": True, "Share": False, "lat": False, "lon": False}
        ),
        labels={"Share": "% of all HEIs"},
        color_discrete_map={"Public": COLORS["public"], "Private": COLORS["private"]},
        size_max=38,
        zoom=4.2,
        center={"lat": 30.3, "lon": 69.5},
    )
    fig.update_layout(**base_layout("Map Location — City-wise HEIs" + (" (% of all HEIs)" if pct else ""), height=460))
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


def year_growth_chart(year_df, mode="Numbers"):
    """Percentage mode expresses both lines as a share of today's total HEIs:
    the running total becomes 'how much of today's system existed by year X'
    (reaching 100% at the latest year) and new-per-year becomes the share of
    all HEIs founded that year."""
    pct = is_pct(mode)
    total = float(year_df["Cumulative_Total"].max()) or 1.0
    cum = year_df["Cumulative_Total"] / total * 100 if pct else year_df["Cumulative_Total"]
    new = year_df["New_Added"] / total * 100 if pct else year_df["New_Added"]
    cum_text = [f"{v:.0f}%" for v in cum] if pct else list(cum)
    new_text = [f"{v:.1f}%" for v in new] if pct else list(new)
    hover = "%{y:.1f}%" if pct else "%{y:,.0f}"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=cum,
            mode="lines+markers+text",
            name="Total HEIs Established Over the Years" if not pct else "Cumulative % of today's HEIs",
            line=dict(color=COLORS["positive"], width=3),
            marker=dict(size=5),
            text=cum_text,
            textposition="top center",
            textfont=dict(size=8, color=COLORS["positive"]),
            hovertemplate=hover + "<extra>Cumulative</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=new,
            mode="lines+markers+text",
            name="New HEIs Established Within a Year" if not pct else "% of HEIs founded that year",
            line=dict(color=COLORS["private"], width=2),
            marker=dict(size=5),
            text=new_text,
            textposition="bottom center",
            textfont=dict(size=8, color=COLORS["private"]),
            hovertemplate=hover + "<extra>New</extra>",
        )
    )
    fig.update_layout(**base_layout("Increase in HEIs over the years (1959–2025)", height=480))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5),
        xaxis_title="Year",
        yaxis_title="Share of today's HEIs (%)" if pct else "Number of HEIs",
        hovermode="x unified",
        margin=dict(t=50, b=80, l=40, r=20),
    )
    if pct:
        fig.update_yaxes(range=[-5, 115], ticksuffix="%", tickformat=".0f")
    else:
        fig.update_yaxes(range=[-15, year_df["Cumulative_Total"].max() * 1.15])
    return fig


def province_sector_bar_chart(province_df, mode="Numbers"):
    """Percentage mode = Private/Public split *within* each province."""
    pct = is_pct(mode)
    df = province_df[province_df["Province"] != "TOTAL (PAKISTAN)"].copy()
    df[["Private", "Public"]] = df[["Private", "Public"]].fillna(0)
    both = df["Private"] + df["Public"]
    if pct:
        private, public = share(df["Private"], both), share(df["Public"], both)
        fmt = lambda v: f"{v:.1f}%"
    else:
        private, public = df["Private"], df["Public"]
        fmt = lambda v: f"{int(v):,}"
    x = df["Province"].reset_index(drop=True)
    fig = go.Figure()
    for name, y, color in (("Private", private, COLORS["private"]), ("Public", public, COLORS["public"])):
        fig.add_trace(go.Bar(
            x=x, y=y, name=name, marker_color=color,
            text=[fmt(v) for v in y], textposition="outside", cliponaxis=False,
            textfont=dict(size=10, color=COLORS["text_on_light"]),
        ))
    fig.update_layout(**base_layout("Province & Sector-wise HEIs", height=460))
    fig.update_layout(
        barmode="group",
        showlegend=True,
        xaxis_title="",
        yaxis_title="Share of Province HEIs (%)" if pct else "Number of HEIs",
        legend=legend_below(-0.38, "Sector"),
        margin=dict(t=50, b=130, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25)
    peak = float(max(private.max(), public.max())) if len(private) else 0
    fig.update_yaxes(range=[0, peak * 1.18 if peak else 1])
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    return fig


def sector_donut_chart(sector_df, mode="Numbers"):
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
        textinfo="percent" if is_pct(mode) else "value+percent",
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
