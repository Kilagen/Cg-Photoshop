from typing import List

from PyQt6.QtWidgets import QCheckBox, QMenu, QComboBox

from back import ColorSpace, Backend
from front.controller import Controller
from front.image_view import ImageView


class ColorSpaceController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView, spaces: List[ColorSpace]):
        super().__init__(title, backend, image_view)
        self.setMinimumSize(300, 100)
        self.backend = backend

        self.checkbox = QCheckBox("Convert?")
        self.combobox = QComboBox()
        self.spaces = spaces
        for space in self.spaces:
            self.combobox.addItem(space.name())

        self.add_hor_layout().add_widget(self.checkbox).add_widget(self.combobox).build_layout()
        self.attach_button().build()
        self.attach_action(menu)

    def accept(self):
        enabled = self.checkbox.isChecked()
        space = self.spaces[self.combobox.currentIndex()]

        self.backend.change_colorspace(space, enabled)
        self.update_image_view()
