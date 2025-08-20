from PyQt5.QtWidgets import ( QWidget, QLabel,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                              QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ProcessingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Image Processing")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #6ab1ea; margin-top: 40px;")

        # Instructions
        instructions = QLabel("Upload your astronomical images for calibration and reduction")
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

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(upload_btn)
        btn_layout.addWidget(process_btn)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(instructions)
        layout.addLayout(btn_layout)
        layout.addWidget(progress)
        layout.addStretch()

        self.setLayout(layout)

    def upload_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Astronomical Images", "",
            "Image Files (*.fits *.fit *.tif *.tiff *.jpg *.jpeg *.png)"
        )
        if files:
            QMessageBox.information(self, "Files Selected",
                                    f"{len(files)} image(s) selected for processing")