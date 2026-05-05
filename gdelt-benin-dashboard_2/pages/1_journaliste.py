import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, get_monthly_stats, get_dept_stats, get_actor_stats, COLORS

st.set_page_config(page_title="Vue Journaliste · GDELT Bénin", layout="wide")

st.markdown("""
<style>
.metric-card { background:#f1efe8; border-radius:10px; padding:16px 20px; margin-bottom:8px; }
.metric-val  { font-size:26px; font-weight:600; color:#2c2c2a; line-height:1.1; }
.metric-lbl  { font-size:13px; color:#5f5e5a; margin-top:4px; }
.badge { display:inline-block; font-size:11px; padding:2px 10px; border-radius:20px; margin-top:6px; font-weight:500; }
.badge-r { background:#fcebeb; color:#a32d2d; }
.badge-o { background:#faeeda; color:#854f0b; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📰 Vue Journaliste")
    st.caption("Conflits, acteurs, tensions")
    st.divider()
    st.page_link("app.py",                label="← Accueil",     icon="🏠")
    st.page_link("pages/2_chercheur.py",  label="Chercheur",     icon="🔬")
    st.page_link("pages/3_decideur.py",   label="Décideur",      icon="🗺️")
    st.divider()

    df_all = load_data()
    mois_dispo = sorted(df_all["month"].unique().tolist())
    mois_sel = st.multiselect("Filtrer par mois", mois_dispo, default=mois_dispo,
                               format_func=lambda m: m[5:] + "/" + m[2:4])
    dept_dispo = sorted(df_all["DepartementBenin"].dropna().unique().tolist())
    dept_sel = st.multiselect("Filtrer par département", dept_dispo, default=dept_dispo)

# ── Données filtrées ──────────────────────────────────────
df = load_data()
df = df[df["month"].isin(mois_sel) & df["DepartementBenin"].isin(dept_sel)]

# ── KPIs ─────────────────────────────────────────────────
st.title("📰 Vue Journaliste — Conflits & Tensions")
st.caption(f"{len(df):,} événements · {len(mois_sel)} mois · {len(dept_sel)} départements sélectionnés")

k1, k2, k3, k4 = st.columns(4)
n_conf = int(df["IsConflict"].sum())
n_mat  = int((df["QuadLabel"] == "Conflit materiel").sum())
dept_top = df[df["IsConflict"]==1]["DepartementBenin"].value_counts().idxmax()
actor_top = df[df["IsNegative"]==1]["Actor1Name"].value_counts().idxmax()

with k1:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{n_conf:,}</div><div class="metric-lbl">événements conflictuels</div><span class="badge badge-o">{round(n_conf/len(df)*100,1)}% du total</span></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{n_mat:,}</div><div class="metric-lbl">conflits matériels</div><span class="badge badge-r">physiques / directs</span></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{dept_top}</div><div class="metric-lbl">dépt. le plus conflictuel</div><span class="badge badge-r">en volume absolu</span></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="metric-card"><div class="metric-val" style="font-size:16px">{actor_top}</div><div class="metric-lbl">acteur le + négatif</div><span class="badge badge-o">en nb articles</span></div>', unsafe_allow_html=True)

st.divider()

# ── Graphiques Mensuels ───────────────────────────────────
st.subheader("Évolution mensuelle des conflits")

monthly = (
    df.groupby("month").agg(
        total=("IsConflict","count"),
        conflits=("IsConflict","sum"),
        conflit_materiel=("QuadLabel", lambda x: (x=="Conflit materiel").sum()),
        conflit_verbal=("QuadLabel", lambda x: (x=="Conflit verbal").sum()),
        goldstein=("GoldsteinScale","mean"),
    ).reset_index()
)
monthly["pct_conflit"] = (monthly["conflits"] / monthly["total"] * 100).round(1)
monthly["mois_label"] = monthly["month"].str[5:] + "/" + monthly["month"].str[2:4]

tab1, tab2, tab3 = st.tabs(["Nombre de conflits", "Part de conflits (%)", "Indice Goldstein"])

with tab1:
    fig = go.Figure()
    fig.add_bar(x=monthly["mois_label"], y=monthly["conflit_materiel"], name="Matériel", marker_color=COLORS["rouge"])
    fig.add_bar(x=monthly["mois_label"], y=monthly["conflit_verbal"],   name="Verbal",   marker_color=COLORS["orange"])
    fig.update_layout(barmode="stack", height=340, margin=dict(t=20,b=20,l=20,r=20),
                      legend=dict(orientation="h", y=1.05), plot_bgcolor="white", paper_bgcolor="white")
    fig.update_xaxes(gridcolor="#f0efe8"); fig.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.bar(monthly, x="mois_label", y="pct_conflit", color_discrete_sequence=[COLORS["rouge"]])
    fig2.update_layout(height=340, margin=dict(t=20,b=20,l=20,r=20), plot_bgcolor="white", paper_bgcolor="white",
                       xaxis_title="", yaxis_title="% conflits")
    fig2.update_xaxes(gridcolor="#f0efe8"); fig2.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = go.Figure()
    fig3.add_scatter(x=monthly["mois_label"], y=monthly["goldstein"].round(3),
                     mode="lines+markers", line=dict(color=COLORS["bleu"], width=2.5),
                     marker=dict(size=7, color=COLORS["bleu"]), fill="tozeroy",
                     fillcolor="rgba(55,138,221,0.08)")
    fig3.update_layout(height=340, margin=dict(t=20,b=20,l=20,r=20), plot_bgcolor="white", paper_bgcolor="white",
                       xaxis_title="", yaxis_title="Goldstein (+ = stabilisant)")
    fig3.update_xaxes(gridcolor="#f0efe8"); fig3.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Conflits par département ──────────────────────────────
st.subheader("Conflits par département")

dept = (
    df.groupby("DepartementBenin").agg(
        total=("IsConflict","count"),
        conflit_materiel=("QuadLabel", lambda x: (x=="Conflit materiel").sum()),
        conflit_verbal=("QuadLabel", lambda x: (x=="Conflit verbal").sum()),
        goldstein=("GoldsteinScale","mean"),
    ).reset_index()
)
dept["total_conflits"] = dept["conflit_materiel"] + dept["conflit_verbal"]
dept["pct_conflit"] = (dept["total_conflits"] / dept["total"] * 100).round(1)
dept = dept.sort_values("total_conflits")

fig4 = go.Figure()
fig4.add_bar(y=dept["DepartementBenin"], x=dept["conflit_materiel"], name="Matériel",
             orientation="h", marker_color=COLORS["rouge"])
fig4.add_bar(y=dept["DepartementBenin"], x=dept["conflit_verbal"],   name="Verbal",
             orientation="h", marker_color=COLORS["orange"])
fig4.update_layout(barmode="stack", height=420, margin=dict(t=20,b=20,l=20,r=20),
                   legend=dict(orientation="h", y=1.02), plot_bgcolor="white", paper_bgcolor="white")
fig4.update_xaxes(gridcolor="#f0efe8"); fig4.update_yaxes(gridcolor="#f0efe8")
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Acteurs négatifs ──────────────────────────────────────
st.subheader("Acteurs les plus associés à des articles négatifs")

actors = (
    df[df["Actor1Name"].isin(df["Actor1Name"].value_counts().head(12).index)]
    .groupby("Actor1Name").agg(
        total=("IsConflict","count"),
        negatifs=("IsNegative","sum"),
        tone=("AvgTone","mean"),
    ).reset_index()
    .sort_values("negatifs")
)

col_a, col_b = st.columns([2, 1])

with col_a:
    fig5 = px.bar(actors, y="Actor1Name", x="negatifs", orientation="h",
                  color_discrete_sequence=[COLORS["rouge"]],
                  labels={"negatifs": "Nb articles négatifs", "Actor1Name": ""})
    fig5.update_layout(height=420, margin=dict(t=20,b=20,l=20,r=20),
                       plot_bgcolor="white", paper_bgcolor="white")
    fig5.update_xaxes(gridcolor="#f0efe8"); fig5.update_yaxes(gridcolor="#f0efe8")
    st.plotly_chart(fig5, use_container_width=True)

with col_b:
    st.markdown("**Ton moyen par acteur** (+ = positif)")
    tone_df = actors.sort_values("tone")[["Actor1Name","tone"]].copy()
    tone_df["tone"] = tone_df["tone"].round(3)
    tone_df.columns = ["Acteur", "Ton moyen"]
    st.dataframe(tone_df, hide_index=True, use_container_width=True, height=420)

st.divider()
st.caption("Source : GDELT Project · GDELT Bénin 2025")
