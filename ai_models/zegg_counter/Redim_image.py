# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:11:44 2026

@author: hugoz
"""

import cv2
from config import BORDER_MODE, TARGET_H, TARGET_W

def resize_and_pad(image):

    h, w = image.shape[:2]

    scale = min(
        TARGET_W / w,
        TARGET_H / h
    )

    new_w = int(w * scale)
    new_h = int(h * scale)

    image = cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )

    pad_w = TARGET_W - new_w
    pad_h = TARGET_H - new_h

    left = pad_w // 2
    right = pad_w - left

    top = pad_h // 2
    bottom = pad_h - top

    image = cv2.copyMakeBorder(
        image,
        top,
        bottom,
        left,
        right,
        borderType=BORDER_MODE
    )

    return image, scale, left, top