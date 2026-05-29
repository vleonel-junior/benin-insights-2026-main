# 🇧🇯 Bénin Pulse — Plateforme de Décision Media Intelligence

> **Ce que le monde dit du Bénin correspond-il à ce qui s'y passe vraiment — et qu'est-ce que ça change pour moi ?**
>
> Bénin Pulse croise le regard international (GDELT + FMI) et la réalité locale (médias béninois) pour transformer la perception médiatique en outil de décision concret.

---

## Table des matières

1. [Vision & Positionnement](#1-vision--positionnement)
2. [Architecture du projet](#2-architecture-du-projet)
3. [Sources de données](#3-sources-de-données)
4. [Pipeline analytique](#4-pipeline-analytique)
5. [Modèles & Méthodes](#5-modèles--méthodes)
6. [Dashboard décisionnel](#6-dashboard-décisionnel)
7. [Installation & Lancement](#7-installation--lancement)
8. [Résultats clés](#8-résultats-clés)
9. [Stack technique](#9-stack-technique)
10. [Équipe](#10-équipe)

---

## 1. Vision & Positionnement

### La question centrale

Les médias internationaux construisent une image du Bénin fondée sur des signaux de crise, des agrégats régionaux et une couverture majoritairement négative. Les médias locaux béninois documentent quant à eux un pays en transformation économique active, avec des réformes concrètes sur l'investissement, la diaspora et l'industrie. **Ces deux lectures coexistent sans jamais être confrontées.**

Bénin Pulse est la première plateforme à combiner ces deux sources pour répondre à une question simple : **est-ce que ce que le monde dit du Bénin change ce que tu dois faire ?**

### Trois profils cibles, trois lectures différentes

| Profil | Question décisionnelle |
|---|---|
| **Investisseur étranger** | Le Bénin est-il stable et dans quel secteur s'engager par rapport à ses voisins ? |
| **Diaspora & Opérateur économique** | Comment créer, investir ou s'installer concrètement au Bénin aujourd'hui ? |
| **Afro-descendant** | Quelle est la réalité du Bénin débarrassée du prisme réducteur international ? |
| **Journaliste / Acteur Médias** | Sur quels angles d'enquête les médias béninois doivent-ils se focaliser pour déconstruire les stéréotypes ? |
| **Décideur Public / Gouvernement** | Les réformes sont-elles bien perçues et y a-t-il un fossé de communication à combler ? |

### Ce qui différencie Bénin Pulse

La combinaison de deux sources que personne ne croise aujourd'hui au même endroit :

- **GDELT + FMI** — le signal médiatique international et les données macroéconomiques comparatives
- **Médias locaux béninois** — 32 000+ articles extraits via WordPress API, RSS et scraping direct, enrichis par classification NLP zero-shot (XLM-RoBERTa)

Ce croisement produit de la **media intelligence appliquée à un pays**, transformée en outil d'orientation — pas en agrégateur d'information.

---

## 2. Architecture du projet

```
benin-pulse/
│
├── notebooks/
│   ├── 01_Data_extraction_GDELT.ipynb        # BigQuery → 7 tables GDELT + FMI
│   └── 02_Data_extraction_Medias_Locaux.ipynb # Scraping médias locaux + NLP zero-shot
│
├── data/
│   ├── raw/
│   │   ├── benin_events_clean.csv            # Événements GDELT (25 629 lignes)
│   │   ├── comparatif_regional.csv           # Bénin vs 6 pays voisins
│   │   ├── benin_eco_events.csv              # Coopérations économiques
│   │   ├── benin_bilateral.csv               # Relations bilatérales
│   │   ├── benin_media_bias.csv              # Biais médiatique local vs international
│   │   ├── benin_sector_themes.csv           # Radar sectoriel (GKG)
│   │   └── fmi_comparatif.csv                # Macro-économie FMI 2018–2026
│   └── processed/
│       ├── benin_pulse_donnees_propres.csv   # Articles locaux classifiés (NLP)
│       └── benin_raw_media.csv               # Articles bruts collectés (32 222 lignes)
│
├── dashboard/
│   ├── app.py                                # Application Streamlit multi-profils
│   ├── requirements.txt
│   └── data/                                 # Copies locales des CSV
│
└── README.md
```

---

## 3. Sources de données

Le projet mobilise **trois sources distinctes**, combinées pour la première fois dans un même outil décisionnel.

### 3.1 GDELT — Signal médiatique international (BigQuery)

Extraction via `gdelt-bq.gdeltv2` sur Google BigQuery, fenêtre glissante **12 mois (mai 2025 → mai 2026)**.

| Table produite | Contenu | Lignes |
|---|---|---|
| `benin_events_clean.csv` | Événements enrichis : acteurs, codes CAMEO, GoldsteinScale, AvgTone, géolocalisation, source_type | 25 629 |
| `comparatif_regional.csv` | Agrégats mensuels pour 7 pays : Bénin, Togo, Ghana, Nigeria, Niger, Burkina Faso, Cameroun | 91 |
| `benin_eco_events.csv` | Événements de coopération économique (EventRootCode 04–06, GoldsteinScale > 0) | 10 079 |
| `benin_bilateral.csv` | Relations bilatérales Bénin–9 partenaires, mois par mois | 104 |
| `benin_media_bias.csv` | Ton moyen et conflictualité par type de source (local / régional / international) sur périodes de crise annotées | 151 |
| `benin_sector_themes.csv` | Radar sectoriel par mois (parsing V2Themes du GKG) | 117 |

**Rigueur géographique — 4 niveaux de protection contre la contamination Nigeria :**
1. `ActionGeo_CountryCode != 'NI'`
2. Bounding box GPS : lat [6.10, 12.42] / lon [0.77, 3.85]
3. Liste noire de toponymes nigérians (`Benin City`, `Edo State`, `Warri`, etc.)
4. Contrôle Python post-extraction → 0 anomalie détectée sur les 25 629 événements

### 3.2 FMI — Données macroéconomiques comparatives

Extraction via l'API publique `imf.org/external/datamapper`, 6 indicateurs sur 2018–2026 pour 7 pays :

| Indicateur | Code FMI |
|---|---|
| Croissance réelle du PIB (%) | `NGDP_RPCH` |
| Inflation (%) | `PCPIPCH` |
| Dette publique / PIB (%) | `GGXWDG_NGDP` |
| Balance courante / PIB (%) | `BCA_NGDPD` |
| PIB par habitant (USD) | `NGDPDPC` |
| Taux de chômage (%) | `LUR` |

### 3.3 Médias locaux béninois — Signal de terrain

Collecte de **32 222 articles** (jan. 2025 → mai 2026) depuis 3 types de sources :

| Type | Sources | Articles |
|---|---|---|
| **WordPress API** | La Nouvelle Tribune, Le Matinal, Matin Libre, Ecobenin | ~32 000 |
| **RSS** | RFI Bénin, 24h au Bénin, Banouto, La Nation, gouv.bj, BCEAO | ~35 |
| **HTML direct** | gouv.bj/actualites/, investinbenin.com | variable |

**Classification NLP zero-shot** sur un échantillon représentatif de 2 000 articles via `joeddav/xlm-roberta-large-xnli` (GPU T4), avec une taxonomie de 20 thèmes métier :

```
diaspora_retour · création_entreprise · industrie_GDIZ · fiscalité_réglementation
opportunités_investissement · croissance_économique · sécurité_stabilité · tourisme
agriculture_agrobusiness · numérique_innovation · infrastructure_énergie · foncier_immobilier
gouvernance_institutionnelle · relations_internationales · vodun_culture_religieuse
vie_quotidienne · droits_libertés · santé_éducation · culture_identité · environnement_climat
```

---

## 4. Pipeline analytique

### Notebook 01 — Extraction GDELT + FMI

Exécuté sur **Google Colab** avec authentification Google Cloud.

```
Google BigQuery (gdelt-bq.gdeltv2)
    ├─ events_partitioned  ──▶  benin_events_clean.csv
    ├─ gkg_partitioned     ──▶  benin_sector_themes.csv
    ├─ events (agrégé)     ──▶  comparatif_regional.csv
    ├─ events (filtré)     ──▶  benin_eco_events.csv
    ├─ events (bilatéral)  ──▶  benin_bilateral.csv
    └─ events (biais)      ──▶  benin_media_bias.csv

API FMI (imf.org/datamapper)
    └─ 6 indicateurs × 7 pays  ──▶  fmi_comparatif.csv
```

**Périodes de crise annotées automatiquement** pour l'analyse du biais médiatique :

| Label | Période |
|---|---|
| `Attaque_Alibori_Avr2025` | 15–30 avr. 2025 |
| `CoupEtat_Dec2025` | 5–15 déc. 2025 |
| `Attaque_Kofouno_Mar2026` | 3–10 mars 2026 |
| `Election_Presidentielle` | 15–30 avr. 2026 |

### Notebook 02 — Extraction médias locaux + NLP

```
Sources WordPress / RSS / HTML
    └─ Collecte (requests + feedparser + BeautifulSoup)
            └─ benin_raw_media.csv (32 222 articles)
                    └─ Classification zero-shot (XLM-RoBERTa, T4 GPU)
                            └─ benin_pulse_donnees_propres.csv (2 000 articles classifiés)
```

---

## 5. Modèles & Méthodes

### Analyse du biais médiatique

Comparaison systématique du **ton moyen (AvgTone)** et du **GoldsteinScale** entre sources locales et internationales sur les périodes de crise annotées.

**Résultat observé sur le Coup d'État de décembre 2025 :**

| Source | Ton moyen | GoldsteinScale moyen |
|---|---|---|
| Local | +6.87 | +2.63 |
| Régional | -3.48 | -1.60 |
| International | -2.47 | +0.23 |

→ Écart de **+9.3 points de ton** entre médias locaux et internationaux sur le même événement.

### Classification NLP zero-shot

- **Modèle** : `joeddav/xlm-roberta-large-xnli` (robuste sur le français et les langues locales)
- **Approche** : multi-label, seuil de confiance à 0.50
- **Throughput** : batch_size=64, truncation à 128 tokens, GPU T4
- **Résultat** : 2 000 articles classifiés, thème dominant `gouvernance_institutionnelle` (18.3%), suivi de `relations_internationales` (14.4%) et `numérique_innovation` (6.5%)

### Analyse comparative GDELT / Médias locaux

| Indicateur | Presse internationale (GDELT) | Presse locale (Bénin) |
|---|---|---|
| Taux de conflictualité | 25.9% | 4.7% |
| Ton moyen | -1.50 | +4.05 |
| Couverture diaspora/investissement | < 1% | ~10% |

---

## 6. Dashboard décisionnel

Application **Streamlit** accessible en ligne et personnalisée par profil utilisateur.

**🌐 Démo publique :** [https://benin-observatoire.streamlit.app/](https://benin-observatoire.streamlit.app/)

### Navigation par profil

Le dashboard adapte entièrement son contenu, ses questions décisionnelles et ses visualisations selon le profil sélectionné :

#### 👔 Investisseur étranger
| Onglet | Contenu |
|---|---|
| Diagnostic Macroéconomique (FMI) | Comparatif PIB/inflation/dette 2018–2026 pour 7 pays ; classement régional 2026 |
| Risque Régional & Stabilité (GDELT) | Taux coopération vs conflit par pays ; diagnostic de sécurité médiatique |
| Secteurs Porteurs & Opportunités | Volume de mentions par secteur ; actualités d'investissement récentes |
| Partenaires & Confiance | Agences officielles partenaires (APIEx, CCIB) ; protocole d'audit indépendant |

#### 💼 Diaspora & Opérateur économique
| Onglet | Contenu |
|---|---|
| Entreprendre & S'installer | Articles classifiés sur la diaspora et la création d'entreprise, liens sources vérifiés |
| Fiscalité, Infrastructures & GDIZ | Réformes fiscales, zone industrielle Glo-Djigbé |
| Logistique & Douanes | Relations bilatérales par partenaire (qualité, volume, alertes) |
| Pulse Citoyen | Métriques d'expérience terrain (délai création entreprise, port, consulats) |

#### 🌍 Afro-descendant
| Onglet | Contenu |
|---|---|
| Vérité vs Récits Globaux | Confrontation chiffrée presse locale vs internationale sur conflictualité et ton |
| Culture, Tourisme & Vie Quotidienne | Articles culturels, sentiment sectoriel tourisme |
| Climat Sécuritaire Réel | Localisation précise des incidents ; note sécurité par région (population) |
| Vérification Terrain | Indice de sécurité ressentie par ville ; flux réseaux sociaux filtrés |

#### ✏️ Journaliste / Acteur Médias
| Onglet | Contenu |
|---|---|
| Diagnostic des Biais | Évolution hebdomadaire du ton par type de source (local / régional / international) |
| Angles Morts & Opportunités d'Articles | Comparaison couverture locale vs internationale par secteur ; sujets sous-couverts |
| Charte du Détail | Recommandations éditoriales pratiques pour contrer le cadrage réducteur |

#### 🏛️ Décideur Public / Gouvernement
| Onglet | Contenu |
|---|---|
| Suivi de l'Impact des Réformes | Satisfaction citoyenne vs ton médiatique par réforme |
| Détection d'Angles Morts Stratégiques | Écarts de perception critiques nuisant à la réputation internationale |
| Baromètre de Perception Citoyenne | Confiance dans l'action gouvernementale ; top préoccupations citoyennes |

---

## 7. Installation & Lancement

### Prérequis

- Python 3.9+
- Compte Google Cloud avec accès BigQuery (notebook 01 uniquement)
- GPU recommandé pour la classification NLP (notebook 02) — testé sur T4 via Google Colab

### Installation

```bash
git clone https://github.com/<votre-org>/benin-pulse.git
cd benin-pulse
pip install -r requirements.txt
```

**Dépendances supplémentaires pour le notebook 02 :**
```bash
pip install transformers torch feedparser beautifulsoup4 tqdm lxml
```

### Récupération des données

Les CSV issus de BigQuery ne sont pas versionnés. Deux options :

**Option A — Régénérer depuis BigQuery**
```
1. Ouvrir notebooks/01_Data_extraction_GDELT.ipynb sur Google Colab
2. Authentifier avec un compte Google Cloud (projet : hackathon-benin-insight)
3. Exécuter toutes les cellules → CSV sauvegardés sur Google Drive
```

**Option B — Depuis le Drive partagé**
```
https://drive.google.com/drive/folders/1GxSqPlL_Wxs1RJRO4R2zAEsficxM8MXU
```

### Ordre d'exécution

```
01_Data_extraction_GDELT.ipynb          ← Colab (BigQuery + FMI)
        ↓
02_Data_extraction_Medias_Locaux.ipynb  ← Colab GPU (scraping + NLP)
        ↓
dashboard/app.py                        ← Streamlit local ou cloud
```

### Lancer le dashboard

```bash
cd dashboard
streamlit run app.py
```

Accessible à `http://localhost:8501`.

---

## 8. Résultats clés

### Le biais médiatique international est mesurable et quantifié

- **Presse internationale** : 25.9% de conflictualité, ton moyen -1.50
- **Presse locale** : 4.7% de conflictualité, ton moyen +4.05
- Sur le Coup d'État de décembre 2025 : écart de **+9.3 points de ton** entre sources locales et internationales
- Les médias locaux consacrent ~10% de leur couverture à la diaspora et à l'investissement, contre < 1% pour les sources internationales

### Le Bénin performe significativement mieux que sa couverture médiatique ne le laisse entendre

- **Croissance du PIB 2026 : +7.0%** — 1ère d'Afrique de l'Ouest (source FMI)
- **Inflation 2026 : 2.0%** — maîtrisée, bien en dessous du Nigeria (+16%) et du Ghana (+22.9% en 2024)
- **Dette/PIB : 57.2%** — profil sain (< 60%), en amélioration depuis le pic de 2023
- **GoldsteinScale moyen : +0.60** — positif malgré une distribution bimodale révélatrice

### La menace sécuritaire est géographiquement circonscrite

- 74.4% des événements GDELT impliquant le Bénin sont coopératifs
- Les incidents sécuritaires se concentrent sur les zones frontalières nord (Alibori, Karimama) — éloignées des pôles économiques
- Note de sécurité ressentie : 4.7–4.8/5 à Cotonou et Ouidah ; 2.3/5 à la frontière nord

### La presse locale documente une transformation économique réelle

Top thèmes identifiés par NLP dans les médias béninois :
1. `gouvernance_institutionnelle` (18.3%)
2. `relations_internationales` (14.4%)
3. `numérique_innovation` (6.5%) — quasi-absent de la presse internationale
4. `diaspora_retour` (5.5%) — totalement ignoré à l'étranger
5. `industrie_GDIZ` (3.0%) — 18 unités opérationnelles, +25 000 emplois

---

## 9. Stack technique

| Catégorie | Technologies |
|---|---|
| **Extraction GDELT** | Google BigQuery, `google-cloud-bigquery`, Google Colab |
| **Extraction médias locaux** | `requests`, `feedparser`, `beautifulsoup4`, `lxml` |
| **Extraction FMI** | API REST `imf.org/external/datamapper` |
| **Manipulation** | `pandas >= 2.0`, `numpy >= 1.24` |
| **NLP / Classification** | `transformers` (XLM-RoBERTa), `torch`, GPU T4 |
| **Visualisation** | `plotly >= 5.15` |
| **Dashboard** | `streamlit >= 1.28` |
| **Environnement** | Python 3.9+, Google Colab (notebooks), local (dashboard) |

---

## 10. Équipe

Projet réalisé dans le cadre du **Hackathon Bénin Insights 2026**.

| Nom | Rôle |
|---|---|
| **Léonel Junior VODOUNOU** | ML Engineer |
| **Fidèle TCHANDO** | ML Engineer |
| **Ibrahima KONE** | Data Engineer |
| **Georges AYENI** | Data Analyst |

---

## Licence & Contact

Données source : [The GDELT Project](https://www.gdeltproject.org/) · [FMI DataMapper](https://www.imf.org/external/datamapper/) · Médias béninois (open web)

---

*Dernière mise à jour : mai 2026*