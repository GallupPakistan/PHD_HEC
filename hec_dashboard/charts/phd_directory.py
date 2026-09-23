import math
import random
import textwrap

import plotly.graph_objects as go
from charts._base import base_layout
from styles.theme import COLORS, FONTS, BOARD_COLOR_SEQUENCE


def _wrap(label, width=16):
    return "<br>".join(textwrap.wrap(label, width=width))


def phd_year_area_chart(year_df):
    """Single-series PhD-output trend across ~26 years -- a gold filled
    line rather than a 27-bar chart (too dense to label cleanly), matching
    the house style already used for other single-metric year trends
    (HEI growth, enrolment, graduates) elsewhere in this dashboard."""
    df = year_df[year_df["Year"] != "Total"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Year"], y=df["Total PhDs Produced"],
            mode="lines+markers",
            name="PhDs Produced",
            line=dict(color=COLORS["gold"], width=3),
            marker=dict(size=5, color=COLORS["gold"]),
            fill="tozeroy",
            fillcolor="rgba(201,168,76,0.15)",
            hovertemplate="%{x}<br>%{y:,} PhDs<extra></extra>",
        )
    )
    fig.update_layout(**base_layout("Year-wise PhDs Produced", height=460))
    fig.update_layout(
        showlegend=False,
        xaxis_title="Year",
        yaxis_title="PhDs Produced",
        margin=dict(t=50, b=90, l=60, r=20),
        hovermode="x unified",
    )
    fig.update_xaxes(tickangle=-45, automargin=True)
    fig.update_yaxes(tickformat=",")
    return fig


def discipline_bar_chart(discipline_df):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[_wrap(d) for d in discipline_df["Discipline"]],
            y=discipline_df["Numbers"],
            marker_color=COLORS["accent"],
            text=[f"{v:,}" for v in discipline_df["Numbers"]],
            textposition="outside",
            textfont=dict(size=10, color=COLORS["text_on_light"]),
        )
    )
    fig.update_layout(**base_layout("PhDs Produced Popularity by Subject Keywords", height=440))
    fig.update_layout(
        xaxis_title="Discipline",
        yaxis_title="Total PhDs Produced",
        margin=dict(t=50, b=120, l=50, r=20),
    )
    fig.update_xaxes(tickfont=dict(size=9))
    fig.update_yaxes(tickformat=",")
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


def subject_wordcloud_chart(subject_df):
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
                hovertext=f"{word}<br><b>{count:,}</b> PhDs Produced",
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