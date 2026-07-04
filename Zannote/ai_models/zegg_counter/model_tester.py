# -*- coding: utf-8 -*-
'''
Permet d'évaluer les performances d'un modèle post entrainement 
'''

import torch

from pathlib import Path
from torch.utils.data import DataLoader

from model_ancien_V001_V002  import EggUNet # à modifier si anciennes versions
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
    "models/V002/best_model.pt"
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
    
    print(f"Threshold               : {metrics['threshold']:.2f}")
    print(f"Min distance            : {metrics['min_distance']}")
    print(f"MAE                     : {metrics['mae']:.2f} eggs")
    print(f"MAE std                 : {metrics['mae_std']:.2f}")
    print(f"Relative MAE            : {metrics['relative_mae']*100:.2f}%")
    print(f"Relative MAE std        : {metrics['relative_mae_std']*100:.2f}%")


if __name__ == "__main__":
    main()