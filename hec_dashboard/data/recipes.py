import re
import pandas as pd
import streamlit as st
from config.settings import DATA_FILE


@st.cache_data
def load_province_table():
    df = pd.read_excel(DATA_FILE, "Sheet4", skiprows=1)
    df.columns = ["Province", "Private", "Public", "Total"]
    df = df.drop(index=0).reset_index(drop=True)
    for c in ["Private", "Public", "Total"]:
        df[c] = pd.to_numeric(df[c])
    return df


@st.cache_data
def load_sector_summary():
    df = pd.read_excel(DATA_FILE, "Sheet3", skiprows=1)
    df.columns = ["Sector", "Count"]
    df = df.drop(index=0).reset_index(drop=True)
    df = df[df["Sector"] != "TOTAL"]
    df["Count"] = pd.to_numeric(df["Count"])
    return df


@st.cache_data
def load_year_growth():
    df = pd.read_excel(DATA_FILE, "Sheet2", skiprows=2)
    df.columns = ["Year", "Cumulative_Total", "New_Added"]
    df = df.dropna(subset=["Year"])
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    df["Cumulative_Total"] = pd.to_numeric(df["Cumulative_Total"])
    df["New_Added"] = pd.to_numeric(df["New_Added"])
    return df


@st.cache_data
def load_city_map():
    df = pd.read_excel(DATA_FILE, "Sheet5", skiprows=1)
    df.columns = ["City_raw", "Public", "Private", "Total"]
    df = df.drop(index=0).reset_index(drop=True)

    def parse_city(s):
        m = re.match(r"(.+?)\s*\(([\d.]+)°E,\s*([\d.]+)°N\)", s)
        return pd.Series([m.group(1), float(m.group(2)), float(m.group(3))])

    df[["City", "lon", "lat"]] = df["City_raw"].apply(parse_city)
    for c in ["Public", "Private", "Total"]:
        df[c] = pd.to_numeric(df[c])
    return df
