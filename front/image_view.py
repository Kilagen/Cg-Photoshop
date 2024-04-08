from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class ImageView(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.picture = QLabel("")

    def set_image(self, pixmap: QPixmap):
        self.picture.setPixmap(pixmap)
