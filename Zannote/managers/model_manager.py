# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 10:33:31 2026
Gestionnaire des modèles Zannote
"""

from pathlib import Path
import json


class ModelManager:

    def __init__(
        self,
        models_path="models"
    ):

        self.models_path = Path(
            models_path
        )

    # ---------------------------------------------------------
    # Liste des modèles disponibles
    # ---------------------------------------------------------

    def list_models(self):

        if not self.models_path.exists():

            return []

        models = sorted(
            [
                folder.name
                for folder in self.models_path.iterdir()
                if (
                    folder.is_dir()
                    and
                    folder.name.startswith("V")
                )
            ]
        )

        return models

    # ---------------------------------------------------------
    # Lecture d'un fichier json
    # ---------------------------------------------------------

    @staticmethod
    def load_json(path):

        path = Path(path)

        if not path.exists():

            return {}

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    # ---------------------------------------------------------
    # Métadata
    # ---------------------------------------------------------

    def get_metadata(
        self,
        version
    ):

        return self.load_json(

            self.models_path
            /
            version
            /
            "metadata.json"

        )

    # ---------------------------------------------------------
    # Métriques
    # ---------------------------------------------------------

    def get_metrics(
        self,
        version
    ):

        return self.load_json(

            self.models_path
            /
            version
            /
            "metrics.json"

        )

    # ---------------------------------------------------------
    # Historique
    # ---------------------------------------------------------

    def get_history(
        self,
        version
    ):

        return self.load_json(

            self.models_path
            /
            version
            /
            "history.json"

        )

    # ---------------------------------------------------------
    # Chemin du modèle
    # ---------------------------------------------------------

    def get_model_path(
        self,
        version
    ):

        return (

            self.models_path
            /
            version
            /
            "best_model.pt"

        )

    # ---------------------------------------------------------
    # Toutes les infos utiles
    # ---------------------------------------------------------

    def get_model_info(
        self,
        version
    ):

        metadata = self.get_metadata(
            version
        )

        metrics = self.get_metrics(
            version
        )

        return {

            **metadata,

            **metrics,

            "model_path": str(

                self.get_model_path(
                    version
                )

            )

        }

    # ---------------------------------------------------------
    # Vérifie qu'un modèle est complet
    # ---------------------------------------------------------

    def is_valid_model(
        self,
        version
    ):

        folder = (
            self.models_path
            /
            version
        )

        required_files = [

            folder / "best_model.pt",

            folder / "metadata.json",

            folder / "metrics.json"

        ]

        return all(

            file.exists()

            for file in required_files

        )

    # ---------------------------------------------------------
    # Dernier modèle entraîné
    # ---------------------------------------------------------

    def get_latest_model(self):

        models = self.list_models()

        if len(models) == 0:

            return None

        return models[-1]
    
    def list_models_display(self):

        items = []
    
        for version in self.list_models():
    
            metrics = self.get_metrics(version)
    
            rel = metrics.get(
                "relative_mae",
                None
            )
    
            if rel is None:
    
                text = version
    
            else:
    
                text = (
                    f"{version} "
                    f"(Erreur {100*rel:.1f} %)"
                )
    
            items.append(
                (
                    version,
                    text
                )
            )
    
        return items