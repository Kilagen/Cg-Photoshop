import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QFileDialog

from back import Backend
from front.image_view import ImageView


class OpenController(QAction):
    def __init__(self, title: str, parent: QWidget, backend: Backend, image_view: ImageView):
        super().__init__(title, parent)
        self.backend = backend
        self.image_view = image_view
        self.triggered.connect(self.accept)

    def accept(self):
        filename = QFileDialog.getOpenFileName(self.parent(), 'Open file', os.getcwd(), "All files (*.*)")
        if not os.path.isfile(filename[0]):
            return

        self.backend.read_image(filename[0])
        pixmap = self.backend.get_view()
        self.image_view.set_image(pixmap)
