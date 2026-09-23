import pandas as pd
import streamlit as st

from data.enrolment_recipes import (
    load_gender_wise,
    apply_filters,
    PROVINCES,
    YEAR_ORDER,
)
from data.ratios_recipes import load_discipline_gender, DISCIPLINE_ORDER


def load_gender_year_table(provinces, years):
    df = apply_filters(load_gender_wise(), provinces, years)
    agg = df.groupby("Year", as_index=False)[["Female", "Male", "Total"]].sum()
    agg["Year"] = pd.Categorical(agg["Year"], categories=YEAR_ORDER, ordered=True)
    return agg.sort_values("Year").reset_index(drop=True)


def load_gender_summary(provinces, years):
    """Female/Male split (count + %) for the selected filters — feeds the gender pie chart."""
    df = apply_filters(load_gender_wise(), provinces, years)
    female = int(df["Female"].sum())
    male = int(df["Male"].sum())
    total = female + male
    return pd.DataFrame(
        {
            "Gender": ["Female", "Male"],
            "Count": [female, male],
            "Percentage": [round(female / total * 100, 2), round(male / total * 100, 2)],
        }
    )


@st.cache_data
def _province_cumulative_totals():
    """Each province's all-years combined enrolment — the base the discipline %s are relative to."""
    df = load_gender_wise()
    return df.groupby("Province")["Total"].sum()


def load_discipline_count_table(provinces):
    """Discipline & Gender-wise Enrolment as raw headcounts, with a Total row.

    The source discipline data only ships as province-wise %s with no year
    breakdown, so this panel responds to the Province filter only (not Year) —
    counts are reconstructed as % x each province's cumulative (all-years) total.
    """
    provinces = provinces or PROVINCES
    disc = load_discipline_gender()
    disc = disc[disc["Province"].isin(provinces)].copy()
    bases = _province_cumulative_totals()
    disc["Female"] = disc.apply(lambda r: r["Female_Pct"] / 100 * bases[r["Province"]], axis=1)
    disc["Male"] = disc.apply(lambda r: r["Male_Pct"] / 100 * bases[r["Province"]], axis=1)

    agg = disc.groupby("Discipline", as_index=False)[["Female", "Male"]].sum()
    agg["Female"] = agg["Female"].round().astype(int)
    agg["Male"] = agg["Male"].round().astype(int)
    agg["Total"] = agg["Female"] + agg["Male"]
    agg["Discipline"] = pd.Categorical(agg["Discipline"], categories=DISCIPLINE_ORDER, ordered=True)
    agg = agg.sort_values("Discipline").reset_index(drop=True)
    agg["Discipline"] = agg["Discipline"].astype(str)

    total_row = pd.DataFrame(
        [{
            "Discipline": "Total",
            "Female": int(agg["Female"].sum()),
            "Male": int(agg["Male"].sum()),
            "Total": int(agg["Total"].sum()),
        }]
    )
    return pd.concat([agg, total_row], ignore_index=True)
