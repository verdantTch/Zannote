# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:18:21 2026

@author: hugoz
"""
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence



class ImageView(QGraphicsView):
    def __init__(self):

        super().__init__()
        
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.zoom_factor = 1.15


        
    def wheelEvent(self, event):
    
        factor = self.zoom_factor
    
        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1/factor, 1/factor)
    
        event.accept()
    
        # Rafraîchir l'affichage du zoom
        window = self.window()
    
        if hasattr(window, "update_status"):
            window.update_status()