from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QPushButton

from back import Backend
from front.image_view import ImageView
from front.widget_controller import WidgetController


class Controller(WidgetController):
    def __init__(self, title: str, backend: Backend, image_view: ImageView):
        super().__init__(title)
        self.button = QPushButton("Ok")
        self.backend = backend
        self.image_view = image_view

    @abstractmethod
    def accept(self):
        pass

    def attach_button(self) -> 'Controller':
        self.add_widget(self.button)
        self.button.clicked.connect(self.accept)

        return self

    def update_image_view(self):
        pixmap = self.backend.get_view()
        self.image_view.set_image(pixmap)
