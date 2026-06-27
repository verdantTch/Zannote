# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:03:17 2026

@author: hugoz
"""
# -*- coding: utf-8 -*-

from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch

from torch.utils.data import Dataset

from heatmap import generate_heatmap

from config import TARGET_H, TARGET_W, BORDER_MODE, SIGMA


class EggDataset(Dataset):
    
    def __init__(
        self,
        image_dir,
        label_dir,
        split_file=None,
        transform=None,
        sigma=SIGMA
    ):

        self.image_dir = Path(image_dir)
        self.label_dir = Path(label_dir)

        self.transform = transform
        self.sigma = sigma

        self.images = sorted(
            [
                p
                for p in self.image_dir.iterdir()
                if p.suffix.lower() in (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".bmp",
                    ".tif",
                    ".tiff"
                )
            ]
        )

        if split_file is not None:
        
            with open(
                split_file,
                "r",
                encoding="utf-8"
            ) as f:
        
                allowed_images = {
                    line.strip()
                    for line in f
                    if line.strip()
                }
        
            self.images = [
                p
                for p in self.images
                if p.name in allowed_images
            ]
        print(f"{len(self.images)} images chargées")
        
        
    def __len__(self):

        return len(self.images)

    def resize_and_pad(self, image):

        h, w = image.shape[:2]

        scale = min(
            TARGET_W / w,
            TARGET_H / h
        )

        new_w = int(w * scale)
        new_h = int(h * scale)

        image = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA
        )

        pad_w = TARGET_W - new_w
        pad_h = TARGET_H - new_h

        left = pad_w // 2
        right = pad_w - left

        top = pad_h // 2
        bottom = pad_h - top

        image = cv2.copyMakeBorder(
            image,
            top,
            bottom,
            left,
            right,
            borderType=BORDER_MODE
        )

        return image, scale, left, top

    def _load_keypoints(
        self,
        image_name
    ):

        csv_path = self.label_dir / f"{image_name}.csv"

        if not csv_path.exists():
            return []

        df = pd.read_csv(csv_path)

        return list(
            zip(
                df["x"],
                df["y"]
            )
        )

    @staticmethod
    def estimate_background(image):

        border = np.concatenate([
            image[0, :],
            image[-1, :],
            image[:, 0],
            image[:, -1]
        ])

        return int(np.median(border))
    
    def __getitem__(
        self,
        idx
    ):
    
        image_path = self.images[idx]
    
        image_name = image_path.stem
    
        # -------------------------
        # Lecture image
        # -------------------------
    
        image = cv2.imread(str(image_path))
    
        if image is None:
            raise ValueError(
                f"Impossible de lire l'image : {image_path}"
            )
    
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )
    
        # -------------------------
        # Resize + padding
        # -------------------------
    
        image, scale, left, top = self.resize_and_pad(
            image
        )
    
        # -------------------------
        # Chargement annotations
        # -------------------------
    
        keypoints = self._load_keypoints(
            image_name
        )
    
        # Correction des coordonnées
        keypoints = [
            (
                x * scale + left,
                y * scale + top
            )
            for x, y in keypoints
        ]
    
        # -------------------------
        # Albumentations
        # -------------------------
    
        if self.transform:
    
            background = self.estimate_background(
                image
            )
    
            transform = self.transform(
                background
            )
    
            transformed = transform(
                image=image,
                keypoints=keypoints
            )
    
            image = transformed["image"]
    
            keypoints = transformed["keypoints"]
    
        # -------------------------
        # Heatmap
        # -------------------------
    
        heatmap = generate_heatmap(
    
            keypoints,
    
            TARGET_H,
    
            TARGET_W,
    
            sigma=self.sigma
    
        )
    
        # -------------------------
        # Tensor image
        # -------------------------
    
        image = (
            torch.tensor(
                image,
                dtype=torch.float32
            )
            .permute(
                2,
                0,
                1
            )
            / 255.0
        )
    
        # -------------------------
        # Tensor heatmap
        # -------------------------
    
        heatmap = (
            torch.tensor(
                heatmap,
                dtype=torch.float32
            )
            .unsqueeze(0)
        )
    
        return {
    
            "image": image,
    
            "heatmap": heatmap,
    
            "keypoints": keypoints,
    
            "image_name": image_name
    
        }