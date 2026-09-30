"""Extra data helpers used by the added visuals (province-wise views, top-N
lists, decade roll-ups, heat-map matrices).  Everything here works on the
same Excel files as the rest of the dashboard -- nothing is invented."""
import pandas as pd
import streamlit as st

from config.settings import DATA_FILE, PHD_DIRECTORY_DATA_FILE
from data.enrolment_recipes import (
    load_gender_wise, load_level_wise, load_sector_wise,
    apply_filters as enrol_filters, PROVINCES, YEAR_ORDER as ENROL_YEARS,
)
from data.passout_recipes import (
    load_gender_wise as passout_gender, load_level_wise as passout_level,
    apply_filters as passout_filters, YEAR_ORDER as PASSOUT_YEARS,
)
from data.faculty_recipes import (
    load_by_province as faculty_by_province, load_by_gender as faculty_by_gender,
    apply_filters as faculty_filters, QUALIFICATION_COLS, QUALIFICATIONS, FACULTY_TYPES,
)

LEVEL_COLS = ["Bachelor", "Master", "MS_Mphil", "PGD", "PhD"]
LEVEL_LABELS = {"MS_Mphil": "MS/Mphil"}


def _order_provinces(df, col="Province"):
    df = df.copy()
    df[col] = pd.Categorical(df[col], categories=PROVINCES, ordered=True)
    return df.sort_values(col).reset_index(drop=True).assign(**{col: lambda d: d[col].astype(str)})


# ---------------------------------------------------------------------------
# Enrolment -- province-wise
# ---------------------------------------------------------------------------
def enrol_by_province(provinces, years, kind="gender"):
    """kind: gender -> Female/Male/Total, sector -> Private/Public/Total,
    level -> Bachelor..PhD/Total.  One row per province (years summed)."""
    loader, cols = {
        "gender": (load_gender_wise, ["Female", "Male", "Total"]),
        "sector": (load_sector_wise, ["Private", "Public", "Total"]),
        "level": (load_level_wise, LEVEL_COLS + ["Total"]),
    }[kind]
    df = enrol_filters(loader(), provinces, years)
    return _order_provinces(df.groupby("Province", as_index=False)[cols].sum())


def enrol_province_year(provinces, years):
    """Province x Year matrix of total enrolment (heat-map / trend lines)."""
    df = enrol_filters(load_gender_wise(), provinces, years)
    pv = df.pivot_table(index="Province", columns="Year", values="Total", aggfunc="sum")
    pv = pv.reindex(index=[p for p in PROVINCES if p in pv.index],
                    columns=[y for y in ENROL_YEARS if y in pv.columns])
    return pv.fillna(0)


# ---------------------------------------------------------------------------
# Graduates (passout) -- province-wise
# ---------------------------------------------------------------------------
def passout_by_province(provinces, years, kind="gender"):
    loader, cols = {
        "gender": (passout_gender, ["Female", "Male", "Total"]),
        "level": (passout_level, LEVEL_COLS + ["Total"]),
    }[kind]
    df = passout_filters(loader(), provinces, years)
    return _order_provinces(df.groupby("Province", as_index=False)[cols].sum())


def passout_province_year(provinces, years):
    df = passout_filters(passout_gender(), provinces, years)
    pv = df.pivot_table(index="Province", columns="Year", values="Total", aggfunc="sum")
    pv = pv.reindex(index=[p for p in PROVINCES if p in pv.index],
                    columns=[y for y in PASSOUT_YEARS if y in pv.columns])
    return pv.fillna(0)


def level_totals(level_agg):
    """Sum a year-wise level table into one Level / Count table (donut)."""
    return pd.DataFrame({
        "Level": [LEVEL_LABELS.get(c, c) for c in LEVEL_COLS],
        "Count": [int(level_agg[c].sum()) for c in LEVEL_COLS],
    })


# ---------------------------------------------------------------------------
# Faculty -- province-wise
# ---------------------------------------------------------------------------
def faculty_type_by_province(provinces, years, faculty_types=None, qualifications=None):
    """Full Time / Part Time headcount per province (respects the PhD /
    Non-PhD filter by summing only the selected qualification columns)."""
    df = faculty_filters(faculty_by_province(), provinces, years, faculty_types)
    quals = qualifications or QUALIFICATIONS
    cols = [QUALIFICATION_COLS[q] for q in quals]
    df = df.assign(Count=df[cols].sum(axis=1))
    pv = df.pivot_table(index="Province", columns="Faculty_Type", values="Count", aggfunc="sum").fillna(0)
    for c in FACULTY_TYPES:
        if c not in pv.columns:
            pv[c] = 0
    pv = pv[FACULTY_TYPES].reset_index()
    pv["Total"] = pv[FACULTY_TYPES].sum(axis=1)
    return _order_provinces(pv)


def faculty_gender_by_province(provinces, years, faculty_types=None):
    df = faculty_filters(faculty_by_gender(), provinces, years, faculty_types)
    agg = df.groupby("Province", as_index=False)[["Female", "Male"]].sum()
    agg["Total"] = agg["Female"] + agg["Male"]
    return _order_provinces(agg)


# ---------------------------------------------------------------------------
# Universities (HEIS_Data.xlsx)
# ---------------------------------------------------------------------------
def hei_decades(year_df):
    """Net increase in HEIs per decade, taken from the running total (so the
    decades add up to today's 278 HEIs).  The source's separate 'New_Added'
    column sums to more than the running total, so it is not used here."""
    df = year_df.sort_values("Year").copy()
    df["Decade"] = (df["Year"] // 10 * 10).astype(int)
    end_of_decade = df.groupby("Decade")["Cumulative_Total"].max()
    out = end_of_decade.diff().fillna(end_of_decade).reset_index()
    out.columns = ["Decade", "Added"]
    out["Added"] = out["Added"].astype(int)
    last_year = int(df["Year"].max())
    out["Label"] = [f"{d}s" if d + 9 <= last_year else f"{d}–{last_year}" for d in out["Decade"]]
    return out


@st.cache_data
def hei_specialisation():
    """HEIs by specialisation, from the institution directory (Sheet1)."""
    df = pd.read_excel(DATA_FILE, "Sheet1")
    fix = {"general": "General / Multi-discipline", "Agriculture & Veternity": "Agriculture & Veterinary"}
    df["Type"] = df["Discipline"].replace(fix)
    out = df.groupby("Type", as_index=False).size().rename(columns={"size": "Count"})
    return out.sort_values("Count", ascending=False).reset_index(drop=True), len(df)


# ---------------------------------------------------------------------------
# PhD Directory
# ---------------------------------------------------------------------------
# The PhD directory has no Province column, but every university name ends
# with its city / region.  Rules are checked in order (first match wins).
_PHD_PROVINCE_RULES = [
    ("AJ&K", ["ajk", "aj&k", "azad jammu", "kotli", "mirpur", "muzaffarabad", "nerian", "rawalakot", "poonch"]),
    ("Gilgit-Baltistan", ["gilgit", "karakurum", "karakoram", "baltistan", "skardu"]),
    ("Federal", ["islamabad", "nust", "comsats", "aiou", "numl", "pieas", "federal urdu", "foundation university",
                 "quaid-i-azam", "quaid i azam", "bahria", "riphah", "air university", "capital university", "ndu"]),
    ("Balochistan", ["quetta", "balochistan", "khuzdar", "turbat", "lasbela", "uthal", "bolan"]),
    ("Khyber Pakhtunkhwa", ["peshawar", "khyber", "d.i. khan", "dera ismail", "gomal", "kohat", "mansehra", "swabi",
                            "abbottabad", "mardan", "malakand", "chakdara", "dir", "sheringal", "haripur", "bannu",
                            "nowshera", "lakki", "topi", "hazara", "kust", "qurtuba", "qurtaba", "charsadda", "swat", "karak", "kust"]),
    ("Sindh", ["karachi", "sindh", "jamshoro", "hyderabad", "khairpur", "sukkur", "tandojam", "larkana", "nawabshah",
               "shaheed benazir", "dow university", "liaquat", "mehran", "ned university", "iba"]),
    ("Punjab", ["lahore", "punjab", "faisalabad", "bahawalpur", "rawalpindi", "multan", "taxila", "gujranwala",
                "sialkot", "sargodha", "gujrat", "okara", "wah", "arid agriculture", "pir mehr ali", "bahauddin",
                "gcu", "government college", "lums", "uet", "engineering and technology, lahore", "vehari",
                "rahim yar khan", "sahiwal", "jhang", "khanewal", "narowal", "layyah", "pakpattan", "attock", "chakwal", "mianwali"]),
]


def _phd_province(name: str) -> str:
    n = str(name).lower()
    for prov, keys in _PHD_PROVINCE_RULES:
        # 'dir', 'iba', 'wah', 'uet', 'ndu' are short -> match as whole words
        for k in keys:
            if len(k) <= 4:
                import re
                if re.search(rf"(?<![a-z]){re.escape(k)}(?![a-z])", n):
                    return prov
            elif k in n:
                return prov
    return "Not identifiable"


@st.cache_data
def phd_universities():
    df = pd.read_excel(PHD_DIRECTORY_DATA_FILE, "University")
    df["Province"] = df["University"].apply(_phd_province)
    return df


def phd_by_province():
    df = phd_universities()
    out = df.groupby("Province", as_index=False)["Numbers"].sum().rename(columns={"Numbers": "PhDs"})
    return out.sort_values("PhDs", ascending=False).reset_index(drop=True)


def phd_top_universities(n=15):
    df = phd_universities()
    out = df.groupby("University", as_index=False)["Numbers"].sum()
    return out.sort_values("Numbers", ascending=False).head(n).reset_index(drop=True)


def phd_top_subjects(n=10):
    df = pd.read_excel(PHD_DIRECTORY_DATA_FILE, "Subject")
    df = df[df["Subject"] != "Legacy"]
    return df.sort_values("Numbers", ascending=False).head(n).reset_index(drop=True)


def phd_year_series():
    """Year (int) / PhDs for 2001 onward. Years up to 2000 are one lumped row
    in the source data, so they are reported separately instead of being
    drawn as a giant first point that flattens the real trend."""
    from data.phd_directory_recipes import load_year
    df = load_year().copy()
    df["Year"] = df["Year"].astype(int)
    early = int(df.loc[df["Year"] <= 2000, "Numbers"].sum())
    later = df[df["Year"] > 2000].sort_values("Year").reset_index(drop=True)
    return later, early


# ---------------------------------------------------------------------------
# Discipline x Province (Enrolment Details)
# ---------------------------------------------------------------------------
def clean_discipline(name):
    """'05 Natural sciences, ...' -> 'Natural sciences, ...' (drops the code prefix)."""
    parts = str(name).split(" ", 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else str(name)


def discipline_by_province(provinces):
    """Estimated enrolment headcount, Discipline x Province.  The source only
    has each province's discipline mix in %, so headcount = % x that
    province's all-years enrolment (same estimate the rest of the page uses).
    Returns (matrix DataFrame: rows=disciplines, cols=provinces)."""
    from data.details_recipes import _province_cumulative_totals
    from data.ratios_recipes import load_discipline_gender, DISCIPLINE_ORDER
    provinces = provinces or PROVINCES
    df = load_discipline_gender()
    df = df[df["Province"].isin(provinces) & ~df["Discipline"].str.startswith("00")].copy()
    base = _province_cumulative_totals()
    df["Count"] = (df["Female_Pct"] + df["Male_Pct"]) / 100 * df["Province"].map(base)
    pv = df.pivot_table(index="Discipline", columns="Province", values="Count", aggfunc="sum").fillna(0)
    pv = pv.reindex(index=[d for d in DISCIPLINE_ORDER if d in pv.index],
                    columns=[p for p in PROVINCES if p in pv.columns])
    pv.index = [clean_discipline(d) for d in pv.index]
    return pv.round().astype(int)
