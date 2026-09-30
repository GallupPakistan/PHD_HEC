import plotly.express as px
import plotly.graph_objects as go
from charts._base import base_layout, is_pct, share, fmt_compact, legend_below
from styles.theme import COLORS, BOARD_COLOR_SEQUENCE


def _fmt_millions(v):
    return f"{v / 1_000_000:.2f}M"


def hei_growth_mini_chart(year_df, mode="Numbers"):
    """Percentage mode = running total as a share of today's total HEIs."""
    pct = is_pct(mode)
    total = float(year_df["Cumulative_Total"].max()) or 1.0
    y = year_df["Cumulative_Total"] / total * 100 if pct else year_df["Cumulative_Total"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=year_df["Year"],
            y=y,
            mode="lines",
            name="Cumulative % of today's HEIs" if pct else "Total HEIs (running total)",
            line=dict(color=COLORS["gold"], width=3),
            fill="tozeroy",
            fillcolor="rgba(201,168,76,0.15)",
        )
    )
    fig.update_layout(**base_layout("HEIs Established Over the Years (1959–2025)", height=340))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.25),
        xaxis_title="Year",
        yaxis_title="Share of today's HEIs (%)" if pct else "Total HEIs",
        margin=dict(t=50, b=80, l=50, r=20),
        hovermode="x unified",
    )
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f", range=[0, 105])
    return fig


def province_hei_bar_chart(province_bars, mode="Numbers"):
    """One trace per province (drawn as 'overlay' so each bar stays centred
    on its tick) — that's what gives every colour a legend entry."""
    pct = is_pct(mode)
    total = float(province_bars["Total"].sum())
    fig = go.Figure()
    peak = 0
    for i, (prov, val) in enumerate(zip(province_bars["Province"], province_bars["Total"])):
        y = (val / total * 100) if (pct and total) else float(val)
        peak = max(peak, y)
        fig.add_trace(
            go.Bar(
                x=[prov], y=[y], name=prov,
                marker_color=BOARD_COLOR_SEQUENCE[i % len(BOARD_COLOR_SEQUENCE)],
                text=[f"{y:.1f}%" if pct else f"{int(val):,}"],
                textposition="outside", cliponaxis=False,
                textfont=dict(size=11, color=COLORS["text_on_light"]),
                hovertemplate=("%{x}: %{y:.1f}%<extra></extra>" if pct else "%{x}: %{y:,.0f}<extra></extra>"),
            )
        )
    fig.update_layout(**base_layout("HEIs by Province", height=400))
    fig.update_layout(
        barmode="overlay",
        showlegend=True,
        legend=legend_below(-0.32, "Province"),
        xaxis_title="",
        yaxis_title="Share of HEIs (%)" if pct else "Total HEIs",
        margin=dict(t=50, b=110, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(range=[0, peak * 1.2 if peak else 1])
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    return fig


def _trend_chart(x, total, title, name, color, fill, mode, y_title, height=340):
    """Total-over-time area chart. Percentage mode shows year-over-year growth
    (a total has no 'share' of itself, growth is its natural % view)."""
    pct = is_pct(mode)
    y = total.astype(float).reset_index(drop=True)
    if pct:
        y = y.pct_change() * 100
        label_name = "Year-over-year growth"
        text = ["" if v != v else f"{v:+.1f}%" for v in y]
        hover = "%{y:+.1f}%"
    else:
        label_name = name
        text = [fmt_compact(v) for v in y]
        hover = "%{y:,.0f}"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x.astype(str).reset_index(drop=True), y=y,
            mode="lines+markers+text", name=label_name,
            line=dict(color=color, width=3), marker=dict(size=6),
            fill="tozeroy", fillcolor=fill,
            text=text, textposition="top center",
            textfont=dict(size=9, color=color), cliponaxis=False,
            hovertemplate=f"{hover}<extra>{label_name}</extra>",
        )
    )
    fig.update_layout(**base_layout(title + (" — YoY Growth" if pct else ""), height=height))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.42),
        xaxis_title="Year",
        yaxis_title="Growth vs previous year (%)" if pct else y_title,
        margin=dict(t=50, b=110, l=50, r=20),
        hovermode="x unified",
    )
    fig.update_xaxes(tickangle=-25)
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    else:
        fig.update_yaxes(tickformat=".1s")
        peak = float(y.max()) if len(y) else 0
        fig.update_yaxes(range=[0, peak * 1.18 if peak else 1])
    return fig


def enrolment_trend_mini_chart(gender_agg, mode="Numbers"):
    return _trend_chart(
        gender_agg["Year"], gender_agg["Total"], "Total Enrolment Over the Years",
        "Total Enrolment", COLORS["accent"], "rgba(59,130,246,0.12)", mode, "Enrolment",
    )


def graduates_trend_mini_chart(gender_agg, mode="Numbers"):
    return _trend_chart(
        gender_agg["Year"], gender_agg["Total"], "Graduates (Passout) Over the Years",
        "Total Graduates", COLORS["positive"], "rgba(34,197,94,0.12)", mode, "Graduates",
    )


def level_stacked_bar_chart(level_agg, mode="Numbers"):
    """Stacked bars per year. Percentage mode normalises every year to 100%.
    Segment labels are drawn only where the segment is >= 5% of the year's
    total, so PGD/PhD slivers don't turn into an unreadable pile of text."""
    pct = is_pct(mode)
    level_cols = [("Bachelor", BOARD_COLOR_SEQUENCE[0]), ("Master", BOARD_COLOR_SEQUENCE[1]),
                  ("MS_Mphil", BOARD_COLOR_SEQUENCE[2]), ("PGD", BOARD_COLOR_SEQUENCE[3]),
                  ("PhD", BOARD_COLOR_SEQUENCE[4])]
    labels = {"MS_Mphil": "MS/Mphil"}
    cols = [c for c, _ in level_cols]
    year_total = level_agg[cols].sum(axis=1).reset_index(drop=True)
    x = level_agg["Year"].astype(str).reset_index(drop=True)

    fig = go.Figure()
    for col, color in level_cols:
        raw = level_agg[col].reset_index(drop=True).astype(float)
        sh = share(raw, year_total)
        y = sh if pct else raw
        text = [
            ((f"{s:.0f}%" if pct else fmt_compact(v)) if s >= 5 else "")
            for v, s in zip(raw, sh)
        ]
        fig.add_trace(
            go.Bar(
                x=x, y=y, name=labels.get(col, col), marker_color=color,
                text=text, textposition="inside", insidetextanchor="middle",
                textfont=dict(size=9, color="#FFFFFF"),
                hovertemplate=("%{x}<br>%{y:.1f}%<extra>" if pct else "%{x}<br>%{y:,.0f}<extra>")
                + labels.get(col, col) + "</extra>",
            )
        )
    fig.update_layout(**base_layout("Enrolment by Qualification Level", height=480))
    fig.update_layout(
        barmode="stack",
        showlegend=True,
        xaxis_title="Year",
        yaxis_title="Share of Enrolment (%)" if pct else "Enrolment",
        legend=legend_below(-0.38, "Qualification"),
        margin=dict(t=50, b=140, l=60, r=20),
    )
    fig.update_xaxes(tickangle=-25, automargin=True)
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f", range=[0, 100])
    else:
        fig.update_yaxes(tickformat=".1s")
    return fig


def discipline_bar_chart_overview(disc_df, mode="Numbers"):
    """Top disciplines, one trace each so every colour has a legend entry.
    Percentage mode uses the 'Share' column (share of ALL disciplines,
    not just the ones shown) supplied by overview_recipes.overview_discipline."""
    pct = is_pct(mode)
    shares = disc_df["Share"] if "Share" in disc_df.columns else share(disc_df["Total"])
    order = list(disc_df["Discipline"])
    fig = go.Figure()
    peak = 0
    for i, (name, val, sh) in enumerate(zip(disc_df["Discipline"], disc_df["Total"], shares)):
        x = float(sh) if pct else float(val)
        peak = max(peak, x)
        fig.add_trace(
            go.Bar(
                y=[name], x=[x], orientation="h", name=name,
                marker_color=BOARD_COLOR_SEQUENCE[i % len(BOARD_COLOR_SEQUENCE)],
                text=[f"{x:.1f}%" if pct else f"{val:,.0f}"],
                textposition="outside", cliponaxis=False,
                textfont=dict(size=11, color=COLORS["text_on_light"]),
                hovertemplate=("%{y}<br>%{x:.1f}%<extra></extra>" if pct else "%{y}<br>%{x:,.0f}<extra></extra>"),
            )
        )
    fig.update_layout(**base_layout("Enrolment by Discipline (Top 8)", height=560))
    fig.update_layout(
        barmode="overlay",
        showlegend=True,
        legend=dict(**legend_below(-0.16, "Discipline"), traceorder="reversed", font=dict(size=10)),
        xaxis_title="Share of Enrolment (%)" if pct else "Enrolment",
        yaxis_title="",
        margin=dict(t=50, b=150, l=10, r=110),
    )
    fig.update_xaxes(range=[0, peak * 1.32 if peak else 1])
    if pct:
        fig.update_xaxes(ticksuffix="%", tickformat=".0f")
    else:
        fig.update_xaxes(tickformat=".1s")
    fig.update_yaxes(automargin=True, categoryorder="array", categoryarray=order)
    return fig


def faculty_province_bar_chart(prov_agg, mode="Numbers"):
    """Percentage mode = PhD vs Non-PhD split *within* each province."""
    pct = is_pct(mode)
    total = prov_agg["PhD"] + prov_agg["Non_PhD"]
    if pct:
        phd, non = share(prov_agg["PhD"], total), share(prov_agg["Non_PhD"], total)
        fmt = lambda v: f"{v:.1f}%"
    else:
        phd, non = prov_agg["PhD"], prov_agg["Non_PhD"]
        fmt = lambda v: f"{int(v):,}"
    x = prov_agg["Province"].reset_index(drop=True)
    fig = go.Figure()
    for name, y, color in (("PhD", phd, COLORS["gold"]), ("Non-PhD", non, COLORS["accent"])):
        fig.add_trace(go.Bar(
            x=x, y=y, name=name, marker_color=color,
            text=[fmt(v) for v in y], textposition="outside", cliponaxis=False,
            textfont=dict(size=9, color=COLORS["text_on_light"]),
        ))
    fig.update_layout(**base_layout("Faculty by Province (PhD vs Non-PhD)", height=440))
    fig.update_layout(
        barmode="group",
        showlegend=True,
        xaxis_title="",
        yaxis_title="Share of Province Faculty (%)" if pct else "Faculty Count",
        legend=legend_below(-0.30, "Qualification"),
        margin=dict(t=50, b=130, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-35, automargin=True)
    peak = float(max(phd.max(), non.max())) if len(phd) else 0
    fig.update_yaxes(range=[0, peak * 1.18 if peak else 1])
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    return fig


def faculty_gender_donut_chart(gender_df, mode="Numbers"):
    pct = is_pct(mode)
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
        textinfo="percent" if pct else "value+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=12, color="#FFFFFF"),
        sort=False,
    )
    fig.update_layout(**base_layout("Faculty Gender Split", height=360))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5, title=dict(text="Gender")),
        margin=dict(t=50, b=50, l=30, r=30),
        annotations=[dict(text=f"{total:,}<br>Total", x=0.5, y=0.5, font_size=14, showarrow=False)],
    )
    return fig


def phd_year_bar_chart(phd_df, mode="Numbers"):
    pct = is_pct(mode)
    raw = phd_df["Total PhDs Produced"].reset_index(drop=True).astype(float)
    y = share(raw) if pct else raw
    fig = go.Figure(
        go.Bar(
            x=phd_df["Year"].reset_index(drop=True),
            y=y,
            name="Share of all PhDs" if pct else "PhDs produced",
            marker_color=COLORS["gold"],
            text=[f"{v:.1f}%" if pct else fmt_compact(v) for v in y],
            textposition="outside", cliponaxis=False,
            textfont=dict(size=8, color=COLORS["text_on_light"]),
            hovertemplate=("%{x}: %{y:.1f}%<extra></extra>" if pct else "%{x}: %{y:,.0f}<extra></extra>"),
        )
    )
    fig.update_layout(**base_layout("PhD Graduates Registered, by Year", height=340))
    fig.update_layout(
        showlegend=True,
        legend=legend_below(-0.45),
        xaxis_title="Year",
        yaxis_title="Share of All PhDs (%)" if pct else "PhDs Produced",
        margin=dict(t=50, b=110, l=50, r=20),
    )
    fig.update_xaxes(tickangle=-45)
    peak = float(y.max()) if len(y) else 0
    fig.update_yaxes(range=[0, peak * 1.2 if peak else 1])
    if pct:
        fig.update_yaxes(ticksuffix="%", tickformat=".0f")
    return fig
