# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 19:29:31 2026

@author: hugoz
"""

# -*- coding: utf-8 -*-

from pathlib import Path

import json
import shutil
import torch
import csv

import matplotlib.pyplot as plt

from datetime import datetime

from config import (
    MODEL_PATH
)


class VersionManager:

    def __init__(self):

        self.model_dir = Path(
            MODEL_PATH
        )

        self.model_dir.mkdir(
            exist_ok=True
        )


    def save_loss_curve(self, version_path, history, best_epoch):
    
        import matplotlib.pyplot as plt
    
        epochs = [h["epoch"] for h in history]
        train_loss = [h["train_loss"] for h in history]
        val_loss = [h["val_loss"] for h in history]
    
        plt.figure(figsize=(8, 5))
    
        plt.plot(
            epochs,
            train_loss,
            label="Train loss",
            linewidth=2
        )
    
        plt.plot(
            epochs,
            val_loss,
            label="Validation loss",
            linewidth=2
        )
    
        plt.axvline(
            best_epoch,
            color="green",
            linestyle="--",
            linewidth=2,
            label=f"Best epoch ({best_epoch}) for previous models"
        )
    
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training history")
        plt.grid(True)
        plt.legend()
    
        plt.tight_layout()
    
        plt.savefig(
            version_path / "loss_curve.png",
            dpi=300
        )
    
        plt.close()
        
    def save_history(self, version_path, history):
    
        with open(
            version_path / "history.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
    
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "epoch",
                    "train_loss",
                    "val_loss",
                    "learning_rate"
                ]
            )
    
            writer.writeheader()
            writer.writerows(history)
            
            
    def get_next_version(self):

        versions = []
        for folder in self.model_dir.iterdir():
        
            if (
                folder.is_dir()
                and
                folder.name.startswith("V")
            ):
        
                try:

                    versions.append(
                        int(
                            folder.name.replace("V","")
                        )
                    )
        
                except ValueError:
        
                    pass
                

        if len(versions) == 0:

            return "V001"

        return (
            "V"
            f"{max(versions)+1:03d}"
        )
    
    def cleanup_empty_versions(self):

        for folder in self.model_dir.iterdir():
    
            if (
                folder.is_dir()
                and
                folder.name.startswith("V")
            ):
    
                if len(list(folder.iterdir())) == 0:
                    folder.rmdir()
                
                
    def save_model(
        self,
        model,
        version_path
    ):
    
        torch.save(
            model.state_dict(),
            version_path / "model.pt"
        )


    def save_config(
        self,
        version_path,
        config_file
    ):
    
        self.copy_file(
            config_file,
            version_path / "config.py"
        )
      
        
    def save_split(
        self,
        version_path,
        train_split,
        val_split
    ):
    
        self.copy_file(
            train_split,
            version_path / "train_split.txt"
        )
    
        self.copy_file(
            val_split,
            version_path / "val_split.txt"
        )


    def create_version_folder(self):
        self.cleanup_empty_versions()
        
        version = (
            self.get_next_version()
        )

        version_path = (
            self.model_dir
            /
            version
        )

        version_path.mkdir()

        return (
            version,
            version_path
        )


    def save_json(
        self,
        data,
        path
    ):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )


    def save_metadata(
        self,
        version_path,
        metadata
    ):

        self.save_json(

            metadata,

            version_path
            /
            "metadata.json"

        )


    def save_metrics(
        self,
        version_path,
        metrics
    ):

        self.save_json(

            metrics,

            version_path
            /
            "metrics.json"

        )


    def copy_file(
        self,
        source,
        destination
    ):

        shutil.copy2(
            source,
            destination
        )