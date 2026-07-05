# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:04:47 2026

@author: hugoz
"""
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """
    Dice loss adaptée à une sortie de type heatmap (valeurs continues entre 0 et 1).
    Complète bien BCEWithLogitsLoss car elle est directement sensible au
    recouvrement (overlap) entre la heatmap prédite et la heatmap cible,
    ce qui aide notamment quand les "points" à détecter sont petits et peu
    nombreux par rapport au fond de l'image (fort déséquilibre de classes).
    """

    def __init__(
        self,
        smooth=1.0
    ):

        super().__init__()
        self.smooth = smooth

    def forward(
        self,
        logits,
        targets
    ):

        probs = torch.sigmoid(logits)

        probs = probs.reshape(probs.size(0), -1)
        targets = targets.reshape(targets.size(0), -1)

        intersection = (probs * targets).sum(dim=1)

        dice_score = (2.0 * intersection + self.smooth) / (
            probs.sum(dim=1) + targets.sum(dim=1) + self.smooth
        )

        return 1.0 - dice_score.mean()


class BCEDiceLoss(nn.Module):
    """
    Combine BCEWithLogitsLoss (stable pour l'optimisation pixel par pixel)
    et DiceLoss (sensible au recouvrement global de la zone d'intérêt).
    bce_weight / dice_weight permettent de doser l'influence de chacune.
    """

    def __init__(
        self,
        bce_weight=0.45,
        dice_weight=0.55
    ):

        super().__init__()

        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()

        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

    def forward(
        self,
        logits,
        targets
    ):

        bce_loss = self.bce(logits, targets)
        dice_loss = self.dice(logits, targets)

        return (
            self.bce_weight * bce_loss
            + self.dice_weight * dice_loss
        )


class CountLoss(nn.Module):
    """
    Loss pour la branche de comptage dédiée (pas pour la heatmap).

    On utilise une L1 RELATIVE plutôt qu'une L1 brute :
    - Ça correspond exactement à la métrique relative_mae utilisée pour
      évaluer/sélectionner le meilleur modèle -> on optimise directement
      ce qu'on cherche à améliorer.
    - Ça reste dans une échelle bornée (~0-1 en général), comparable à
      BCE/Dice, sans avoir besoin d'un poids ajusté à la magnitude des
      comptes (contrairement à une L1 brute où l'erreur peut valoir
      plusieurs dizaines/centaines selon vos images).
    - eps évite la division par zéro sur les images sans œuf (true_count=0),
      cohérent avec ce qu'on avait discuté pour evaluate.py.
    """

    def __init__(
        self,
        eps=1.0
    ):

        super().__init__()
        self.eps = eps

    def forward(
        self,
        predicted_counts,
        true_counts
    ):

        true_counts = true_counts.float()

        relative_error = (
            torch.abs(predicted_counts - true_counts)
            / (true_counts + self.eps)
        )

        return relative_error.mean()


class BCEDiceCountLoss(nn.Module):
    """
    Loss combinée finale utilisée pour l'entraînement :
    - BCE + Dice (forme/recouvrement de la heatmap, pixel par pixel)
    - Count loss (comptage direct, via la branche de comptage dédiée
      d'EggUNet, PAS via la somme de la heatmap)
    """

    def __init__(
        self,
        bce_weight=0.4,
        dice_weight=0.6,
        count_weight=0.3
    ):

        super().__init__()

        self.bce_dice = BCEDiceLoss(
            bce_weight=bce_weight,
            dice_weight=dice_weight
        )

        self.count = CountLoss()

        self.count_weight = count_weight

    def forward(
        self,
        heatmap_logits,
        predicted_counts,
        targets,
        true_counts
    ):

        bce_dice_loss = self.bce_dice(heatmap_logits, targets)

        count_loss = self.count(predicted_counts, true_counts)

        return (
            bce_dice_loss
            + self.count_weight * count_loss
        )


class DoubleConv(
    nn.Module
):

    def __init__(
        self,
        in_channels,
        out_channels,
        dropout=0.0
    ):

        super().__init__()

        layers = [

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(
                inplace=True
            ),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(
                out_channels
            ),

            nn.ReLU(
                inplace=True
            )
        ]

        # Dropout uniquement si demandé (réservé aux couches profondes)
        if dropout > 0:
            layers.append(
                nn.Dropout2d(
                    p=dropout
                )
            )

        self.conv = nn.Sequential(*layers)

    def forward(
        self,
        x
    ):

        return self.conv(x)


class EggUNet(
    nn.Module
):

    def __init__(self):

        super().__init__()
        
        # Encodeur
        self.enc1 = DoubleConv(
            3,
            32
        )
        
        self.pool1 = nn.MaxPool2d(
            2
        )
        
        self.enc2 = DoubleConv(
            32,
            64
        )
        
        self.pool2 = nn.MaxPool2d(
            2
        )
        
        self.enc3 = DoubleConv(
            64,
            128
        )
        
        self.pool3 = nn.MaxPool2d(
            2
        )

        # --- Niveau de profondeur supplémentaire (NOUVEAU) ---
        # Dropout léger : on entre dans les couches "profondes"
        self.enc4 = DoubleConv(
            128,
            256,
            dropout=0.1
        )

        self.pool4 = nn.MaxPool2d(
            2
        )

        # Goulot d'étranglement
        # Dropout le plus fort : c'est la couche la plus profonde du réseau
        self.bottleneck = DoubleConv(
            256,
            512,
            dropout=0.15
        )

        # --- Branche de comptage dédiée (NOUVEAU) ---
        # Le bottleneck contient l'information globale/contextuelle de
        # l'image (peu importe la position précise des œufs). On exploite
        # ça directement pour prédire le compte, sans dépendre de la
        # heatmap ni de sa somme (qui n'est pas un vrai proxy du compte :
        # gaussiennes non normalisées à sigma=15, combinées par np.maximum
        # et non par addition -> la somme dépend de la densité spatiale,
        # pas seulement du nombre d'œufs).
        self.count_head = nn.Sequential(

            nn.AdaptiveAvgPool2d(1),   # (B, 512, H, W) -> (B, 512, 1, 1)

            nn.Flatten(),               # (B, 512)

            nn.Linear(512, 128),

            nn.ReLU(inplace=True),

            nn.Dropout(0.2),

            nn.Linear(128, 1)
        )
        
        #  Décodeur
        self.up4 = nn.ConvTranspose2d(
            512,
            256,
            kernel_size=2,
            stride=2
        )

        self.dec4 = DoubleConv(
            512,
            256,
            dropout=0.1
        )

        self.up3 = nn.ConvTranspose2d(
            256,
            128,
            kernel_size=2,
            stride=2
        )
        
        self.dec3 = DoubleConv(
            256,
            128
        )
        
        self.up2 = nn.ConvTranspose2d(
            128,
            64,
            kernel_size=2,
            stride=2
        )
        
        self.dec2 = DoubleConv(
            128,
            64
        )
        
        self.up1 = nn.ConvTranspose2d(
            64,
            32,
            kernel_size=2,
            stride=2
        )

        self.dec1 = DoubleConv(
            64,
            32
        )
        
        # Sortie
        self.final = nn.Conv2d(
            32,
            1,
            kernel_size=1
        )
        
    def forward(
        self,
        x
    ):
        e1 = self.enc1(x)

        p1 = self.pool1(e1)
        
        e2 = self.enc2(p1)
        
        p2 = self.pool2(e2)
        
        e3 = self.enc3(p2)
        
        p3 = self.pool3(e3)

        e4 = self.enc4(p3)

        p4 = self.pool4(e4)
        
        b = self.bottleneck(p4)

        # Branche de comptage : lit directement le bottleneck, en
        # parallèle du décodeur. squeeze(1) : (B, 1) -> (B,)
        predicted_count = self.count_head(b).squeeze(1)

        d4 = self.up4(b)

        d4 = torch.cat(
            [d4, e4],
            dim=1
        )

        d4 = self.dec4(d4)

        d3 = self.up3(d4)


        d3 = torch.cat(
            [d3, e3],
            dim=1
        )

        d3 = self.dec3(d3)
        
        d2 = self.up2(d3)

        d2 = torch.cat(
            [d2, e2],
            dim=1
        )
        
        d2 = self.dec2(d2)
        
        d1 = self.up1(d2)

        d1 = torch.cat(
            [d1, e1],
            dim=1
        )
        
        d1 = self.dec1(d1)

        heatmap = self.final(d1)

        return heatmap, predicted_count