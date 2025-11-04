from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QProgressBar, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor


class ProcessingScreen(QWidget):
    def __init__(self):
        super().__init__()
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
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def upload_images(self):
        main_window = self.window()
        dialog = QFileDialog(main_window, "Select Astronomical Images")
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter("Image Files (*.fits *.fit *.fts)")

        # Force a readable palette
        palette = QPalette()
        palette.setColor(QPalette.Base, QColor(255, 255, 255))  # input/background
        palette.setColor(QPalette.Text, QColor(0, 0, 0))  # text color
        palette.setColor(QPalette.Button, QColor(240, 240, 240))  # button background
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # button text
        dialog.setPalette(palette)

        if dialog.exec_():
            files = dialog.selectedFiles()
            if files:
                if len(files) == 1:
                    QMessageBox.information(main_window, "File Selected",
                                        f"{len(files)} image selected for processing")
                else:
                    QMessageBox.information(main_window, "Files Selected",
                                            f"{len(files)} images selected for processing")