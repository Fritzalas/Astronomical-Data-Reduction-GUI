from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
                             QStackedWidget, QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPainter, QLinearGradient, QBrush
import random

class StarryBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = []
        self.twinkle_timer = QTimer(self)
        self.twinkle_timer.timeout.connect(self.update_stars)
        self.twinkle_timer.start(100)  # Update every 100ms

        # Create stars
        for _ in range(100):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            self.stars.append([x, y, size, brightness])

    def resizeEvent(self, event):
        # Regenerate stars when window is resized
        self.stars = []
        for _ in range(100):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            self.stars.append([x, y, size, brightness])
        super().resizeEvent(event)

    def update_stars(self):
        # Randomly change brightness of some stars
        for star in self.stars:
            if random.random() < 0.05:  # 5% chance to twinkle
                star[3] = random.randint(100, 255)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw dark blue background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 15, 30))
        gradient.setColorAt(1, QColor(5, 10, 20))
        painter.fillRect(self.rect(), QBrush(gradient))

        # Draw stars
        for x, y, size, brightness in self.stars:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(brightness, brightness, brightness))
            painter.drawEllipse(x, y, size, size)