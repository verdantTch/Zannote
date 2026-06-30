# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 17:08:08 2026

@author: hugoz
"""

# test_predict.py
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


import torch
from predictor import Predictor
import matplotlib.pyplot as plt


predictor = Predictor(
    model_path="models/V001/best_model.pt",
    device=torch.device("cpu")
)

heatmap, scale, left, top = (
    predictor.predict_heatmap(
        "test.jpg"
    )
)

print(
    heatmap.shape
)

plt.imshow(
    heatmap,
    cmap="hot"
)

plt.colorbar()

plt.show()
