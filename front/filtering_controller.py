from typing import List

from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QMenu

from back import Backend
from front.controller import Controller
from front.image_view import ImageView


from inspect import signature


class FilterController(Controller):
    def __init__(
            self,
            title: str,
            menu: QMenu,
            backend: Backend,
            image_view: ImageView,
            image_filter: type
    ):
        super().__init__(title, backend, image_view)

        self.button = QPushButton("Ok")
        self.image_filter = image_filter

        filter_signature = signature(image_filter)
        filter_args = list(filter_signature.parameters.keys())
        self.fields: List[QLineEdit] = list()
        self.types: List[type] = list()
        for arg in filter_args:
            default_value = filter_signature.parameters[arg].default
            field = QLineEdit(str(default_value))
            self.types.append(type(default_value))
            self.fields.append(field)
            self.add_widget(QLabel(arg)).add_widget(field)

        self.attach_button()
        self.build()

        self.attach_action(menu)

    def accept(self):
        args = list()
        for field, f_type in zip(self.fields, self.types):
            args.append(f_type(field.text()))

        self.backend.filter_image(self.image_filter(*args))
        self.update_image_view()
