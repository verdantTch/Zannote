# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:04:38 2026

@author: hugoz
"""

import albumentations as A
from config import BORDER_MODE


# Première phase d'entrainement  == petites variations dans l'image
def get_phase1_transform(border_color="black"): # Per défaut on remplit en noir 

    return A.Compose(
        [
            A.HorizontalFlip(p=0.5),
        
            A.VerticalFlip(p=0.5),
        
            A.ShiftScaleRotate(
                shift_limit=0.05,
                scale_limit=0.2,
                rotate_limit=40,
                border_mode=BORDER_MODE,
                fill=border_color,
                p=0.5
            ),
            
            A.Defocus(
                radius=(2,4),          # Large defocus radius
                alias_blur=(0.4, 0.6),   # Strong aliasing
                p=0.5
             ),
        
            A.ColorJitter(
                brightness=0.3,
                contrast=0.2,
                saturation=0.1,
                hue=0.05,
                p=0.5
            )
        ],

        keypoint_params=A.KeypointParams(
            format="xy",
            remove_invisible=True
        )
    )

# Seconde phase d'entrainement  == plus grandes variations dans l'image
def get_phase2_transform(border_color="black"): # Per défaut on remplit en noir 

    return A.Compose(
        [
            A.HorizontalFlip(p=0.5),
        
            A.VerticalFlip(p=0.5),
        
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.25,
                rotate_limit=50,
                border_mode=BORDER_MODE,
                fill=border_color,
                p=0.7
            ),
            
            A.Defocus(
                radius=(2,8),          
                alias_blur=(0.4, 0.6),   
                p=0.5
             ),
        
            A.ColorJitter(
                brightness=0.3,
                contrast=0.3,
                saturation=0.3,
                hue=0.1,
                p=0.7
            )
        ],

        keypoint_params=A.KeypointParams(
            format="xy",
            remove_invisible=True
        )
    )