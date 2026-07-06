# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 16:53:52 2026

@author: hugoz
"""

import os
import glob

def comparer_dossiers(dossier_csv, DOSSIER_IMAGES):
    """
    Compare les fichiers CSV et les images (JPG, PNG, TIFF, etc.) dans deux dossiers différents.
    Met en évidence les fichiers qui n'ont pas de correspondance.
    
    Args:
        dossier_csv (str): Chemin vers le dossier contenant les fichiers .csv
        DOSSIER_IMAGES (str): Chemin vers le dossier contenant les fichiers images
    """
    
    # Vérifier que les dossiers existent
    if not os.path.exists(dossier_csv):
        print(f"❌ Erreur: Le dossier CSV '{dossier_csv}' n'existe pas.")
        return
    
    if not os.path.exists(DOSSIER_IMAGES):
        print(f"❌ Erreur: Le dossier images '{DOSSIER_IMAGES}' n'existe pas.")
        return
    
    # Récupérer tous les fichiers CSV
    fichiers_csv = glob.glob(os.path.join(dossier_csv, "*.csv"))
    
    # Récupérer TOUS les fichiers image (extensions courantes)
    extensions_image = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif', 
                        '*.bmp', '*.gif', '*.webp', '*.svg', '*.ico']
    
    fichiers_image = []
    for ext in extensions_image:
        fichiers_image.extend(glob.glob(os.path.join(DOSSIER_IMAGES, ext)))
    
    # Extraire les noms de base (sans extension)
    noms_csv = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_csv}
    noms_image = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_image}
    
    # Trouver les correspondances
    ensemble_csv = set(noms_csv.keys())
    ensemble_image = set(noms_image.keys())
    
    # Fichiers présents uniquement dans CSV
    seulement_csv = ensemble_csv - ensemble_image
    
    # Fichiers présents uniquement dans les images
    seulement_image = ensemble_image - ensemble_csv
    
    # Fichiers présents dans les deux
    dans_les_deux = ensemble_csv & ensemble_image
    
    # Afficher les résultats
    print("=" * 70)
    print(f"📊 COMPARAISON DES DOSSIERS")
    print("=" * 70)
    print(f"📁 Dossier CSV : {dossier_csv}")
    print(f"   📄 Fichiers CSV trouvés : {len(fichiers_csv)}")
    print(f"📁 Dossier Images : {DOSSIER_IMAGES}")
    print(f"   🖼️  Fichiers image trouvés : {len(fichiers_image)}")
    
    # Afficher la répartition par extension
    extensions_trouvees = {}
    for f in fichiers_image:
        ext = os.path.splitext(f)[1].lower()
        extensions_trouvees[ext] = extensions_trouvees.get(ext, 0) + 1
    
    if extensions_trouvees:
        print("   📋 Extensions trouvées :")
        for ext, count in sorted(extensions_trouvees.items()):
            print(f"      • {ext}: {count} fichier(s)")
    
    print("=" * 70)
    
    print(f"\n✅ Fichiers présents dans les deux dossiers : {len(dans_les_deux)}")
    if dans_les_deux:
        for nom in sorted(dans_les_deux):
            # Trouver l'extension du fichier image correspondant
            chemin_image = noms_image[nom]
            ext_image = os.path.splitext(chemin_image)[1]
            print(f"   ✓ {nom}.csv ↔ {nom}{ext_image}")
    
    if seulement_csv:
        print(f"\n⚠️  Fichiers UNIQUEMENT dans le dossier CSV (manquent en image) : {len(seulement_csv)}")
        for nom in sorted(seulement_csv):
            print(f"   ✗ {nom}.csv")
            print(f"     → {noms_csv[nom]}")
    
    if seulement_image:
        print(f"\n⚠️  Fichiers UNIQUEMENT dans le dossier images (manquent en CSV) : {len(seulement_image)}")
        for nom in sorted(seulement_image):
            chemin_image = noms_image[nom]
            ext_image = os.path.splitext(chemin_image)[1]
            print(f"   ✗ {nom}{ext_image}")
            print(f"     → {chemin_image}")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Correspondances parfaites : {len(dans_les_deux)} paires")
    print(f"❌ Fichiers CSV sans image : {len(seulement_csv)}")
    print(f"❌ Fichiers image sans CSV : {len(seulement_image)}")
    
    if seulement_csv or seulement_image:
        print("\n💡 SUGGESTIONS :")
        if seulement_csv:
            print(f"   - Créez {len(seulement_csv)} fichier(s) image pour les CSV manquants")
            print(f"     Noms : {', '.join(sorted(seulement_csv)[:5])}{'...' if len(seulement_csv) > 5 else ''}")
        if seulement_image:
            print(f"   - Créez {len(seulement_image)} fichier(s) CSV pour les images manquantes")
            print(f"     Noms : {', '.join(sorted(seulement_image)[:5])}{'...' if len(seulement_image) > 5 else ''}")
    else:
        print("\n🎉 TOUS LES FICHIERS SONT APPAIRÉS !")
    
    print("=" * 70)
    
    return seulement_csv, seulement_image, dans_les_deux


def comparer_dossiers_detail(dossier_csv, DOSSIER_IMAGES):
    """
    Version plus détaillée qui affiche également les différences de casse ou de caractères spéciaux.
    """
    from difflib import SequenceMatcher
    
    if not os.path.exists(dossier_csv) or not os.path.exists(DOSSIER_IMAGES):
        print("❌ Un des dossiers n'existe pas.")
        return None, None, None
    
    fichiers_csv = glob.glob(os.path.join(dossier_csv, "*.csv"))
    
    # Récupérer TOUS les fichiers image
    extensions_image = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif', 
                        '*.bmp', '*.gif', '*.webp', '*.svg', '*.ico']
    
    fichiers_image = []
    for ext in extensions_image:
        fichiers_image.extend(glob.glob(os.path.join(DOSSIER_IMAGES, ext)))
    
    noms_csv = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_csv}
    noms_image = {os.path.splitext(os.path.basename(f))[0]: f for f in fichiers_image}
    
    ensemble_csv = set(noms_csv.keys())
    ensemble_image = set(noms_image.keys())
    
    seulement_csv = ensemble_csv - ensemble_image
    seulement_image = ensemble_image - ensemble_csv
    dans_les_deux = ensemble_csv & ensemble_image
    
    print("\n🔍 RECHERCHE DE CORRESPONDANCES APPROXIMATIVES")
    print("-" * 70)
    
    suggestions = {}
    for nom_csv in seulement_csv:
        for nom_image in seulement_image:
            # Vérifier si les noms sont similaires (ignore la casse)
            if nom_csv.lower() == nom_image.lower():
                suggestions[nom_csv] = nom_image
            # Vérifier avec un score de similarité
            elif SequenceMatcher(None, nom_csv.lower(), nom_image.lower()).ratio() > 0.8:
                if nom_csv not in suggestions:
                    suggestions[nom_csv] = nom_image
    
    if suggestions:
        print("🔎 Correspondances probables (différences de casse ou fautes de frappe) :")
        for csv, image in suggestions.items():
            # Trouver l'extension du fichier image
            chemin_image = noms_image[image]
            ext_image = os.path.splitext(chemin_image)[1]
            print(f"   • {csv}.csv ↔ {image}{ext_image}")
    else:
        print("   Aucune correspondance approximative trouvée.")
    
    return seulement_csv, seulement_image, dans_les_deux


# ============ EXEMPLE D'UTILISATION ============

if __name__ == "__main__":
    # Définir les chemins des dossiers (à modifier selon votre configuration)
    DOSSIER_CSV = r"D:\Documents\Codage\Python\Wolbachia_Sicard\GH_code_Zannote\Zannote\ai_models\zegg_counter\dataset\test\labels"  # Dossier contenant les fichiers .csv
    DOSSIER_IMAGES = r"D:\Documents\Codage\Python\Wolbachia_Sicard\GH_code_Zannote\Zannote\ai_models\zegg_counter\dataset\test\images"  # Dossier contenant les fichiers images
    
    # Exécuter la comparaison
    seulement_csv, seulement_image, dans_les_deux = comparer_dossiers(DOSSIER_CSV, DOSSIER_IMAGES)
    
    # Optionnel : version avec détection de similarités
    print("\n" + "=" * 70)
    seulement_csv_detail, seulement_image_detail, dans_les_deux_detail = comparer_dossiers_detail(DOSSIER_CSV, DOSSIER_IMAGES)