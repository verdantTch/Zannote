# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:16:23 2026

@author: hugoz
"""

import torch
import numpy as np

from peak_detection import detect_peaks


def evaluate_model(
    model,
    dataloader,
    device,
    threshold=0.5,
    min_distance=8
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

            batch_keypoints = (
                batch["keypoints"]
            )

            for i in range(len(probabilities)):
            
                heatmap = probabilities[i, 0]
            
                predicted_points = detect_peaks(
                    heatmap,
                    threshold=threshold,
                    min_distance=min_distance
                )
            
                predicted_count = len(predicted_points)
                true_count = len(batch_keypoints[i])
            
                error = abs(predicted_count - true_count)
            
                abs_errors.append(error)
            
                if true_count > 0:
                    relative_errors.append(error / true_count)
    
    metrics = {
        "mae": float(np.mean(abs_errors)) if abs_errors else 0.0,
        "mae_std": float(np.std(abs_errors)) if abs_errors else 0.0,
        "relative_mae": float(np.mean(relative_errors)) if relative_errors else 0.0,
        "relative_mae_std": float(np.std(relative_errors)) if relative_errors else 0.0,
    }
    
    return metrics

