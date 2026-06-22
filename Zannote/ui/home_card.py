# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)

from PyQt6.QtCore import (
    Qt,
    QSize
)

from utils.icons import svg_to_icon


class HomeCard(QWidget):

    def __init__(
        self,
        title,
        color,
        description,
        icon_path,
        callback
    ):
        super().__init__()

        self.setFixedSize(
            550,
            650
        )

        layout = QVBoxLayout(self)

        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.setSpacing(20)

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {color};
        """)

        button = QPushButton()

        button.setFixedSize(
            450,
            450
        )

        button.setIcon(
            svg_to_icon(icon_path)
        )

        button.setIconSize(
            QSize(400,400)
        )

        button.clicked.connect(callback)

        button.setStyleSheet(f"""
            QPushButton{{
                background:white;
                border:2px solid #D9D9D9;
                border-radius:25px;
            }}
        
            QPushButton:hover{{
                border:4px solid {color};
                background:{color};
            }}
        
            QPushButton:pressed{{
                border:4px solid {color};
                background:#F0F0F0;
            }}
        """)

        description_label = QLabel(description)

        description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        description_label.setStyleSheet("""
            font-size:28px;
            color:#555555;
        """)

        layout.addStretch()

        layout.addWidget(title_label)

        layout.addWidget(
            button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            description_label
        )

        layout.addStretch()
