from PyQt6.QtWidgets import QCheckBox, QMenu

from back import Backend
from front.controller import Controller
from front.image_view import ImageView


class LayersController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, backend, image_view)

        self.setMinimumSize(300, 75)
        self.channels = [QCheckBox() for _ in range(3)]

        builder = self.add_hor_layout()
        for channel in self.channels:
            channel.setChecked(True)
            self.add_widget(channel)
        builder.build_layout().build()
        self.attach_button()
        self.build()
        self.attach_action(menu)

    def accept(self):
        for i in range(3):
            self.backend.switch_layer(i, not self.channels[i].isChecked())

        print(self.backend.turnoff_layers)
        self.update_image_view()

    def show(self):
        channels_names = self.backend.colorspace.channels()
        for c, n in zip(self.channels, channels_names):
            c.setText(n)
        super().show()
