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
    QApplication,
    QScrollArea,
    QToolButton
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
    
        outer_layout = QHBoxLayout(parent)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        scroll_content = QWidget()
        
        center_layout = QHBoxLayout(scroll_content)
        center_layout.addStretch()
        
        content = QWidget()
        content.setMinimumWidth(900)

        content.setMaximumWidth(2000)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(18)
        
        center_layout.addWidget(content)
        center_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        
        outer_layout.addWidget(scroll)  
                
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
    
        layout.addSpacing(25)
    
        #
        # Répertoire modèles
        #
    
        model_path_layout = QHBoxLayout()
    
        # Après avoir créé le QLineEdit du répertoire des modèles
        self.model_dir_edit = QLineEdit(
            str(
                Path(MODEL_PATH).resolve()
            )
        )
        
        # Récupérer la largeur du QLineEdit
        model_dir_width = self.model_dir_edit.width()
        
        # Puis définir la même largeur pour le QComboBox
        self.model_box = QComboBox()
        self.model_box.setMinimumWidth(model_dir_width)
    
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
                font-size:20px;
                font-weight:bold;
                border:2px solid #D9D9D9;
                border-radius:16px;
                margin-top:14px;
                padding:18px;
                background:white;
            }
        
            QGroupBox::title{
                subcontrol-origin: margin;
                left:18px;
                padding:0 8px;
                color:#11BED5;
            }
        """)
        
        infos_main_layout = QVBoxLayout(infos_group)
        self.date_label = QLabel("-")
        self.median_error_label = QLabel("-")
        self.median_relative_error_label = QLabel("-")
        self.mae_label = QLabel("-")
        self.mae_std_label = QLabel("-")
        
        
        parent.setStyleSheet("""
                             
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow{
                image:none;
                width:0px;
                height:0px;
                border-left:5px solid transparent;
                border-right:5px solid transparent;
                border-bottom:7px solid #11BED5;
            }
            
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow{
                image:none;
                width:0px;
                height:0px;
                border-left:5px solid transparent;
                border-right:5px solid transparent;
                border-top:7px solid #11BED5;
            }
            
            QSpinBox::up-button, QDoubleSpinBox::up-button{
                subcontrol-origin:border;
                subcontrol-position:top right;
                width:22px;
                border-left:1px solid #D0D0D0;
                border-bottom:1px solid #D0D0D0;
                background:white;
            }
            
            QSpinBox::down-button, QDoubleSpinBox::down-button{
                subcontrol-origin:border;
                subcontrol-position:bottom right;
                width:22px;
                border-left:1px solid #D0D0D0;
                background:white;
            }
            
            QWidget{
                background:#F5F5F5;
                font-size:15px;
            }
        
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox{
                background:white;
                border:1px solid #D0D0D0;
                border-radius:8px;
                padding:6px;
                min-height:28px;
            }
        
            QPushButton{
                background:white;
                border:2px solid #11BED5;
                border-radius:10px;
                padding:8px 16px;
                font-weight:bold;
                color:#11BED5;
            }
        
            QPushButton:hover{
                background:#11BED5;
                color:white;
            }
        
            QPushButton:disabled{
                background:#E0E0E0;
                border:2px solid #BBBBBB;
                color:#888888;
            }
        
            QProgressBar{
                border:1px solid #D0D0D0;
                border-radius:8px;
                text-align:center;
                height:24px;
                background:white;
            }
        
            QProgressBar::chunk{
                background:#11BED5;
                border-radius:8px;
            }
        """)
                
                
        def make_value_label(label):
        
            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        
            label.setFixedWidth(130)
        
            label.setStyleSheet("""
                QLabel{
                    font-size:16px;
                    font-weight:bold;
                    color:#222222;
                    background:#F0FBFD;
                    border:1px solid #11BED5;
                    border-radius:8px;
                    padding:5px;
                }
            """)
        
        
        def add_row(layout, label_text, value_label, tooltip=None):
        
            row = QHBoxLayout()
        
            label = QLabel(label_text)
        
            label.setFixedWidth(180)
        
            label.setAlignment(
                Qt.AlignmentFlag.AlignRight
                |
                Qt.AlignmentFlag.AlignVCenter
            )
        
            label.setStyleSheet("""
                QLabel{
                    font-size:16px;
                    color:#555555;
                    background:white;
                }
            """)
        
            if tooltip:
                label.setToolTip(tooltip)
        
            make_value_label(
                value_label
            )
        
            row.addWidget(label)
        
            row.addSpacing(15)
        
            row.addWidget(value_label)
        
            row.addStretch()
        
            layout.addLayout(row)
        
        
        add_row(
            infos_main_layout,
            "Date du modèle",
            self.date_label
        )
        
        section_title = QLabel("Performances")
        
        section_title.setStyleSheet("""
            QLabel{
                font-size:17px;
                font-weight:bold;
                color:#11BED5;
                background:white;
                margin-top:10px;
            }
        """)
        
        infos_main_layout.addWidget(section_title)
        
        add_row(
            infos_main_layout,
            "Erreur médiane",
            self.median_error_label,
            "Médiane de l'erreur absolue en nombre d'œufs."
        )
        
        add_row(
            infos_main_layout,
            "Erreur médiane relative",
            self.median_relative_error_label,
            "Médiane de l'erreur relative (=rapporté au nombre réel) en %."
        )
                
        add_row(
            infos_main_layout,
            "Erreur moyenne",
            self.mae_label,
            "Écart moyen entre le nombre d'œufs prédit et le nombre réel."
        )
        
        
        add_row(
            infos_main_layout,
            "σ Erreur moyenne",
            self.mae_std_label,
            "Écart-type de l'erreur moyenne absolue."
        )
                
        infos_group.setFixedWidth(450)  # ajuste la valeur selon la largeur souhaitée
        
        layout.addWidget(infos_group)
        layout.setAlignment(infos_group, Qt.AlignmentFlag.AlignHCenter)
        
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
        self.advanced_button = QToolButton()
        self.advanced_button.setText("▶ Paramètres avancés")
        self.advanced_button.setCheckable(True)
        self.advanced_button.setChecked(False)
        self.advanced_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextOnly
        )
        
        self.advanced_button.setStyleSheet("""
            QToolButton{
                background:transparent;
                border:none;
                font-size:16px;
                font-weight:bold;
                color:#222222;
                text-align:left;
                padding:6px;
            }
        
            QToolButton:hover{
                color:#11BED5;
            }
        """)
        
        layout.addWidget(self.advanced_button)
        
        self.advanced_widget = QGroupBox()
        self.advanced_widget.setVisible(False)
        
        advanced_layout = QGridLayout(self.advanced_widget)
        
        self.threshold = QDoubleSpinBox()
        self.threshold.setDecimals(2)
        self.threshold.setRange(0, 1)
        self.threshold.setSingleStep(0.01)
        self.threshold.setValue(PEAK_THRESHOLD)
        
        self.min_distance = QSpinBox()
        self.min_distance.setRange(1, 100)
        self.min_distance.setValue(PEAK_MIN_DISTANCE)
        
        advanced_layout.addWidget(
            QLabel("Seuil de détection des oeufs"),
            0,
            0
        )
        
        advanced_layout.addWidget(
            self.threshold,
            0,
            1
        )
        
        advanced_layout.addWidget(
            QLabel("Distance minimale (px) séparant des oeufs"),
            1,
            0
        )
        
        advanced_layout.addWidget(
            self.min_distance,
            1,
            1
        )
        
        layout.addWidget(self.advanced_widget)
        
        self.advanced_button.clicked.connect(
            self.toggle_advanced_parameters
        )
                
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
    
        best_index = -1
        best_score = float("inf")
    
        for index, (version, text) in enumerate(
            self.model_manager.list_models_display()
        ):
    
            self.model_box.addItem(
                text,
                version
            )
    
            info = self.model_manager.get_model_info(
                version
            )
    
            score = info.get(
                "median_relative_error",
                None
            )
    
            if score is None:
                score = info.get(
                    "mae",
                    None
                )
    
            if score is not None and score < best_score:
    
                best_score = score
                best_index = index
    
        if best_index >= 0:
    
            self.model_box.setCurrentIndex(
                best_index
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
        
    def toggle_advanced_parameters(self):

        checked = self.advanced_button.isChecked()
    
        self.advanced_widget.setVisible(
            checked
        )
    
        self.advanced_button.setText(
            "▼ Paramètres avancés"
            if checked
            else
            "▶ Paramètres avancés"
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
    
        median_error = info.get("median_error", None)
        
        self.median_error_label.setText(
            "-"
            if median_error is None
            else f"{median_error:.2f}"
        )
        
        median_relative_error = info.get("median_relative_error", None)
        
        self.median_relative_error_label.setText(
            "-"
            if median_relative_error is None
            else f"{100 * median_relative_error:.2f} %"
        )
            
        self.mae_label.setText(
            str(
                info.get(
                    "mae",
                    "-"
                )
            )
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
        
        
        threshold = info.get(
            "threshold",
            PEAK_THRESHOLD
        )
        
        min_distance = info.get(
            "min_distance",
            PEAK_MIN_DISTANCE
        )
        
        self.threshold.setValue(
            float(threshold)
        )
        
        self.min_distance.setValue(
            int(min_distance)
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