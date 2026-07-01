# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 23:39:29 2026

@author: hugoz
"""
import torch

from model import EggUNet
from trainer import Trainer
from augmentations import get_phase1_transform

from config import (
    IMAGE_PATH, 
    TEST_IMAGE_PATH, 
    SPLIT_PATH, 
    LABEL_PATH, 
    TRAIN_SPLIT,
    VAL_SPLIT
    )

from dataset import EggDataset


from split_dataset import (
    create_train_val_split
)


create_train_val_split()

train_dataset = EggDataset(
    image_dir=IMAGE_PATH,
    label_dir=LABEL_PATH,
    split_file=TRAIN_SPLIT,
    transform=get_phase1_transform # On initialise l'augmentation (la phase 2 est codée dans le trainer.py)
)

val_dataset = EggDataset(
    image_dir=IMAGE_PATH,
    label_dir=LABEL_PATH,
    split_file=VAL_SPLIT,
    transform=None
)


device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

model = EggUNet()

trainer = Trainer(model, train_dataset, val_dataset, device)
trainer.fit()