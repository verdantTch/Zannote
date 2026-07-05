# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 16:49:15 2026

@author: hugoz
"""

import torch
import cv2

# Mettre des . en fonction du niveau de la racine
from .model import EggUNet
from .Redim_image import resize_and_pad
from .post_processing import detect_peaks
from .post_processing import restore_points
from .prediction_export import save_zannote_csv, summary_row, save_summary

from pathlib import Path



class Predictor:

    def __init__(
        self,
        model_path,
        device
    ):

        self.device = device
        self.model = EggUNet()
        self.model.load_state_dict(
            torch.load(
                model_path,
                map_location=device
            )
        )

        self.model.to(device)

        self.model.eval()
        
    def preprocess(
        self,
        image_path
    ):
    
        image = cv2.imread(
            str(image_path)
        )
        
        # Afficher une erreur si l'image n'est pas lue 
        if image is None:
            raise FileNotFoundError(image_path)
            
        height, width = image.shape[:2]
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )
    
        image, scale, left, top = (
            resize_and_pad(image)
        )
    
        image = (
            torch.tensor(
                image,
                dtype=torch.float32
            )
            .permute(2, 0, 1)
            / 255.0
        )
    
        image = image.unsqueeze(0)
    
        return (
            image.to(self.device),
            scale,
            left,
            top,
            width,
            height
        )
    

    def predict_folder(
        self,
        image_folder,
        output_folder,
        threshold=0.5,
        min_distance=8,
        progress_callback=None
    ):
    
        image_folder = Path(image_folder)
        output_folder = Path(output_folder)
    
        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )
    
        images = []
        summary = []
    
        for ext in (
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.bmp",
            "*.tif",
            "*.tiff"
        ):
            images.extend(image_folder.glob(ext))
        images = sorted(images)
        
        for i, image in enumerate(images):
        
            points = self.predict_points(
                image,
                threshold,
                min_distance
            )
        
            save_zannote_csv(
                image,
                points,
                output_folder
            )
            
            summary.append(
                summary_row(
                    image.stem,
                    points
                )
            )
        
            if progress_callback is not None:
                progress_callback(i + 1, len(images))
        
        save_summary(
            summary,
            image_folder
        )
    
        return len(images)


        
    def predict_points(
        self,
        image_path,
        threshold=0.5,
        min_distance=8
    ):
    
        (
            heatmap,
            scale,
            left,
            top,
            width,
            height,
            predicted_count_head
        ) = self.predict_heatmap(image_path)
    
        points = detect_peaks(
            heatmap,
            threshold,
            min_distance
        )
    
        points = restore_points(
            points,
            scale,
            left,
            top,
            width,
            height
        )
    
        return points

    def predict_heatmap(
        self,
        image_path
    ):
    
        image, scale, left, top, width, height = self.preprocess(image_path)
    
        with torch.no_grad():
    
            output, predicted_count = self.model(
                image
            )
    
            heatmap = torch.sigmoid(
                output
            )
    
        return (
            heatmap.cpu().numpy()[0,0],
            scale,
            left,
            top,
            width,
            height,
            float(predicted_count.cpu().item())
        )