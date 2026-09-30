import math
import random
import textwrap

import plotly.graph_objects as go
from charts._base import apply_finalize, base_layout, is_pct, share, fmt_compact, legend_below
from styles.theme import COLORS, FONTS, BOARD_COLOR_SEQUENCE


def _wrap(label, width=16):
    return "<br>".join(textwrap.wrap(label, width=width))


def phd_year_area_chart(year_df, mode="Numbers"):
    """PhDs produced per year, 2001 onward. Full-width, one tick every 2 years,
    horizontal (no rotated/overlapping labels), no per-point text.
    2026 is a partial year, so it is drawn as a dashed hop with its own legend
    entry instead of looking like a real drop-off. `year_df` comes from
    data.extra_recipes.phd_year_series()."""
    df = year_df.reset_index(drop=True)
    done = df[df["Year"] < df["Year"].max()]
    last = df.tail(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=done["Year"], y=done["Numbers"], mode="lines+markers", name="PhDs produced",
        line=dict(color=COLORS["gold"], width=3), marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(201,168,76,0.15)",
        hovertemplate="%{x}: %{y:,.0f} PhDs<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=last["Year"], y=last["Numbers"], mode="lines+markers", name=f"{int(df['Year'].max())} (partial year)",
        line=dict(color=COLORS["gold"], width=3, dash="dash"),
        marker=dict(size=9, symbol="circle-open", line=dict(width=2)),
        hovertemplate="%{x}: %{y:,.0f} PhDs so far<extra></extra>",
    ))
    fig.update_layout(**base_layout("Year-wise PhDs Produced", height=460))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0.0),
        margin=dict(t=105, b=70, l=70, r=30),
        xaxis_title="Year", yaxis_title="PhDs Produced", hovermode="x unified",
    )
    fig.update_xaxes(dtick=2, tickangle=0, tickfont=dict(size=12))
    fig.update_yaxes(tickformat=",", rangemode="tozero", gridcolor="rgba(0,0,0,0.06)")
    return fig


def _clean_discipline(name):
    """'05 Natural sciences, mathematics and statistics' -> 'Natural sciences, mathematics and statistics'."""
    parts = str(name).split(" ", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else str(name)


def discipline_bar_chart(discipline_df, mode="Numbers"):
    """Horizontal bars with the FULL discipline name on the left (the old
    vertical bars forced 10 long names into a rotated jumble). Biggest on top."""
    df = discipline_df.sort_values("Numbers", ascending=True).reset_index(drop=True)
    names = [_clean_discipline(d) for d in df["Discipline"]]
    vals = df["Numbers"].astype(float)
    fig = go.Figure(go.Bar(
        y=names, x=vals, orientation="h", marker_color=COLORS["accent"],
        text=[f"{int(v):,}" for v in vals], textposition="outside", cliponaxis=False,
        textfont=dict(size=12, color=COLORS["text_on_light"]),
        hovertemplate="%{y}<br>%{x:,.0f} PhDs<extra></extra>",
    ))
    fig.update_layout(**base_layout("PhDs Produced by Discipline", height=max(420, 44 * len(df) + 110)))
    fig.update_layout(showlegend=False, margin=dict(t=60, b=60, l=10, r=80), bargap=0.3,
                      xaxis_title="PhDs Produced")
    fig.update_xaxes(range=[0, float(vals.max()) * 1.15], tickformat="~s", gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(automargin=True, tickfont=dict(size=13), ticksuffix="  ")
    return fig


def _place_words(df, width=1040, height=520):
    """Simple spiral word-cloud placement: bigger/more-popular words first,
    walked outward from the centre until a non-overlapping spot is found."""
    words = df["Subject"].tolist()
    counts = df["Numbers"].tolist()
    max_c, min_c = max(counts), min(counts)

    def font_size(c):
        if max_c == min_c:
            return 28
        return 13 + (c - min_c) / (max_c - min_c) * 45

    rng = random.Random(42)
    placed_boxes = []
    positions = []
    for word, c in zip(words, counts):
        size = font_size(c)
        w = 0.60 * size * len(word)
        h = 1.25 * size
        angle = rng.uniform(0, 2 * math.pi)
        radius = 0.0
        x = y = 0.0
        for _ in range(1500):
            x = radius * math.cos(angle)
            y = radius * math.sin(angle) * 0.6
            x0, x1 = x - w / 2, x + w / 2
            y0, y1 = y - h / 2, y + h / 2
            fits_canvas = x0 >= -width / 2 and x1 <= width / 2 and y0 >= -height / 2 and y1 <= height / 2
            overlaps = any(
                x0 < px1 + 6 and x1 > px0 - 6 and y0 < py1 + 6 and y1 > py0 - 6
                for (px0, py0, px1, py1) in placed_boxes
            )
            if fits_canvas and not overlaps:
                break
            angle += 0.45
            radius += 3.2
        placed_boxes.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        positions.append((x, y, size))
    return positions


def subject_wordcloud_chart(subject_df, mode="Numbers", grand_total=None):
    """Percentage mode changes the hover to '% of all PhDs' (word size is
    relative either way, so it is unchanged)."""
    pct = is_pct(mode) and grand_total
    positions = _place_words(subject_df)
    colors = [BOARD_COLOR_SEQUENCE[i % len(BOARD_COLOR_SEQUENCE)] for i in range(len(subject_df))]
    random.Random(7).shuffle(colors)

    fig = go.Figure()
    for (x, y, size), word, count, color in zip(
        positions, subject_df["Subject"], subject_df["Numbers"], colors
    ):
        fig.add_trace(
            go.Scatter(
                x=[x], y=[y], mode="text", text=[word],
                textfont=dict(size=size, color=color, family=FONTS["body"]),
                hovertext=(f"{word}<br><b>{count / grand_total * 100:.2f}%</b> of all PhDs" if pct
                           else f"{word}<br><b>{count:,}</b> PhDs Produced"),
                hoverinfo="text",
                hoverlabel=dict(bgcolor=color, font=dict(color="#FFFFFF", size=13, family=FONTS["body"])),
                showlegend=False,
            )
        )
    fig.update_xaxes(visible=False, range=[-540, 540], fixedrange=True)
    fig.update_yaxes(visible=False, range=[-300, 300], fixedrange=True)
    fig.update_layout(**base_layout("PhDs Produced Popularity by Subject Keywords", height=460))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=10, l=10, r=10))
    return fig


apply_finalize(globals())
