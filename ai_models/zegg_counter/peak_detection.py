# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:13:28 2026

@author: hugoz
"""

import numpy as np

from scipy.ndimage import (
    maximum_filter
)


def detect_peaks(
    heatmap,
    threshold=0.5,
    min_distance=8
):

    local_max = (
        maximum_filter(
            heatmap,
            size=min_distance
        )
        ==
        heatmap
    )

    peaks = (
        local_max
        &
        (heatmap > threshold)
    )

    ys, xs = np.where(
        peaks
    )

    return list(
        zip(xs, ys)
    )