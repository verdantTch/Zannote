# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:17:35 2026

@author: hugoz
"""

import os


class ImageManager:

    EXTENSIONS = (
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff"
    )

    def __init__(self):

        self.folder = None
        self.images = []
        self.current_index = 0

    def contains_images(self, folder):
    
        extensions = (
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tif",
            ".tiff"
        )
    
        for file in os.listdir(folder):
    
            if file.lower().endswith(extensions):
                return True
    
        return False
    
    def load_folder(
        self,
        folder
    ):

        self.folder = folder

        self.images = sorted([
            os.path.join(folder, f)

            for f in os.listdir(folder)

            if f.lower().endswith(
                self.EXTENSIONS
            )
        ])

        self.current_index = 0

    def current_image(self):

        if not self.images:
            return None

        return self.images[
            self.current_index
        ]

    def next_image(self):

        if (
            self.current_index
            < len(self.images)-1
        ):
            self.current_index += 1

    def previous_image(self):

        if self.current_index > 0:
            self.current_index -= 1