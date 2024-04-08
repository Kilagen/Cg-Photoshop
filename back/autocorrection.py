import numpy as np
import numpy.typing as npt
import typing as tp

from .colorspace import *
from .utils import convert_gamma


def get_histograms(image: npt.NDArray[int]) -> tp.Tuple[npt.NDArray[int], ...]:
    print(image.shape)
    layers = [image[:, :, i] for i in range(image.shape[-1])]
    layer_bins = [np.bincount(np.ravel(layer), minlength=256) for layer in layers]
    return tuple(layer_bins)


def get_noise_percentile(histogram: npt.NDArray[int], noise: float) -> tp.Tuple[int, int]:
    total_count = np.sum(histogram)
    noise_count = int(total_count * noise)
    low = 0
    low_count = 0
    while low_count + histogram[low] < noise_count:
        low_count += histogram[low]
        low += 1

    high = 255
    high_count = 0
    while high_count + histogram[high] < noise_count:
        high_count += histogram[high]
        high -= 1

    return low, high


def autocorrect_rgb_like(
        image: npt.NDArray[float],
        noise: float,
        colorspace: ColorSpace,
        store_gamma: float,
        display_gamma: float
) -> npt.NDArray[float]:
    image = colorspace.to_rgb(image)
    image = convert_gamma(image, store_gamma, display_gamma)
    histograms = get_histograms(np.floor(image * 255).astype(np.uint8))

    low, high = 255, 0
    for histogram in histograms:
        _low, _high = get_noise_percentile(histogram=histogram, noise=noise)
        if _low < low:
            low = _low
        if _high > high:
            high = _high
    if low < high:
        low /= 255
        high /= 255
        image = (image - low) / (high - low)
    image = convert_gamma(image, display_gamma, store_gamma)
    return np.clip(colorspace.from_rgb(image), 0, 1)


def autocorrect_last_i(
        image: npt.NDArray[float],
        noise: float
) -> npt.NDArray[float]:
    histograms = get_histograms(np.floor(image[:, :, -1:] * 255).astype(np.uint8))
    low, high = 255, 0
    for histogram in histograms:
        _low, _high = get_noise_percentile(histogram=histogram, noise=noise)
        if _low < low:
            low = _low
        if _high > high:
            high = _high
    if low < high:
        low /= 255
        high /= 255
        image[:, :, -1] = (image[:, :, -1] - low) / (high - low)
    return np.clip(image, 0, 1)


def autocorrect_first_y(
        image: npt.NDArray[float],
        noise: float
) -> npt.NDArray[float]:
    histograms = get_histograms(np.floor(image[:, :, :1] * 255).astype(np.uint8))
    low, high = 255, 0
    for histogram in histograms:
        _low, _high = get_noise_percentile(histogram=histogram, noise=noise)
        if _low < low:
            low = _low
        if _high > high:
            high = _high
    if low < high:
        low /= 255
        high /= 255
        image[:, :, 0] = (image[:, :, 0] - low) / (high - low)
    return np.clip(image, 0, 1)


def autocorrect(
        image: npt.NDArray[float],
        noise: float,
        colorspace: ColorSpace,
        store_gamma: float,
        display_gamma: float
) -> npt.NDArray[float]:

    if colorspace.name() in [RGBSpace().name(), CMYSpace().name()]:
        return autocorrect_rgb_like(image, noise, colorspace, store_gamma, display_gamma)
    elif colorspace.name() in [HSLSpace().name(), HSVSpace().name()]:
        return autocorrect_last_i(image, noise)
    elif colorspace.name() in [YCoCgSpace().name(), YCbCr601Space().name(), YCbCr709Space().name()]:
        return autocorrect_first_y(image, noise)
    else:
        raise NotImplementedError(f"Unknown colorspace {colorspace.name()}")
