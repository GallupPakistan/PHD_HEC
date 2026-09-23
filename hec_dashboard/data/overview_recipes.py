import pandas as pd
import streamlit as st

from data.recipes import load_province_table, load_sector_summary, load_year_growth, load_city_map
from data.enrolment_recipes import (
    load_gender_wise as load_enrolment_gender_wise,
    load_level_wise as load_enrolment_level_wise,
    apply_filters as enrolment_apply_filters,
    aggregate_by_year as enrolment_aggregate_by_year,
)
from data.details_recipes import load_gender_summary, load_discipline_count_table
from data.faculty_recipes import (
    load_by_province as load_faculty_by_province,
    load_by_gender as load_faculty_by_gender,
    YEAR_ORDER as FACULTY_YEAR_ORDER,
)
from data.passout_recipes import (
    load_gender_wise as load_passout_gender_wise,
    apply_filters as passout_apply_filters,
    aggregate_by_year as passout_aggregate_by_year,
    YEAR_ORDER as PASSOUT_YEAR_ORDER,
)
from data.phd_directory_recipes import year_table as phd_year_table, total_phds


def _years_for(selected_years, available_years):
    """Intersect the sidebar's selected years with what a dataset actually has.

    Some datasets (Faculty, Graduates) cover a narrower year range than the
    sidebar filter (which is built from the broadest dataset, Enrolment). If
    the user's selection doesn't overlap a dataset's own years at all, fall
    back to that dataset's full range instead of silently returning an empty
    chart.
    """
    if not selected_years:
        return []
    matched = [y for y in selected_years if y in available_years]
    return matched or []


@st.cache_data
def overview_universities():
    """Not affected by the Province/Year sidebar filters -- the source data
    for these charts (map, sector split, growth trend) is pre-aggregated
    with no per-record Province/Year to filter on."""
    province_df = load_province_table()
    sector_df = load_sector_summary()
    year_df = load_year_growth()
    city_df = load_city_map()
    total_row = province_df[province_df["Province"] == "TOTAL (PAKISTAN)"]
    total_heis = int(total_row["Total"].iloc[0]) if not total_row.empty else int(province_df["Total"].sum())
    province_bars = province_df[province_df["Province"] != "TOTAL (PAKISTAN)"].copy()
    return province_bars, sector_df, year_df, city_df, total_heis


@st.cache_data
def overview_enrolment(provinces=None, years=None):
    gender_agg = enrolment_aggregate_by_year(
        enrolment_apply_filters(load_enrolment_gender_wise(), provinces, years), ["Female", "Male", "Total"]
    )
    level_agg = enrolment_aggregate_by_year(
        enrolment_apply_filters(load_enrolment_level_wise(), provinces, years),
        ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD", "Total"],
    )
    gender_summary = load_gender_summary(provinces, years)
    latest_total = int(gender_agg["Total"].iloc[-1]) if not gender_agg.empty else 0
    return gender_agg, level_agg, gender_summary, latest_total


@st.cache_data
def overview_discipline(top_n=8, provinces=None):
    """Responds to the Province filter only -- the source discipline data has
    no year breakdown (see details_recipes.load_discipline_count_table)."""
    disc = load_discipline_count_table(provinces)
    disc = disc[disc["Discipline"] != "Total"].copy()
    disc = disc.sort_values("Total", ascending=False).head(top_n)
    return disc.sort_values("Total", ascending=True)  # ascending for horizontal bar (largest on top)


@st.cache_data
def overview_faculty(provinces=None, years=None):
    faculty_years = _years_for(years, FACULTY_YEAR_ORDER)
    by_province = load_faculty_by_province()
    if provinces:
        by_province = by_province[by_province["Province"].isin(provinces)]
    if faculty_years:
        by_province = by_province[by_province["Year"].isin(faculty_years)]
    prov_agg = by_province.groupby("Province", as_index=False)[["Non_PhD", "PhD"]].sum()
    prov_agg["Total"] = prov_agg["Non_PhD"] + prov_agg["PhD"]
    total_faculty = int(prov_agg["Total"].sum())

    by_gender = load_faculty_by_gender()
    if provinces:
        by_gender = by_gender[by_gender["Province"].isin(provinces)]
    if faculty_years:
        by_gender = by_gender[by_gender["Year"].isin(faculty_years)]
    female = int(by_gender["Female"].sum())
    male = int(by_gender["Male"].sum())
    gender_df = pd.DataFrame({"Gender": ["Female", "Male"], "Count": [female, male]})

    return prov_agg, gender_df, total_faculty


@st.cache_data
def overview_graduates(provinces=None, years=None):
    graduate_years = _years_for(years, PASSOUT_YEAR_ORDER)
    gender_agg = passout_aggregate_by_year(
        passout_apply_filters(load_passout_gender_wise(), provinces, graduate_years), ["Female", "Male", "Total"]
    )
    latest_total = int(gender_agg["Total"].iloc[-1]) if not gender_agg.empty else 0
    return gender_agg, latest_total


@st.cache_data
def overview_phd():
    """Not affected by the Province/Year sidebar filters -- the PhD Directory
    source sheets have no Province column, and Year isn't filterable here."""
    df = phd_year_table()
    df = df[df["Year"] != "Total"].copy()
    return df, total_phds()