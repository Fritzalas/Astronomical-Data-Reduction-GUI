import os

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout
from astropy.io import fits
import numpy as np
from PyQt5.QtCore import Qt

class FITSViewer(QLabel):
    """DS9-like interactive viewer showing pixel counts on mouse move."""
    def __init__(self, fits_file):
        super().__init__()
        self.fits_file = fits_file

        hdul = fits.open(fits_file)
        self.data = hdul[0].data
        hdul.close()

        self.data = np.nan_to_num(self.data)
        if self.data.ndim > 2:
            self.data = self.data[0]

        vmin, vmax = np.percentile(self.data, (1, 99))
        norm_data = np.clip(self.data, vmin, vmax)
        norm_data = ((norm_data - vmin) / (vmax - vmin) * 255).astype(np.uint8)

        self.img_height, self.img_width = norm_data.shape
        image = QImage(norm_data, self.img_width, self.img_height, QImage.Format_Grayscale8)
        self.pixmap = QPixmap.fromImage(image)
        self.setPixmap(self.pixmap)

        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if self.pixmap.isNull():
            return

        label_width = self.width()
        label_height = self.height()
        pixmap_width = self.pixmap.width()
        pixmap_height = self.pixmap.height()

        scale_x = pixmap_width / label_width
        scale_y = pixmap_height / label_height

        img_x = int(x * scale_x)
        img_y = int(y * scale_y)

        if 0 <= img_x < self.img_width and 0 <= img_y < self.img_height:
            count = self.data[img_y, img_x]
            self.setToolTip(f"X: {img_x}, Y: {img_y}, Count: {count:.2f}")


class ImageDialog(QDialog):
    """Popup dialog to show a FITS image with DS9-like interaction."""

    def __init__(self, fits_file):
        super().__init__()
        self.setWindowTitle(os.path.basename(fits_file))

        layout = QVBoxLayout()
        viewer = FITSViewer(fits_file)
        viewer.setScaledContents(True)  # Image scales to fit QLabel
        layout.addWidget(viewer)
        self.setLayout(layout)

        # Set a reasonable fixed size (you can adjust as needed)
        self.setMinimumSize(400, 400)
        self.setMaximumSize(800, 600)  # Won’t grow beyond this size
        self.resize(600, 500)  # Default initial size