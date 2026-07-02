# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 12:41:08 2026

@author: hugoz
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel
)

from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QAction
)

from PyQt6.QtCore import (
    Qt,
    QSize
)

from PyQt6.QtSvg import (
    QSvgRenderer
)

# Make sure this is correctly imported from your project
from ui.home_card import HomeCard



# Only define svg_to_icon once
def svg_to_icon(
    path,
    size=QSize(1024, 1024)
):
    renderer = QSvgRenderer(path)

    pixmap = QPixmap(size)

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(pixmap)

    renderer.render(painter)

    painter.end()

    return QIcon(pixmap)


class AIMenu(QMainWindow):  # Changed from QWidget to QMainWindow

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Zannote IA"
        )

        icon = svg_to_icon(
            "assets/logo_IA.svg"
        )

        self.setWindowIcon(icon)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.build_ui(central_widget)

        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )
        
        self.create_toolbar()


    def build_ui(self, parent_widget):
        main_layout = QVBoxLayout(parent_widget)

        title = QLabel(
            "Zannote IA"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet("""
            font-size:48px;
            font-weight:bold;
            color:#11BED5;
        """)

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(
            120
        )

        train_card = HomeCard(
            title="Entraîner",
            color="#11BED5",
            description="Créer un\nnouveau modèle",
            icon_path="assets/logo_IA.svg",
            callback=self.train_model
        )

        infer_card = HomeCard(
            title="Utiliser",
            color="#11BED5",
            description="Prédire\navec un modèle",
            icon_path="assets/logo_IA.svg",
            callback=self.use_model
        )

        cards_layout.addStretch()

        cards_layout.addWidget(
            train_card
        )

        cards_layout.addWidget(
            infer_card
        )

        cards_layout.addStretch()

        main_layout.addStretch()

        main_layout.addWidget(
            title
        )

        main_layout.addSpacing(
            50
        )

        main_layout.addLayout(
            cards_layout
        )

        main_layout.addStretch()

        self.setStyleSheet("""
            QWidget{
                background:#F5F5F5;
            }
        """)

    def create_toolbar(self):
        toolbar = self.addToolBar(
            "Main"
        )
        
        home_action = QAction(
            svg_to_icon("assets/home.svg"),
            "",
            self
        )
        
        home_action.setToolTip(
            "Retour au menu principal"
        )
        
        home_action.triggered.connect(
            self.return_home
        )
        
        toolbar.addAction(
            home_action
        )

    
    def return_home(self):
        from ui.home_page import HomePage
        self.home = HomePage()
        self.home.show()
        self.close()

        
    def train_model(self):
        from ui.train_model_menu import TrainModelMenu
        self.TrainWindow = TrainModelMenu()
        self.TrainWindow.show()
        self.close()

    def use_model(self):
        from ui.use_model_menu import UseModelMenu
        self.UseWindow = UseModelMenu()
        self.UseWindow.show()
        self.close()
