"""
Benin Pulse - Collecte + Analyse medias locaux beninois
Produit : benin_local_media.csv
Sources : API WordPress + Google News RSS
Analyse : Google Gemini (google-genai)
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
import feedparser
from google import genai

# -----------------------------------------
# METTEZ VOTRE CLE ICI - ne la partagez jamais
# -----------------------------------------
API_KEY = "AQ.Ab8RN6JiEqU_TK0NQYiXx532jk4NJCZHkrlaANaqZgTpqSX7WA"


# -----------------------------------------
# 1. CONFIGURATION
# -----------------------------------------
client = genai.Client(api_key=API_KEY)
DATE_DEBUT = "2025-01-01"
DATE_FIN   = "2026-05-31"

# Sources WordPress (API directe)
SOURCES_WP = [
    {"nom": "La Nouvelle Tribune", "url": "https://lanouvelletribune.info"},
    {"nom": "Matin Libre",         "url": "https://matinlibre.com"},
    {"nom": "Benin Intelligent",   "url": "https://beninpresse.com"},
    {"nom": "24 Heures au Benin",  "url": "https://www.24haubenin.info"},
    {"nom": "Le Matinal",          "url": "https://lematinal.bj"},
    {"nom": "Dadje Infos",         "url": "https://dadje.info"},
]

# Sources Google News RSS
SOURCES_GNEWS = [
    {"nom": "Banouto",          "query": "Benin site:banouto.bj"},
    {"nom": "Agence Benin Presse", "query": "Benin site:abp.bj"},
    {"nom": "La Nation Benin",  "query": "Benin site:lanationbenin.info"},
    {"nom": "Fraternite",       "query": "Benin site:fraternite.bj"},
    {"nom": "aCotonou",         "query": "investissement diaspora economie Benin site:acotonou.com"},
    {"nom": "Benin.info",       "query": "investissement diaspora economie Benin site:benin.info"},
    {"nom": "gouv.bj",          "query": "Benin site:gouv.bj"},
    {"nom": "APIEX",            "query": "investissement GDIZ Benin site:apiex.bj"},
]

# Mots-cles pour filtrer les articles hors-sujet (WordPress uniquement)
MOTS_BENIN = [
    "benin", "cotonou", "beninois", "beninoise",
    "abomey", "parakou", "ouidah", "porto-novo", "natitingou",
    "talon", "wadagni", "gdiz", "apiex"
]

# -----------------------------------------
# 2. FILTRE BENIN (pour WordPress)
# -----------------------------------------
def concerne_benin(titre, resume):
    texte = (titre + " " + resume).lower()
    return any(mot in texte for mot in MOTS_BENIN)

# -----------------------------------------
# 3. ANALYSE PAR GEMINI
# -----------------------------------------
def analyser_avec_gemini(titre, resume):
    prompt = (
        "Tu es un analyste specialise sur le Benin.\n\n"
        "Voici un article de presse beninoise :\n"
        f"Titre : {titre}\n"
        f"Resume : {resume}\n\n"
        "Classe cet article en choisissant UN SEUL theme parmi :\n"
        "diaspora_retour, vie_quotidienne, droits_libertes, sante_education, culture_identite,\n"
        "opportunites_investissement, croissance_economique, gouvernance_institutionnelle,\n"
        "fiscalite_reglementation, relations_internationales,\n"
        "creation_entreprise, foncier_immobilier, agriculture_agrobusiness,\n"
        "industrie_GDIZ, numerique_innovation,\n"
        "infrastructure_energie, securite_stabilite, tourisme,\n"
        "vodun_culture_religieuse, environnement_climat, general\n\n"
        "Reponds UNIQUEMENT en JSON :\n"
        "{\n"
        '  "theme": "theme choisi",\n'
        '  "sentiment": "positif, negatif ou neutre",\n'
        '  "pertinent": true ou false,\n'
        '  "raison": "une phrase courte"\n'
        "}\n"
        "pertinent=true si l article interesse un investisseur, membre de la diaspora ou operateur economique.\n"
        "Aucun texte avant ou apres le JSON."
    )
    
    max_tentatives = 5
    for tentative in range(max_tentatives):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", # Mise à jour du modèle
                contents=prompt,
            )
            texte = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(texte)
            
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                import re
                match = re.search(r"retryDelay.*?(\d+)s", msg)
                delai = int(match.group(1)) + 3 if match else 65
                print(f"       Quota atteint. Attente {delai}s (tentative {tentative+1}/{max_tentatives})...")
                time.sleep(delai)
            else:
                print(f"       Gemini erreur : {msg[:80]}")
                return {"theme": "general", "sentiment": "neutre", "pertinent": False, "raison": "erreur"}
                
    return {"theme": "general", "sentiment": "neutre", "pertinent": False, "raison": "quota epuise"}

# -----------------------------------------
# 4. COLLECTE WORDPRESS
# -----------------------------------------
def collecter_wp(source):
    articles = []
    page = 1
    date_limite_basse = datetime.strptime(DATE_DEBUT, "%Y-%m-%d")
    date_limite_haute = datetime.strptime(DATE_FIN, "%Y-%m-%d")
    headers = {"User-Agent": "Mozilla/5.0"}
    ignores = 0
    print(f"\n  [WP] {source['nom']}")
    
    while True:
        try:
            api_url = f"{source['url']}/wp-json/wp/v2/posts?page={page}&per_page=50"
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"     API indisponible pour {source['nom']}")
                break
                
            posts = response.json()
            if not posts:
                break
                
            stop = False
            for post in posts:
                date_raw = post.get("date", "").split("T")[0]
                try:
                    date_article = datetime.strptime(date_raw, "%Y-%m-%d")
                except:
                    continue
                    
                if date_article > date_limite_haute:
                    continue
                if date_article < date_limite_basse:
                    stop = True
                    break
                    
                titre = BeautifulSoup(
                    post.get("title", {}).get("rendered", ""), "html.parser"
                ).get_text().strip()
                resume = BeautifulSoup(
                    post.get("excerpt", {}).get("rendered", ""), "html.parser"
                ).get_text()[:600].strip()
                url = post.get("link", "")
                
                if not concerne_benin(titre, resume):
                    ignores += 1
                    continue
                    
                print(f"     [OK] {titre[:65]}...")
                analyse = analyser_avec_gemini(titre, resume)
                
                # --- CORRECTION DU DELAI ---
                # 4.5 secondes garantit un maximum d'environ 13 requêtes par minute
                time.sleep(4.5) 
                
                articles.append({
                    "date":       date_raw,
                    "source":     source["nom"],
                    "titre":      titre,
                    "resume":     resume,
                    "url":        url,
                    "theme":      analyse.get("theme", "general"),
                    "sentiment":  analyse.get("sentiment", "neutre"),
                    "pertinent":  analyse.get("pertinent", False),
                    "raison":     analyse.get("raison", ""),
                    "type_media": "local_wp",
                })
                
            print(f"     Page {page} : {len(articles)} articles Benin | {ignores} ignores")
            if stop:
                break
            page += 1
            time.sleep(2)
            
        except Exception as e:
            print(f"     Erreur page {page} : {e}")
            break
            
    return articles

# -----------------------------------------
# 5. COLLECTE GOOGLE NEWS RSS
# -----------------------------------------
def collecter_gnews(source):
    articles = []
    date_limite_basse = datetime.strptime(DATE_DEBUT, "%Y-%m-%d")
    date_limite_haute = datetime.strptime(DATE_FIN, "%Y-%m-%d")
    print(f"\n  [RSS] {source['nom']}")
    
    try:
        url_rss = f"https://news.google.com/rss/search?q={source['query'].replace(' ', '+')}&hl=fr&gl=BJ&ceid=BJ:fr"
        feed = feedparser.parse(url_rss)
        
        for entry in feed.entries:
            titre = entry.get("title", "").strip()
            resume = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()[:600].strip()
            url = entry.get("link", "")
            
            date_raw_tuple = entry.get("published_parsed") or entry.get("updated_parsed")
            if date_raw_tuple:
                date_article = datetime(*date_raw_tuple[:6])
                date_raw = date_article.strftime("%Y-%m-%d")
            else:
                continue
                
            if date_article > date_limite_haute or date_article < date_limite_basse:
                continue
                
            print(f"     [OK] {titre[:65]}...")
            analyse = analyser_avec_gemini(titre, resume)
            
            # --- CORRECTION DU DELAI ---
            time.sleep(4.5) 
            
            articles.append({
                "date":       date_raw,
                "source":     source["nom"],
                "titre":      titre,
                "resume":     resume,
                "url":        url,
                "theme":      analyse.get("theme", "general"),
                "sentiment":  analyse.get("sentiment", "neutre"),
                "pertinent":  analyse.get("pertinent", False),
                "raison":     analyse.get("raison", ""),
                "type_media": "local_gnews",
            })
            
        print(f"     Total : {len(articles)} articles collectes")
        
    except Exception as e:
        print(f"     Erreur RSS : {e}")
        
    return articles

# -----------------------------------------
# 6. COLLECTE PRINCIPALE
# -----------------------------------------
def collecter_tout():
    tous_articles = []
    print("=" * 55)
    print("  BENIN PULSE - Collecte medias locaux")
    print(f"  Periode : {DATE_DEBUT} -> {DATE_FIN}")
    print("=" * 55)
    
    # WordPress
    print("\n--- Sources WordPress ---")
    for source in SOURCES_WP:
        articles = collecter_wp(source)
        tous_articles.extend(articles)
        time.sleep(3)
        
    # Google News RSS
    print("\n--- Sources Google News RSS ---")
    for source in SOURCES_GNEWS:
        articles = collecter_gnews(source)
        tous_articles.extend(articles)
        time.sleep(2)
        
    if not tous_articles:
        print("\nAucun article collecte.")
        return
        
    df = pd.DataFrame(tous_articles)
    
    # Deduplication sur le titre
    df = df.drop_duplicates(subset=["titre"])
    df = df.sort_values("date", ascending=False)
    df_pertinent = df[df["pertinent"] == True].copy()
    
    print("\n" + "=" * 55)
    print("  RESULTATS FINAUX")
    print("=" * 55)
    print(f"Total collecte        : {len(df)} articles")
    print(f"Articles pertinents   : {len(df_pertinent)} articles")
    
    print(f"\nRepartition par theme :")
    print(df_pertinent["theme"].value_counts().to_string())
    
    print(f"\nRepartition par sentiment :")
    print(df_pertinent["sentiment"].value_counts().to_string())
    
    print(f"\nRepartition par source :")
    print(df_pertinent["source"].value_counts().to_string())
    
    df.to_csv("benin_local_media_all.csv", index=False, encoding="utf-8-sig")
    df_pertinent.to_csv("benin_local_media.csv", index=False, encoding="utf-8-sig")
    
    print(f"\nExports reussis :")
    print(f"   benin_local_media.csv     -> {len(df_pertinent)} articles pertinents")
    print(f"   benin_local_media_all.csv -> {len(df)} articles au total")

if __name__ == "__main__":
    collecter_tout()