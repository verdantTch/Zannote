# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 11:14:34 2026

@author: hugoz
"""

# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def save_prediction_csv(
    image_name,
    width,
    height,
    points,
    output_csv
):

    rows = []

    for egg_id, (x, y, conf) in enumerate(
        points,
        start=1
    ):

        rows.append(
            {
                "image": image_name,
                "width": width,
                "height": height,
                "egg_id": egg_id,
                "x": x,
                "y": y,
                "confidence": conf
            }
        )

    pd.DataFrame(
        rows
    ).to_csv(
        output_csv,
        index=False
    )


def summary_row(
    image_name,
    points
):

    confidences = [
        p[2]
        for p in points
    ]

    if len(confidences):

        mean_conf = float(
            np.mean(
                confidences
            )
        )

        std_conf = float(
            np.std(
                confidences
            )
        )

    else:

        mean_conf = 0
        std_conf = 0

    return {

        "image":
            image_name,

        "egg_count":
            len(points),

        "mean_confidence":
            mean_conf,

        "std_confidence":
            std_conf

    }