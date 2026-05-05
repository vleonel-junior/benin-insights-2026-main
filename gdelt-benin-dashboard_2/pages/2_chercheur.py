import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, get_source_stats, get_theme_stats, COLORS

st.set_page_config(page_title="Vue Chercheur · GDELT Bénin", layout="wide")

st.markdown("""
<style>
.metric-card { background:#f1efe8; border-radius:10px; padding:16px 20px; margin-bottom:8px; }
.metric-val  { font-size:26px; font-weight:600; color:#2c2c2a; line-height:1.1; }
.metric-lbl  { font-size:13px; color:#5f5e5a; margin-top:4px; }
.badge { display:inline-block; font-size:11px; padding:2px 10px; border-radius:20px; margin-top:6px; font-weight:500; }
.badge-b { background:#e6f1fb; color:#185fa5; }
.badge-o { background:#faeeda; color:#854f0b; }
.badge-g { background:#eaf3de; color:#3b6d11; }
.insight { background:#f1efe8; border-left:3px solid #534AB7; padding:12px 16px; border-radius:6px; margin:8px 0; font-size:14px; color:#3d3d3a; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔬 Vue Chercheur")
    st.caption("Sources, émotions, corrélations")
    st.divider()
    st.page_link("app.py",                label="← Accueil",    icon="🏠")
    st.page_link("pages/1_journaliste.py",label="Journaliste",  icon="📰")
    st.page_link("pages/3_decideur.py",   label="Décideur",     icon="🗺️")
    st.divider()
    metric_src = st.selectbox("Métrique sources", [
        "Taux de conflit (%)", "Taux négatif (%)",
        "Intensité émotionnelle", "Écart de ton (ToneGap)"
    ])

st.title("🔬 Vue Chercheur — Couverture médiatique & Biais émotionnels")
st.caption("Analyse de 7 types de sources · 5 thèmes · émotions GCAM · corrélation Goldstein/Tone")

# ── KPIs ─────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="metric-card"><div class="metric-val">7</div><div class="metric-lbl">types de sources</div><span class="badge badge-b">presse, TV, officiel…</span></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="metric-card"><div class="metric-val">0,51</div><div class="metric-lbl">corrélation Goldstein/Tone</div><span class="badge badge-b">modérée, significative</span></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="metric-card"><div class="metric-val">Trust</div><div class="metric-lbl">émotion dominante globale</div><span class="badge badge-g">toutes sources</span></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="metric-card"><div class="metric-val">1 271</div><div class="metric-lbl">événements ToneGap &gt; 5</div><span class="badge badge-o">fort écart positif/négatif</span></div>', unsafe_allow_html=True)

st.divider()

# ── Couverture par source ─────────────────────────────────
st.subheader("Couverture médiatique par type de source")

src = get_source_stats()
metric_map = {
    "Taux de conflit (%)":       ("pct_conflit",  COLORS["rouge"]),
    "Taux négatif (%)":          ("pct_negatif",  COLORS["orange"]),
    "Intensité émotionnelle":    ("intensite",    COLORS["violet"]),
    "Écart de ton (ToneGap)":    ("tonegap",      COLORS["bleu"]),
}
col_key, col_color = metric_map[metric_src]
src_sorted = src.sort_values(col_key, ascending=True)

fig1 = px.bar(src_sorted, y="SourceType", x=col_key, orientation="h",
              color_discrete_sequence=[col_color],
              labels={col_key: metric_src, "SourceType": ""})
fig1.update_layout(height=320, margin=dict(t=20,b=20,l=20,r=20),
                   plot_bgcolor="white", paper_bgcolor="white")
fig1.update_xaxes(gridcolor="#f0efe8"); fig1.update_yaxes(gridcolor="#f0efe8")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
<div class="insight">
<b>Insight :</b> Les médias publics (42,4%) et agences officielles (39,2%) publient
<i>plus</i> de contenu négatif que la presse indépendante (39,0%). Les sites gouvernementaux
ont le ToneGap le plus élevé — discours plus polarisé, peu de nuances.
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Biais émotionnel par thème ────────────────────────────
st.subheader("Biais émotionnel par thème (vs baseline globale)")

themes = get_theme_stats()
baseline = {"anger": 0.945, "fear": 0.756, "joy": 1.985, "trust": 2.488}

fig2 = go.Figure()
emotions = [
    ("anger", "Colère",    COLORS["rouge"]),
    ("fear",  "Peur",      COLORS["orange"]),
    ("joy",   "Joie",      COLORS["vert"]),
    ("trust", "Confiance", COLORS["bleu"]),
]
for col, label, color in emotions:
    fig2.add_bar(name=label, x=themes["theme"], y=themes[col].round(3),
                 marker_color=color)

# Ligne baseline anger
fig2.update_layout(barmode="group", height=360, margin=dict(t=20,b=20,l=20,r=20),
                   legend=dict(orientation="h", y=1.05),
                   plot_bgcolor="white", paper_bgcolor="white",
                   yaxis_title="Score émotionnel moyen")
fig2.update_xaxes(gridcolor="#f0efe8"); fig2.update_yaxes(gridcolor="#f0efe8")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div class="insight">
<b>Insight :</b> Le thème Conflit/Sécurité est le <i>seul</i> avec un ton moyen négatif (−0,17).
Il génère 2× plus de colère que la baseline (+22%) et le plus de peur.
L'Économie est le thème le plus joyeux — la couverture reste optimiste même en contexte tendu.
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Corrélation Goldstein / Tone ──────────────────────────
st.subheader("Corrélation Goldstein × Ton médiatique")

col_g, col_e = st.columns(2)

with col_g:
    corr_data = pd.DataFrame({
        "Contexte":     ["Tous événements", "Thème Conflit", "Thème Économie", "Thème Gouvernance"],
        "Corrélation":  [0.513, 0.564, 0.459, 0.513],
        "Couleur":      [COLORS["gris"], COLORS["rouge"], COLORS["bleu"], COLORS["violet"]],
    })
    fig3 = px.bar(corr_data, y="Contexte", x="Corrélation", orientation="h",
                  color="Contexte",
                  color_discrete_map={r: c for r, c in zip(corr_data["Contexte"], corr_data["Couleur"])},
                  range_x=[0, 0.7])
    fig3.update_layout(height=280, showlegend=False, margin=dict(t=20,b=20,l=20,r=20),
                       plot_bgcolor="white", paper_bgcolor="white",
                       xaxis_title="Coefficient de corrélation (r)")
    fig3.update_xaxes(gridcolor="#f0efe8"); fig3.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("r = 0,51 global — La corrélation est plus forte pour les conflits (0,56) que pour l'économie (0,46).")

with col_e:
    st.markdown("**Émotion dominante par source** (empilé)")
    dom_data = pd.DataFrame({
        "Source": ["Agence off.", "Média pub.", "Officiel", "Presse éco.", "Site gouv.", "Web TV"],
        "Trust":    [161, 221, 231, 192, 161, 284],
        "Joy":      [143, 198, 176, 126, 112, 207],
        "Surprise": [34,  73,  55,  52,  30,  59],
        "Fear":     [35,  47,  43,  40,  39,  55],
        "Anger":    [53,  56,  47,  39,  33,  67],
    })
    fig4 = go.Figure()
    emo_colors = [COLORS["bleu"], COLORS["vert"], COLORS["orange"], COLORS["orange"], COLORS["rouge"]]
    for emo, color in zip(["Trust","Joy","Surprise","Fear","Anger"],
                          [COLORS["bleu"], COLORS["vert"], "#EF9F27", "#FAC775", COLORS["rouge"]]):
        fig4.add_bar(name=emo, y=dom_data["Source"], x=dom_data[emo],
                     orientation="h", marker_color=color)
    fig4.update_layout(barmode="stack", height=280, margin=dict(t=20,b=20,l=20,r=20),
                       legend=dict(orientation="h", y=1.05),
                       plot_bgcolor="white", paper_bgcolor="white")
    fig4.update_xaxes(gridcolor="#f0efe8"); fig4.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Scatter interactif ────────────────────────────────────
st.subheader("Explorer : Goldstein vs Ton médiatique (échantillon)")
df = load_data()
sample = df.sample(min(800, len(df)), random_state=42)
fig5 = px.scatter(sample, x="GoldsteinScale", y="AvgTone",
                  color="QuadLabel", opacity=0.5,
                  color_discrete_map={
                      "Conflit materiel": COLORS["rouge"],
                      "Conflit verbal":   COLORS["orange"],
                      "Coopération":      COLORS["vert"],
                      "Coopération mat.": COLORS["bleu"],
                  },
                  labels={"GoldsteinScale": "Goldstein (stabilité)", "AvgTone": "Ton moyen"},
                  trendline="ols")
fig5.update_layout(height=380, margin=dict(t=20,b=20,l=20,r=20),
                   plot_bgcolor="white", paper_bgcolor="white",
                   legend=dict(orientation="h", y=1.02))
fig5.update_xaxes(gridcolor="#f0efe8"); fig5.update_yaxes(gridcolor="#f0efe8")
st.plotly_chart(fig5, use_container_width=True)
st.caption("Droite de tendance OLS · r = 0,51 · Les événements conflictuels (rouge/orange) se concentrent en bas à gauche.")

st.divider()
st.caption("Source : GDELT Project · GDELT Bénin 2025")
