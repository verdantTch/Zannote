# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 12:23:49 2026

@author: hugoz
"""
import cv2
from pathlib import Path
import os

# Taille de l'image cible en cas de rognage d'image
TARGET_H = 2048
TARGET_W = 3072


# En cas de redimentionnement de l'image on comble en multipliant la dernière ligne / colone de pixels
BORDER_MODE = cv2.BORDER_CONSTANT      # noir ou couleur fixe


# Heatmap
SIGMA = 15
SIGMA_VAR = 3

# Training
BATCH_SIZE = 1 # Permet de regroupper les données pour la bach propagation
EARLY_STOPPING_PATIENCE = 15
N_EPOCHS = 100 # Nombre de pas d'amélioration du loss (ou de passage dans le U-net pour l'améliorer)
LEARNING_RATE = 8e-5 # Pas d'apprentissage 
NUM_WORKERS = 0
WEIGHT_DECAY = 1e-4  # Pour optimizer à ajuster, 1e-5 à 1e-3 selon l'overfitting observé
BCE_WEIGHT = 0.4
DICE_WEIGHT = 0.6

# Validation
VAL_RATIO = 0.15
RANDOM_SEED = 4  # 42 Controle de la répartition aléatoire pour les dataset


# Test
TEST_SIZE = 50

# Ratio de changement d'augmentation
AUG2_PATIENCE = 6 # Nombre d'époques sans amélioration de la relative_mae avant de passer aux augmentations phase 2

# Processing de la carte de probabilité prédite par le modèle
PEAK_THRESHOLD = 0.65 # Seuil de probabilité au dela duquel on considère qu'il y a un oeuf
PEAK_MIN_DISTANCE = 12 # Distance minimale en pixel séparant des oeuf

# =====================================================
# Chemins vers les différents répertoires et fichiers
# =====================================================
# Racine (dataset, code, split...) : reste sur le disque local/Colab,
# car ces données ne changent pas pendant l'entraînement.
RACINE = os.getcwd()

DATASET_PATH = os.path.join(RACINE,"dataset")

# Chemin des datas d'entraînement et de validation
IMAGE_PATH = os.path.join(DATASET_PATH,"images")
LABEL_PATH = os.path.join(DATASET_PATH,"labels")

# Chemin des datas de testing (non vues pendant l'entraînement)
TEST_IMAGE_PATH = os.path.join(DATASET_PATH,"test","images")
TEST_LABEL_PATH = os.path.join(DATASET_PATH,"test","labels")

# Chemin vers le dossier split (répartition du dataset en test et validation)
SPLIT_PATH = os.path.join(DATASET_PATH,"split")
TRAIN_SPLIT = os.path.join(DATASET_PATH,"train.txt")
VAL_SPLIT = os.path.join(DATASET_PATH,"val.txt")


# -----------------------------------------------------
# Détection Colab + redirection des sorties (modèles,
# checkpoints, historique...) vers Google Drive, pour
# survivre à un plantage/déconnexion de la VM Colab.
# -----------------------------------------------------
try:
    import google.colab  # noqa: F401
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:

    DRIVE_MOUNT_POINT = "/content/drive"

    if not os.path.isdir(os.path.join(DRIVE_MOUNT_POINT, "MyDrive")):
        from google.colab import drive
        drive.mount(DRIVE_MOUNT_POINT)

    # Dossier sur votre Drive où seront stockés modèles/checkpoints/historique.
    # A adapter selon l'organisation que vous voulez sur votre Drive.
    MODELS_RACINE = os.path.join(
        DRIVE_MOUNT_POINT, "MyDrive", "Zannote_models"
    )
    os.makedirs(MODELS_RACINE, exist_ok=True)

else:
    # En local (ex: Anaconda), on garde le comportement d'origine
    MODELS_RACINE = RACINE


# Modèles
MODEL_PATH = (
    os.path.join(MODELS_RACINE,"ai_models","zegg_counter","models")
)

METADATA_PATH = (
    os.path.join(MODELS_RACINE,"metadata.json")
)

TRAINING_HISTORY_PATH = (
    os.path.join(MODELS_RACINE,"training_history.json")
)

MODEL_PREFIX = "v"

GRADIENT_CLIPPING = 1 # Normalisation pour stabiliser l'apprentissage du modèle