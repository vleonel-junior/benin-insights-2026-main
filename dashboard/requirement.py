#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bénin Pulse - Détecteur et Installateur de Dépendances.
Ce script vérifie l'installation des paquets Python nécessaires au bon fonctionnement 
du Dashboard et des scripts de traitement, et propose de les installer s'ils sont manquants.
"""

import sys
import subprocess
import importlib.util

# Liste des paquets requis et leur description
REQUIREMENTS = {
    "streamlit": "Framework pour le Dashboard Web interactif",
    "pandas": "Manipulation et analyse des données tabulaires (CSV, JSON)",
    "plotly": "Création de graphiques dynamiques et interactifs",
    "numpy": "Calculs numériques et statistiques pour la simulation",
    "tweepy": "Intégration de l'API X (Twitter) pour le Social Listening",
    "requests": "Requêtes HTTP pour récupérer des données en ligne"
}

def check_package(package_name):
    """Vérifie si un paquet est installé dans l'environnement Python actuel."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    """Tente d'installer un paquet via uv (si disponible) ou pip."""
    # Détecter si 'uv' est installé pour une vitesse d'installation accrue
    uv_available = False
    try:
        subprocess.run(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        uv_available = True
    except FileNotFoundError:
        pass

    if uv_available:
        print(f"📦 Installation de {package_name} via uv...")
        cmd = ["uv", "pip", "install", package_name]
    else:
        print(f"📦 Installation de {package_name} via pip...")
        cmd = [sys.executable, "-m", "pip", "install", package_name]

    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de {package_name} : {e}")
        return False

def main():
    print("=" * 70)
    print("🇧🇯  BÉNIN PULSE - CONTRÔLE DES DÉPENDANCES PYTHON")
    print("=" * 70)
    print("Vérification de l'environnement local...\n")

    missing_packages = []
    installed_packages = []

    # Affichage de l'état de chaque paquet
    for package, description in REQUIREMENTS.items():
        installed = check_package(package)
        status = "🟢 Installé" if installed else "🔴 Manquant"
        print(f"🔹 {package:<12} | {status:<10} | {description}")
        
        if installed:
            installed_packages.append(package)
        else:
            missing_packages.append(package)

    print("\n" + "=" * 70)

    if not missing_packages:
        print("✅ Tout est prêt ! Toutes les dépendances sont installées.")
        print("Vous pouvez lancer le dashboard avec la commande :")
        print("👉 streamlit run app.py")
        print("=" * 70)
        sys.exit(0)

    print(f"⚠️ {len(missing_packages)} dépendance(s) manquante(s) détectée(s) :")
    print(", ".join(missing_packages))
    print("-" * 70)
    
    # Demande d'installation automatique
    try:
        response = input("Voulez-vous les installer automatiquement maintenant ? (O/n) : ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nOperation annulée.")
        sys.exit(1)
        
    if response in ['', 'o', 'oui', 'y', 'yes']:
        success_count = 0
        for package in missing_packages:
            if install_package(package):
                success_count += 1
        
        print("\n" + "=" * 70)
        if success_count == len(missing_packages):
            print("🎉 Toutes les dépendances ont été installées avec succès !")
            print("Lancez le dashboard avec :")
            print("👉 streamlit run app.py")
        else:
            print(f"⚠️ Installation partielle : {success_count}/{len(missing_packages)} paquets installés.")
            print("Veuillez installer manuellement les dépendances restantes.")
        print("=" * 70)
    else:
        print("\nInstallation annulée. Vous devrez installer les paquets requis manuellement :")
        print(f"pip install {' '.join(missing_packages)}")
        print("=" * 70)

if __name__ == "__main__":
    main()
