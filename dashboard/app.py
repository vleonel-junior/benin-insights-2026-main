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
    import os
    DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "gdelt_replubique_benin_clean_.csv")
    df = pd.read_csv(DATA_PATH)
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

    import numpy as np
    def norm(s): return (s - s.min()) / (s.max() - s.min() + 1e-9)

    df_map = df.groupby("DepartementBenin").agg(
        nb_conflits=("IsConflict", "sum"),
        pct_conflit=("IsConflict", "mean"),
        goldstein=("GoldsteinScale", "mean"),
        emotion_intensity=("GKG_EmotionIntensity", "mean"),
        total=("IsConflict", "count"),
    ).reset_index()

    df_map["risk_score"] = (
        0.4 * norm(df_map["pct_conflit"]) +
        0.4 * norm(-df_map["goldstein"]) +
        0.2 * norm(df_map["emotion_intensity"])
    ) * 100

    df_map["lat"] = df_map["DepartementBenin"].map(lambda d: DEPT_COORDS.get(d, {}).get("lat"))
    df_map["lon"] = df_map["DepartementBenin"].map(lambda d: DEPT_COORDS.get(d, {}).get("lon"))
    df_map["pct_conflit_label"] = (df_map["pct_conflit"] * 100).round(1)
    df_map["risk_score_r"] = df_map["risk_score"].round(1)
    df_map = df_map.dropna(subset=["lat", "lon"])

    fig_map = px.scatter_mapbox(
        df_map,
        lat="lat", lon="lon",
        size="nb_conflits",
        color="risk_score",
        hover_name="DepartementBenin",
        hover_data={
            "pct_conflit_label": True,
            "risk_score_r": True,
            "total": True,
            "lat": False, "lon": False,
            "risk_score": False,
        },
        labels={
            "pct_conflit_label": "% conflit",
            "risk_score_r": "Score de risque",
            "total": "Total événements",
        },
        color_continuous_scale=["#639922", "#EF9F27", "#E24B4A"],
        size_max=45,
        zoom=6,
        center={"lat": 9.3, "lon": 2.3},
        mapbox_style="carto-positron",
        title="Carte des départements — Score de risque (taille = nb conflits)",
    )
    fig_map.update_layout(
        height=480,
        margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Risque"),
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

# ─── ROW 6 : ANALYSE PRÉDICTIVE ───────────────────────────────────────────────
st.markdown("---")
st.subheader("🤖 Analyse Prédictive & Modélisation")

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Détection de ruptures",
    "🔴 Prédiction de conflit",
    "🟡 Clustering départements",
    "🔵 Prévision des tensions",
])

# ── TAB 1 : PELT / BinSeg ─────────────────────────────────────────────────────
with tab1:
    st.markdown("**Question :** *Quand la situation médiatique a-t-elle brusquement changé ?*")
    try:
        import ruptures as rpt
        from sklearn.preprocessing import StandardScaler

        weekly = df.set_index(
            pd.to_datetime(df["date"], errors="coerce")
        ).resample("W").agg(
            goldstein=("GoldsteinScale", "mean"),
            tone=("AvgTone", "mean"),
            conflict_rate=("IsConflict", "mean"),
        ).dropna()

        signal_multi = StandardScaler().fit_transform(
            weekly[["goldstein", "tone", "conflict_rate"]]
        )

        algo_bs = rpt.Binseg(model="rbf").fit(signal_multi)
        bkps = algo_bs.predict(n_bkps=4)
        rupture_dates = [weekly.index[i - 1] for i in bkps if i < len(weekly)]

        # Courbe Goldstein + Ton + lignes de rupture
        fig_pelt = go.Figure()
        fig_pelt.add_trace(go.Scatter(
            x=weekly.index, y=weekly["goldstein"],
            name="Goldstein (stabilité)", line=dict(color="#3498db", width=2),
        ))
        fig_pelt.add_trace(go.Scatter(
            x=weekly.index, y=weekly["tone"],
            name="Ton médiatique", line=dict(color="#e67e22", width=2, dash="dot"),
        ))
        for rd in rupture_dates:
            fig_pelt.add_vline(
                x=rd.timestamp() * 1000,
                line_dash="dash", line_color="#e74c3c", line_width=2,
                annotation_text=f"⚡ {rd.strftime('%b %Y')}",
                annotation_position="top",
                annotation_font_color="#e74c3c",
            )
        fig_pelt.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.4)
        fig_pelt.update_layout(
            title="Série temporelle hebdomadaire — Ruptures structurelles détectées",
            xaxis_title="Semaine",
            yaxis_title="Score moyen",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=420,
        )
        st.plotly_chart(fig_pelt, use_container_width=True)

        st.info(
            f"**{len(rupture_dates)} ruptures détectées** : "
            + ", ".join([f"**{d.strftime('%B %Y')}**" for d in rupture_dates])
            + ". Ces moments correspondent à des changements brusques et simultanés "
            "du ton médiatique, de la stabilité politique et du taux de conflictualité."
        )
    except ImportError:
        st.warning("Module `ruptures` non disponible. Ajoutez-le au requirements.txt.")

# ── TAB 2 : RANDOM FOREST ─────────────────────────────────────────────────────
with tab2:
    st.markdown("**Question :** *Quels facteurs prédisent le mieux un événement conflictuel ?*")
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, f1_score

        df_rf = df.copy()
        df_rf["dept_encoded"] = df_rf["DepartementBenin"].astype("category").cat.codes

        features_rf = [
            "GKG_ThemeConflict", "GKG_ThemeEconomy", "GKG_ThemeGovern",
            "GKG_ThemeHumanDev", "GKG_ThemeEnviro", "GKG_EmotionIntensity",
            "GCAM_Anger", "GCAM_Fear", "GCAM_Joy", "GCAM_Trust", "GCAM_Surprise",
            "NumArticles", "MediaWeight", "dept_encoded",
        ]
        feature_labels = [
            "Thème Conflit", "Thème Économie", "Thème Gouvernance",
            "Dév. humain", "Environnement", "Intensité émotionnelle",
            "Colère", "Peur", "Joie", "Confiance", "Surprise",
            "Nb articles", "Poids médiatique", "Département",
        ]

        X_rf = df_rf[features_rf]
        y_rf = df_rf["IsConflict"]
        X_tr, X_te, y_tr, y_te = train_test_split(X_rf, y_rf, test_size=0.2, random_state=42)

        rf_model = RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1)
        rf_model.fit(X_tr, y_tr)
        y_pred_rf = rf_model.predict(X_te)

        acc = accuracy_score(y_te, y_pred_rf)
        f1 = f1_score(y_te, y_pred_rf)

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Accuracy", f"{acc:.1%}")
        m2.metric("⚖️ F1-Score", f"{f1:.1%}")
        m3.metric("🌳 Arbres", "150")

        importances_rf = pd.DataFrame({
            "Feature": feature_labels,
            "Importance": rf_model.feature_importances_,
        }).sort_values("Importance", ascending=True)

        fig_rf = px.bar(
            importances_rf,
            x="Importance", y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale=["#bdc3c7", "#3498db", "#e74c3c"],
            title="Importance des features — Random Forest",
            text=importances_rf["Importance"].apply(lambda v: f"{v:.1%}"),
        )
        fig_rf.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(t=40, b=20),
            height=420,
        )
        fig_rf.update_traces(textposition="outside")
        st.plotly_chart(fig_rf, use_container_width=True)

        top3 = importances_rf.sort_values("Importance", ascending=False).head(3)["Feature"].tolist()
        st.info(
            f"Le modèle prédit les conflits avec **{acc:.1%} de précision** (F1={f1:.1%}). "
            f"Les 3 facteurs les plus déterminants sont : **{top3[0]}**, **{top3[1]}** et **{top3[2]}**. "
            "Les signaux émotionnels (colère, peur, joie) dominent sur les signaux thématiques."
        )
    except ImportError:
        st.warning("Module `scikit-learn` non disponible.")

# ── TAB 3 : KMEANS ────────────────────────────────────────────────────────────
with tab3:
    st.markdown("**Question :** *Quelles zones du Bénin ont un profil de risque similaire ?*")
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        DEPT_COORDS_KM = {
            "Alibori":{"lat":11.30,"lon":2.85}, "Atacora":{"lat":10.63,"lon":1.65},
            "Atlantique":{"lat":6.65,"lon":2.25}, "Borgou":{"lat":9.50,"lon":2.78},
            "Collines":{"lat":8.35,"lon":2.30}, "Couffo":{"lat":7.03,"lon":1.75},
            "Donga":{"lat":9.72,"lon":1.68}, "Littoral":{"lat":6.37,"lon":2.42},
            "Mono":{"lat":6.80,"lon":1.62}, "Oueme":{"lat":6.75,"lon":2.60},
            "Plateau":{"lat":7.35,"lon":2.58}, "Zou":{"lat":7.50,"lon":2.18},
        }
        CLUSTER_LABELS = {0: "🟢 Zone stable", 1: "🟠 Sous tension", 2: "🔴 Zone critique"}
        CLUSTER_COLORS = {0: "#2ecc71", 1: "#e67e22", 2: "#e74c3c"}

        km_df = df.groupby("DepartementBenin").agg(
            pct_conflit=("IsConflict", "mean"),
            goldstein=("GoldsteinScale", "mean"),
            avg_tone=("AvgTone", "mean"),
            emotion=("GKG_EmotionIntensity", "mean"),
        ).reset_index()

        scaler_km = StandardScaler()
        X_km = scaler_km.fit_transform(km_df[["pct_conflit", "goldstein", "avg_tone", "emotion"]])
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        km_df["cluster_id"] = kmeans.fit_predict(X_km)

        # Réassigner les clusters par ordre de risque croissant (pct_conflit)
        cluster_risk = km_df.groupby("cluster_id")["pct_conflit"].mean().sort_values()
        risk_map = {old: new for new, old in enumerate(cluster_risk.index)}
        km_df["cluster_id"] = km_df["cluster_id"].map(risk_map)
        km_df["cluster_label"] = km_df["cluster_id"].map(CLUSTER_LABELS)

        km_df["lat"] = km_df["DepartementBenin"].map(lambda d: DEPT_COORDS_KM.get(d, {}).get("lat"))
        km_df["lon"] = km_df["DepartementBenin"].map(lambda d: DEPT_COORDS_KM.get(d, {}).get("lon"))
        km_df["pct_label"] = (km_df["pct_conflit"] * 100).round(1)
        km_df["color"] = km_df["cluster_id"].map(CLUSTER_COLORS)

        fig_km = px.scatter_mapbox(
            km_df,
            lat="lat", lon="lon",
            color="cluster_label",
            size="pct_conflit",
            hover_name="DepartementBenin",
            hover_data={"pct_label": True, "goldstein": ":.2f", "lat": False, "lon": False, "pct_conflit": False},
            color_discrete_map={v: CLUSTER_COLORS[k] for k, v in CLUSTER_LABELS.items()},
            labels={"pct_label": "% conflit", "goldstein": "Goldstein moy.", "cluster_label": "Profil"},
            size_max=35,
            zoom=6,
            center={"lat": 9.3, "lon": 2.3},
            mapbox_style="carto-positron",
            title="Profils de risque par département (KMeans k=3)",
        )
        fig_km.update_layout(
            height=460,
            margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_km, use_container_width=True)

        col_cl1, col_cl2, col_cl3 = st.columns(3)
        for cid, label in CLUSTER_LABELS.items():
            depts = km_df[km_df["cluster_id"] == cid]["DepartementBenin"].tolist()
            col = [col_cl1, col_cl2, col_cl3][cid]
            with col:
                st.markdown(f"**{label}**")
                st.markdown(", ".join(depts) if depts else "—")

        st.info(
            "Le clustering KMeans (k=3) identifie trois profils distincts basés sur le taux de conflit, "
            "le score Goldstein, le ton médiatique et l'intensité émotionnelle. "
            "Les départements d'un même cluster partagent une dynamique médiatique similaire."
        )
    except ImportError:
        st.warning("Module `scikit-learn` non disponible.")

# ── TAB 4 : PRÉVISION POLYNOMIALE ─────────────────────────────────────────────
with tab4:
    st.markdown("**Question :** *Vers où va la tendance des tensions dans les prochains mois ?*")

    monthly_gold = df.groupby("month")["GoldsteinScale"].mean().reset_index()
    monthly_gold["month_dt"] = pd.to_datetime(monthly_gold["month"])
    monthly_gold = monthly_gold.sort_values("month_dt")

    x_hist = np.arange(len(monthly_gold))
    y_hist = monthly_gold["GoldsteinScale"].values
    coeffs_p = np.polyfit(x_hist, y_hist, 2)
    poly = np.poly1d(coeffs_p)

    # Projection 3 mois
    n_proj = 3
    x_proj = np.arange(len(monthly_gold), len(monthly_gold) + n_proj)
    last_date = monthly_gold["month_dt"].iloc[-1]
    proj_dates = [last_date + pd.DateOffset(months=i + 1) for i in range(n_proj)]

    y_fit = poly(x_hist)
    y_proj = poly(x_proj)

    # Intervalle de confiance basé sur résidus
    residuals = y_hist - y_fit
    std_resid = residuals.std()
    ci_factor = 1.96

    fig_proj = go.Figure()

    # Données historiques
    fig_proj.add_trace(go.Scatter(
        x=monthly_gold["month_dt"], y=y_hist,
        mode="lines+markers",
        name="Goldstein observé",
        line=dict(color="#3498db", width=2),
        marker=dict(size=7),
    ))

    # Courbe ajustée
    fig_proj.add_trace(go.Scatter(
        x=monthly_gold["month_dt"], y=y_fit,
        mode="lines",
        name="Tendance ajustée",
        line=dict(color="#9b59b6", width=2, dash="dot"),
    ))

    # Projection + intervalle
    fig_proj.add_trace(go.Scatter(
        x=proj_dates + proj_dates[::-1],
        y=list(y_proj + ci_factor * std_resid) + list((y_proj - ci_factor * std_resid)[::-1]),
        fill="toself",
        fillcolor="rgba(231,76,60,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Intervalle de confiance 95%",
    ))
    fig_proj.add_trace(go.Scatter(
        x=proj_dates, y=y_proj,
        mode="lines+markers",
        name="Projection 3 mois",
        line=dict(color="#e74c3c", width=2, dash="dash"),
        marker=dict(size=9, symbol="diamond"),
    ))

    fig_proj.add_vline(
        x=monthly_gold["month_dt"].iloc[-1].timestamp() * 1000,
        line_dash="dash", line_color="gray", opacity=0.6,
        annotation_text="Aujourd'hui →",
        annotation_position="top left",
    )
    fig_proj.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.4)

    fig_proj.update_layout(
        title="Prévision du Goldstein Scale — Régression polynomiale degré 2",
        xaxis_title="Mois",
        yaxis_title="GoldsteinScale moyen",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
    )
    st.plotly_chart(fig_proj, use_container_width=True)

    trend_dir = "📈 haussière (stabilisation)" if coeffs_p[0] > 0 or y_proj[-1] > y_hist[-1] else "📉 baissière (dégradation)"
    st.info(
        f"La tendance pour les 3 prochains mois est **{trend_dir}**. "
        f"Le modèle prédit un Goldstein moyen de **{y_proj[-1]:.2f}** en {proj_dates[-1].strftime('%B %Y')} "
        f"(intervalle 95% : [{y_proj[-1] - ci_factor*std_resid:.2f}, {y_proj[-1] + ci_factor*std_resid:.2f}]). "
        "Cette projection est indicative — elle suppose que les dynamiques actuelles restent stables."
    )

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🇧🇯 **Observatoire Médiatique Bénin** · Hackathon GDELT 2025 · "
    "Données : GDELT Project (gdeltproject.org) · "
    "Dashboard construit avec Streamlit & Plotly"
)