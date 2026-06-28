# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 10:14:56 2026

@author: hugoz
"""

# Documentation Zannote 

## Description des installations à effectuer
# Installation de Zannote / ZeggCounter

## Prérequis

* Python 3.11 ou supérieur
* Git
* Environ 20 Go d'espace disque libre recommandés
* Pour l'entraînement : GPU NVIDIA recommandé (CUDA)
* CPU uniquement possible mais fortement plus lent

---

## Création de l'environnement Python

### Avec conda

```bash
conda create -n zannote python=3.11
conda activate zannote
```

### Ou avec venv

```bash
python -m venv zannote_env
```

Sous Windows :

```bash
zannote_env\Scripts\activate
```

Sous Linux :

```bash
source zannote_env/bin/activate
```

---

## Installation de PyTorch

### GPU NVIDIA (recommandé)

Consulter la commande officielle correspondant à la version CUDA installée :

https://pytorch.org/get-started/locally/

Exemple :

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### CPU uniquement

```bash
pip install torch torchvision torchaudio
```

---

## Installation des dépendances du projet

```bash
pip install numpy
pip install pandas
pip install opencv-python
pip install albumentations
pip install scipy
pip install matplotlib
pip install tqdm
pip install pyqt6
pip install pyqt6-svg
```

Ou en une seule commande :

```bash
pip install numpy pandas opencv-python albumentations scipy matplotlib tqdm pyqt6 pyqt6-svg
```

---

## Vérification de PyTorch

Lancer :

```python
import torch

print(torch.__version__)
print(torch.cuda.is_available())
```

Résultat attendu :

```text
True
```

si un GPU CUDA est correctement détecté.

---

## Structure attendue du dataset

```text
dataset/

├── images/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
│
├── labels/
│   ├── image_001.csv
│   ├── image_002.csv
│   └── ...
│
└── test/
    ├── images/
    └── labels/
```

Chaque CSV doit contenir :

```csv
x,y
125,412
318,940
742,1051
```

---

## Lancement de l'entraînement

```bash
python train.py
```

Les modèles entraînés sont automatiquement sauvegardés dans :

```text
models/
├── V001/
├── V002/
├── ...
```

avec :

```text
model.pt
metrics.json
metadata.json
config.py
train_split.txt
val_split.txt
```

