
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
sys.path.append('.')

import torch
import matplotlib.pyplot as plt
from predictor import Predictor


# Créer le prédicteur
predictor = Predictor(
    model_path="models/V002/best_model.pt",
    device=torch.device("cpu")
)

# Prédire avec l'image (chemin à adapter !)
try:
    heatmap, scale, left, top, width, height = predictor.predict_heatmap("test.png")
    print(f"Heatmap shape: {heatmap.shape}")
    print(f"Scale: {scale}, Left: {left}, Top: {top}, Width: {width}, Height: {height}")
    
    # Afficher la heatmap
    plt.imshow(heatmap, cmap="hot")
    plt.colorbar()
    plt.show()
    
except FileNotFoundError:
    print("❌ Erreur : Le fichier 'test.png' n'a pas été trouvé.")
    print("Assurez-vous que l'image existe dans le dossier courant ou spécifiez un chemin complet.")