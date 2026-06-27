# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:05:02 2026

@author: hugoz
"""
import torch
import torch.nn as nn
from config import BATCH_SIZE, NUM_WORKERS, LEARNING_RATE, N_EPOCHS
from version_manager import (
    VersionManager
)

from datetime import datetime

from pathlib import Path

from torch.utils.data import DataLoader
 
class Trainer:
    def __init__(
        self,
        model,
        train_dataset,
        val_dataset,
        device
    ):
        self.device = device

        self.model = model.to(device)
        self.best_loss = float("inf")
        self.train_loader = DataLoader(
        
            train_dataset,
        
            batch_size=BATCH_SIZE,
        
            shuffle=True,
        
            num_workers=NUM_WORKERS
        
        )
        self.val_loader = DataLoader(

            val_dataset,
        
            batch_size=BATCH_SIZE,
        
            shuffle=False,
        
            num_workers=NUM_WORKERS
        
        )
        self.criterion = (
            nn.BCEWithLogitsLoss()
            )
        
        self.optimizer = torch.optim.Adam(
    
        self.model.parameters(),
    
        lr=LEARNING_RATE
        
        )
            
    def train_epoch(self):
        self.model.train()
        running_loss = 0
        
        for batch in self.train_loader:
            images = batch["image"].to(
                self.device
            )
            
            targets = batch["heatmap"].to(
                self.device
            )
            
            outputs = self.model(
                images
            )
            
            loss = self.criterion(
                outputs,
                targets
            )
            
            self.optimizer.zero_grad()
            
            loss.backward()
            
            self.optimizer.step()
            
            running_loss += (
                loss.item()
            )
            
        return (
            running_loss
            /
            len(self.train_loader)
        )
        
    def validate(self):
    
        self.model.eval()
    
        running_loss = 0
    
        with torch.no_grad():
    
            for batch in self.val_loader:
    
                images = batch["image"].to(
                    self.device
                )
    
                targets = batch["heatmap"].to(
                    self.device
                )
    
                outputs = self.model(
                    images
                )
    
                loss = self.criterion(
                    outputs,
                    targets
                )
    
                running_loss += (
                    loss.item()
                )
    
        return (
            running_loss
            /
            max(
                len(self.val_loader),
                1
            )
        )
        
    def fit(self):
        for epoch in range(
            N_EPOCHS
        ):
            train_loss = (
                self.train_epoch()
            )
            
            val_loss = (
                self.validate()
            )
            
            print(
                f"Epoch {epoch+1}"
                f" | Train={train_loss:.4f}"
                f" | Val={val_loss:.4f}"
            )
            print(
                f"Train batches : {len(self.train_loader)}"
            )
            
            print(
                f"Val batches : {len(self.val_loader)}"
            )
            
            if val_loss < self.best_loss:
                
                version_manager = VersionManager()

                version_name, version_path = (
                    version_manager.create_version_folder()
                )
                
                self.best_loss = val_loss
                version_manager.save_metrics(
                    version_path,
                    {
                        "best_val_loss":
                            float(val_loss),
                
                        "epoch":
                            epoch + 1
                
                    }
                
                )
                torch.save(
                    self.model.state_dict(),
                    "best_model.pt"
                )
            version_manager.save_metadata(

                version_path,
            
                {
            
                    "version":
                        version_name,
            
                    "date":
                        datetime.now().isoformat(),
            
                    "epochs":
                        N_EPOCHS,
            
                    "learning_rate":
                        LEARNING_RATE,
            
                    "batch_size":
                        BATCH_SIZE
            
                }
            
            )
