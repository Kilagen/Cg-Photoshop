import typing as tp
from abc import abstractmethod

from PyQt6.QtWidgets import QMenu, QLineEdit, QLabel

from back import Backend
from front.controller import Controller
from front.image_view import ImageView


class GammaController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, backend, image_view)

        self.gamma = QLineEdit()
        self.add_widget(QLabel("Set Gamma:")).add_widget(self.gamma)

        self.attach_button()
        self.build()
        self.attach_action(menu)

    def accept(self):
        try:
            gamma = float(self.gamma.text())
        except ValueError:
            raise Exception("Expected float value with dot separator")
        assert gamma == 0 or 0.01 <= gamma <= 100, "Expected zero gamma value (srgb) or value inbetween 0.01 and 100"
        self.do_gamma(gamma)
        self.update_image_view()

    @abstractmethod
    def do_gamma(self, gamma: float):
        pass


class StoreGammaController(GammaController):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, menu, backend, image_view)

    def do_gamma(self, gamma: float):
        self.backend.change_store_gamma(gamma)


class DisplayGammaController(GammaController):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, menu, backend, image_view)

    def do_gamma(self, gamma: float):
        self.backend.change_display_gamma(gamma)

