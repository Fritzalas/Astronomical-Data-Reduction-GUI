from PyQt5.QtWidgets import (QMainWindow, QWidget,
                             QVBoxLayout,
                             QStackedWidget)

from GUI.ProcessingScreen import ProcessingScreen
from GUI.StarryBackground import StarryBackground
from GUI.WelcomeScreen import WelcomeScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AstroReduct - Astronomical Image Reduction Software")
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(800, 600)

        # Central widget with starry background
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create background
        self.background = StarryBackground()
        main_layout.addWidget(self.background)

        # Create stacked widget for screens
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        # Create screens
        self.welcome_screen = WelcomeScreen()
        self.processing_screen = ProcessingScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.processing_screen)

        # Add stacked widget to background
        self.background_layout = QVBoxLayout(self.background)
        self.background_layout.addWidget(self.stacked_widget)

        # Connect the welcome screen button
        self.welcome_screen.start_processing = self.show_processing_screen

    def show_processing_screen(self):
        self.stacked_widget.setCurrentIndex(1)