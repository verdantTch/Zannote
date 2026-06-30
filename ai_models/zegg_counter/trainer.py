# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:05:02 2026

@author: hugoz
"""
import torch
import torch.nn as nn
import logging

from torch.utils.tensorboard import SummaryWriter
from tqdm.auto import tqdm
from config import BATCH_SIZE, NUM_WORKERS, LEARNING_RATE, N_EPOCHS, GRADIENT_CLIPPING, AUG2_ratio
from version_manager import (
    VersionManager
)
from augmentations import (
    get_phase1_transform,
    get_phase2_transform
)

from datetime import datetime

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
        
        # Pour sauvegarde des messages de progression de l'entraînement 
        self.logger = logging.getLogger("Trainer")
        self.logger.setLevel(logging.INFO)

        self.scaler = torch.amp.GradScaler(
            "cuda",
            enabled=(self.device.type == "cuda") # enabled permet de ne rien changer en cas d'entraînement sur CPU
        )
        
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
        
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer=self.optimizer,
            mode="min",      # on minimise la loss
            factor=0.5,      # LR = LR × 0.5
            patience=8,      # attendre 5 epochs
            threshold=1e-4,  # amélioration minimale
            min_lr=1e-7      # ne jamais descendre sous cette valeur
        )
        
        # Early stopping si pas d'amélioration
        self.early_stopping_patience = 15
        self.epochs_without_improvement = 0
        print(f"Device : {device}")
        if device.type == "cuda":
            print(torch.cuda.get_device_name(0))
            
    def train_epoch(self):
    
        self.model.train()
    
        running_loss = 0
    
        progress_bar = tqdm(
            self.train_loader,
            desc="Training",
            leave=False,
            unit="batch"
        )
    
        for batch in progress_bar:
    
            images = batch["image"].to(self.device)
            targets = batch["heatmap"].to(self.device)
    
            self.optimizer.zero_grad()
            
            with torch.amp.autocast(
                "cuda",
                enabled=(self.device.type == "cuda")
            ):
                outputs = self.model(images)
            
                loss = self.criterion(
                    outputs,
                    targets
                )
            
            self.scaler.scale(loss).backward()
            
            
            if GRADIENT_CLIPPING is not None:
                self.scaler.unscale_(self.optimizer)
            
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    max_norm=GRADIENT_CLIPPING
                )
                        
            self.scaler.step(self.optimizer)
            self.scaler.update()
                
            running_loss += loss.item()
    
            progress_bar.set_postfix(
                loss=f"{loss.item():.4f}"
            )
    
        return running_loss / max(len(self.train_loader), 1)
        
    def validate(self):
    
        self.model.eval()
    
        running_loss = 0
    
        with torch.no_grad():
    
            progress_bar = tqdm(
                self.val_loader,
                desc="Validation",
                leave=False,
                unit="batch"
            )
    
            for batch in progress_bar:
    
                images = batch["image"].to(self.device)
                targets = batch["heatmap"].to(self.device)
    
                with torch.amp.autocast(
                    "cuda",
                    enabled=(self.device.type == "cuda")
                ):
                
                    outputs = self.model(images)
                
                    loss = self.criterion(
                        outputs,
                        targets
                    )
    
                running_loss += loss.item()
    
                progress_bar.set_postfix(
                    loss=f"{loss.item():.4f}"
                )
    
        return running_loss / max(len(self.val_loader), 1)
        
    def fit(self):
        best_epoch = None
        
        history = []
        
        version_manager = VersionManager()

        version_name, version_path = (
            version_manager.create_version_folder()
        )
        print(version_path.resolve())
        writer = SummaryWriter(
            log_dir=version_path / "tensorboard"
        )
        
        phase2_epoch = int(AUG2_ratio * N_EPOCHS)

        for epoch in range(N_EPOCHS):
        
            if epoch < phase2_epoch:
                self.train_loader.dataset.set_transform(
                    get_phase1_transform
                    )
            else:
                self.train_loader.dataset.set_transform(
                    get_phase2_transform
                    )
            # Message de changement de phase d'entrainement
            if epoch == phase2_epoch:
                print("\n===== Passage aux augmentations Phase 2 =====\n")
                
            train_loss = (
                self.train_epoch()
            )
            
            val_loss = (self.validate())
            
            self.scheduler.step(val_loss)
            
            current_lr = self.optimizer.param_groups[0]["lr"]
            
            history.append(
                {
                    "epoch": epoch + 1,
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                    "learning_rate": current_lr
                }
            )
            
            writer.add_scalar(
                "Loss/Train",
                train_loss,
                epoch + 1
            )
            
            writer.add_scalar(
                "Loss/Validation",
                val_loss,
                epoch + 1
            )
            
            writer.add_scalar(
                "Learning Rate",
                current_lr,
                epoch + 1
            )
            
            message = (
                f"Epoch {epoch+1}/{N_EPOCHS}"
                f" | Train={train_loss:.4f}"
                f" | Val={val_loss:.4f}"
                f" | LR={current_lr:.2e} ||==|| " # Learning rate
                f" Train batches={len(self.train_loader)}"
                f" | Val batches={len(self.val_loader)}"
            )
            
            print(message)

            self.logger.info(message)

            
            if val_loss < self.best_loss:
            
                self.best_loss = val_loss
                best_epoch = epoch + 1
                self.epochs_without_improvement = 0
            
                version_manager.save_metrics(
                    version_path,
                    {
                        "best_val_loss": float(val_loss),
                        "train_loss": float(train_loss),
                        "epoch": best_epoch
                    }
                )
            
                torch.save(
                    self.model.state_dict(),
                    version_path / "best_model.pt"
                )
            
            else:
            
                self.epochs_without_improvement += 1
            
                self.logger.info(
                    f"No improvement "
                    f"{self.epochs_without_improvement}/"
                    f"{self.early_stopping_patience}"
                )
            
                if self.epochs_without_improvement >= self.early_stopping_patience:
            
                    self.logger.info("Early stopping")            
                    break   
                
        # Sauvegarde de l'historique pour retracer les courbes de loss
        version_manager.save_history(
            version_path,
            history
        )
        
        # Enregistrement de la courbe de loss pour chaque entrainement
        version_manager.save_loss_curve(
            version_path,
            history,
            best_epoch
        )
        
        # Sauvegarde des métadata
        version_manager.save_metadata(

            version_path,
            {
                "version":version_name,
                "date":datetime.now().isoformat(),
                "epochs_requested": N_EPOCHS,
                "epochs_completed": epoch + 1,
                "best_epoch": best_epoch,
                "learning_rate":LEARNING_RATE,
                "batch_size":BATCH_SIZE
            }
        
        )
        
        writer.close()
