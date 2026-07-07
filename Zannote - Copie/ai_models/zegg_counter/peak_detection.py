# -*- coding: utf-8 -*-

import numpy as np

from scipy.ndimage import (
    maximum_filter
)

from config import PEAK_THRESHOLD, PEAK_MIN_DISTANCE


def detect_peaks(
    heatmap,
    threshold=PEAK_THRESHOLD,
    min_distance=PEAK_MIN_DISTANCE
):

    local_max = (
        maximum_filter(
            heatmap,
            size=2 * min_distance + 1
        )
        ==
        heatmap
    )

    peaks = (
        local_max
        &
        (heatmap >= threshold)
    )

    ys, xs = np.where(
        peaks
    )

    points = []

    for x, y in zip(xs, ys):

        points.append(
            (
                int(x),
                int(y),
                float(
                    heatmap[y, x]
                )
            )
        )

    return points