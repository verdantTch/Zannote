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
    
        #
        # Informations
        #
    
        infos = QGridLayout()
    
        self.date_label = QLabel("-")
        self.epoch_label = QLabel("-")
        self.loss_label = QLabel("-")
        self.mae_label = QLabel("-")
        self.rel_mae_label = QLabel("-")
    
        infos.addWidget(
            QLabel("Date"),
            0,
            0
        )
    
        infos.addWidget(
            self.date_label,
            0,
            1
        )
    
        infos.addWidget(
            QLabel("Epoch optimal"),
            1,
            0
        )
    
        infos.addWidget(
            self.epoch_label,
            1,
            1
        )
    
        infos.addWidget(
            QLabel("Validation loss"),
            2,
            0
        )
    
        infos.addWidget(
            self.loss_label,
            2,
            1
        )
    
        infos.addWidget(
            QLabel("MAE"),
            3,
            0
        )
    
        infos.addWidget(
            self.mae_label,
            3,
            1
        )
    
        infos.addWidget(
            QLabel("Erreur relative"),
            4,
            0
        )
    
        infos.addWidget(
            self.rel_mae_label,
            4,
            1
        )
    
        layout.addLayout(
            infos
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
    
        self.run_button = QPushButton(
            "Lancer l'analyse"
        )
        
        self.run_button.clicked.connect(
            self.run_prediction
        )
    
        self.run_button.setMinimumHeight(
            50
        )
    
        layout.addWidget(
            self.run_button
        )
    
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
    
        self.epoch_label.setText(
            str(
                info.get(
                    "epoch",
                    "-"
                )
            )
        )
    
        self.loss_label.setText(
            str(
                info.get(
                    "best_val_loss",
                    "-"
                )
            )
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
        
        output_folder = image_folder / "Labels"
        
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