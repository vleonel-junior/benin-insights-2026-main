import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin · Observatoire Médiatique GDELT",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PALETTE ──────────────────────────────────────────────────────────────────
COLORS = {
    "Cooperation verbale":    "#2ecc71",
    "Cooperation materielle": "#27ae60",
    "Conflit verbal":         "#e67e22",
    "Conflit materiel":       "#e74c3c",
}
EMOTION_COLORS = {
    "Trust":    "#3498db",
    "Joy":      "#f1c40f",
    "Anger":    "#e74c3c",
    "Surprise": "#9b59b6",
    "Fear":     "#e67e22",
    "Sadness":  "#95a5a6",
}
DEPT_ORDER = [
    "Atlantique","Littoral","Borgou","Plateau","Donga",
    "Alibori","Couffo","Oueme","Collines","Zou","Atacora","Mono"
]

# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/gdelt_replubique_benin_clean_.csv")
    df["month_dt"] = pd.to_datetime(df["month"])
    df["month_label"] = df["month_dt"].dt.strftime("%b %Y")
    return df

df_raw = load_data()

# ─── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/200px-Flag_of_Benin.svg.png",
        width=80,
    )
    st.title("🇧🇯 Filtres")
    st.markdown("---")

    months_available = sorted(df_raw["month"].unique())
    month_start, month_end = st.select_slider(
        "Période",
        options=months_available,
        value=(months_available[0], months_available[-1]),
    )

    depts = st.multiselect(
        "Département(s)",
        options=sorted(df_raw["DepartementBenin"].unique()),
        default=sorted(df_raw["DepartementBenin"].unique()),
    )

    quad_labels = st.multiselect(
        "Type d'événement",
        options=df_raw["QuadLabel"].unique().tolist(),
        default=df_raw["QuadLabel"].unique().tolist(),
    )

    source_types = st.multiselect(
        "Type de source",
        options=sorted(df_raw["SourceType"].unique()),
        default=sorted(df_raw["SourceType"].unique()),
    )

    st.markdown("---")
    st.caption("Données : GDELT Project · 2025\nDashboard : Hackathon Bénin")

# ─── APPLY FILTERS ────────────────────────────────────────────────────────────
df = df_raw[
    (df_raw["month"] >= month_start)
    & (df_raw["month"] <= month_end)
    & (df_raw["DepartementBenin"].isin(depts))
    & (df_raw["QuadLabel"].isin(quad_labels))
    & (df_raw["SourceType"].isin(source_types))
].copy()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style='margin-bottom:0'>🇧🇯 Observatoire Médiatique — République du Bénin</h1>
    <p style='color:#888;margin-top:4px'>Analyse GDELT · Janvier – Décembre 2025 · 8 000 événements médiatiques</p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ─── KPI ROW ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total = len(df)
pct_conflict = df["IsConflict"].mean() * 100
avg_gold = df["GoldsteinScale"].mean()
avg_tone = df["AvgTone"].mean()
dom_emotion = df["GCAM_DominantEmotion"].mode()[0] if total > 0 else "—"

def kpi(col, label, value, help_text="", delta=None):
    with col:
        st.metric(label=label, value=value, delta=delta, help=help_text)

kpi(k1, "📰 Événements", f"{total:,}", "Total après filtres")
kpi(k2, "⚔️ Taux conflit", f"{pct_conflict:.1f}%", "% d'événements conflictuels")
kpi(k3, "⚖️ Goldstein moy.", f"{avg_gold:+.2f}", "Stabilité : + stable, − déstabilisant")
kpi(k4, "🎭 Ton médiatique", f"{avg_tone:+.2f}", "Ton moyen des articles")
kpi(k5, "❤️ Émotion dom.", dom_emotion, "Émotion dominante GCAM")

st.markdown("---")

# ─── ROW 1 : TIMELINE ─────────────────────────────────────────────────────────
st.subheader("📅 Évolution temporelle")

col_t1, col_t2 = st.columns([3, 2])

with col_t1:
    # Events per month by QuadLabel
    monthly_quad = (
        df.groupby(["month", "QuadLabel"])
        .size()
        .reset_index(name="count")
    )
    fig_timeline = px.bar(
        monthly_quad,
        x="month",
        y="count",
        color="QuadLabel",
        color_discrete_map=COLORS,
        labels={"month": "Mois", "count": "Événements", "QuadLabel": "Type"},
        title="Nombre d'événements par mois et type",
        barmode="stack",
    )
    fig_timeline.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with col_t2:
    # Goldstein evolution
    monthly_gold = df.groupby("month")["GoldsteinScale"].mean().reset_index()
    monthly_gold.columns = ["month", "goldstein"]
    monthly_tone = df.groupby("month")["AvgTone"].mean().reset_index()
    monthly_tone.columns = ["month", "tone"]
    merged = monthly_gold.merge(monthly_tone, on="month")

    fig_gs = go.Figure()
    fig_gs.add_trace(go.Scatter(
        x=merged["month"], y=merged["goldstein"],
        name="Goldstein", line=dict(color="#3498db", width=2),
        mode="lines+markers"
    ))
    fig_gs.add_trace(go.Scatter(
        x=merged["month"], y=merged["tone"],
        name="Ton médiatique", line=dict(color="#e74c3c", width=2, dash="dot"),
        mode="lines+markers"
    ))
    fig_gs.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig_gs.update_layout(
        title="Tensions & Ton médiatique mois/mois",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20),
        yaxis_title="Score moyen",
    )
    st.plotly_chart(fig_gs, use_container_width=True)

# ─── ROW 2 : GÉOGRAPHIE ───────────────────────────────────────────────────────
st.subheader("🗺️ Géographie des événements")

col_m1, col_m2 = st.columns([3, 2])

with col_m1:
    df_map = df.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"])
    fig_map = px.scatter_mapbox(
        df_map,
        lat="ActionGeo_Lat",
        lon="ActionGeo_Long",
        color="QuadLabel",
        size="NumArticles",
        hover_name="ActionGeo_FullName",
        hover_data={"Actor1Name": True, "EventLabel": True, "GoldsteinScale": ":.2f"},
        color_discrete_map=COLORS,
        zoom=5.5,
        center={"lat": 9.5, "lon": 2.3},
        mapbox_style="open-street-map",
        opacity=0.65,
        size_max=18,
        title="Carte des événements (taille = nb articles)",
    )
    fig_map.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_m2:
    dept_stats = (
        df.groupby("DepartementBenin")
        .agg(
            total=("IsConflict", "count"),
            pct_conflit=("IsConflict", "mean"),
            goldstein=("GoldsteinScale", "mean"),
        )
        .reset_index()
        .sort_values("total", ascending=True)
    )
    dept_stats["pct_conflit_label"] = (dept_stats["pct_conflit"] * 100).round(1)

    fig_dept = px.bar(
        dept_stats,
        x="total",
        y="DepartementBenin",
        orientation="h",
        color="pct_conflit",
        color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
        labels={"total": "Événements", "DepartementBenin": "Département", "pct_conflit": "% conflit"},
        title="Événements par département (couleur = % conflit)",
        text="total",
    )
    fig_dept.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20),
        coloraxis_colorbar=dict(title="% conflit", tickformat=".0%"),
    )
    fig_dept.update_traces(textposition="outside")
    st.plotly_chart(fig_dept, use_container_width=True)

# ─── ROW 3 : THÈMES & ÉMOTIONS ────────────────────────────────────────────────
st.subheader("🎯 Thèmes & Émotions")

col_th1, col_th2, col_th3 = st.columns(3)

with col_th1:
    theme_counts = {
        "Économie":     df["GKG_ThemeEconomy"].sum(),
        "Développement humain": df["GKG_ThemeHumanDev"].sum(),
        "Conflit":      df["GKG_ThemeConflict"].sum(),
        "Gouvernance":  df["GKG_ThemeGovern"].sum(),
        "Environnement":df["GKG_ThemeEnviro"].sum(),
    }
    theme_df = pd.DataFrame(
        list(theme_counts.items()), columns=["Thème", "Événements"]
    ).sort_values("Événements", ascending=True)

    fig_themes = px.bar(
        theme_df,
        x="Événements",
        y="Thème",
        orientation="h",
        color="Événements",
        color_continuous_scale="Blues",
        title="Répartition thématique",
        text="Événements",
    )
    fig_themes.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=40, b=20),
    )
    fig_themes.update_traces(textposition="outside")
    st.plotly_chart(fig_themes, use_container_width=True)

with col_th2:
    emo_counts = df["GCAM_DominantEmotion"].value_counts().reset_index()
    emo_counts.columns = ["Émotion", "count"]
    emo_counts["color"] = emo_counts["Émotion"].map(EMOTION_COLORS)

    fig_emo = px.pie(
        emo_counts,
        names="Émotion",
        values="count",
        color="Émotion",
        color_discrete_map=EMOTION_COLORS,
        hole=0.5,
        title="Distribution des émotions dominantes",
    )
    fig_emo.update_traces(textposition="inside", textinfo="percent+label")
    fig_emo.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig_emo, use_container_width=True)

with col_th3:
    # Radar GCAM moyens
    emo_means = df[["GCAM_Anger","GCAM_Fear","GCAM_Joy","GCAM_Sadness","GCAM_Trust","GCAM_Surprise"]].mean()
    labels = ["Colère","Peur","Joie","Tristesse","Confiance","Surprise"]
    values = emo_means.values.tolist()
    values += values[:1]
    labels_loop = labels + [labels[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=labels_loop,
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.3)",
        line=dict(color="#3498db", width=2),
        name="Intensité émotionnelle",
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title="Profil émotionnel moyen (GCAM)",
        margin=dict(t=60, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─── ROW 4 : ACTEURS & SOURCES ────────────────────────────────────────────────
st.subheader("🏛️ Acteurs & Sources médiatiques")

col_a1, col_a2 = st.columns(2)

with col_a1:
    top_actors = (
        df.groupby("Actor1Name")
        .agg(
            total=("IsConflict", "count"),
            pct_conflit=("IsConflict", "mean"),
            goldstein=("GoldsteinScale", "mean"),
        )
        .reset_index()
        .sort_values("total", ascending=False)
        .head(12)
        .sort_values("total", ascending=True)
    )

    fig_actors = px.bar(
        top_actors,
        x="total",
        y="Actor1Name",
        orientation="h",
        color="goldstein",
        color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
        color_continuous_midpoint=0,
        labels={"total": "Événements", "Actor1Name": "Acteur", "goldstein": "Goldstein moy."},
        title="Top 12 acteurs (couleur = Goldstein moyen)",
        text="total",
    )
    fig_actors.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=20),
        coloraxis_colorbar=dict(title="Goldstein"),
    )
    fig_actors.update_traces(textposition="outside")
    st.plotly_chart(fig_actors, use_container_width=True)

with col_a2:
    top_sources = (
        df.groupby(["SourceDomain", "SourceType"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(12)
        .sort_values("count", ascending=True)
    )
    source_color_map = {
        "Presse en ligne":   "#3498db",
        "Web TV":            "#9b59b6",
        "Media public":      "#2ecc71",
        "Officiel":          "#e67e22",
        "Presse economique": "#1abc9c",
        "Agence officielle": "#f39c12",
        "Site gouv.":        "#e74c3c",
    }

    fig_sources = px.bar(
        top_sources,
        x="count",
        y="SourceDomain",
        orientation="h",
        color="SourceType",
        color_discrete_map=source_color_map,
        labels={"count": "Articles", "SourceDomain": "Source", "SourceType": "Type"},
        title="Top 12 sources médiatiques",
        text="count",
    )
    fig_sources.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
    )
    fig_sources.update_traces(textposition="outside")
    st.plotly_chart(fig_sources, use_container_width=True)

# ─── ROW 5 : TABLEAU ÉVÉNEMENTS RÉCENTS ───────────────────────────────────────
st.subheader("🔍 Données brutes — événements")

with st.expander("Afficher / masquer le tableau (100 derniers événements filtrés)"):
    cols_show = [
        "date", "DepartementBenin", "Actor1Name", "EventLabel",
        "QuadLabel", "GoldsteinScale", "AvgTone",
        "GCAM_DominantEmotion", "SourceDomain", "ToneCategory"
    ]
    st.dataframe(
        df[cols_show].sort_values("date", ascending=False).head(100),
        use_container_width=True,
        height=350,
    )

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🇧🇯 **Observatoire Médiatique Bénin** · Hackathon GDELT 2025 · "
    "Données : GDELT Project (gdeltproject.org) · "
    "Dashboard construit avec Streamlit & Plotly"
)
