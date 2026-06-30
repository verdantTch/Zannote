 # -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 10:04:47 2026

@author: hugoz
"""
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn

class DoubleConv(
    nn.Module
):

    def __init__(
        self,
        in_channels,
        out_channels
    ):

        super().__init__()

        self.conv = nn.Sequential(

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
        )

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
        
        # Goulot d'étranglement
        self.bottleneck = DoubleConv(
            128,
            256
        )
        
        #  Décodeur
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
        
        b = self.bottleneck(p3)
        

        d3 = self.up3(b)


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
        