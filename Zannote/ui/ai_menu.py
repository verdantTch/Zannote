# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 12:41:08 2026

@author: hugoz
"""

from PyQt6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QLabel
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvg import QSvgRenderer


def svg_to_icon(path, size=QSize(1024, 1024)):
    renderer = QSvgRenderer(path)

    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


class AIMenu(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zannote IA")
        
        # Icone
        icon = svg_to_icon("assets/logo_IA.svg")
        self.setWindowIcon(icon)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Zannote IA"))

        train_btn = QPushButton("Entraîner un modèle")
        infer_btn = QPushButton("Utiliser un modèle")

        layout.addWidget(train_btn)
        layout.addWidget(infer_btn)
        
        # Grand écran
        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )
