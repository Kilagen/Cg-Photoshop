from abc import ABC, abstractmethod

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QBoxLayout, QMenu


class ControllerBuilder(ABC):
    @abstractmethod
    def add_widget(self, widget: QWidget):
        pass

    @abstractmethod
    def add_layout(self, direction: str):
        pass

    @abstractmethod
    def build_layout(self):
        pass


class LayoutBuilder(ControllerBuilder):
    def __init__(self, parent, direction):
        self.__layout = QHBoxLayout() if direction == "hor" else (QVBoxLayout() if direction == "ver" else None)
        self.__parent = parent

    def add_widget(self, widget) -> ControllerBuilder:
        self.__layout.addWidget(widget)
        return self

    def add_layout(self, direction: str) -> 'LayoutBuilder':
        return LayoutBuilder(self, direction)

    def build_layout(self) -> object:
        self.__parent.prepare_layout(self.__layout)
        return self.__parent

    def prepare_layout(self, layout: QBoxLayout):
        self.__layout.addLayout(layout)


class ActionController(QAction):
    def __init__(self, title: str, parent: QWidget, window: QWidget):
        super().__init__(title, parent)
        self.window = window
        self.triggered.connect(self.window.show)


class WidgetController(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.setWindowTitle(self.title)

        self.__central_layout = QVBoxLayout()

    def add_widget(self, widget):
        self.__central_layout.addWidget(widget)
        return self

    def add_hor_layout(self) -> LayoutBuilder:
        return LayoutBuilder(self, "hor")

    def add_ver_layout(self) -> LayoutBuilder:
        return LayoutBuilder(self, "ver")

    def attach_action(self, parent: QMenu):
        action = ActionController(self.title, parent, self)
        parent.addAction(action)

        return self

    def build(self):
        self.setLayout(self.__central_layout)

        return self

    def prepare_layout(self, layout: QBoxLayout):
        self.__central_layout.addLayout(layout)
