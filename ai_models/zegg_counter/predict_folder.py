# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 11:12:16 2026

@author: hugoz
"""
# -*- coding: utf-8 -*-

from pathlib import Path

import cv2
import pandas as pd

from predictor import Predictor
from peak_detection import detect_peaks
from prediction_export import (
    save_prediction_csv,
    summary_row
)


def predict_folder(
    image_dir,
    predictor,
    threshold=0.5,
    min_distance=8
):

    image_dir = Path(
        image_dir
    )

    summary = []

    image_files = sorted(
        [
            p
            for p in image_dir.iterdir()
            if p.suffix.lower()
            in (
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".tif",
                ".tiff"
            )
        ]
    )

    for image_path in image_files:

        print(
            image_path.name
        )

        heatmap, scale, left, top = (
            predictor.predict_heatmap(
                image_path
            )
        )

        points = detect_peaks(
            heatmap,
            threshold,
            min_distance
        )

        image = cv2.imread(
            str(image_path)
        )

        h, w = image.shape[:2]

        csv_path = (
            image_path.parent
            /
            f"{image_path.stem}.csv"
        )

        save_prediction_csv(
            image_path.stem,
            w,
            h,
            points,
            csv_path
        )

        summary.append(
            summary_row(
                image_path.name,
                points
            )
        )

    excel_path = (
        image_dir
        /
        f"{image_dir.name}.xlsx"
    )

    pd.DataFrame(
        summary
    ).to_excel(
        excel_path,
        index=False
    )

    print(
        f"Résultats enregistrés : {excel_path}"
    )
