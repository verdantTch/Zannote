# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QAction

from utils.icons import svg_to_icon


class TrainModelMenu(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Entraîner un modèle"
        )

        self.setWindowIcon(
            svg_to_icon("assets/logo_IA.svg")
        )

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout = QVBoxLayout(
            central
        )

        layout.addStretch()

        title = QLabel(
            "🚧 Cette page n'existe pas encore :)"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet("""
            font-size:42px;
            font-weight:bold;
            color:#11BED5;
        """)

        subtitle = QLabel(
            "L'entraînement des modèles sera disponible\n"
            "dans une prochaine version."
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle.setStyleSheet("""
            font-size:22px;
            color:#666666;
        """)

        layout.addWidget(title)

        layout.addSpacing(25)

        layout.addWidget(subtitle)

        layout.addStretch()

        self.create_toolbar()

        self.setStyleSheet("""
            QWidget{
                background:#F5F5F5;
            }
        """)

        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )


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
            self.return_menu
        )

        toolbar.addAction(
            home_action
        )


    def return_menu(self):

        from ui.home_page import HomePage

        self.close()

        self.menu = HomePage()

        self.menu.show()