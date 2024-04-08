import os
import typing as tp

import numpy as np
from PyQt6.QtWidgets import QMenu, QComboBox, QFileDialog

from back import Backend
from back.saving import ImageSaver
from front.controller import Controller
from front.image_view import ImageView


class SaveController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView, writers: tp.List[ImageSaver]):
        super().__init__(title, backend, image_view)
        self.setMinimumSize(300, 100)
        self.writers = writers

        self.combobox = QComboBox()
        for writer in self.writers:
            self.combobox.addItem(writer.name())

        self.add_hor_layout().add_widget(self.combobox).build_layout()
        self.attach_button().build()
        self.attach_action(menu)

    def accept(self):
        writer = self.writers[self.combobox.currentIndex()]
        filename = QFileDialog.getSaveFileName(self, 'Save file', os.getcwd(), "All files (*.*)")[0]
        if not os.path.exists(os.path.dirname(filename)):
            return

        writer.save((self.backend.image_holder.get_image() * 255).astype(np.uint8), open(filename, "wb"))
        self.hide()
