# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:13:48 2026

@author: hugoz
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QSize, Qt
from ui.main_window import MainWindow


def svg_to_icon(path, size=QSize(1024, 1024)):
    renderer = QSvgRenderer(path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    from PyQt6.QtGui import QPainter
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


    
def main():
    app = QApplication(sys.argv)

    icon = svg_to_icon("assets/logo.svg")
    app.setWindowIcon(icon)
    window = MainWindow()
    window.setWindowIcon(icon)
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()