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

    total_abs_error = 0

    total_images = 0

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

            for i in range(
                len(probabilities)
            ):

                heatmap = (
                    probabilities[i, 0]
                )

                predicted_points = (
                    detect_peaks(
                        heatmap,
                        threshold=threshold,
                        min_distance=min_distance
                    )
                )

                predicted_count = len(
                    predicted_points
                )

                true_count = len(
                    batch_keypoints[i]
                )

                total_abs_error += abs(
                    predicted_count
                    -
                    true_count
                )

                total_images += 1

    mae = (
        total_abs_error
        /
        total_images
    )

    return mae