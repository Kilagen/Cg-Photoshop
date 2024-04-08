from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider, QMenu, QComboBox, QLabel

from back import Backend, ImageDitherer
from front.controller import Controller
from front.image_view import ImageView


class DitheringController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView, ditherers: List[ImageDitherer]):
        super().__init__(title, backend, image_view)
        self.setMinimumSize(300, 100)
        self.backend = backend

        self.label = QLabel()
        self.label.setText("1")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 8)
        self.slider.setPageStep(1)
        self.slider.valueChanged.connect(self.update_label)
        self.combobox = QComboBox()
        self.ditherers = ditherers
        for ditherer in self.ditherers:
            self.combobox.addItem(ditherer.name())

        self.add_hor_layout().add_widget(self.label).add_widget(self.slider).add_widget(self.combobox).build_layout()
        self.attach_button().build()
        self.attach_action(menu)

    def update_label(self, value) -> None:
        self.label.setText(str(value))

    def accept(self):
        n_bits = self.slider.value()
        ditherer = self.ditherers[self.combobox.currentIndex()]

        self.backend.dither(ditherer, n_bits)
        self.update_image_view()
