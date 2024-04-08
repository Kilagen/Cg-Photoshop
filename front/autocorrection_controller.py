import matplotlib
import typing as tp

from PyQt6.QtWidgets import QMenu, QLineEdit, QLabel

from back import Backend
from front.controller import Controller
from front.image_view import ImageView


from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use('QtAgg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=15, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.red_axes = fig.add_subplot(311)
        self.green_axes = fig.add_subplot(312)
        self.blue_axes = fig.add_subplot(313)
        super(MplCanvas, self).__init__(fig)


class AutocorrectionController(Controller):
    def __init__(self, title: str, menu: QMenu, backend: Backend, image_view: ImageView):
        super().__init__(title, backend, image_view)

        self.histograms_view = MplCanvas()
        self.alpha = QLineEdit()
        self.add_widget(self.histograms_view).add_widget(QLabel("Alpha:")).add_widget(self.alpha)

        self.attach_button()
        self.build()
        self.attach_action(menu)

    def build_histograms(self):
        hists = self.backend.get_histograms()
        colors = ["red", "green", "blue"]
        h_view = self.histograms_view
        titles = self.backend.colorspace.channels()
        axes = [h_view.red_axes, h_view.green_axes, h_view.blue_axes]
        for i in range(3):
            axes[i].cla()
            if not self.backend.turnoff_layers[i]:
                values = hists[i]
                color = colors[i]
                axes[i].stairs(values / sum(values), color=color, fill=True)
                axes[i].set_title(titles[i])
        h_view.draw()

    def accept(self):
        try:
            alpha = float(self.alpha.text())
        except ValueError:
            raise Exception("Expected float value with dot separator")
        assert 0 <= alpha < 0.5, "Expected alpha value from [0;0.5)"
        self.backend.autocorrect(alpha)
        self.build_histograms()
        self.update_image_view()

    def show(self):
        self.build_histograms()
        super().show()
