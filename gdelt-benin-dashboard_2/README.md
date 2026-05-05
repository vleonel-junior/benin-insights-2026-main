# GDELT Bénin 2025 — Tableau de bord national

Application Streamlit multi-profils pour l'analyse des données GDELT sur le Bénin (jan–déc 2025).

## Structure

```
gdelt-benin-dashboard/
├── app.py                    # Accueil + navigation
├── utils.py                  # Chargement & cache des données
├── data/
│   └── gdelt_benin_clean.csv # Dataset GDELT filtré Bénin
├── pages/
│   ├── 1_journaliste.py      # Conflits, acteurs, tensions
│   ├── 2_chercheur.py        # Sources, émotions, corrélations
│   └── 3_decideur.py         # Risques, zones, thèmes
└── requirements.txt
```

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Cloud

1. Pousser ce dépôt sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repo → sélectionner `app.py`
4. Deploy — URL publique en 2 minutes

## Source des données

[GDELT Project](https://www.gdeltproject.org/) — Global Database of Events, Language, and Tone.
Période : Janvier–Décembre 2025 · 8 000 événements · Bénin.
