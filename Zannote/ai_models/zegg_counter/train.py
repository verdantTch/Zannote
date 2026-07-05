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
from version_manager import VersionManager
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
version_manager = VersionManager()
resume_from = None

latest_checkpoint = version_manager.find_latest_checkpoint()
best_checkpoint = version_manager.find_best_checkpoint()

if latest_checkpoint is not None or best_checkpoint is not None:

    if latest_checkpoint is not None:
        print(
            f"\nDernier checkpoint trouvé : "
            f"{latest_checkpoint.parent.name}/{latest_checkpoint.name}"
        )

    if best_checkpoint is not None:
        print(
            f"Meilleur checkpoint trouvé : "
            f"{best_checkpoint.parent.name}/{best_checkpoint.name}"
        )

    print(
        "\nReprendre l'entraînement depuis :"
        "\n  [d] le Dernier checkpoint (dernier epoch entraîné)"
        "\n  [b] le meilleur checkpoint (Best relative_mae)"
        "\n  [n] Non, repartir de zéro"
    )

    while True:

        answer = input(
            "Votre choix [d/b/n] : "
        ).strip().lower()

        if answer == "d" and latest_checkpoint is not None:
            resume_from = latest_checkpoint
            break
        elif answer == "b" and best_checkpoint is not None:
            resume_from = best_checkpoint
            break
        elif answer == "n":
            resume_from = None
            break
        else:
            print(
                "Réponse invalide ou checkpoint indisponible pour ce choix. "
                "Veuillez répondre par d, b ou n."
            )

trainer = Trainer(
    model,
    train_dataset,
    val_dataset,
    device
)
trainer.fit(
    resume_from=resume_from
)