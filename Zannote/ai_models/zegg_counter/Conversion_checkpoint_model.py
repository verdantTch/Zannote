# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 01:07:17 2026

@author: hugoz
"""

import torch

from model import EggUNet

checkpoint_path = r"D:\Downloads\checkpoint_epoch_8.pt"

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

model = EggUNet()

checkpoint = torch.load(
    checkpoint_path,
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(device)
model.eval()

torch.save(
    model.state_dict(),
    r"D:\Downloads\best_model.pt"
)