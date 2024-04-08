import contextlib

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QScrollArea, QHBoxLayout, QVBoxLayout, QMenuBar, QWidget

from back import *
from back.saving import P5Saver, P6Saver
from back.scaling import *
from .colorspace_controller import ColorSpaceController
from .gamma_controller import StoreGammaController, DisplayGammaController

from .image_view import ImageView
from .open_controller import OpenController
from .layers_controller import LayersController
from .save_controller import SaveController

# <-- LAB 5 -->
from .gradient_controller import GradientController
from .dithering_controller import DitheringController

# <-- LAB 6 -->
from .autocorrection_controller import AutocorrectionController

# <-- LAB 7 -->
from .scaling_controller import ScaleController

# <-- LAB 8 -->
from .filtering_controller import FilterController
import back.filtering as filtr


class PhotoshopWindow(QMainWindow):
    def __init__(self, backend: Backend):
        super().__init__()

        self.backend = backend
        self.image_view = ImageView()
        self.error_box = PhotoshopWindow.setup_error_box(self)
        self.scroll = self.setup_scrolling()
        self.menu_bar = self.setup_menu_bar(self, backend)
        self.setup_window()

        self.setup_central_layout()

    def setup_window(self) -> None:
        self.setGeometry(0, 0, 760, 780)
        self.setWindowTitle("Photoshop")

    def setup_central_layout(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        horizontal_layout = QHBoxLayout()

        self.setCentralWidget(main_widget)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(horizontal_layout)

        horizontal_layout.addWidget(self.scroll)

    @contextlib.contextmanager
    def capture_exceptions(self) -> tp.Iterator[None]:
        try:
            print(0)
            try:
                print(1)
                yield
            except Exception as e:
                print(2)
                self.error_box.setText(str(e))
                self.error_box.exec()
        finally:
            pass

    def setup_scrolling(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.image_view.picture)
        return scroll

    @staticmethod
    def setup_error_box(parent: QWidget) -> QMessageBox:
        error_box = QMessageBox(parent=parent)
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle("Error")
        return error_box

    def setup_menu_bar(self, parent: QMainWindow, backend: Backend) -> QMenuBar:
        menu_bar = QMenuBar()
        writers = [P5Saver(), P6Saver()]

        file_menu = menu_bar.addMenu("File")
        open_action = OpenController("Open", file_menu, backend, self.image_view)
        file_menu.addAction(open_action)
        SaveController("Save", file_menu, self.backend, self.image_view, writers)

        converters: tp.List[ColorSpace] = [
            RGBSpace(),
            CMYSpace(),
            YCbCr601Space(),
            YCbCr709Space(),
            HSLSpace(),
            HSVSpace(),
            YCoCgSpace()
        ]

        settings_menu = menu_bar.addMenu("Settings")
        ColorSpaceController("Change colorspace", settings_menu, self.backend, self.image_view, converters)
        LayersController("Switch layer", settings_menu, self.backend, self.image_view)
        StoreGammaController("Change Store Gamma", settings_menu, self.backend, self.image_view)
        DisplayGammaController("Change Display Gamma", settings_menu, self.backend, self.image_view)

        # <-- LAB 5 -->
        ditherers: tp.List[ImageDitherer] = [
            RandomDitherer(),
            OrderedDitherer(),
            AtkinsonDitherer(),
            FloydSteinbergDitherer()
        ]
        DitheringController("Dithering", settings_menu, self.backend, self.image_view, ditherers)
        GradientController("Draw Gradient", file_menu, self.backend, self.image_view)

        # <-- LAB 6 -->
        AutocorrectionController("Autocorrection", settings_menu, self.backend, self.image_view)

        # <-- LAB 7 -->
        scalers: tp.List[OneDimensionScaler] = [NearestScaler(), LinearScaler(), SplineScaler(), LanczosScaler()]
        ScaleController("Scale image", settings_menu, self.backend, self.image_view, scalers)

        # <-- LAB 8 -->
        filter_menu = menu_bar.addMenu("Filters")
        for image_filter in [
            filtr.GaussianFilter,
            filtr.BoxBlurFilter,
            filtr.ThresholdFilter,
            filtr.SobelFilter,
            filtr.MedianFilter,
            filtr.UnsharpMaskingFilter,
            filtr.OtsuThresholdFilter
            ]:
            FilterController(image_filter.name(), filter_menu, self.backend, self.image_view, image_filter)

        return menu_bar
