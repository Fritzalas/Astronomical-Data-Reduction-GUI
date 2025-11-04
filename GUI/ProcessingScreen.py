import os
import shutil

import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QProgressBar, QTabWidget, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
from astropy.io import fits


class ProcessingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.flat_images_layout = None
        self.lights_images_layout = None
        self.bias_images_layout = None
        self.lights_tab = None
        self.bias_tab = None
        self.flat_tab = None
        self.tabs = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget for Bias, Flat, Lights
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
                    QTabWidget::pane { border: 0; background: transparent; }
                    QTabBar::tab { background: #222222; color: white; padding: 8px 20px; }
                    QTabBar::tab:selected { background: #3a7ebc; color: white; }
                """)
        main_layout.addWidget(self.tabs)

        # Create individual tabs
        self.bias_tab = self.create_stage_tab("Bias frames processing")
        self.flat_tab = self.create_stage_tab("Flat frames processing")
        self.lights_tab = self.create_stage_tab("Light frames processing")

        # Add tabs
        self.tabs.addTab(self.bias_tab, "Bias")
        self.tabs.addTab(self.flat_tab, "Flat")
        self.tabs.addTab(self.lights_tab, "Lights")

        self.setLayout(main_layout)

    def create_stage_tab(self, stage_name):
        tab = QWidget()
        layout = QVBoxLayout()

        # Tab name inside content
        stage_label = QLabel(stage_name)
        stage_label.setAlignment(Qt.AlignCenter)
        stage_font = QFont()
        stage_font.setPointSize(20)
        stage_font.setWeight(QFont.Bold)
        stage_label.setFont(stage_font)
        stage_label.setAlignment(Qt.AlignCenter)
        stage_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-top: 20px;")

        # Instructions
        instructions = QLabel(f"Upload your {stage_name.lower()} frames for processing")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #d6d6d6; margin-bottom: 30px;")

        # Upload button
        upload_btn = QPushButton("Upload Images")
        upload_btn.setMinimumHeight(40)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a7ebc;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a8ecc;
            }
        """)
        upload_btn.clicked.connect(self.upload_images)

        # Process button
        process_btn = QPushButton("Process Images")
        process_btn.setMinimumHeight(40)
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a7e5c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8e6c;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
        """)
        process_btn.setEnabled(False)

        # Progress bar
        progress = QProgressBar()
        progress.setVisible(False)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(upload_btn)
        btn_layout.addWidget(process_btn)

        # Add widgets to layout
        layout.addWidget(stage_label)
        layout.addWidget(instructions)
        layout.addLayout(btn_layout)
        layout.addWidget(progress)
        layout.setSpacing(10)  # vertical spacing between widgets
        layout.setContentsMargins(10, 10, 10, 10)  # reduce outer margins

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        images_container = QWidget()
        images_layout = QGridLayout()
        images_container.setLayout(images_layout)
        # Also adjust the images grid layout:
        images_layout.setSpacing(5)  # minimal space between images
        images_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(images_container)
        layout.addWidget(scroll_area)

        # Keep references depending on the stage
        if "Bias" in stage_name:
            self.bias_images_layout = images_layout
        elif "Flat" in stage_name:
            self.flat_images_layout = images_layout
        elif "Light" in stage_name:
            self.lights_images_layout = images_layout

        tab.setLayout(layout)
        return tab

    def upload_images(self):
        main_window = self.window()
        dialog = QFileDialog(main_window, "Select Astronomical Images")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("Image Files (*.fits *.fit *.fts)")

        if dialog.exec_():
            files = dialog.selectedFiles()
            if not files:
                return

            # Determine which tab is active
            current_tab_index = self.tabs.currentIndex()
            stage_name = self.tabs.tabText(current_tab_index).upper()
            folder_name = stage_name  # Use tab name as folder name

            # Create folder if it doesn't exist
            dest_folder = os.path.join(os.getcwd(), folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            # Select the correct layout to display images
            if stage_name == "BIAS":
                images_layout = self.bias_images_layout
            elif stage_name == "FLAT":
                images_layout = self.flat_images_layout
            else:
                images_layout = self.lights_images_layout

            # Clear previous images
            for i in reversed(range(images_layout.count())):
                widget = images_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # Copy files and add thumbnails
            row, col = 0, 0
            max_cols = 4  # max 4 images per row

            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy(file_path, dest_path)

                ext = os.path.splitext(file_path)[1].lower()

                if ext in [".fits", ".fit", ".fts"]:

                    hdul = fits.open(file_path)
                    data = hdul[0].data
                    hdul.close()

                    if data is not None:
                        data = np.nan_to_num(data)
                        vmin, vmax = np.percentile(data, (1, 99))
                        data = np.clip(data, vmin, vmax)
                        data = (data - vmin) / (vmax - vmin)  # normalize 0-1
                        data = (data * 255).astype(np.uint8)

                        if data.ndim > 2:
                            data = data[0]  # take first channel if 3D

                        height, width = data.shape
                        image = QImage(data, width, height, QImage.Format_Grayscale8)
                        pixmap = QPixmap.fromImage(image)
                else:
                    pixmap = QPixmap(file_path)

                # Display image if valid
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label = QLabel()
                    label.setPixmap(pixmap)
                    label.setToolTip(filename)
                    images_layout.addWidget(label, row, col)

                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

            QMessageBox.information(main_window, "Files Selected",
                                    f"{len(files)} images selected for processing")