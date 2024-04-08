import typing as tp
import numpy.typing as npt
import numpy as np
from PyQt6.QtGui import QPixmap, QImage

# <-- LAB 8 -->
from .filtering import Filter

from .storing import ImageHolder
from .reading import read_image
from .colorspace import ColorSpace, RGBSpace
from .utils import convert_gamma
from .scaling import Scaler, OneDimensionScaler
from .autocorrection import get_histograms, autocorrect
from .dithering import ImageDitherer


class Backend:
    def __init__(self):
        self.image_holder = ImageHolder()
        self.colorspace: ColorSpace = RGBSpace()
        self.store_gamma: float = 0.0
        self.display_gamma: float = 0.0
        self.turnoff_layers: tp.List[bool, bool, bool] = [False, False, False]

    def get_view(self) -> QPixmap:
        image = self.image_holder.get_image()

        rgb_image = np.clip(self.colorspace.to_rgb(image), 0, 1)
        gamma_corrected_rgb_image = convert_gamma(rgb_image, self.store_gamma, self.display_gamma)

        gamma_corrected_rgb_image[:, :, self.turnoff_layers] = 0.0
        if sum(self.turnoff_layers) == 2:
            value = gamma_corrected_rgb_image[:, :, 2]
            for i in range(2):
                if not self.turnoff_layers[i]:
                    value = gamma_corrected_rgb_image[:, :, i]
            for i in range(3):
                gamma_corrected_rgb_image[:, :, i] = value

        scaled_image = np.array(gamma_corrected_rgb_image * 255, dtype=np.uint8)
        height, width, channel = scaled_image.shape
        bytes_per_line = 3 * width
        image = QImage(scaled_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(image)

    def read_image(self, image_path: str) -> None:
        image = read_image(image_path)
        self.colorspace = RGBSpace()
        self.store_gamma = 0.0
        self.display_gamma = 0.0
        self.image_holder.set_image(image)

    def change_colorspace(self, colorspace: ColorSpace, convert: bool = True) -> None:
        if convert:
            old_stored_image = self.image_holder.get_image()
            rgb_image = self.colorspace.to_rgb(old_stored_image)
            new_stored_image = colorspace.from_rgb(rgb_image)
            self.image_holder.set_image(new_stored_image)
        self.colorspace = colorspace

    def change_store_gamma(self, gamma: float) -> None:
        image = self.image_holder.get_image()
        rgb_image = self.colorspace.to_rgb(image)
        linear_rgb_image = convert_gamma(rgb_image, self.store_gamma, 1.0)
        reassigned_gamma_linear_rgb_image = convert_gamma(linear_rgb_image, 1.0, gamma)
        reassigned_gamma_image = self.colorspace.from_rgb(reassigned_gamma_linear_rgb_image)
        self.store_gamma = gamma
        self.image_holder.set_image(reassigned_gamma_image)

    def change_display_gamma(self, value: float) -> None:
        self.display_gamma = value

    def switch_layer(self, layer: int, value: bool) -> None:
        self.turnoff_layers[layer] = value

    # <-- LAB 5 -->
    def dither(self, image_dither: ImageDitherer, n_bits: int):
        assert 1 <= n_bits <= 8, "Expected bits count from 1 to 8"
        image = self.image_holder.get_image()
        rgb_image = self.colorspace.to_rgb(image)
        linear_rgb_image = convert_gamma(rgb_image, self.store_gamma, 1)
        image = image_dither.dither(image=linear_rgb_image, n_bits=n_bits)
        image = convert_gamma(image, 1, self.store_gamma)
        self.image_holder.set_image(self.colorspace.from_rgb(image))

    # <-- LAB 6 -->
    def get_histograms(self):
        view = self.image_holder.get_image() * 255
        return get_histograms(np.round(view).astype(np.uint8))

    def autocorrect(self, noise: float):
        assert 0 <= noise < 0.5, f"Expected noise in [0; 0,5), got {noise:.2g}"
        image = self.image_holder.get_image()
        image = autocorrect(
            image=image,
            noise=noise,
            colorspace=self.colorspace,
            store_gamma=self.store_gamma,
            display_gamma=self.display_gamma
        )
        self.image_holder.set_image(image)

    # <-- LAB 7 -->
    def scale_image(
            self,
            scaler: OneDimensionScaler,
            height: int, width: int,
            h_offset: int, w_offset: int,
            **kwargs
    ) -> None:
        rgb_image = self.colorspace.to_rgb(self.image_holder.get_image())
        linear_image = convert_gamma(rgb_image, self.store_gamma, 1)
        scaled_linear_image = Scaler.scale(
            odscaler=scaler,
            image=linear_image,
            height=height, width=width,
            h_offset=h_offset, w_offset=w_offset,
            **kwargs)
        rgb_scaled_image = convert_gamma(scaled_linear_image, 1, self.store_gamma)
        scaled_image = self.colorspace.from_rgb(rgb_scaled_image)
        self.image_holder.set_image(scaled_image)

    # <-- LAB 8 -->
    def filter_image(self, image_filter: Filter) -> None:
        rgb_image = self.colorspace.to_rgb(self.image_holder.get_image())
        linear_image = convert_gamma(rgb_image, self.store_gamma, 1)
        filtered_image = image_filter.apply_to(linear_image)
        rgb_filtered_image = convert_gamma(filtered_image, 1, self.store_gamma)
        self.image_holder.set_image(rgb_filtered_image)
