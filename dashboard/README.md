# 🇧🇯 Bénin Pulse - Média Intelligence & Aide à la Décision

**Bénin Pulse** est une plateforme décisionnelle interactive développée sous Streamlit. Elle croise le regard des médias internationaux (GDELT, GKG, FMI) avec la réalité locale béninoise (presse locale RSS, retours d'expériences citoyens et de la diaspora) afin d'aider différents profils d'acteurs à prendre des décisions éclairées.

---

## 🎯 Objectifs et Publics Cibles
* **Investisseurs Étrangers** : Valider la stabilité macroéconomique, mesurer le risque géopolitique et identifier les opportunités.
* **Diaspora & Opérateurs Économiques** : Obtenir des informations pratiques sur les incitations, les réformes (GDIZ, APIEx) et la logistique.
* **Afro-descendants** : Accéder à une lecture objective et factuelle du climat sécuritaire et socioculturel.
* **Journalistes & Acteurs Médias** : Identifier les biais médiatiques internationaux pour enrichir la couverture locale.
* **Décideurs Publics & Gouvernement** : Suivre le baromètre de confiance et l'impact perçu des réformes.

---

## 💾 Données & Modèle
Le dashboard s'appuie sur une base de données de **150 000 enregistrements réels** compilés (GDELT Events, GKG, presse locale béninoise) et enrichis de retours citoyens contextualisés :
* `social_feed.json` (48 Mo) : Base principale au format JSON utilisée pour le Social Listening.
* `large_social_feed.csv` : Version alternative en CSV (fallback automatique).

---

## 🛠️ Installation et Configuration

Pour exécuter le projet localement après avoir recréé votre environnement virtuel, suivez ces instructions.

### 1. Recréer l'environnement virtuel (`venv`)

#### Méthode rapide avec `uv` (recommandée) :
```bash
# Crée le venv
uv venv .venv

# Active le venv
source .venv/bin/activate

# Installe les dépendances
uv pip install -r requirements.txt
```

#### Méthode standard avec `pip` :
```bash
# Crée le venv
python3 -m venv .venv

# Active le venv
source .venv/bin/activate

# Installe les dépendances
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### Lancer le Dashboard Streamlit :
```bash
streamlit run app.py
```
Le serveur démarrera par défaut sur [http://localhost:8501](http://localhost:8501).

### Régénérer ou actualiser la base de données (150 000 lignes) :
```bash
python generate_large_feed.py
```
Ce script relira les exports GDELT et la presse locale pour reconstruire les fichiers `large_social_feed.csv` et `social_feed.json`.

---

## 📁 Structure des Fichiers Clés
* `app.py` : Code source principal du dashboard Streamlit (glassmorphic dark theme).
* `generate_large_feed.py` : Script ETL de compilation des 150 000 lignes.
* `requirement.py` : Script Python interactif de vérification des dépendances.
* `requirements.txt` : Liste des dépendances pip du projet.
