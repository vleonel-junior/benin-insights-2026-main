# 🇧🇯 Observatoire Médiatique — République du Bénin

Dashboard interactif d'analyse des données GDELT sur le Bénin (2025).

## Structure

```
dashboard/
├── app.py                  ← Application Streamlit principale
├── requirements.txt        ← Dépendances Python
└── data/
    └── gdelt_replubique_benin_clean_.csv
```

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Cloud (gratuit, URL publique)

1. Créer un compte sur [share.streamlit.io](https://share.streamlit.io)
2. Pusher ce dossier sur un repo GitHub public
3. Sur Streamlit Cloud → **New app** → sélectionner le repo → `app.py`
4. Cliquer **Deploy** → URL publique générée en ~2 minutes

## Fonctionnalités

- **Filtres sidebar** : période, département, type d'événement, source
- **5 KPIs** : total événements, taux conflit, Goldstein, ton médiatique, émotion dominante
- **Timeline** : évolution mensuelle par type + courbe Goldstein/Ton
- **Carte interactive** : scatter mapbox des événements géolocalisés
- **Géographie** : classement des 12 départements par intensité/conflit
- **Thèmes** : répartition des 5 grandes thématiques GKG
- **Émotions** : donut GCAM + radar profil émotionnel moyen
- **Acteurs** : top 12 acteurs colorés par stabilité Goldstein
- **Sources** : top 12 médias par type
- **Tableau brut** : 100 derniers événements filtrés

## Stack technique

| Outil | Rôle |
|-------|------|
| Streamlit | Framework UI |
| Pandas | Manipulation données |
| Plotly Express | Charts interactifs |
| Plotly Go | Radar & cartes avancées |
