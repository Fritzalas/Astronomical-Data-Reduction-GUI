import os
import shutil

import numpy as np
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QProgressBar, QTabWidget, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
from astropy.io import fits
from functools import partial
from GUI.FITSViewer import ImageDialog


def open_image_dialog(file_path, _):
    """Open FITS image in DS9-like dialog."""
    dialog = ImageDialog(file_path)
    dialog.setAttribute(Qt.WA_DeleteOnClose)  # Ensure proper deletion
    dialog.exec_()


class ProcessingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.current_files = None
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
        process_btn.clicked.connect(self.process_images)
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

    def process_images(self):
        main_window = self.window()
        current_tab_index = self.tabs.currentIndex()
        stage_name = self.tabs.tabText(current_tab_index).upper()

        if not hasattr(self, "current_files") or not self.current_files:
            QMessageBox.warning(main_window, "No files", "Please upload images first.")
            return

        dest_folder = os.path.join(os.getcwd(), stage_name)

        # --- BIAS PROCESSING ---
        if stage_name == "BIAS":

            bias_files = [os.path.join(dest_folder, f) for f in os.listdir(dest_folder)
                          if f.lower().endswith((".fits", ".fit", ".fts"))]

            if len(bias_files) == 0:
                QMessageBox.warning(main_window, "No files", "No bias frames found.")
                return

            # =================== CONFIGURATION ===================
            output_file = os.path.join(dest_folder, "MasterBias.fits")
            combine_method = "median"  # 'median' or 'average'
            reject_method = "minmax"  # 'minmax', 'sigclip', 'pclip', or None
            nlow = 0  # Minmax low pixels to reject
            nhigh = 1  # Minmax high pixels to reject
            scale = "none"  # 'none', 'median', 'mean', 'mode'
            statsec = None  # Optional section: [x1, x2, y1, y2]
            blank = 0.0  # Value for empty pixels
            clobber = True
            # =====================================================

            # --- Load all images into stack ---
            frames = []
            for bf in bias_files:
                data = fits.getdata(bf).astype(np.float64)
                if statsec:
                    x1, x2, y1, y2 = map(int, statsec)
                    data = data[y1:y2, x1:x2]
                frames.append(data)
            stack = np.array(frames)  # shape: (N_images, height, width)

            # --- Apply minmax rejection ---
            if reject_method.lower() == "minmax":
                if len(stack) > nlow + nhigh:
                    stack_sorted = np.sort(stack, axis=0)
                    stack_rejected = stack_sorted[nlow: len(stack_sorted) - nhigh, :, :]
                else:
                    stack_rejected = stack
            else:
                stack_rejected = stack

            # Replace NaNs with blank
            stack_rejected = np.nan_to_num(stack_rejected, nan=blank)

            # --- Apply scaling ---
            scaled_stack = stack_rejected.copy()
            if scale.lower() not in ("none", ""):
                for i in range(scaled_stack.shape[0]):
                    img = scaled_stack[i]
                    factor = 1.0
                    if scale.lower() == "median":
                        factor = np.median(img)
                    elif scale.lower() == "mean":
                        factor = np.mean(img)
                    elif scale.lower() == "mode":
                        factor = np.median(img) - 1.4826 * np.median(np.abs(img - np.median(img)))
                    if factor != 0:
                        scaled_stack[i] = img / factor

            # --- Combine images ---
            if combine_method.lower() == "median":
                master = np.median(scaled_stack, axis=0)
            elif combine_method.lower() == "average":
                master = np.mean(scaled_stack, axis=0)
            else:
                raise ValueError(f"Unknown combine method: {combine_method}")

            # --- Save Master Bias ---
            fits.writeto(output_file, master, overwrite=clobber)
            # ---- Display MASTER BIAS in UI ----
            master_bias_path = os.path.join(dest_folder, 'MasterBias.fits')

            # Clear grid
            for i in reversed(range(self.bias_images_layout.count())):
                widget = self.bias_images_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # Create thumbnail
            with fits.open(master_bias_path) as hdul:
                data = np.nan_to_num(hdul[0].data)

            vmin, vmax = np.percentile(data, (1, 99))
            data = np.clip(data, vmin, vmax)
            data = ((data - vmin) / (vmax - vmin) * 255).astype(np.uint8)
            if data.ndim > 2:
                data = data[0]

            data_copy = data.copy()
            h, w = data_copy.shape
            image = QImage(data_copy.data, w, h, w, QImage.Format_Grayscale8)
            image = image.copy()  # VERY IMPORTANT
            pixmap = QPixmap.fromImage(image).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setToolTip("Master Bias")
            label.setAlignment(Qt.AlignCenter)

            label.mousePressEvent = lambda event, fp=master_bias_path: open_image_dialog(fp, event)

            self.bias_images_layout.addWidget(label, 0, 0)
            # Enable Process button ONLY for BIAS tab
            process_btn = self.tabs.currentWidget().findChildren(QPushButton)[1]
            process_btn.setEnabled(False)
            QMessageBox.information(main_window, "Master Bias Created", "MasterBias.fits has been successfully generated!")

    def upload_images(self):
        main_window = self.window()
        dialog = QFileDialog(main_window, "Select Astronomical Images")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("Image Files (*.fits *.fit *.fts)")

        if dialog.exec_():
            files = dialog.selectedFiles()
            if not files:
                return

            current_tab_index = self.tabs.currentIndex()
            stage_name = self.tabs.tabText(current_tab_index).upper()
            folder_name = stage_name
            dest_folder = os.path.join(os.getcwd(), folder_name)
            os.makedirs(dest_folder, exist_ok=True)
            for f in os.listdir(dest_folder):
                file_path = os.path.join(dest_folder, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            if stage_name == "BIAS":
                images_layout = self.bias_images_layout
            elif stage_name == "FLAT":
                images_layout = self.flat_images_layout
            else:
                images_layout = self.lights_images_layout

            for i in reversed(range(images_layout.count())):
                widget = images_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            row, col = 0, 0
            max_cols = 4

            for file_path in files:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy(file_path, dest_path)

                ext = os.path.splitext(file_path)[1].lower()

                pixmap = None
                if ext in [".fits", ".fit", ".fts"]:
                    hdul = fits.open(file_path)
                    data = hdul[0].data
                    hdul.close()

                    if data is not None:
                        data = np.nan_to_num(data)
                        vmin, vmax = np.percentile(data, (1, 99))
                        data = np.clip(data, vmin, vmax)
                        data = ((data - vmin) / (vmax - vmin) * 255).astype(np.uint8)
                        if data.ndim > 2:
                            data = data[0]
                        h, w = data.shape
                        image = QImage(data, w, h, QImage.Format_Grayscale8)
                        pixmap = QPixmap.fromImage(image)
                else:
                    pixmap = QPixmap(file_path)

                if pixmap is not None and not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label = QLabel()
                    label.setPixmap(pixmap)
                    label.setToolTip(filename)
                    label.setAlignment(Qt.AlignCenter)

                    label.mousePressEvent = partial(open_image_dialog, file_path)

                    images_layout.addWidget(label, row, col)
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

            self.current_files = files
            # Enable Process button ONLY for BIAS tab
            process_btn = self.tabs.currentWidget().findChildren(QPushButton)[1]
            process_btn.setEnabled(stage_name == "BIAS")
            QMessageBox.information(main_window, "Files Selected",
                                    f"{len(files)} images selected for processing")