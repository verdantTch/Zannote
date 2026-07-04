# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:16:23 2026
@author: hugoz
"""
import torch
import numpy as np
from config import PEAK_THRESHOLD, PEAK_MIN_DISTANCE
from peak_detection import detect_peaks
def evaluate_model(
    model,
    dataloader,
    device,
    threshold=PEAK_THRESHOLD,
    min_distance=PEAK_MIN_DISTANCE
):
    model.eval()
    
    abs_errors = []
    relative_errors = []
    with torch.no_grad():
        for batch in dataloader:
            images = batch["image"].to(device)
            outputs = model(images)
            probabilities = torch.sigmoid(
                outputs
            )
            probabilities = (
                probabilities
                .cpu()
                .numpy()
            )
            true_counts = batch["egg_count"]
            image_names = batch["image_name"]
            for i in range(len(probabilities)):
            
                heatmap = probabilities[i, 0]
            
                predicted_points = detect_peaks(
                    heatmap,
                    threshold=threshold,
                    min_distance=min_distance
                )
            
                predicted_count = len(predicted_points)
                true_count = int(true_counts[i]) 
                image_name = image_names[i]
                
                print(
                    f"{image_name} || Prédiction={predicted_count}"
                    f" || Nombre réel={true_count}"
                )
                error = abs(predicted_count - true_count)

                # IMPORTANT : cette ligne alimente le MAE (erreur absolue).
                # Elle doit être appelée pour CHAQUE image, y compris
                # celles à true_count == 0, sinon "mae" reste 0.0 par défaut.
                abs_errors.append(error)
            
                if true_count > 0:
                    relative_errors.append(error / true_count)
                else:
                    # image vide : 0% d'erreur si rien prédit, 100% sinon (ou autre convention à vous)
                    relative_errors.append(0.0 if predicted_count == 0 else 1.0)
    
    metrics = {
        "threshold": threshold,
        "min_distance": min_distance,
        "mae": float(np.mean(abs_errors)) if abs_errors else 0.0,
        "mae_std": float(np.std(abs_errors)) if abs_errors else 0.0,
        "relative_mae": float(np.mean(relative_errors)) if relative_errors else 0.0,
        "relative_mae_std": float(np.std(relative_errors)) if relative_errors else 0.0,
    }
    
    return metrics