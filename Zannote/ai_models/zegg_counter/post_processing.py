# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 13:46:06 2026

@author: hugoz
"""

import numpy as np
from skimage.feature import peak_local_max


def detect_peaks(
    heatmap,
    threshold=0.5,
    min_distance=8
):
    coords = peak_local_max(
        heatmap,
        min_distance=min_distance,
        threshold_abs=threshold
    )

    # passage en (x,y)
    return [(int(c[1]), int(c[0])) for c in coords]


def restore_points(
    points,
    scale,
    left,
    top,
    width,
    height
):
    restored = []

    for x, y in points:

        x = (x - left) / scale
        y = (y - top) / scale

        if 0 <= x < width and 0 <= y < height:
            restored.append(
                (
                    int(round(x)),
                    int(round(y))
                )
            )

    return restored