# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 23:39:29 2026

@author: hugoz
"""
import torch

from model import EggUNet
from trainer import Trainer

from config import (
    IMAGE_PATH, 
    TEST_IMAGE_PATH, 
    SPLIT_PATH, 
    LABEL_PATH, 
    TRAIN_SPLIT,
    VAL_SPLIT
    )

from dataset import EggDataset
from transforms import get_train_transform
from split_dataset import (
    create_train_val_split
)


create_train_val_split(
    image_dir=IMAGE_PATH,
    test_dir=TEST_IMAGE_PATH,
    output_dir=SPLIT_PATH
)

train_dataset = EggDataset(
    image_dir=IMAGE_PATH,
    label_dir=LABEL_PATH,
    split_file=TRAIN_SPLIT,
    transform=get_train_transform
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

trainer = Trainer(

    model,

    train_dataset,

    val_dataset,

    device

)

trainer.fit()