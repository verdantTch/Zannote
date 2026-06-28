# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:53:52 2026

@author: hugoz
"""

import os
import glob

def comparer_dossiers(dossier_csv, dossier_jpg):
    """
    Compare les fichiers CSV et JPG dans deux dossiers différents.
    Met en évidence les fichiers qui n'ont pas de correspondance.
    
    Args:
        dossier_csv (str): Chemin vers le dossier contenant les fichiers .csv
        dossier_jpg (str): Chemin vers le dossier contenant les fichiers .jpg
    """
    
    # Vérifier que les dossiers existent
    if not os.path.exists(dossier_csv):
        print(f"❌ Erreur: Le dossier CSV '{dossier_csv}' n'existe pas.")
        return
    
    if not os.path.exists(dossier_jpg):
        print(f"❌ Erreur: Le dossier JPG '{dossier_jpg}' n'existe pas.")
        return
    
    # Récupérer tous les fichiers avec les extensions spécifiées
    fichiers_csv = glob.glob(os.path.join(dossier_csv, "*.csv"))
    fichiers_jpg = glob.glob(os.path.join(dossier_jpg, "*.jpg"))
    fichiers_jpeg = glob.glob(os.path.join(dossier_jpg, "*.jpeg"))
    fichiers_jpg.extend(fichiers_jpeg)  # Ajouter aussi les .jpeg
    
    # Extraire les noms de base (sans extension)
    noms_csv = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_csv}
    noms_jpg = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_jpg}
    
    # Trouver les correspondances
    ensemble_csv = set(noms_csv.keys())
    ensemble_jpg = set(noms_jpg.keys())
    
    # Fichiers présents uniquement dans CSV
    seulement_csv = ensemble_csv - ensemble_jpg
    
    # Fichiers présents uniquement dans JPG
    seulement_jpg = ensemble_jpg - ensemble_csv
    
    # Fichiers présents dans les deux
    dans_les_deux = ensemble_csv & ensemble_jpg
    
    # Afficher les résultats
    print("=" * 70)
    print(f"📊 COMPARAISON DES DOSSIERS")
    print("=" * 70)
    print(f"📁 Dossier CSV : {dossier_csv}")
    print(f"   📄 Fichiers CSV trouvés : {len(fichiers_csv)}")
    print(f"📁 Dossier JPG : {dossier_jpg}")
    print(f"   🖼️  Fichiers JPG trouvés : {len(fichiers_jpg)}")
    print("=" * 70)
    
    print(f"\n✅ Fichiers présents dans les deux dossiers : {len(dans_les_deux)}")
    if dans_les_deux:
        for nom in sorted(dans_les_deux):
            print(f"   ✓ {nom}")
    
    if seulement_csv:
        print(f"\n⚠️  Fichiers UNIQUEMENT dans le dossier CSV (manquent en JPG) : {len(seulement_csv)}")
        for nom in sorted(seulement_csv):
            print(f"   ✗ {nom}.csv")
            print(f"     → {noms_csv[nom]}")
    
    if seulement_jpg:
        print(f"\n⚠️  Fichiers UNIQUEMENT dans le dossier JPG (manquent en CSV) : {len(seulement_jpg)}")
        for nom in sorted(seulement_jpg):
            print(f"   ✗ {nom}.jpg")
            print(f"     → {noms_jpg[nom]}")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Correspondances parfaites : {len(dans_les_deux)} paires")
    print(f"❌ Fichiers CSV sans JPG : {len(seulement_csv)}")
    print(f"❌ Fichiers JPG sans CSV : {len(seulement_jpg)}")
    
    if seulement_csv or seulement_jpg:
        print("\n💡 SUGGESTIONS :")
        if seulement_csv:
            print(f"   - Créez {len(seulement_csv)} fichier(s) JPG pour les CSV manquants")
            print(f"     Noms : {', '.join(sorted(seulement_csv)[:5])}{'...' if len(seulement_csv) > 5 else ''}")
        if seulement_jpg:
            print(f"   - Créez {len(seulement_jpg)} fichier(s) CSV pour les JPG manquants")
            print(f"     Noms : {', '.join(sorted(seulement_jpg)[:5])}{'...' if len(seulement_jpg) > 5 else ''}")
    else:
        print("\n🎉 TOUS LES FICHIERS SONT APPAIRÉS !")
    
    print("=" * 70)
    
    return seulement_csv, seulement_jpg, dans_les_deux


def comparer_dossiers_detail(dossier_csv, dossier_jpg):
    """
    Version plus détaillée qui affiche également les différences de casse ou de caractères spéciaux.
    """
    from difflib import SequenceMatcher
    
    if not os.path.exists(dossier_csv) or not os.path.exists(dossier_jpg):
        print("❌ Un des dossiers n'existe pas.")
        return None, None, None
    
    fichiers_csv = glob.glob(os.path.join(dossier_csv, "*.csv"))
    fichiers_jpg = glob.glob(os.path.join(dossier_jpg, "*.jpg"))
    fichiers_jpeg = glob.glob(os.path.join(dossier_jpg, "*.jpeg"))
    fichiers_jpg.extend(fichiers_jpeg)
    
    noms_csv = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_csv}
    noms_jpg = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_jpg}
    
    ensemble_csv = set(noms_csv.keys())
    ensemble_jpg = set(noms_jpg.keys())
    
    seulement_csv = ensemble_csv - ensemble_jpg
    seulement_jpg = ensemble_jpg - ensemble_csv
    dans_les_deux = ensemble_csv & ensemble_jpg
    
    print("\n🔍 RECHERCHE DE CORRESPONDANCES APPROXIMATIVES")
    print("-" * 70)
    
    suggestions = {}
    for nom_csv in seulement_csv:
        for nom_jpg in seulement_jpg:
            # Vérifier si les noms sont similaires (ignore la casse)
            if nom_csv.lower() == nom_jpg.lower():
                suggestions[nom_csv] = nom_jpg
            # Vérifier avec un score de similarité
            elif SequenceMatcher(None, nom_csv.lower(), nom_jpg.lower()).ratio() > 0.8:
                if nom_csv not in suggestions:
                    suggestions[nom_csv] = nom_jpg
    
    if suggestions:
        print("🔎 Correspondances probables (différences de casse ou fautes de frappe) :")
        for csv, jpg in suggestions.items():
            print(f"   • {csv}.csv ↔ {jpg}.jpg")
    else:
        print("   Aucune correspondance approximative trouvée.")
    
    return seulement_csv, seulement_jpg, dans_les_deux


# ============ EXEMPLE D'UTILISATION ============

if __name__ == "__main__":
    # Définir les chemins des dossiers (à modifier selon votre configuration)
    DOSSIER_CSV = r"D:\Documents\Codage\Python\Wolbachia_Sicard\GH_code_Zannote\ai_models\zegg_counter\dataset\labels"  # Dossier contenant les fichiers .csv
    DOSSIER_JPG = r"D:\Documents\Codage\Python\Wolbachia_Sicard\GH_code_Zannote\ai_models\zegg_counter\dataset\images"  # Dossier contenant les fichiers .jpg
    
    # Exécuter la comparaison
    seulement_csv, seulement_jpg, dans_les_deux = comparer_dossiers(DOSSIER_CSV, DOSSIER_JPG)
    
    # Optionnel : version avec détection de similarités
    print("\n" + "=" * 70)
    seulement_csv_detail, seulement_jpg_detail, dans_les_deux_detail = comparer_dossiers_detail(DOSSIER_CSV, DOSSIER_JPG)
