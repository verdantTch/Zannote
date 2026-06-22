from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog
)


from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import QSize, Qt


from ui.annotation_window import AnnotationWindow
from ui.ai_menu import AIMenu

from ui.home_card import HomeCard
from utils.icons import svg_to_icon



class HomePage(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Zannote"
        )

        icon = svg_to_icon("assets/logo.svg")
        self.setWindowIcon(icon)  # fenêtre + barre des tâches


        self.build_ui()
        
        # Grand écran
        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(120)

        annotation_card = HomeCard(
            title="Zannote",
            color = "#FF0000",
            description="Annotation manuelle\net vérification",
            icon_path="assets/logo.svg",
            callback=self.open_annotation
        )

        ai_card = HomeCard(
            title="Zannote IA",
            color = "#11BED5",
            description="Comptage IA\n",
            icon_path="assets/logo_IA.svg",
            callback=self.open_ai_menu
        )

        cards_layout.addStretch()

        cards_layout.addWidget(
            annotation_card
        )

        cards_layout.addWidget(
            ai_card
        )

        cards_layout.addStretch()

        main_layout.addStretch()

        main_layout.addLayout(cards_layout)

        main_layout.addStretch()

        self.setStyleSheet("""
            QWidget{
                background:#F5F5F5;
            }
        """)
        
    def open_annotation(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir dossier images"
        )

        if not folder:
            return

        self.annotation_window = AnnotationWindow()

        self.annotation_window.load_folder(
            folder
        )

        self.annotation_window.show()

        self.close()
        
    def open_ai_menu(self):

        self.ai_menu = AIMenu()

        self.ai_menu.show()

        self.close()