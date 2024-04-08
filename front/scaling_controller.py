from typing import List

from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QMenu, QComboBox

from back import Backend
from back.scaling import OneDimensionScaler, Scaler
from front.controller import Controller
from front.image_view import ImageView


class ScaleController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView, scalers: List[OneDimensionScaler]):
        super().__init__(title, backend, image_view)
        self.button = QPushButton("Ok")

        self.width = QLineEdit()
        self.height = QLineEdit()
        self.h_offset = QLineEdit("0")
        self.w_offset = QLineEdit("0")
        self.b = QLineEdit("0")
        self.c = QLineEdit("0.5")
        self.scalers = scalers
        self.scaler = QComboBox()
        self.scaler.addItems(list(map(lambda x: x.name(), scalers)))

        self.add_widget(self.scaler)
        self.add_widget(QLabel("Width, px")).add_widget(self.width)
        self.add_widget(QLabel("Height, px")).add_widget(self.height)
        self.add_widget(QLabel("h offset, px")).add_widget(self.h_offset)
        self.add_widget(QLabel("w offset, px")).add_widget(self.w_offset)
        self.add_widget(QLabel("B")).add_widget(self.b)
        self.add_widget(QLabel("C")).add_widget(self.c)

        self.attach_button()
        self.build()

        self.attach_action(menu)

    def accept(self):
        scaler = self.scalers[self.scaler.currentIndex()]
        width = int(self.width.text())
        height = int(self.height.text())
        h_offset = int(self.h_offset.text())
        w_offset = int(self.w_offset.text())
        b = float(self.b.text())
        c = float(self.c.text())

        self.backend.scale_image(scaler, height, width, h_offset, w_offset, b=b, c=c)
        self.update_image_view()
