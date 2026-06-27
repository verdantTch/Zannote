# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:19:14 2026

@author: hugoz
"""

from pathlib import Path
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import (
    QAction,
    QColor,
    QFont,
    QBrush,
    QPen,
    QIcon,
    QPainter,
    QShortcut,
    QPixmap,
    QKeySequence
)

from PyQt6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsSimpleTextItem,
    QMessageBox,
    QWidget,         
    QComboBox,
    QHBoxLayout,       
    QLabel,           
    QSizePolicy,
    QGraphicsRectItem,
    QVBoxLayout,
    QGraphicsTextItem
)

from ui.image_view import ImageView

from graphics.annotation_item import (
    AnnotationItem,
    Cross_width
)

from managers.annotation_manager import (
    AnnotationManager
)

from managers.image_manager import (
    ImageManager
)

from managers.csv_manager import (
    CsvManager
)

from utils.icons import svg_to_icon


class AnnotationWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        icon = svg_to_icon("assets/logo.svg")
        
        # Grand écran =====================
        self.setWindowState(
            Qt.WindowState.WindowMaximized
        )
        # ================================
        
        self.image_selector = QComboBox()

        self.image_selector.currentIndexChanged.connect(
            self.goto_image
        )
        
        self.setWindowIcon(icon)  # fenêtre + barre des tâches
        self.setWindowTitle(
            "Zannote"
        )
        
        self.resize(
            1600,
            1000
        )

        self.annotation_manager = (
            AnnotationManager()
        )

        self.image_manager = (
            ImageManager()
        )

        self.csv_manager = None

        self.scene = QGraphicsScene()

        self.view = ImageView()

        self.view.setScene(
            self.scene
        )

        # Bannière supérieure ===============================================================================
        central_widget = QWidget()
        
        layout = QVBoxLayout(
            central_widget
        )
        self.banner_widget = QWidget()
        
        banner_layout = QHBoxLayout(
            self.banner_widget
        )
        
        banner_layout.addWidget(
            QLabel("Image :")
        )
        
        banner_layout.addWidget(
            self.image_selector
        )
        
        banner_layout.addStretch()
        
        layout.addWidget(
            self.banner_widget
        )
        
        self.banner_widget.hide() # Cacher la bannière avant l'ouverture d'un dossier
        #  ===============================================================================
        
        self.image_name_label = QLabel()
        
        self.image_name_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        
        self.image_name_label.setStyleSheet("""
        QLabel {
            background-color: rgba(255,255,255,180);
            color: black;
            font-weight: bold;
            padding: 4px;
        }
        """)
        
        layout.addWidget(
            self.view
        )
        
        self.setCentralWidget(
            central_widget
        )
        self.pixmap_item = None

        self.annotation_items = []

        self.number_items = []

        self.show_numbers = True

        self.create_toolbar()
        

        self.statusBar().clearMessage()
        
        self.view.mousePressEvent = (
            self.image_mouse_press
        )
        
        self.left_status = QLabel()
        self.right_status = QLabel()
        
        
        self.statusBar().addWidget(
            self.left_status
        )
        
        self.statusBar().addPermanentWidget(
            self.right_status
        )
        
        # Paramètres d'affichage des chiffres
        self.number_size = 18
        self.number_color = QColor(
            255,
            0,
            0
        )
        
        # Désactiver par défaut l'annotation
        self.view.setEnabled(False)
        
        #  Raccourcis clavier ========================
        QShortcut(
            QKeySequence("Z"),
            self,
            activated=self.undo
        )
        
        QShortcut(
            QKeySequence("M"),
            self,
            activated=self.toggle_numbers
        )
        
        QShortcut(
            QKeySequence("A"),
            self,
            activated=self.previous_image
        )
        
        QShortcut(
            QKeySequence("S"),
            self,
            activated=self.next_image
        )
        # ===============================================

    # =====================================================
    # TOOLBAR
    # =====================================================

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
        
        toolbar.addSeparator()

        open_action = QAction(
            "Ouvrir dossier",
            self
        )

        open_action.triggered.connect(
            self.open_folder
        )

        toolbar.addAction(
            open_action
        )

        toolbar.addSeparator()

        prev_action = QAction(
            "◀",
            self
        )

        prev_action.triggered.connect(
            self.previous_image
        )

        toolbar.addAction(
            prev_action
        )

        next_action = QAction(
            "▶",
            self
        )

        next_action.triggered.connect(
            self.next_image
        )

        toolbar.addAction(
            next_action
        )

        toolbar.addSeparator()

        undo_action = QAction(
            "Annuler",
            self
        )

        undo_action.triggered.connect(
            self.undo
        )

        toolbar.addAction(
            undo_action
        )
                
        container = QWidget()
        layout = QHBoxLayout(container)
        
        layout.addStretch()
        
        shortcut_label = QLabel("""
        <i><b>Z</b> : Annuler &nbsp; || &nbsp;
        <b>M</b> : Afficher/ masquer les numéros &nbsp; || &nbsp;
        <b>A</b> : Image précédente &nbsp; || &nbsp;
        <b>S</b> : Image suivante &nbsp; || &nbsp;
        <b>Clic gauche</b> : Ajouter &nbsp; || &nbsp;
        <b>Clic droit</b> : Supprimer le plus proche </i> &nbsp;   
        """)
        
        layout.addWidget(shortcut_label)
        
        toolbar.addWidget(container)
        


    def return_home(self):
    
        self.autosave()
    
        self.close()
    
        from ui.home_page import HomePage
    
        self.home = HomePage()
    
        self.home.show()
        
    # =====================================================
    # Accéder à une image via le menu déroulant
    # =====================================================
    def goto_image(self, index):
    
        if index < 0:
            return
    
        self.autosave()
    
        self.image_manager.current_index = index
    
        self.load_current_image()
        self.sync_image_selector()

        
        
    # =====================================================
    # Mise à jour du menu déroulant
    # =====================================================
    def update_image_selector(self):

        current = (
            self.image_selector.currentIndex()
        )
    
        self.image_selector.blockSignals(
            True
        )
    
        self.image_selector.clear()
    
        for image_path in self.image_manager.images:
    
            image_name = Path(
                image_path
            ).stem
    
            csv_path = os.path.join(
                self.csv_manager.label_folder,
                f"{image_name}.csv"
            )
    
            if os.path.exists(csv_path):
    
                text = (
                    f"✓ {Path(image_path).name}"
                )
    
            else:
    
                text = (
                    f"{Path(image_path).name}"
                )
    
            self.image_selector.addItem(
                text
            )
    
        self.image_selector.setCurrentIndex(
            current
        )
    
        self.image_selector.blockSignals(
            False
        )
    # =====================================================
    # DOSSIER
    # =====================================================
    def load_folder(self, folder):
    
        self.image_manager.load_folder(folder)
    
        if len(self.image_manager.images) == 0:
    
            QMessageBox.warning(
                self,
                "Aucune image",
                "Le dossier sélectionné ne contient aucune image ou leur format n'est pas compatible."
            )
    
            self.view.setEnabled(False)
            self.banner_widget.hide()
        
            return False
    
        label_folder = os.path.join(
            folder,
            "Labels"
        )
    
        self.csv_manager = CsvManager(label_folder)
    
        self.image_manager.current_index = 0
    
        self.update_image_selector()
    
        self.load_current_image()
    
        self.sync_image_selector()
    
        self.banner_widget.show()
    
        self.view.setEnabled(True)
        return True

    
    # Lorsqu'un fichiera déjà été ouvert
    def open_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choisir dossier images"
        )
    
        if folder:
            self.load_folder(folder)
                   

        
    # =====================================================
    # IMAGE
    # =====================================================

    def load_current_image(self):

        image_path = (
            self.image_manager.current_image()
        )

        if image_path is None:
            return

        self.scene.clear()

        self.annotation_items.clear()

        self.number_items.clear()

        pixmap = QPixmap(
            image_path
        )

        self.pixmap_item = (
            QGraphicsPixmapItem(
                pixmap
            )
        )

        self.scene.addItem(
            self.pixmap_item
        )

        self.annotation_manager.annotations.clear()

        image_name = Path(
            image_path
        ).stem

        points = (
            self.csv_manager.load_annotations(
                image_name
            )
        )

        for x, y in points:

            self.annotation_manager.add_annotation(
                int(x),
                int(y)
            )

        self.rebuild_annotations()


        self.view.resetTransform()
        
        self.view.fitInView(
            self.pixmap_item,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self.base_zoom = (
            self.view.transform().m11()
        )
        
        self.view.zoom = 1.0


        self.update_status()
        



    # =====================================================
    # ANNOTATIONS
    # =====================================================

    def rebuild_annotations(self):

        for item in self.annotation_items:
            self.scene.removeItem(item)

        for item in self.number_items:
            self.scene.removeItem(item)

        self.annotation_items.clear()

        self.number_items.clear()

        for idx, ann in enumerate(
            self.annotation_manager.annotations,
            start=1
        ):

            point_item = AnnotationItem(
                ann.x,
                ann.y
            )

            self.scene.addItem(
                point_item
            )

            self.annotation_items.append(
                point_item
            )

            if self.show_numbers:
                txt = QGraphicsSimpleTextItem(
                    str(idx)
                )
                font = QFont()
                font.setPointSize(
                    self.number_size
                )
                
                txt.setFont(font)
                
                txt.setBrush(
                    self.number_color
)

                txt.setPos(
                    ann.x + 5,
                    ann.y + 5
                )

                self.scene.addItem(
                    txt
                )

                self.number_items.append(
                    txt
                )

    # =====================================================
    # AUTOSAVE
    # =====================================================

    def autosave(self):

        if self.csv_manager is None:
            return

        image_path = (
            self.image_manager.current_image()
        )

        image_name = Path(
            image_path
        ).stem

        width = (
            self.pixmap_item.pixmap().width()
        )

        height = (
            self.pixmap_item.pixmap().height()
        )

        self.csv_manager.save_annotations(
            image_name,
            width,
            height,
            self.annotation_manager.annotations
        )
        
        self.update_image_selector()

    # =====================================================
    # SOURIS
    # =====================================================

    def image_mouse_press(
        self,
        event
    ):
        # On prévient les clics avant qu'un fichier ne soit ouvert
        if self.pixmap_item is None:
            return
        
        scene_pos = (
            self.view.mapToScene(
                event.pos()
            )
        )

        x = int(
            scene_pos.x()
        )

        y = int(
            scene_pos.y()
        )

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            # On s'assure que la souris soit dans le cadre de l'image ===
            scene_pos = self.view.mapToScene(
                event.pos()
            )
            
            x = int(scene_pos.x())
            y = int(scene_pos.y())
            
            pixmap = self.pixmap_item.pixmap()
            
            width = pixmap.width()
            height = pixmap.height()
            
            if (
                x < 0
                or y < 0
                or x >= width
                or y >= height
            ):
                return
            # ============================================================
            # On s'assure que deux clics ne sont pas au même endroit

            MIN_DISTANCE = Cross_width + 1 # séparation légèrement supérieure à la taille de la croix pour permettre la sélection
            
            can_add = True
            
            for ann in self.annotation_manager.annotations:
            
                if (
                    abs(ann.x - x) < MIN_DISTANCE
                    and
                    abs(ann.y - y) < MIN_DISTANCE
                ):
                    can_add = False
                    break
            
            if can_add:
            
                self.annotation_manager.add_annotation(
                    x,
                    y
                )


            self.rebuild_annotations()

            self.autosave()

        elif (
            event.button()
            == Qt.MouseButton.RightButton
        ):

            self.annotation_manager.remove_nearest(
                x,
                y
            )

            self.rebuild_annotations()

            self.autosave()

        else:

            super(
                ImageView,
                self.view
            ).mousePressEvent(
                event
            )

        self.update_status()

    # =====================================================
    # UNDO
    # =====================================================

    def undo(self):

        self.annotation_manager.undo()

        self.rebuild_annotations()

        self.autosave()

        self.update_status()


    def add_image_banner(self, image_name):
    
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
    
        text_item = QGraphicsTextItem(
            image_name
        )
    
        text_item.setFont(font)
    
        text_item.setDefaultTextColor(
            QColor("black")
        )
    
        text_item.setPos(
            10,
            5
        )
    
        rect = text_item.boundingRect()
    
        banner = QGraphicsRectItem(
            0,
            0,
            rect.width() + 20,
            rect.height() + 10
        )
    
        banner.setBrush(
            QBrush(
                QColor(
                    255,
                    255,
                    255,
                    180
                )
            )
        )
    
        banner.setPen(
            QPen(
                Qt.PenStyle.NoPen
            )
        )
    
        banner.setZValue(
            1000
        )
    
        text_item.setZValue(
            1001
        )
    
        self.scene.addItem(
            banner
        )
    
        self.scene.addItem(
            text_item
        )
    # =====================================================
    # NAVIGATION
    # =====================================================

    def next_image(self):

        if self.image_manager.current_index < len(self.image_manager.images) - 1:
    
            self.image_manager.current_index += 1
            
            # Mise à jour de la liste déroulante
            self.load_current_image()
            self.sync_image_selector()

    def previous_image(self):

        if self.image_manager.current_index > 0:
    
            self.image_manager.current_index -= 1
    
            self.load_current_image()
            
            # Mise à jour de la liste déroulante
            self.image_selector.blockSignals(True)
            self.sync_image_selector()

    # =====================================================
    # STATUS BAR
    # =====================================================

    def update_status(self):

        total = len(
            self.annotation_manager.annotations
        )
    
        current = (
            self.image_manager.current_index + 1
        )
    
        total_images = len(
            self.image_manager.images
        )

        
        zoom = (
            self.view.transform().m11()
            / self.base_zoom
            * 100
        )
        
        self.left_status.setText(
            f"Nombre d'œufs : {total}  ||  "
            f" Image {current}/{total_images}  ||  "
            f"Zoom : {zoom:.0f}%  "
        )
        
        self.right_status.setText(
            f"✓ Sauvegarde automatique active | "
            f"{total} annotations enregistrées "
        )
        
    # =====================================================
    # Afficher / Masquer les numéros 
    # =====================================================
    def toggle_numbers(self):
    
        self.show_numbers = (
            not self.show_numbers
        )
    
        self.rebuild_annotations()
        
        
    # =====================================================
    # Synchronisation de la liste déroulante
    # =====================================================
    def sync_image_selector(self):

        self.image_selector.blockSignals(True)
    
        self.image_selector.setCurrentIndex(
            self.image_manager.current_index
        )
    
        self.image_selector.blockSignals(False)

    # =====================================================
    # FERMETURE
    # =====================================================

    def closeEvent(
        self,
        event
    ):

        self.autosave()

        event.accept()