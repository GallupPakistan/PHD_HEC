import pandas as pd
import streamlit as st
from config.settings import PHD_DIRECTORY_DATA_FILE

# Tiny/unclassified buckets that the source data carries but that aren't a
# real discipline or subject keyword, so charts drop them.
EXCLUDED_DISCIPLINES = {"00 Generic programmes and qualifications", "UNKNOWN"}
EXCLUDED_SUBJECTS = {"Legacy"}


@st.cache_data
def load_year():
    return pd.read_excel(PHD_DIRECTORY_DATA_FILE, "Year")


@st.cache_data
def load_discipline():
    return pd.read_excel(PHD_DIRECTORY_DATA_FILE, "Discipline")


@st.cache_data
def load_subject():
    return pd.read_excel(PHD_DIRECTORY_DATA_FILE, "Subject")


@st.cache_data
def load_university():
    return pd.read_excel(PHD_DIRECTORY_DATA_FILE, "University")


def total_phds():
    return int(load_year()["Numbers"].sum())


def year_table():
    """Year-wise PhDs produced. Years up to 2000 are rolled into one row
    (the source data only has a single, sparsely populated row per year that
    far back), followed by one row per year and a Total row."""
    df = load_year().copy()
    df["YearInt"] = df["Year"].astype(int)
    early = df[df["YearInt"] <= 2000]
    later = df[df["YearInt"] > 2000].sort_values("YearInt")

    rows = [{"Year": f"Up to {early['YearInt'].max()}", "Total PhDs Produced": int(early["Numbers"].sum())}]
    rows += [{"Year": str(y), "Total PhDs Produced": int(n)} for y, n in zip(later["YearInt"], later["Numbers"])]
    rows.append({"Year": "Total", "Total PhDs Produced": int(df["Numbers"].sum())})
    return pd.DataFrame(rows)


def discipline_chart_data():
    """Numbered discipline categories only, sorted by popularity."""
    df = load_discipline().copy()
    df = df[~df["Discipline"].isin(EXCLUDED_DISCIPLINES)]
    return df.sort_values("Numbers", ascending=False).reset_index(drop=True)


def subject_wordcloud_data(top_n=45):
    """Top subject keywords by PhDs produced, for the word-cloud visual."""
    df = load_subject().copy()
    df = df[~df["Subject"].isin(EXCLUDED_SUBJECTS)]
    return df.sort_values("Numbers", ascending=False).head(top_n).reset_index(drop=True)
