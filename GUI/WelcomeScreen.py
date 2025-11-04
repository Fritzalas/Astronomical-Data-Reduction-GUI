from PyQt5.QtWidgets import (QWidget, QLabel,
                             QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class WelcomeScreen(QWidget):
    start_processing_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("AstroReduct")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #6ab1ea; margin-top: 80px;")

        # Subtitle
        subtitle = QLabel("Astronomical Image Reduction Software")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #d6d6d6; margin-bottom: 40px;")

        # Welcome message
        welcome_msg = QLabel("Welcome to AstroReduct - your powerful tool for processing astronomical images. "
                             "Reduce noise, calibrate, and enhance your celestial photographs with professional-grade algorithms.")
        welcome_msg.setAlignment(Qt.AlignCenter)
        welcome_msg.setWordWrap(True)
        welcome_msg.setStyleSheet("color: #a0a0a0; margin: 30px 50px; font-size: 14px;")

        # Start button
        start_button = QPushButton("Begin Image Processing")
        start_button.setMinimumHeight(45)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #3a7ebc;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a8ecc;
            }
            QPushButton:pressed {
                background-color: #2a6eac;
            }
        """)
        start_button.clicked.connect(self.start_processing_signal.emit)

        # Add widgets to layout
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(welcome_msg)
        main_layout.addStretch()
        main_layout.addWidget(start_button)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def start_processing(self):
        # This will be connected to the main window's page switching
        pass