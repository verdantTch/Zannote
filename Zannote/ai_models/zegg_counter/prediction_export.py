# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 11:14:34 2026

@author: hugoz
"""

# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import cv2
from pathlib import Path


def save_zannote_csv(
    image_path,
    points,
    output_folder
):
    image = cv2.imread(str(image_path))
    height, width = image.shape[:2]

    image_name = Path(image_path).stem

    rows = []

    for i, (x, y) in enumerate(points, start=1):

        rows.append({
            "image": image_name,
            "width": width,
            "height": height,
            "egg_id": i,
            "x": x,
            "y": y,
            "confidence": 1.0
        })

    df = pd.DataFrame(rows)

    output_file = Path(output_folder) / f"{image_name}.csv"

    df.to_csv(
        output_file,
        index=False
    )

    return output_file


def summary_row(image_name, points):

    return {
        "image": image_name,
        "egg_count": len(points)
    }

def save_summary(rows, output_folder):

    df = pd.DataFrame(rows)

    output_file = Path(output_folder) / "Summary.xlsx"

    df.to_excel(
        output_file,
        index=False
    )

    return output_file