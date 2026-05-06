# 🇧🇯 Bénin Insights 2026 — Observatoire Médiatique GDELT

> Analyse des événements médiatiques au Bénin sur l'année 2025 à partir des données GDELT, avec modélisation ML, détection de ruptures et prédiction prospective du risque socio-politique.

---

## Table des matières

1. [Contexte & Objectif](#1-contexte--objectif)
2. [Architecture du projet](#2-architecture-du-projet)
3. [Sources de données](#3-sources-de-données)
4. [Pipeline analytique](#4-pipeline-analytique)
5. [Modèles & Méthodes](#5-modèles--méthodes)
6. [Dashboard interactif](#6-dashboard-interactif)
7. [Installation & Lancement](#7-installation--lancement)
8. [Résultats clés](#8-résultats-clés)
9. [Stack technique](#9-stack-technique)
10. [Équipe](#équipe)

---

## 1. Contexte & Objectif

Ce projet a été développé dans le cadre du **Hackathon Bénin Insights**. Il vise à analyser la couverture médiatique internationale du Bénin en 2025 à travers la base de données [GDELT](https://www.gdeltproject.org/), qui indexe en temps réel les événements extraits de la presse mondiale.

**Question centrale :** Le Bénin, souvent présenté comme un « îlot de stabilité » en Afrique de l'Ouest, confirme-t-il ce statut dans sa couverture médiatique, et quels signaux précoces permettent d'anticiper des épisodes d'instabilité ?

**Trois angles d'analyse :**

- **Descriptif** — Cartographier les événements sur l'année 2025 (volume, tonalité, type, géographie)
- **Comparatif** — Positionner le Bénin par rapport à ses voisins (Nigeria, Niger, Burkina Faso, Mali, Togo, Ghana, Sénégal)
- **Prédictif** — Construire un indice de risque composite (IRC) et projeter son évolution à 4 et 12 semaines via Prophet

---

## 2. Architecture du projet

```
benin-insights-2026/
│
├── notebooks/
│   ├── 01_Data_extraction_GDELT.ipynb   # Extraction BigQuery → Google Drive
│   ├── 02_EDA.ipynb                     # Analyse exploratoire multi-niveaux
│   ├── 03_ML_models.ipynb               # Clustering, classification, ruptures
│   └── 04_Prediction_Prospective_Benin.ipynb  # IRC, Prophet, Early Warning
│
├── data/
│   ├── raw/
│   │   └── eventsBenin.parquet          # Données brutes (Parquet)
│   └── processed/
│       └── gdelt_republique_benin_clean.csv   # Dataset principal nettoyé
│
├── models/
│   ├── models_bundle.pkl        # Scaler, PCA, K-Means, DBSCAN, PELT, RF, XGBoost
│   └── models_prospectifs.pkl   # Prophet + IRC (modèles prospectifs)
│
├── dashboard/
│   ├── app.py                   # Application Streamlit
│   ├── requirements.txt
│   └── data/
│       └── gdelt_replubique_benin_clean_.csv  # Copie locale pour le dashboard
│
├── requirements.txt
└── README.md
```

---

## 3. Sources de données

Le projet mobilise **deux sources GDELT distinctes**, avec des périmètres et des usages différents.

### 3.1 Source BigQuery — Extraction via Google Colab (`01_Data_extraction_GDELT.ipynb`)

Accès à l'API publique `gdelt-bq.gdeltv2` sur Google BigQuery, couvrant la **période du 1er janvier au 31 décembre 2025**. Trois tables sont extraites et sauvegardées sur Google Drive :
👉 [Accéder au Drive](https://drive.google.com/drive/folders/1GxSqPlL_Wxs1RJRO4R2zAEsficxM8MXU?usp=sharing)

| Fichier CSV | Table BigQuery source | Contenu |
|---|---|---|
| `benin_events_clean.csv` | `gdeltv2.events_partitioned` | Événements bruts enrichis : acteurs, codes CAMEO, GoldsteinScale, AvgTone, géolocalisation |
| `benin_gkg.csv` | `gdeltv2.gkg_partitioned` | Métadonnées sémantiques par article : V2Themes, V2Locations, V2Persons, V2Organizations, V2Tone |
| `comparatif_regional_1.csv` | `gdeltv2.events_partitioned` | Agrégats mensuels pour 8 pays (Bénin + 7 voisins) : nb événements, Goldstein moyen, % conflits, % coopération |

**Filtres appliqués :**
- Exclusion explicite de « Benin City » (Nigeria) — fréquente source de pollution dans les requêtes Bénin
- Filtre combiné : `Actor1CountryCode = 'BEN'` **OU** `Actor2CountryCode = 'BEN'` **OU** `ActionGeo_CountryCode = 'BN'`
- Table GKG : filtre `V2Locations LIKE '%#BN#%'`
- Table GKG : suppression de la colonne `GCAM` (trop volumineuse → plusieurs TB/an) au profit de `V2Tone`

**Ces deux fichiers CSV (`benin_events_clean.csv` et `benin_gkg.csv`) sont utilisés dans le notebook `02_EDA.ipynb` mais ne sont pas versionnés dans ce dépôt.** Ils doivent être récupérés depuis le Drive ou regénérés via le notebook 01.

---

### 3.2 Source GDELT Project direct — Données intérieures (`data/processed/`)

Un second dataset a été extrait directement depuis [gdeltproject.org](https://www.gdeltproject.org/), avec un focus plus granulaire sur les **territoires intérieurs du Bénin** (niveau département/commune). C'est ce dataset qui constitue la base principale des analyses ML, de la prédiction et du dashboard.

| Fichier | Emplacement | Usage |
|---|---|---|
| `gdelt_republique_benin_clean.csv` | `data/processed/` | Notebook 02 (EDA partielle), 03 (ML), 04 (Prédiction), Dashboard |
| `gdelt_replubique_benin_clean_.csv` | `dashboard/data/` | Copie utilisée par le dashboard Streamlit |

> **Note orthographique :** Le nom de fichier contient une légère coquille (`replubique` au lieu de `republique`) — cohérence à maintenir avec le code existant.

---

## 4. Pipeline analytique

### Notebook 01 — Extraction (`01_Data_extraction_GDELT.ipynb`)

Exécuté sur **Google Colab** avec authentification Google Cloud.

```
Google BigQuery (gdelt-bq.gdeltv2)
    ├─ events_partitioned  ──▶  benin_events_clean.csv
    ├─ gkg_partitioned     ──▶  benin_gkg.csv
    └─ events (agrégé)     ──▶  comparatif_regional_1.csv
                                        │
                               Google Drive + local /content/
```

Pré-traitement appliqué à la sortie :
- Suppression des doublons (756 lignes, soit 2,40 %)
- Suppression des lignes sans géolocalisation `ActionGeo_FullName` (37 lignes, 0,12 %)
- **Résultat final : 30 711 événements propres**

---

### Notebook 02 — EDA (`02_EDA.ipynb`)

Analyse exploratoire structurée en **4 niveaux progressifs**, mobilisant les deux sources de données :

| Niveau | Contenu |
|---|---|
| **Niveau 1** | Dimensions, types, valeurs manquantes, doublons, plage temporelle |
| **Niveau 2** | Distributions des variables clés (GoldsteinScale, AvgTone, QuadClass, volume mensuel) |
| **Niveau 3** | Évolution temporelle : courbes mensuelles, volatilité du ton, détection des anomalies (creux juin, pic décembre) |
| **Niveau 4** | Comparaison régionale — Bénin vs 7 pays voisins sur les indicateurs de conflictualité |

**Insights structurants issus de l'EDA :**
- Distribution bimodale du GoldsteinScale → polarisation réelle de la couverture
- 25,5 % des événements sont conflictuels (QuadClass 3 ou 4) — 1 événement sur 4
- Ton médiatique moyen légèrement négatif (-1,39) mais sans dramatisation
- Deux anomalies temporelles majeures : creux en juin, pic en décembre 2025

---

### Notebook 03 — Modélisation ML (`03_ML_models.ipynb`)

**Dataset :** `gdelt_republique_benin_clean.csv`

**Features utilisées :**
```
GoldsteinNorm | ToneNorm | NumMentions | NumArticles | MediaWeight | IsNorthBenin
```

Trois familles de modèles entraînés :

| Modèle | Type | Objectif |
|---|---|---|
| **PCA** | Réduction de dimension | Visualisation 2D des événements |
| **K-Means** (k optimal via silhouette) | Clustering non-supervisé | Segmentation des profils d'événements |
| **DBSCAN** | Clustering par densité | Détection d'outliers et clusters non-convexes |
| **PELT** (`ruptures`) | Détection de ruptures | Points de bascule dans les séries temporelles |
| **Random Forest** | Classification supervisée | Prédiction `IsConflict` (binaire) |
| **XGBoost** | Classification supervisée | Prédiction `IsConflict` avec importances de variables |

L'ensemble des modèles et artefacts est sérialisé dans `models/models_bundle.pkl`.

---

### Notebook 04 — Prédiction prospective (`04_Prediction_Prospective_Benin.ipynb`)

**Dataset :** `gdelt_models_data.csv` (enrichi par le notebook 03 avec `proba_conflict`)

#### Indice de Risque Composite (IRC)

Score hebdomadaire sur une échelle 0–100 construit à partir de 5 composantes :

| Composante | Poids | Description |
|---|---|---|
| C1 — Conflictualité brute | 30 % | Taux d'événements conflictuels (`IsConflict`) |
| C2 — Probabilité ML | 30 % | Score XGBoost moyen sur la semaine |
| C3 — Goldstein inversé | 20 % | Score Goldstein négativisé (instabilité) |
| C4 — Ton négatif | 10 % | AvgTone inversé |
| C5 — Volume médiatique | 10 % | Nombre d'articles |

**Niveaux de risque :** FAIBLE (0–30) · MODÉRÉ (30–50) · ÉLEVÉ (50–70) · CRITIQUE (70–100)

#### Prévision avec Prophet

- Modèle Meta Prophet entraîné sur les séries hebdomadaires de l'IRC
- Horizon de prédiction : **4 semaines** et **12 semaines**
- Intervalle de confiance à 80 %
- Intégration d'événements politiques béninois (élections) comme régresseurs externes
- Résultats sauvegardés dans `models/models_prospectifs.pkl`

#### Explicabilité (SHAP)

Analyse des contributions de chaque variable à la prédiction de risque individuelle.

---

## 5. Modèles & Méthodes

### Résumé des fichiers modèles

| Fichier | Contenu |
|---|---|
| `models/models_bundle.pkl` | `scaler`, `kmeans`, `pca`, `dbscan`, `perl` (PELT), `rf`, `xgboost`, `feat`, `best_k`, `sil_scores`, `report`, `profile` |
| `models/models_prospectifs.pkl` | Modèle Prophet + artefacts IRC |

### Charger les modèles en Python

```python
import pickle

with open('models/models_bundle.pkl', 'rb') as f:
    bundle = pickle.load(f)

model_rf      = bundle['rf']
model_xgboost = bundle['xgboost']
scaler        = bundle['scaler']
features      = bundle['feat']
kmeans        = bundle['kmeans']
```

---

## 6. Dashboard interactif

Application **Streamlit** localisée dans `dashboard/app.py`.

**Filtres sidebar :**
- Période (slider sur les mois disponibles)
- Département(s)
- Type d'événement (QuadLabel)
- Type de source médiatique

**Sections du dashboard :**

| Section | Contenu |
|---|---|
| **KPIs** | Total événements · Taux de conflit · Goldstein moyen · Ton médiatique · Émotion dominante GCAM |
| **📅 Évolution temporelle** | Volume mensuel par type d'événement (stacked bar) + indicateurs de tendance |
| **🗺️ Géographie** | Carte des événements par département béninois |
| **🎯 Thèmes & Émotions** | Analyse V2Themes et émotions GCAM (Trust, Joy, Anger, Fear, Sadness, Surprise) |
| **🏛️ Acteurs & Sources** | Classement des acteurs, pays, types de sources médiatiques |
| **🔍 Données brutes** | Tableau filtrable des événements |
| **🤖 Analyse prédictive** | 4 onglets : Détection de ruptures · Prédiction de conflit · Clustering départements · (IRC prospectif) |

---

## 7. Installation & Lancement

### Prérequis

- Python 3.9+
- Compte Google Cloud avec accès BigQuery (pour notebook 01 uniquement)
- Google Colab recommandé pour les notebooks 01 et 02 (accès Drive)

### Installation des dépendances

```bash
git clone https://github.com/<votre-org>/benin-insights-2026.git
cd benin-insights-2026
pip install -r requirements.txt
```

**Dépendances supplémentaires pour le notebook 04 :**
```bash
pip install prophet shap plotly ruptures
```

### Récupération des données

Les fichiers CSV extraits via BigQuery ne sont pas versionnés (voir `.gitignore`). Deux options :

**Option A — Régénérer depuis BigQuery**
```
1. Ouvrir notebooks/01_Data_extraction_GDELT.ipynb sur Google Colab
2. Authentifier avec un compte Google Cloud (projet : hackathon-benin-insight)
3. Exécuter toutes les cellules → les CSV sont sauvegardés sur Google Drive
4. Télécharger benin_events_clean.csv et benin_gkg.csv dans data/raw/
```

**Option B — Depuis le Drive partagé**
```
https://drive.google.com/drive/folders/1GxSqPlL_Wxs1RJRO4R2zAEsficxM8MXU
→ Télécharger benin_events_clean.csv et comparatif_regional_1.csv dans data/raw/
```

> Le fichier `gdelt_republique_benin_clean.csv` (source directe GDELT) est déjà inclus dans `data/processed/`.

### Lancer le dashboard

**🌐 Version en ligne (démo publique) :**
👉 [https://benin-observatoire.streamlit.app/](https://benin-observatoire.streamlit.app/)

**En local :**
```bash
cd dashboard
streamlit run app.py
```

Le dashboard sera accessible à `http://localhost:8501`.

### Ordre d'exécution des notebooks

```
01_Data_extraction_GDELT.ipynb   ← Colab uniquement (BigQuery + Drive)
        ↓
02_EDA.ipynb                     ← Colab ou local (nécessite les CSV du Drive)
        ↓
03_ML_models.ipynb               ← Local (gdelt_republique_benin_clean.csv)
        ↓
04_Prediction_Prospective_Benin.ipynb  ← Local (sortie du notebook 03)
```

---

## 8. Résultats clés

### Profil médiatique du Bénin en 2025

- **~30 700 événements** indexés par GDELT impliquant le Bénin (source BigQuery)
- **~8 000 événements** dans le dataset intérieur granulaire (source GDELT direct)
- **64,4 %** des événements sont des déclarations verbales (QuadClass 1) — dominance diplomatique
- **25,5 %** des événements sont conflictuels (QuadClass 3+4) — 1 sur 4, signal fort
- **GoldsteinScale moyen : +0,68** — légèrement positif, mais masquant une distribution bimodale
- **AvgTone moyen : -1,37** — registre légèrement pessimiste dans la presse internationale

### Anomalies temporelles confirmées

| Mois | Signal | Interprétation |
|---|---|---|
| Juin 2025 | Creux (~1 100 événements) | Baisse anormale de la couverture médiatique |
| Décembre 2025 | Pic (~5 700 événements) | Événement(s) majeur(s) à investiguer |

### Segmentation des événements (K-Means)

Deux clusters principaux identifiés par PCA + K-Means :
- **Cluster coopération** : ton positif, Goldstein élevé, acteurs institutionnels
- **Cluster conflit** : ton négatif, Goldstein bas, forte concentration dans le nord du Bénin (`IsNorthBenin = 1`)

### Prédiction de conflit (XGBoost)

Variables les plus discriminantes (importances) :
1. `GoldsteinNorm` — principale variable de stabilité
2. `ToneNorm` — signal sémantique complémentaire
3. `IsNorthBenin` — dimension géographique significative
4. `MediaWeight` — intensité de la couverture comme amplificateur

---

## 9. Stack technique

| Catégorie | Technologies |
|---|---|
| **Extraction** | Google BigQuery, Google Colab, `google-cloud-bigquery` |
| **Manipulation** | `pandas >= 2.0`, `numpy >= 1.24`, `pyarrow >= 13.0` |
| **Visualisation** | `matplotlib >= 3.7`, `seaborn >= 0.12`, `plotly >= 5.15` |
| **Machine Learning** | `scikit-learn >= 1.3`, `xgboost`, `prophet` |
| **Séries temporelles** | `ruptures >= 1.1.9` (PELT), `prophet` (Meta) |
| **Explicabilité** | `shap` |
| **Dashboard** | `streamlit >= 1.28` |
| **Environnement** | Python 3.9+, Google Colab (notebooks 01–02), local (notebooks 03–04 + dashboard) |

---

## Équipe

Projet réalisé dans le cadre du **Hackathon Bénin Insights 2026**.

| Nom | Rôle |
|---|---|
| **Léonel Junior VODOUNOU** | Data Scientist |
| **Fidèle TCHANDO** | ML Engineer |
| **Ibrahima KONE** | Data Engineer |
| **Georges AYENI** | Data Analyst |

---

## Licence & Contact

Données source : [The GDELT Project](https://www.gdeltproject.org/) — licence ouverte (Open Data).

---

*Dernière mise à jour : mai 2026*
