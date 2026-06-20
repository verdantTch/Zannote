# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:17:54 2026

@author: hugoz
"""

from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsLineItem
)

from PyQt6.QtGui import (
    QColor,
    QPen,
    QBrush
)

class AnnotationItem(QGraphicsItemGroup):

    def __init__(self, x, y):

        super().__init__()

        size = 10

        pen = QPen(
            QColor(255,0, 0),  # rouge
            5
        )

        line1 = QGraphicsLineItem(
            x - size,
            y,
            x + size,
            y
        )
        
        line2 = QGraphicsLineItem(
            x,
            y - size,
            x,
            y + size
        )
        
        line1.setPen(pen)
        line2.setPen(pen)

        self.addToGroup(line1)
        self.addToGroup(line2)



