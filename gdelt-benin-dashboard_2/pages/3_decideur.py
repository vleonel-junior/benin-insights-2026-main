import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, get_dept_stats, get_theme_stats, get_zone_monthly, DEPT_COORDS, COLORS

st.set_page_config(page_title="Vue Décideur · GDELT Bénin", layout="wide")

st.markdown("""
<style>
.metric-card { background:#f1efe8; border-radius:10px; padding:16px 20px; margin-bottom:8px; }
.metric-val  { font-size:26px; font-weight:600; color:#2c2c2a; line-height:1.1; }
.metric-lbl  { font-size:13px; color:#5f5e5a; margin-top:4px; }
.badge { display:inline-block; font-size:11px; padding:2px 10px; border-radius:20px; margin-top:6px; font-weight:500; }
.badge-r { background:#fcebeb; color:#a32d2d; }
.badge-o { background:#faeeda; color:#854f0b; }
.badge-g { background:#eaf3de; color:#3b6d11; }
.badge-b { background:#e6f1fb; color:#185fa5; }
.insight { background:#f1efe8; border-left:3px solid #E24B4A; padding:12px 16px; border-radius:6px; margin:8px 0; font-size:14px; color:#3d3d3a; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🗺️ Vue Décideur")
    st.caption("Risques, zones, thèmes sensibles")
    st.divider()
    st.page_link("app.py",                label="← Accueil",    icon="🏠")
    st.page_link("pages/1_journaliste.py",label="Journaliste",  icon="📰")
    st.page_link("pages/2_chercheur.py",  label="Chercheur",    icon="🔬")
    st.divider()
    seuil_risque = st.slider("Seuil score de risque", 20, 35, 28, 1)
    show_materiel = st.checkbox("Afficher conflits matériels uniquement", value=False)

st.title("🗺️ Vue Décideur — Zones à risque & Thèmes sensibles")
st.caption("Score de risque composite : taux de conflit × 0,4 + colère × 10 + peur × 10 + (1 − Goldstein) × 10")

# ── KPIs ─────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="metric-card"><div class="metric-val">Borgou</div><div class="metric-lbl">département le + à risque</div><span class="badge badge-r">score composite 30,8</span></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="metric-card"><div class="metric-val">32,5%</div><div class="metric-lbl">taux conflit — Sécurité</div><span class="badge badge-r">thème le + volatile</span></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="metric-card"><div class="metric-val">Nord</div><div class="metric-lbl">zone la + tendue</div><span class="badge badge-o">colère 0,95 vs 0,83 sud</span></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="metric-card"><div class="metric-val">47,5%</div><div class="metric-lbl">conflits matériels — Zou</div><span class="badge badge-r">le + élevé du pays</span></div>', unsafe_allow_html=True)

st.divider()

# ── Carte bulle des risques ───────────────────────────────
st.subheader("Carte des risques par département")

dept = get_dept_stats()
dept["lat"] = dept["DepartementBenin"].map(lambda d: DEPT_COORDS.get(d, {}).get("lat"))
dept["lon"] = dept["DepartementBenin"].map(lambda d: DEPT_COORDS.get(d, {}).get("lon"))
dept_map = dept.dropna(subset=["lat", "lon"])

if show_materiel:
    size_col = "conflit_materiel"
    size_label = "Conflits matériels"
else:
    size_col = "conflits"
    size_label = "Total conflits"

dept_map = dept_map.copy()
dept_map["risk_level"] = dept_map["risk_score"].apply(
    lambda s: "Élevé" if s >= 30 else ("Modéré+" if s >= 29 else ("Modéré" if s >= 27 else "Faible"))
)

fig_map = px.scatter_mapbox(
    dept_map,
    lat="lat", lon="lon",
    size=size_col,
    color="risk_score",
    hover_name="DepartementBenin",
    hover_data={"pct_conflit": True, "risk_score": True, "lat": False, "lon": False},
    color_continuous_scale=["#639922", "#EF9F27", "#E24B4A"],
    size_max=40,
    zoom=6,
    mapbox_style="carto-positron",
    labels={"risk_score": "Score risque", "pct_conflit": "% conflits", size_col: size_label},
    title=""
)
fig_map.update_layout(height=480, margin=dict(t=10, b=10, l=10, r=10),
                      coloraxis_colorbar=dict(title="Score", thickness=12))
st.plotly_chart(fig_map, use_container_width=True)

# ── Tableau scores de risque ──────────────────────────────
st.subheader("Classement des départements par score de risque")

dept_table = dept[["DepartementBenin", "risk_score", "pct_conflit", "conflit_materiel", "conflit_verbal", "goldstein"]].copy()
dept_table.columns = ["Département", "Score risque", "% conflit", "Conflits mat.", "Conflits verb.", "Goldstein moy."]
dept_table = dept_table.sort_values("Score risque", ascending=False).reset_index(drop=True)
dept_table["Score risque"] = dept_table["Score risque"].round(1)
dept_table["Goldstein moy."] = dept_table["Goldstein moy."].round(3)

alerte = dept_table[dept_table["Score risque"] >= seuil_risque]
st.markdown(f"**{len(alerte)} département(s) au-dessus du seuil {seuil_risque} :** {', '.join(alerte['Département'].tolist())}")

st.dataframe(
    dept_table.style.background_gradient(subset=["Score risque"], cmap="RdYlGn_r"),
    use_container_width=True, hide_index=True, height=340
)

st.divider()

# ── Thèmes sectoriels ─────────────────────────────────────
st.subheader("Volatilité des thèmes sectoriels")

themes = get_theme_stats()
col_t1, col_t2 = st.columns(2)

with col_t1:
    themes_sorted = themes.sort_values("pct_conflit", ascending=True)
    colors_themes = [COLORS["vert"], COLORS["bleu"], COLORS["violet"],
                     COLORS["orange"], COLORS["rouge"]]
    fig_t1 = px.bar(themes_sorted, y="theme", x="pct_conflit", orientation="h",
                    color="theme",
                    color_discrete_sequence=colors_themes,
                    labels={"pct_conflit": "Taux de conflit (%)", "theme": ""},
                    title="Taux de conflit par thème")
    fig_t1.update_layout(showlegend=False, height=300, margin=dict(t=40,b=20,l=20,r=20),
                         plot_bgcolor="white", paper_bgcolor="white")
    fig_t1.update_xaxes(gridcolor="#f0efe8"); fig_t1.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig_t1, use_container_width=True)

with col_t2:
    themes_sorted2 = themes.sort_values("goldstein", ascending=True)
    fig_t2 = px.bar(themes_sorted2, y="theme", x="goldstein", orientation="h",
                    color="theme",
                    color_discrete_sequence=colors_themes,
                    labels={"goldstein": "Goldstein (+ = stable)", "theme": ""},
                    title="Stabilité (Goldstein) par thème")
    fig_t2.update_layout(showlegend=False, height=300, margin=dict(t=40,b=20,l=20,r=20),
                         plot_bgcolor="white", paper_bgcolor="white")
    fig_t2.update_xaxes(gridcolor="#f0efe8"); fig_t2.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig_t2, use_container_width=True)

st.markdown("""
<div class="insight">
<b>Insight :</b> Conflit/Sécurité (32,5% de conflits, Goldstein 0,20) est de loin le thème
le plus instable. L'Agriculture cristallise plus de tensions que l'Économie générale (23,8% vs 16,2%)
— signe direct de tensions dans la filière coton. L'Énergie reste paradoxalement stable.
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Évolution Nord / Centre / Sud ─────────────────────────
st.subheader("Évolution mensuelle du taux de conflit — Nord / Centre / Sud")

zone_df = get_zone_monthly()
mois_labels = [m[5:] + "/" + m[2:4] for m in zone_df["month"]]

fig_z = go.Figure()
zone_colors = {"Nord": COLORS["rouge"], "Centre": COLORS["orange"], "Sud": COLORS["bleu"]}
for zone in ["Nord", "Centre", "Sud"]:
    if zone in zone_df.columns:
        fig_z.add_scatter(
            x=mois_labels, y=zone_df[zone].round(1),
            mode="lines+markers",
            name=zone,
            line=dict(color=zone_colors[zone], width=2.5),
            marker=dict(size=6),
            fill="tozeroy" if zone == "Nord" else None,
            fillcolor=f"rgba({','.join(str(int(zone_colors[zone].lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.06)"
        )
fig_z.update_layout(
    height=360, margin=dict(t=20,b=20,l=20,r=20),
    plot_bgcolor="white", paper_bgcolor="white",
    legend=dict(orientation="h", y=1.05),
    yaxis_title="% conflits",
    xaxis_title=""
)
fig_z.update_xaxes(gridcolor="#f0efe8"); fig_z.update_yaxes(gridcolor="#f0efe8")
st.plotly_chart(fig_z, use_container_width=True)

st.markdown("""
<div class="insight">
<b>Insight :</b> Le Centre (Collines, Zou) est la zone la plus <i>volatile</i> : pics à 34% en janvier,
creux à 17% en septembre. Le Nord est structurellement tendu mais stable. Le Sud fluctue peu,
mais a connu deux pics en mars et octobre — surveiller ces périodes.
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Source : GDELT Project · GDELT Bénin 2025 · Score de risque = taux_conflit × 0,4 + colère × 10 + peur × 10 + (1 − Goldstein) × 10")
