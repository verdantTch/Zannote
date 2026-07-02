# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:03:52 2026

@author: hugoz
"""

# ai/heatmap.py

import numpy as np


def gaussian_2d(
    shape,
    sigma
):
    """
    Génère une gaussienne 2D centrée.
    """

    h, w = shape

    y, x = np.ogrid[
        -h//2:h//2,
        -w//2:w//2
    ]

    gaussian = np.exp(
        -(x**2 + y**2)
        / (2 * sigma**2)
    )

    return gaussian

def generate_heatmap(
    keypoints,
    height,
    width,
    sigma=4 # A chager pour ajuster
):
    """
    Crée une heatmap à partir d'une liste de points.
    """

    heatmap = np.zeros(
        (height, width),
        dtype=np.float32
    )

    radius = sigma * 3

    size = radius * 2 + 1

    kernel = gaussian_2d(
        (size, size),
        sigma
    )

    for x, y in keypoints:

        x = int(x)
        y = int(y)

        left = max(
            0,
            x - radius
        )

        right = min(
            width,
            x + radius + 1
        )

        top = max(
            0,
            y - radius
        )

        bottom = min(
            height,
            y + radius + 1
        )

        k_left = radius - (
            x - left
        )

        k_right = radius + (
            right - x
        )

        k_top = radius - (
            y - top
        )

        k_bottom = radius + (
            bottom - y
        )

        heatmap[
            top:bottom,
            left:right
        ] = np.maximum(
            heatmap[
                top:bottom,
                left:right
            ],
            kernel[
                k_top:k_bottom,
                k_left:k_right
            ]
        )

    return heatmap