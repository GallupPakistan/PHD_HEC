import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE

# PhD / Non-PhD is used consistently in gold/blue across every chart on this
# page (matches the PhD=gold, Non-PhD=accent convention already used for
# faculty on the Overview page) so the qualification split reads as one
# color language wherever it appears; Gender charts use the separate
# pink/blue convention used across the rest of the dashboard.
QUALIFICATION_COLORS = {"PhD": COLORS["gold"], "Non-PhD": COLORS["accent"]}


def province_qualification_bar_chart(province_df):
    """Horizontal stacked bar: PhD vs Non-PhD faculty per province, sorted
    ascending by Total so the largest province renders at the top. Wide
    bargap plus a padded total-label keep the province names (left) and the
    end-of-bar totals (right) from crowding the plot."""
    df = province_df.sort_values("Total", ascending=True).reset_index(drop=True)
    labels = df["Province"].astype(str)
    totals = df["Total"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=df["PhD"], name="PhD", orientation="h",
        marker=dict(color=QUALIFICATION_COLORS["PhD"], line=dict(color="#FFFFFF", width=1)),
    ))
    fig.add_trace(go.Bar(
        y=labels, x=df["Non_PhD"], name="Non-PhD", orientation="h",
        marker=dict(color=QUALIFICATION_COLORS["Non-PhD"], line=dict(color="#FFFFFF", width=1)),
    ))
    fig.update_layout(barmode="stack")
    fig.update_layout(**base_layout("PhD / Non-PhD Faculty by Province", height=460))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="center", x=0.5),
        xaxis_title="Faculty Count",
        bargap=0.35,
        margin=dict(t=50, b=80, l=180, r=90),
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


def qualification_share_donut(pct_row):
    """PhD vs Non-PhD share for the selected (single) year, as a donut with
    the PhD share called out in the centre — a trend line isn't meaningful
    with only one year of faculty data available."""
    long_df = pd.DataFrame({
        "Qualification": ["PhD", "Non-PhD"],
        "Percentage": [pct_row["PhD"], pct_row["Non_PhD"]],
    })
    lead = "PhD" if pct_row["PhD"] >= pct_row["Non_PhD"] else "Non-PhD"
    fig = px.pie(
        long_df, names="Qualification", values="Percentage", hole=0.55,
        color="Qualification", color_discrete_map=QUALIFICATION_COLORS,
    )
    fig.update_traces(
        textinfo="percent", textposition="inside", insidetextorientation="horizontal",
        textfont=dict(size=13, color="#FFFFFF"), sort=False,
        marker=dict(line=dict(color="#FFFFFF", width=2)),
        pull=[0.05 if q == lead else 0 for q in long_df["Qualification"]],
    )
    fig.update_layout(**base_layout("PhD Faculty Share", height=380))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.14, xanchor="center", x=0.5),
        margin=dict(t=50, b=60, l=30, r=30),
        annotations=[
            dict(text=f"{pct_row['PhD']:.1f}%<br>PhD", x=0.5, y=0.5, font_size=14, showarrow=False)
        ],
    )
    return fig


def sector_qualification_bar_chart(sector_df):
    """100%-stacked vertical bar: PhD vs Non-PhD qualification mix for each
    sector (Public/Private), so the two sectors' shares are directly
    comparable side by side."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sector_df["Sector"], y=sector_df["PhD_Pct"], name="PhD",
        marker=dict(color=QUALIFICATION_COLORS["PhD"], line=dict(color="#FFFFFF", width=1)),
        text=[f"{v:.1f}%" for v in sector_df["PhD_Pct"]],
        textposition="inside", textfont=dict(color="#FFFFFF", size=13),
    ))
    fig.add_trace(go.Bar(
        x=sector_df["Sector"], y=sector_df["Non_PhD_Pct"], name="Non-PhD",
        marker=dict(color=QUALIFICATION_COLORS["Non-PhD"], line=dict(color="#FFFFFF", width=1)),
        text=[f"{v:.1f}%" for v in sector_df["Non_PhD_Pct"]],
        textposition="inside", textfont=dict(color="#FFFFFF", size=13),
    ))
    fig.update_layout(barmode="stack")
    fig.update_layout(**base_layout("PhD / Non-PhD Faculty by Sector", height=420))
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
        yaxis_title="Share of Faculty",
        bargap=0.5,
        margin=dict(t=50, b=90, l=60, r=30),
    )
    fig.update_yaxes(range=[0, 108], ticksuffix="%")
    fig.update_xaxes(tickfont=dict(size=12))
    return fig
