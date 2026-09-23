import pandas as pd
import streamlit as st

from config.settings import FACULTY_DATA_FILE

PROVINCES = [
    "AJ&K", "Balochistan", "Federal", "Gilgit-Baltistan",
    "Khyber Pakhtunkhwa", "Punjab", "Sindh",
]

# Only one year of faculty data is currently available from HEC (source sheets
# ship no year-wise history for faculty, unlike the enrolment data). This list
# is deliberately structured the same way as enrolment_recipes.YEAR_ORDER so
# that once older/newer years are added to Faculty_Data.xlsx, they only need
# to be appended here — no other code on this page has to change.
YEAR_ORDER = ["2024-25 (Provisional)"]

FACULTY_TYPES = ["Full Time", "Part Time"]

# PhD/Non-PhD qualification categories, as (display label -> column name).
# The small number of records with no qualification reported in the source
# data are folded into Non-PhD, so only these two categories are exposed.
QUALIFICATION_COLS = {"PhD": "PhD", "Non-PhD": "Non_PhD"}
QUALIFICATIONS = list(QUALIFICATION_COLS)


@st.cache_data
def load_by_province():
    df = pd.read_excel(FACULTY_DATA_FILE, "ByProvince")
    df["Non_PhD"] = df["Non_PhD"] + df["Not_Reported"]
    return df.drop(columns="Not_Reported")


@st.cache_data
def load_by_gender():
    return pd.read_excel(FACULTY_DATA_FILE, "ByGender")


@st.cache_data
def load_by_sector():
    df = pd.read_excel(FACULTY_DATA_FILE, "BySector")
    df["Non_PhD_Pct"] = df["Non_PhD_Pct"] + df["Not_Reported_Pct"]
    return df.drop(columns="Not_Reported_Pct")


def apply_filters(df, provinces, years, faculty_types=None):
    provinces = provinces or PROVINCES
    years = years or YEAR_ORDER
    mask = df["Province"].isin(provinces) & df["Year"].isin(years)
    if "Faculty_Type" in df.columns:
        faculty_types = faculty_types or FACULTY_TYPES
        mask &= df["Faculty_Type"].isin(faculty_types)
    return df[mask]


def _zero_unselected(agg, qualifications):
    """Zero out qualification columns the user has deselected, then recompute Total
    as the sum of what's left — mirrors how a category slicer drives a Total column."""
    qualifications = qualifications or QUALIFICATIONS
    for label, col in QUALIFICATION_COLS.items():
        if label not in qualifications:
            agg[col] = 0
    agg["Total"] = agg[list(QUALIFICATION_COLS.values())].sum(axis=1)
    return agg


def load_province_table(provinces, years, faculty_types=None, qualifications=None):
    """Non-PhD / PhD / Total faculty headcount by province."""
    df = apply_filters(load_by_province(), provinces, years, faculty_types)
    agg = df.groupby("Province", as_index=False)[["Non_PhD", "PhD"]].sum()
    agg = _zero_unselected(agg, qualifications)
    total_row = pd.DataFrame(
        [{
            "Province": "Total",
            "Non_PhD": agg["Non_PhD"].sum(),
            "PhD": agg["PhD"].sum(),
            "Total": agg["Total"].sum(),
        }]
    )
    return pd.concat([agg, total_row], ignore_index=True)


def load_pct_by_year_table(provinces, years, faculty_types=None, qualifications=None):
    """Non-PhD / PhD share of faculty, one row per year (share is of the selected
    qualifications only — deselecting a category removes it from the 100% base)."""
    df = apply_filters(load_by_province(), provinces, years, faculty_types)
    agg = df.groupby("Year", as_index=False)[["Non_PhD", "PhD"]].sum()
    agg = _zero_unselected(agg, qualifications)
    for c in ["Non_PhD", "PhD"]:
        agg[c] = (agg[c] / agg["Total"] * 100).round(2)
    agg["Year"] = pd.Categorical(agg["Year"], categories=YEAR_ORDER, ordered=True)
    return agg.sort_values("Year").reset_index(drop=True).drop(columns="Total")


def load_sector_table(provinces, years, faculty_types=None, qualifications=None):
    """Non-PhD / PhD share of faculty by Sector (Private/Public); mean across
    matching Province + Faculty_Type rows, since only %s (no raw counts) exist.
    Deselecting a qualification zeroes its share and renormalises the rest."""
    df = load_by_sector()
    provinces = provinces or PROVINCES
    years = years or YEAR_ORDER
    faculty_types = faculty_types or FACULTY_TYPES
    df = df[
        df["Province"].isin(provinces)
        & df["Year"].isin(years)
        & df["Faculty_Type"].isin(faculty_types)
    ]
    agg = df.groupby("Sector", as_index=False)[["Non_PhD_Pct", "PhD_Pct"]].mean().round(2)

    qualifications = qualifications or QUALIFICATIONS
    pct_cols = {"PhD": "PhD_Pct", "Non-PhD": "Non_PhD_Pct"}
    for label, col in pct_cols.items():
        if label not in qualifications:
            agg[col] = 0
    base = agg[list(pct_cols.values())].sum(axis=1)
    for col in pct_cols.values():
        agg[col] = (agg[col] / base * 100).round(2).fillna(0)
    return agg


def load_gender_by_year_table(provinces, years, faculty_types=None):
    """Female / Male faculty headcount, one row per year. Not split by
    qualification in the source data, so this table ignores that filter."""
    df = apply_filters(load_by_gender(), provinces, years, faculty_types)
    agg = df.groupby("Year", as_index=False)[["Female", "Male", "Total"]].sum()
    agg["Year"] = pd.Categorical(agg["Year"], categories=YEAR_ORDER, ordered=True)
    return agg.sort_values("Year").reset_index(drop=True)