import pandas as pd
import streamlit as st
from config.settings import ENROLMENT_DATA_FILE

YEAR_ORDER = [
    "2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
    "2019-20", "2020-21", "2021-22", "2022-23",
    "2023-24 (Provisional)", "2024-25 (Provisional)",
]

PROVINCES = [
    "AJ&K", "Balochistan", "Federal", "Gilgit-Baltistan",
    "Khyber Pakhtunkhwa", "Punjab", "Sindh",
]


@st.cache_data
def load_gender_wise():
    return pd.read_excel(ENROLMENT_DATA_FILE, "GenderWise")


@st.cache_data
def load_level_wise():
    return pd.read_excel(ENROLMENT_DATA_FILE, "LevelWise")


@st.cache_data
def load_sector_wise():
    return pd.read_excel(ENROLMENT_DATA_FILE, "SectorWise")


def apply_filters(df, provinces, years):
    provinces = provinces or PROVINCES
    years = years or YEAR_ORDER
    return df[df["Province"].isin(provinces) & df["Year"].isin(years)]


def aggregate_by_year(df, value_cols):
    agg = df.groupby("Year", as_index=False)[value_cols].sum()
    agg["Year"] = pd.Categorical(agg["Year"], categories=YEAR_ORDER, ordered=True)
    return agg.sort_values("Year").reset_index(drop=True)
