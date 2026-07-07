# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 09:59:03 2026

@author: hugoz
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 09:59:16 2026

@author: hugoz
"""
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QGroupBox,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QProgressBar,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QApplication
)

from PyQt6.QtGui import (
    QAction
    )


from PyQt6.QtCore import Qt

from utils.icons import svg_to_icon

from managers.model_manager import ModelManager

from ai_models.zegg_counter.config import (
    MODEL_PATH,
    PEAK_THRESHOLD,
    PEAK_MIN_DISTANCE
)


import torch
from pathlib import Path

from ai_models.zegg_counter.predictor import Predictor



class UseModelMenu(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Utiliser un modèle"
        )

        self.setWindowIcon(
            svg_to_icon("assets/logo_IA.svg")
        )

        self.model_manager = ModelManager(
            MODEL_PATH
        )

        central = QWidget()

        self.setCentralWidget(
            central
        )

        self.build_ui(
            central
        )

        self.create_toolbar()

        self.load_models()

        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )
        
    def build_ui(
        self,
        parent
    ):
    
        layout = QVBoxLayout(parent)
    
        title = QLabel(
            "Utiliser un modèle"
        )
    
        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
    
        title.setStyleSheet("""
            font-size:42px;
            font-weight:bold;
            color:#11BED5;
        """)
    
        layout.addWidget(title)
    
        layout.addSpacing(30)
    
        #
        # Répertoire modèles
        #
    
        model_path_layout = QHBoxLayout()
    
        self.model_dir_edit = QLineEdit(
            str(
                Path(MODEL_PATH).resolve()
            )
        )
    
        browse_models = QPushButton(
            "Modifier..."
        )
    
        browse_models.clicked.connect(
            self.choose_model_directory
        )
    
        model_path_layout.addWidget(
            QLabel("Répertoire des modèles")
        )
    
        model_path_layout.addWidget(
            self.model_dir_edit
        )
    
        model_path_layout.addWidget(
            browse_models
        )
    
        layout.addLayout(
            model_path_layout
        )
    
        layout.addSpacing(20)
    
        #
        # Choix modèle
        #
    
        model_layout = QHBoxLayout()
    
        self.model_box = QComboBox()
    
        self.model_box.currentTextChanged.connect(
            self.update_model_information
        )
    
        model_layout.addWidget(
            QLabel("Modèle")
        )
    
        model_layout.addWidget(
            self.model_box
        )
    
        layout.addLayout(
            model_layout
        )
    
        layout.addSpacing(20)
    
        # -------------------------
        # Informations modèle
        # -------------------------
        
        infos_group = QGroupBox("Informations du modèle")
        
        infos_group.setStyleSheet("""
            QGroupBox{
                font-size:18px;
                font-weight:bold;
                border:2px solid #D9D9D9;
                border-radius:12px;
                margin-top:12px;
                padding:15px;
                background:white;
            }
        
            QGroupBox::title{
                subcontrol-origin: margin;
                left:15px;
                padding:0 6px;
                color:#11BED5;
            }
        """)
        
        infos = QGridLayout(infos_group)
        
        infos.setHorizontalSpacing(20)
        infos.setVerticalSpacing(12)
        
        self.date_label = QLabel("-")
        self.mae_label = QLabel("-")
        self.mae_std_label = QLabel("-")
        self.rel_mae_label = QLabel("-")
        self.rel_mae_std_label = QLabel("-")
        
        def add_info_row(row, label_text, value_label, tooltip=None):
        
            label = QLabel(label_text)
        
            label.setAlignment(
                Qt.AlignmentFlag.AlignRight
                |
                Qt.AlignmentFlag.AlignVCenter
            )
        
            label.setFixedWidth(220)
        
            label.setStyleSheet("""
                font-size:16px;
                color:#555555;
            """)
        
            if tooltip:
                label.setToolTip(tooltip)
        
            value_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        
            value_label.setFixedWidth(140)
        
            value_label.setStyleSheet("""
                QLabel{
                    font-size:16px;
                    font-weight:bold;
                    color:#222222;
                    background:#F0FBFD;
                    border:1px solid #11BED5;
                    border-radius:6px;
                    padding:4px;
                }
            """)
        
            infos.addWidget(
                label,
                row,
                0
            )
        
            infos.addWidget(
                value_label,
                row,
                1
            )
        
        
        add_info_row(
            0,
            "Date",
            self.date_label
        )
        
        
        add_info_row(
            1,
            "MAE",
            self.mae_label,
            "Écart moyen entre le nombre d'œufs prédit et le nombre réel."
        )
        
        add_info_row(
            2,
            "Écart-type MAE",
            self.mae_std_label
        )
        
        add_info_row(
            3,
            "MAE relative",
            self.rel_mae_label,
            "Erreur moyenne exprimée en pourcentage."
        )
        
        add_info_row(
            4,
            "Écart-type relatif",
            self.rel_mae_std_label
        )
        
        infos.setColumnStretch(0, 0)
        infos.setColumnStretch(1, 0)
        infos.setColumnStretch(2, 1)
        
        layout.addWidget(
            infos_group
        )
    
        layout.addSpacing(30)
    
        # -------------------------
        # Dossier images
        # -------------------------
        
        folder_layout = QHBoxLayout()
        
        self.image_folder = QLineEdit()
        self.image_folder.setReadOnly(True)
        
        choose_folder = QPushButton("Choisir...")
        choose_folder.clicked.connect(self.choose_image_folder)
        
        folder_layout.addWidget(QLabel("Dossier contenant les images"))
        folder_layout.addWidget(self.image_folder)
        folder_layout.addWidget(choose_folder)
        
        layout.addLayout(folder_layout)
        

        layout.addSpacing(10)

        #
        # Paramètres
        #
        # Groupe pour les paramètres avancés
        advanced_group = QGroupBox("Paramètres avancés")
        advanced_group.setCheckable(True)
        advanced_group.setChecked(False)  # Désactivé par défaut
        advanced_group.toggled.connect(
            lambda checked: advanced_group.setTitle(
                "▲ Paramètres avancés" if checked else "▼ Paramètres avancés"
            )
        )

        advanced_layout = QGridLayout(advanced_group)
        
        self.threshold = QDoubleSpinBox()
        self.threshold.setDecimals(2)
        self.threshold.setRange(0, 1)
        self.threshold.setSingleStep(0.01)
        self.threshold.setValue(PEAK_THRESHOLD)
        
        self.min_distance = QSpinBox()
        self.min_distance.setRange(1, 100)
        self.min_distance.setValue(PEAK_MIN_DISTANCE)
        # self.heatmap_box = QCheckBox(
        #     "Sauvegarder les heatmaps"
        # )        
        # self.heatmap_box.setChecked(False)
    

        
        
        advanced_layout.addWidget(QLabel("Seuil de détection des oeufs"), 0, 0)
        advanced_layout.addWidget(self.threshold, 0, 1)
        advanced_layout.addWidget(QLabel("Distance minimale (px) séparant des oeufs"), 1, 0)
        advanced_layout.addWidget(self.min_distance, 1, 1)
        # advanced_layout.addWidget(self.heatmap_box)
        
        layout.addWidget(advanced_group)
                
        layout.addSpacing(40)
    
        self.run_button = QPushButton("Lancer l'analyse")
        self.run_button.clicked.connect(self.run_prediction)
        self.run_button.setMinimumHeight(50)
        self.run_button.setMinimumWidth(300)
        self.run_button.setMaximumWidth(400)
        
        # Centrer le bouton
        layout.addWidget(self.run_button)
        layout.setAlignment(self.run_button, Qt.AlignmentFlag.AlignHCenter)
        
        layout.addSpacing(20)
    
        self.progress = QProgressBar()
    
        layout.addWidget(
            self.progress
        )
    
        self.progress_label = QLabel(
            "0 / 0 image"
        )
    
        self.progress_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
    
        layout.addWidget(
            self.progress_label
        )
    
        layout.addStretch()
        
    def load_models(self):
    
        self.model_box.clear()
    
        for version, text in self.model_manager.list_models_display():
    
            self.model_box.addItem(
                text,
                version
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
        
    def update_model_information(self):
    
        version = self.model_box.currentData()
    
        if version is None:
            return
    
        info = self.model_manager.get_model_info(
            version
        )
    
        self.date_label.setText(
            str(
                info.get(
                    "date",
                    "-"
                )
            )[:10]
        )
    
    
        self.mae_label.setText(
            str(
                info.get(
                    "mae",
                    "-"
                )
            )
        )
    
        rel = info.get(
            "relative_mae",
            None
        )
    
        if rel is None:
    
            self.rel_mae_label.setText("-")
    
        else:
    
            self.rel_mae_label.setText(
                f"{100*rel:.2f} %"
            )
        
        mae_std = info.get(
            "mae_std",
            None
        )
        
        if mae_std is None:
        
            self.mae_std_label.setText("-")
        
        else:
        
            self.mae_std_label.setText(
                f"{mae_std:.2f}"
            )
        
        
        rel_std = info.get(
            "relative_mae_std",
            None
        )
        
        if rel_std is None:
        
            self.rel_mae_std_label.setText("-")
        
        else:
        
            self.rel_mae_std_label.setText(
                f"{100 * rel_std:.2f} %"
            )
    
    
    def choose_model_directory(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir un dossier de modèles"
        )
    
        if folder:
    
            self.model_manager = ModelManager(
                folder
            )
    
            self.model_dir_edit.setText(
                folder
            )
    
            self.load_models()
    
    
    def choose_image_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir les images"
        )
    
        if not folder:
            return
    
        self.image_folder.setText(folder)
        
        
        
    def run_prediction(self):
        self.run_button.setEnabled(False)
        version = self.model_box.currentData()
    
        if version is None:
            return
    
        model_path = self.model_manager.get_model_path(version)
    
        predictor = Predictor(
            model_path=model_path,
            device=torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        )
    
        image_folder = Path(self.image_folder.text())
        
        output_folder = image_folder / "labels"
        
        nb = predictor.predict_folder(
        
            image_folder=image_folder,
        
            output_folder=output_folder,
        
            threshold=self.threshold.value(),
        
            min_distance=self.min_distance.value(),
        
            progress_callback=self.update_progress
        )
    
        self.progress.setMaximum(nb)
        self.progress.setValue(nb)
    
        self.progress_label.setText(
            f"{nb} / {nb} images"
        )
        
        QMessageBox.information(
            self,
            "Analyse terminée",
            f"{nb} image(s) traitée(s).\n\nLes fichiers CSV ont été enregistrés."
        )
        self.run_button.setEnabled(True)
        
    
    def update_progress(self, current, total):
    
        self.progress.setMaximum(total)
        self.progress.setValue(current)
    
        self.progress_label.setText(
            f"{current} / {total} images traitées"
        )
    
        QApplication.processEvents()
        
    def get_results_dir(self):
        return Path(self.image_folder.text())