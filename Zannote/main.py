# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:13:48 2026

@author: hugoz
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.home_page import HomePage

from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QSize, Qt    

app = QApplication(sys.argv)
w = HomePage()
w.show()
sys.exit(app.exec())






