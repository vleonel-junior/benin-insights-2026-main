import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("data/gdelt_benin_clean.csv")
    return df

@st.cache_data
def get_monthly_stats():
    df = load_data()
    monthly = df.groupby("month").agg(
        total=("IsConflict", "count"),
        conflits=("IsConflict", "sum"),
        goldstein=("GoldsteinScale", "mean"),
        tone=("AvgTone", "mean"),
        anger=("GCAM_Anger", "mean"),
        fear=("GCAM_Fear", "mean"),
    ).reset_index()
    monthly["pct_conflit"] = (monthly["conflits"] / monthly["total"] * 100).round(1)
    monthly["conflit_materiel"] = df[df["QuadLabel"] == "Conflit materiel"].groupby("month").size().values
    monthly["conflit_verbal"] = df[df["QuadLabel"] == "Conflit verbal"].groupby("month").size().values
    return monthly

@st.cache_data
def get_dept_stats():
    df = load_data()
    dept = df.groupby("DepartementBenin").agg(
        total=("IsConflict", "count"),
        conflits=("IsConflict", "sum"),
        goldstein=("GoldsteinScale", "mean"),
        tone=("AvgTone", "mean"),
        anger=("GCAM_Anger", "mean"),
        fear=("GCAM_Fear", "mean"),
        nb_articles=("NumArticles", "sum"),
    ).reset_index()
    dept["pct_conflit"] = (dept["conflits"] / dept["total"] * 100).round(1)
    dept["conflit_materiel"] = (
        df[df["QuadLabel"] == "Conflit materiel"]
        .groupby("DepartementBenin").size()
        .reindex(dept["DepartementBenin"]).fillna(0).values
    )
    dept["conflit_verbal"] = (
        df[df["QuadLabel"] == "Conflit verbal"]
        .groupby("DepartementBenin").size()
        .reindex(dept["DepartementBenin"]).fillna(0).values
    )
    dept["risk_score"] = (
        dept["pct_conflit"] * 0.4
        + dept["anger"] * 10
        + dept["fear"] * 10
        + (1 - dept["goldstein"]) * 10
    ).round(2)
    return dept

@st.cache_data
def get_actor_stats():
    df = load_data()
    top_actors = df["Actor1Name"].value_counts().head(12).index.tolist()
    actors = (
        df[df["Actor1Name"].isin(top_actors)]
        .groupby("Actor1Name")
        .agg(
            total=("IsConflict", "count"),
            conflits=("IsConflict", "sum"),
            negatifs=("IsNegative", "sum"),
            tone=("AvgTone", "mean"),
            goldstein=("GoldsteinScale", "mean"),
        )
        .reset_index()
    )
    actors["pct_conflit"] = (actors["conflits"] / actors["total"] * 100).round(1)
    return actors.sort_values("negatifs", ascending=False)

@st.cache_data
def get_source_stats():
    df = load_data()
    src = df.groupby("SourceType").agg(
        nb_events=("IsConflict", "count"),
        conflits=("IsConflict", "sum"),
        negatifs=("IsNegative", "sum"),
        tone=("AvgTone", "mean"),
        goldstein=("GoldsteinScale", "mean"),
        intensite=("GKG_EmotionIntensity", "mean"),
        tonegap=("GKG_ToneGap", "mean"),
        anger=("GCAM_Anger", "mean"),
        fear=("GCAM_Fear", "mean"),
        joy=("GCAM_Joy", "mean"),
        trust=("GCAM_Trust", "mean"),
    ).reset_index()
    src["pct_conflit"] = (src["conflits"] / src["nb_events"] * 100).round(1)
    src["pct_negatif"] = (src["negatifs"] / src["nb_events"] * 100).round(1)
    return src

@st.cache_data
def get_theme_stats():
    df = load_data()
    themes = {
        "GKG_ThemeConflict": "Conflit / Sécurité",
        "GKG_ThemeEconomy": "Économie",
        "GKG_ThemeGovern": "Gouvernance",
        "GKG_ThemeHumanDev": "Dév. Humain",
        "GKG_ThemeEnviro": "Environnement",
    }
    rows = []
    for col, label in themes.items():
        sub = df[df[col] == 1]
        rows.append({
            "theme": label,
            "col": col,
            "n": len(sub),
            "pct_conflit": round(sub["IsConflict"].mean() * 100, 1),
            "goldstein": round(sub["GoldsteinScale"].mean(), 3),
            "tone": round(sub["AvgTone"].mean(), 3),
            "anger": round(sub["GCAM_Anger"].mean(), 3),
            "fear": round(sub["GCAM_Fear"].mean(), 3),
            "joy": round(sub["GCAM_Joy"].mean(), 3),
            "trust": round(sub["GCAM_Trust"].mean(), 3),
        })
    return pd.DataFrame(rows)

@st.cache_data
def get_zone_monthly():
    df = load_data()
    return (
        df.groupby(["month", "ZoneBenin"])["IsConflict"]
        .mean()
        .unstack()
        .round(3) * 100
    ).reset_index()

# Coordonnées approximatives des départements (centroïdes)
DEPT_COORDS = {
    "Alibori":    {"lat": 11.30, "lon": 2.85},
    "Atacora":    {"lat": 10.63, "lon": 1.65},
    "Atlantique": {"lat": 6.65,  "lon": 2.25},
    "Borgou":     {"lat": 9.50,  "lon": 2.78},
    "Collines":   {"lat": 8.35,  "lon": 2.30},
    "Couffo":     {"lat": 7.03,  "lon": 1.75},
    "Donga":      {"lat": 9.72,  "lon": 1.68},
    "Littoral":   {"lat": 6.37,  "lon": 2.42},
    "Mono":       {"lat": 6.80,  "lon": 1.62},
    "Oueme":      {"lat": 6.75,  "lon": 2.60},
    "Plateau":    {"lat": 7.35,  "lon": 2.58},
    "Zou":        {"lat": 7.50,  "lon": 2.18},
}

COLORS = {
    "rouge":  "#E24B4A",
    "orange": "#EF9F27",
    "vert":   "#639922",
    "bleu":   "#378ADD",
    "violet": "#534AB7",
    "gris":   "#888780",
}
