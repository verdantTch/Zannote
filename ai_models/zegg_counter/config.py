# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 12:23:49 2026

@author: hugoz
"""
import cv2

# Taille de l'image cible en cas de rognage d'image
TARGET_H = 2048
TARGET_W = 3072


# En cas de redimentionnement de l'image on comble en multipliant la dernière ligne / colone de pixels
BORDER_MODE = cv2.BORDER_CONSTANT      # noir ou couleur fixe


# Heatmap
SIGMA = 15 # Taille des gaussiennes entourant les points d'intérêt ==> à faire varier pour une  meilleure convergence du modèle


# Training
BATCH_SIZE = 2 # Permet de regroupper les données pour la bach propagation
N_EPOCHS = 50 # Nombre de pas
LEARNING_RATE = 1e-4 # Pas d'apprentissage 
LEARNING_RATE = 1e-4
NUM_WORKERS = 0
LEARNING_RATE = 1e-4


# Validation
VAL_RATIO = 0.15
RANDOM_SEED = 42 # Controle de la répartition aléatoire pour les dataset


# Test
TEST_SIZE = 50



# =====================================================
# Chemins vers les différents répertoires et fichiers
# =====================================================
# Racine
DATASET_PATH = (r"...\ai_models\zegg_counter\dataset")

# Chemin des datas d'entraînement et de validation
IMAGE_PATH = (rf"{DATASET_PATH}\images")
LABEL_PATH = (rf"{DATASET_PATH}\labels")

# Chemin des datas de testing (non vues pendant l'entraînement)
TEST_IMAGE_PATH = (rf"{DATASET_PATH}\test\images")
TEST_LABEL_PATH = (rf"{DATASET_PATH}\test\labels")

# Chemin vers le dossier split (répartition du dataset en test et validation)
SPLIT_PATH = (rf"{DATASET_PATH}\split")
TRAIN_SPLIT = (rf"{SPLIT_PATH}\train.txt")
VAL_SPLIT = (rf"{SPLIT_PATH}\val.txt")


# Modèles
MODEL_PATH = (
    r"...\ai_models\zegg_counter\models"
)

METADATA_PATH = (
    r"...\ai_models\zegg_counter\metadata.json"
)

TRAINING_HISTORY_PATH = (
    r"...\ai_models\zegg_counter\training_history.json"
)

MODEL_DIR = "models"
MODEL_PREFIX = "v"