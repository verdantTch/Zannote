# -*- coding: utf-8 -*-
'''
Permet d'évaluer les performances d'un modèle post entrainement 
'''

import torch

from pathlib import Path
from torch.utils.data import DataLoader

from model import EggUNet
from dataset import EggDataset

from evaluate import evaluate_model
from version_manager import VersionManager

from config import (
    TEST_IMAGE_PATH,
    TEST_LABEL_PATH,
    BATCH_SIZE,
    NUM_WORKERS
)


# A modifier : le chemin du modèle à évaluer
MODEL_PATH = (
    "models/V001/best_model.pt"
)


def main():

    device = torch.device(

        "cuda"

        if torch.cuda.is_available()

        else "cpu"

    )

    print(
        f"Device : {device}"
    )

    # -------------------------
    # Chargement modèle
    # -------------------------

    model = EggUNet()

    model.load_state_dict(

        torch.load(
            MODEL_PATH,
            map_location=device
        )

    )

    model.to(device)
    model.eval()

    # -------------------------
    # Dataset test
    # -------------------------

    test_dataset = EggDataset(

        image_dir=TEST_IMAGE_PATH,

        label_dir=TEST_LABEL_PATH,

        transform=None

    )

    test_loader = DataLoader(

        test_dataset,

        batch_size=BATCH_SIZE,

        shuffle=False,

        num_workers=NUM_WORKERS

    )

    # -------------------------
    # Evaluation
    # -------------------------

    metrics = evaluate_model(

        model,

        test_loader,

        device

    )
    

    version_manager = VersionManager()
    
    version_manager.save_metrics(
        Path(MODEL_PATH).parent,
        metrics
    )
        
    print("\n===== RESULTS =====\n")
    
    for key, value in metrics.items():
        print(f"{key:20}: {value}")


if __name__ == "__main__":
    main()