# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:04:47 2026

@author: hugoz
"""
# -*- coding: utf-8 -*-'

import torch
import torch.nn as nn
from config import BCE_WEIGHT, DICE_WEIGHT

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
        bce_weight=BCE_WEIGHT,
        dice_weight=DICE_WEIGHT
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
            dropout=0.05
        )

        self.pool4 = nn.MaxPool2d(
            2
        )

        # Goulot d'étranglement
        # Dropout le plus fort : c'est la couche la plus profonde du réseau
        self.bottleneck = DoubleConv(
            256,
            512,
            dropout=0.1
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
            dropout=0.05
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
        
        return self.final(d1)