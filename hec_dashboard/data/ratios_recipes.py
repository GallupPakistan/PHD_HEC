import pandas as pd
import streamlit as st

from config.settings import DISCIPLINE_DATA_FILE
from data.enrolment_recipes import (
    load_level_wise,
    load_sector_wise,
    apply_filters,
    PROVINCES,
    YEAR_ORDER,
)

LEVEL_COLS = ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD"]
LEVEL_LABELS = {"MS_Mphil": "MS/Mphil"}
SECTOR_COLS = ["Private", "Public"]

DISCIPLINE_ORDER = [
    "00 Generic programmes and qualifications",
    "01 Education",
    "02 Arts and humanities",
    "03 Social sciences, journalism and information",
    "04 Business, administration and law",
    "05 Natural sciences, mathematics and statistics",
    "06 Information and Communication Technologies (ICTs)",
    "07 Engineering, manufacturing and construction",
    "08 Agriculture, forestry, fisheries and veterinary",
    "09 Health and welfare",
    "10 Services",
]


def _pct_by_year(df, value_cols):
    """Sum raw counts per year, then express each column as a % of that year's Total."""
    agg = df.groupby("Year", as_index=False)[value_cols + ["Total"]].sum()
    for c in value_cols:
        agg[c] = (agg[c] / agg["Total"] * 100).round(2)
    agg["Year"] = pd.Categorical(agg["Year"], categories=YEAR_ORDER, ordered=True)
    return agg.sort_values("Year").reset_index(drop=True).drop(columns="Total")


def load_level_ratio_table(provinces, years):
    df = apply_filters(load_level_wise(), provinces, years)
    return _pct_by_year(df, LEVEL_COLS)


def load_sector_ratio_table(provinces, years):
    df = apply_filters(load_sector_wise(), provinces, years)
    return _pct_by_year(df, SECTOR_COLS)


def load_level_ratio_summary(provinces, years):
    """Single aggregated Bachelor/Master/.../PhD split for the selected filters (pie chart)."""
    df = apply_filters(load_level_wise(), provinces, years)
    totals = df[LEVEL_COLS].sum()
    grand_total = totals.sum()
    out = pd.DataFrame(
        {
            "Level": [LEVEL_LABELS.get(c, c) for c in LEVEL_COLS],
            "Percentage": (totals.values / grand_total * 100).round(2),
        }
    )
    return out


@st.cache_data
def load_discipline_gender():
    return pd.read_excel(DISCIPLINE_DATA_FILE, "DisciplineGender")


def load_discipline_ratio_table(provinces):
    provinces = provinces or PROVINCES
    df = load_discipline_gender()
    df = df[df["Province"].isin(provinces)]
    agg = df.groupby("Discipline", as_index=False)[["Female_Pct", "Male_Pct"]].mean().round(2)
    agg["Discipline"] = pd.Categorical(agg["Discipline"], categories=DISCIPLINE_ORDER, ordered=True)
    return agg.sort_values("Discipline").reset_index(drop=True)
