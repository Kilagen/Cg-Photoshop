import typing as tp
from abc import abstractmethod

from PyQt6.QtWidgets import QMenu, QLineEdit, QLabel

from back import Backend
from back.utils import draw_gradient
from front.controller import Controller
from front.image_view import ImageView


class GradientController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, backend, image_view)

        self.width = QLineEdit()
        self.height = QLineEdit()

        self.add_widget(QLabel("Set Width:")).add_widget(self.width)\
            .add_widget(QLabel("Set Height:")).add_widget(self.height)

        self.attach_button()
        self.build()
        self.attach_action(menu)

    def accept(self):
        try:
            width = int(self.width.text())
            height = int(self.height.text())
        except ValueError:
            raise Exception("Expected int value")
        assert 0 < width, "Expected positive width value"
        assert 0 < height, "Expected positive height value"
        self.draw_gradient(height, width)
        self.update_image_view()

    def draw_gradient(self, height: int, width: int):
        gradient = draw_gradient(height, width)
        self.backend.image_holder.set_image(gradient)
        self.backend.store_gamma = 1.0
        self.backend.display_gamma = 1.0
        self.update_image_view()
