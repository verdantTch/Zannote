# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 16:49:15 2026

@author: hugoz
"""

import torch
import cv2

from model import EggUNet
from Redim_image import resize_and_pad

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
            top
        )
    
    def predict_heatmap(
        self,
        image_path
    ):
    
        image, scale, left, top = (
            self.preprocess(
                image_path
            )
        )
    
        with torch.no_grad():
    
            output = self.model(
                image
            )
    
            heatmap = torch.sigmoid(
                output
            )
    
        return (
            heatmap.cpu().numpy()[0, 0],
            scale,
            left,
            top
        )