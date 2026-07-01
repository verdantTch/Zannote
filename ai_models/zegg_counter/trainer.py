# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:05:02 2026

@author: hugoz
"""
import torch
import torch.nn as nn
import logging
import glob
import os


from torch.utils.tensorboard import SummaryWriter
from tqdm.auto import tqdm
from config import BATCH_SIZE, NUM_WORKERS, LEARNING_RATE, N_EPOCHS, GRADIENT_CLIPPING, AUG2_ratio, TRAIN_SPLIT, VAL_SPLIT
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
    
    def save_checkpoint(self, epoch, version_path, is_best=False):
        """Sauvegarde un checkpoint complet de l'entraînement"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_loss': self.best_loss,
            'scaler_state_dict': self.scaler.state_dict() if self.device.type == "cuda" else None,
            'epochs_without_improvement': self.epochs_without_improvement
        }
        
        # Sauvegarde du checkpoint principal
        checkpoint_path = version_path / f"checkpoint_epoch_{epoch+1}.pt"
        torch.save(checkpoint, checkpoint_path)
        
        # Si c'est le meilleur modèle, on le sauvegarde aussi
        if is_best:
            torch.save(checkpoint, version_path / "best_checkpoint.pt")
        
        # Garder seulement les 3 derniers checkpoints pour économiser de l'espace
        self._cleanup_old_checkpoints(version_path, keep=3)
        
        return checkpoint_path
    
    def _cleanup_old_checkpoints(self, version_path, keep=3):
        """Nettoie les anciens checkpoints pour garder seulement les N plus récents"""
        import glob
        checkpoint_files = sorted(
            glob.glob(str(version_path / "checkpoint_epoch_*.pt")),
            key=lambda x: int(x.split('_')[-1].split('.')[0])
        )
        
        # Garder seulement les 'keep' plus récents
        for old_file in checkpoint_files[:-keep]:
            try:
                import os
                os.remove(old_file)
                self.logger.info(f"Suppression du checkpoint ancien: {old_file}")
            except Exception as e:
                self.logger.warning(f"Impossible de supprimer {old_file}: {e}")
    
    def load_checkpoint(self, checkpoint_path):
        """Charge un checkpoint complet"""
        checkpoint = torch.load(
            checkpoint_path,
            map_location=self.device
        )
        
        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )
        
        self.optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )
        
        self.scheduler.load_state_dict(
            checkpoint["scheduler_state_dict"]
        )
        
        self.best_loss = checkpoint["best_loss"]
        
        if checkpoint["scaler_state_dict"] is not None and self.device.type == "cuda":
            self.scaler.load_state_dict(checkpoint["scaler_state_dict"])
        
        self.epochs_without_improvement = checkpoint.get("epochs_without_improvement", 0)
        
        epoch = checkpoint["epoch"]
        self.logger.info(f"Checkpoint chargé: epoch {epoch}")
        
        return epoch+1
    
    def load_latest_checkpoint(self, version_path):
        """Charge automatiquement le dernier checkpoint disponible"""
        import glob
        checkpoint_files = glob.glob(str(version_path / "checkpoint_epoch_*.pt"))
        
        if not checkpoint_files:
            self.logger.info("Aucun checkpoint trouvé, démarrage depuis le début")
            return 0
        
        # Trouver le checkpoint avec le numéro d'epoch le plus élevé
        latest_checkpoint = sorted(
            checkpoint_files,
            key=lambda x: int(x.split('_')[-1].split('.')[0])
        )[-1]
        
        self.logger.info(f"Chargement du checkpoint: {latest_checkpoint}")
        return self.load_checkpoint(latest_checkpoint)
    
    @staticmethod
    def find_checkpoints(version_path):
        """Trouve tous les checkpoints disponibles dans un dossier version"""
        checkpoints = []
        
        for file in glob.glob(str(version_path / "checkpoint_epoch_*.pt")):
            epoch_num = int(file.split('_')[-1].split('.')[0])
            checkpoints.append({
                'path': file,
                'epoch': epoch_num,
                'size': os.path.getsize(file) / (1024 * 1024)  # Taille en MB
            })
        
        return sorted(checkpoints, key=lambda x: x['epoch'])    
    
    def fit(
        self,
        resume_from=None
    ):
    
        best_epoch = None
        history = []
    
        version_manager = VersionManager()
    
        # --------------------------------------------------
        # Nouveau training ou reprise
        # --------------------------------------------------
    
        if resume_from is not None:
    
            version_path = resume_from.parent
    
            version_name = version_path.name
    
            start_epoch = self.load_checkpoint(
                resume_from
            )
    
            print(
                f"Reprise de {version_name}"
            )
    
        else:
    
            version_name, version_path = (
                version_manager.create_version_folder()
            )
    
            start_epoch = 0
    
            print(
                f"Nouvelle version : {version_name}"
            )
    
        print(version_path.resolve())
    
        writer = SummaryWriter(
            log_dir=version_path / "tensorboard"
        )
    
        # --------------------------------------------------
        # Sauvegarde métadonnées initiales
        # --------------------------------------------------
    
        version_manager.save_metadata(
            version_path,
            {
                "version": version_name,
                "date": datetime.now().isoformat(),
                "epochs_requested": N_EPOCHS,
                "start_epoch": start_epoch,
                "learning_rate": LEARNING_RATE,
                "batch_size": BATCH_SIZE,
                "aug2_ratio": AUG2_ratio,
                "gradient_clipping": GRADIENT_CLIPPING
            }
        )
        
        version_manager.save_split(
            version_path,
            TRAIN_SPLIT,
            VAL_SPLIT
        )
    
        phase2_epoch = int(
            AUG2_ratio * N_EPOCHS
        )
    
        # --------------------------------------------------
        # Boucle d'entraînement
        # --------------------------------------------------
    
        for epoch in range(
            start_epoch,
            N_EPOCHS
        ):
    
            if epoch < phase2_epoch:
    
                self.train_loader.dataset.set_transform(
                    get_phase1_transform
                )
    
            else:
    
                self.train_loader.dataset.set_transform(
                    get_phase2_transform
                )
    
            if epoch == phase2_epoch:
    
                print(
                    "\n===== Passage aux augmentations Phase 2 =====\n"
                )
    
            train_loss = self.train_epoch()
    
            val_loss = self.validate()
    
            self.scheduler.step(
                val_loss
            )
    
            current_lr = (
                self.optimizer.param_groups[0]["lr"]
            )
    
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
                f" | LR={current_lr:.2e}"
                f" | Train batches={len(self.train_loader)}"
                f" | Val batches={len(self.val_loader)}"
            )
    
            print(message)
    
            self.logger.info(message)
    
            is_best = (
                val_loss < self.best_loss
            )
    
            if is_best:
    
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
    
            # ------------------------------------------
            # Checkpoint à chaque époque
            # ------------------------------------------
    
            self.save_checkpoint(
                epoch,
                version_path,
                is_best=is_best
            )
    
            # ------------------------------------------
            # Historique
            # ------------------------------------------
    
            version_manager.save_history(
                version_path,
                history
            )
    
            # ------------------------------------------
            # Early stopping
            # ------------------------------------------
    
            if (
                self.epochs_without_improvement
                >=
                self.early_stopping_patience
            ):
    
                self.logger.info(
                    "Early stopping"
                )
    
                break
    
        # --------------------------------------------------
        # Sauvegardes finales
        # --------------------------------------------------
    
        version_manager.save_loss_curve(
            version_path,
            history,
            best_epoch
        )
    
        version_manager.save_metadata(
            version_path,
            {
                "version": version_name,
                "date": datetime.now().isoformat(),
                "epochs_requested": N_EPOCHS,
                "epochs_completed": epoch + 1,
                "best_epoch": best_epoch,
                "best_val_loss": self.best_loss,
                "learning_rate": LEARNING_RATE,
                "batch_size": BATCH_SIZE
            }
        )
        

    
        writer.close()
    
        self.logger.info(
            f"Training terminé "
            f"(best epoch = {best_epoch})"
        )
    
        return history