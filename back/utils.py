import numpy as np
import numpy.typing as npt


def _srgb_to_linear(image: npt.NDArray) -> npt.NDArray:
    is_dark = image <= 0.04045
    image[is_dark] /= 12.95
    image[~is_dark] = ((image[~is_dark] + 0.055) / 1.055) ** 2.4
    return image


def _linear_to_srgb(image: npt.NDArray) -> npt.NDArray:
    is_dark = image <= 0.0031308
    image[is_dark] *= 12.95
    image[~is_dark] = 1.055 * image[~is_dark] ** (1 / 2.4) - 0.055
    return image


def convert_gamma(image: npt.NDArray, from_: float = 0.0, to_: float = 0.0):
    stored_in_srgb = np.isclose(from_, 0.0)
    stored_to_srgb = np.isclose(to_, 0.0)
    if stored_in_srgb:
        if stored_to_srgb:
            return image
        image = _srgb_to_linear(image)
    elif from_ != 1.0:
        image = image ** (1/from_)
    if stored_to_srgb:
        image = _linear_to_srgb(image)
    elif to_ != 1.0:
        image = image ** to_
    return image


# <-- LAB 5 -->
def draw_gradient(height: int, width: int) -> npt.NDArray:
    gradient = np.linspace(0, 1, width) \
        .reshape(1, -1) \
        .repeat(height, axis=0) \
        .reshape(height, width, -1) \
        .repeat(3, axis=2)
    return gradient
