import streamlit as st
from utils import load_data, COLORS

st.set_page_config(
    page_title="GDELT Bénin 2025",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #f8f7f4; }
.metric-card {
    background: #f1efe8;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.metric-val { font-size: 28px; font-weight: 600; color: #2c2c2a; line-height: 1.1; }
.metric-lbl { font-size: 13px; color: #5f5e5a; margin-top: 4px; }
.badge {
    display: inline-block;
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 20px;
    margin-top: 6px;
    font-weight: 500;
}
.badge-r { background: #fcebeb; color: #a32d2d; }
.badge-o { background: #faeeda; color: #854f0b; }
.badge-g { background: #eaf3de; color: #3b6d11; }
.badge-b { background: #e6f1fb; color: #185fa5; }
h1, h2, h3 { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/320px-Flag_of_Benin.svg.png", width=80)
    st.title("GDELT · Bénin 2025")
    st.caption("Analyse de 8 000 événements issus de la base GDELT sur 12 mois.")
    st.divider()
    st.markdown("**Navigation**")
    st.page_link("app.py",                      label="Accueil",      icon="🏠")
    st.page_link("pages/1_journaliste.py",       label="Journaliste",  icon="📰")
    st.page_link("pages/2_chercheur.py",         label="Chercheur",    icon="🔬")
    st.page_link("pages/3_decideur.py",          label="Décideur",     icon="🗺️")
    st.divider()
    st.caption("Source : GDELT Project · Jan–Déc 2025")

# ── Accueil ───────────────────────────────────────────────
st.title("🇧🇯 GDELT Bénin — Tableau de bord national")
st.markdown("Transformez des données mondiales en connaissance locale. Choisissez votre profil pour accéder aux insights qui vous correspondent.")

st.divider()

# KPIs globaux
df = load_data()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">8 000</div>
        <div class="metric-lbl">événements analysés</div>
        <span class="badge badge-b">Jan – Déc 2025</span>
    </div>""", unsafe_allow_html=True)

with col2:
    n_conflits = int(df["IsConflict"].sum())
    pct = round(n_conflits / len(df) * 100, 1)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{n_conflits:,}</div>
        <div class="metric-lbl">événements conflictuels</div>
        <span class="badge badge-o">{pct}% du total</span>
    </div>""", unsafe_allow_html=True)

with col3:
    n_src = df["SourceType"].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{n_src}</div>
        <div class="metric-lbl">types de sources</div>
        <span class="badge badge-g">presse, TV, officiel…</span>
    </div>""", unsafe_allow_html=True)

with col4:
    n_dept = df["DepartementBenin"].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-val">{n_dept}</div>
        <div class="metric-lbl">départements couverts</div>
        <span class="badge badge-b">couverture nationale</span>
    </div>""", unsafe_allow_html=True)

st.divider()

# Cartes profils
st.subheader("Choisissez votre profil")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 📰 Journaliste")
    st.markdown("""
Explorez la **cartographie des conflits** par département, l'évolution mensuelle des tensions
et les acteurs qui génèrent le plus d'articles négatifs.
    """)
    st.page_link("pages/1_journaliste.py", label="Accéder → Vue Journaliste", use_container_width=True)

with c2:
    st.markdown("### 🔬 Chercheur")
    st.markdown("""
Analysez la **couverture par type de source**, les biais émotionnels selon les thèmes
et la corrélation entre Goldstein et ton médiatique.
    """)
    st.page_link("pages/2_chercheur.py", label="Accéder → Vue Chercheur", use_container_width=True)

with c3:
    st.markdown("### 🗺️ Décideur public")
    st.markdown("""
Identifiez les **zones géographiques à risque**, les thèmes sectoriels les plus volatils
et l'évolution des tensions Nord / Centre / Sud.
    """)
    st.page_link("pages/3_decideur.py", label="Accéder → Vue Décideur", use_container_width=True)

st.divider()
st.caption("Données : GDELT Project (Global Database of Events, Language, and Tone) · Hackathon GDELT Bénin 2025")
