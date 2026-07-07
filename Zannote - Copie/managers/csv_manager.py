# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:16:54 2026
@author: hugoz
"""
import os
import pandas as pd

from ai_models.zegg_counter.summary_manager import update_summary


class CsvManager:

    def __init__(self, label_folder, image_folder):
        self.label_folder = label_folder
        self.image_folder = image_folder
        os.makedirs(label_folder, exist_ok=True)

    def get_csv_path(self, image_name):
        return os.path.join(self.label_folder, f"{image_name}.csv")

    def load_annotations(self, image_name):
        path = self.get_csv_path(image_name)
        if not os.path.exists(path):
            return []
        try:
            df = pd.read_csv(path)
            return list(zip(df["x"], df["y"]))
        except Exception as e:
            print(e)
            return []

    def save_annotations(self, image_name, width, height, annotations):

        df = pd.DataFrame({
            "image": [image_name] * len(annotations),
            "width": [width] * len(annotations),
            "height": [height] * len(annotations),
            "egg_id": range(1, len(annotations) + 1),
            "x": [a.x for a in annotations],
            "y": [a.y for a in annotations],
            "confidence": [a.confidence for a in annotations]
        })

        df.to_csv(self.get_csv_path(image_name), index=False)
        self.update_summary()

    def update_summary(self):
        """
        Régénère Summary.xlsx en délégant à ai_models.zegg_counter.
        summary_manager.update_summary, pour un rendu strictement
        identique à celui produit après une prédiction IA.
        """
        return update_summary(self.label_folder, self.image_folder)