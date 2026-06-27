# -*- coding: utf-8 -*-
import torch

from model import EggUNet
model = EggUNet()
x = torch.randn(
    1,
    3,
    2048,
    3072
)
y = model(x)

print(
    x.shape
)

print(
    y.shape
)