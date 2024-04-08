from abc import abstractmethod

import numpy as np
import typing as tp
import numpy.typing as npt


def _get_layers(image: npt.NDArray) -> tp.Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    return tuple(np.transpose(image, (2, 0, 1)))


def _get_hue(r: npt.NDArray, g: npt.NDArray, b: npt.NDArray, _max: npt.NDArray, chroma: npt.NDArray) -> npt.NDArray:
    hue = np.zeros_like(_max)
    for m, add, sub, shift in (
        (r, g, b, 0),
        (g, b, r, 2),
        (b, r, g, 4),
    ):
        mask = (m == _max) & (chroma != 0)
        hue[mask] = ((add - sub)[mask] / chroma[mask] + shift) % 6
    return hue / 6


def _yuv_to_rgb(image: npt.NDArray, kr: float, kb: float) -> npt.NDArray:
    y, u, v = _get_layers(image)
    u = 2 * (1 - kb) * (u - .5)
    v = 2 * (1 - kr) * (v - .5)
    r = y + v
    b = y + u
    g = y - 1 / (1 - kr - kb) * (kr * v + kb * u)
    return np.dstack((r, g, b))


def _rgb_to_yuv(image: npt.NDArray, kr: float, kb: float) -> npt.NDArray:
    r, g, b = _get_layers(image)
    y = kr * r + (1 - kr - kb) * g + kb * b
    u = (b - y) / (2 - 2*kb) + .5
    v = (r - y) / (2 - 2*kr) + .5
    return np.dstack((y, u, v))


class ColorSpace:

    @staticmethod
    @abstractmethod
    def channels() -> tp.Tuple[str, str, str]:
        pass

    def name(self) -> str:
        return "".join(self.channels())

    @staticmethod
    @abstractmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        pass

    @staticmethod
    @abstractmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        pass


class RGBSpace(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "R", "G", "B"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        return image

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        return image


class CMYSpace(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "C", "M", "Y"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        return 1 - image

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        return 1 - image


class HSLSpace(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "H", "S", "L"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        w, h, d = np.shape(image)
        hue, saturation, lightness = (layer.flatten() for layer in _get_layers(image))
        a = saturation * np.minimum(lightness, 1 - lightness)

        def f(n):
            k = (n + hue * 12) % 12
            v = np.minimum(np.minimum(k-3, 9-k), np.ones_like(k))
            v[v < -1] = -1
            return (lightness - a * v).reshape((w, h))

        r, g, b = map(f, (0, 8, 4))

        return np.dstack((r, g, b))

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        w, h, d = np.shape(image)
        r, g, b = (layer.flatten() for layer in _get_layers(image))
        _max = image.max(axis=2).flatten()
        _min = image.min(axis=2).flatten()
        chroma = _max - _min
        lightness = (_max + _min) / 2
        hue = _get_hue(r, g, b, _max, chroma)

        saturation = np.zeros((w, h)).flatten()
        mask = (lightness != 0) & (lightness != 1)
        saturation[mask] = chroma[mask] / (1 - np.abs(2 * lightness - 1)[mask])
        saturation = np.clip(saturation, 0, 1)
        return np.dstack((hue.reshape((w, h)), saturation.reshape((w, h)), lightness.reshape((w, h))))


class HSVSpace(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "H", "S", "V"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        w, h, d = image.shape
        hue, saturation, value = (layer.flatten() for layer in _get_layers(image))

        def f(n):
            k = (n + hue * 6) % 6
            v = np.min(np.dstack((k, 4-k, np.ones_like(k))), axis=-1)
            v[v < 0] = 0
            return (value * (1 - saturation * v)).reshape((w, h))

        r, g, b = map(f, [5, 3, 1])

        return np.dstack((r, g, b))

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        w, h, d = image.shape
        r, g, b = (layer.flatten() for layer in _get_layers(image))
        _max = image.max(axis=2).flatten()
        _min = image.min(axis=2).flatten()
        chroma = _max - _min
        value = _max
        hue = _get_hue(r, g, b, _max, chroma)

        saturation = np.zeros_like(r)
        mask = value != 0
        saturation[mask] = chroma[mask] / value[mask]
        saturation[saturation > 1] = 1
        return np.dstack((
            hue.reshape((w, h)),
            saturation.reshape((w, h)),
            value.reshape((w, h))
        ))


class YCoCgSpace(ColorSpace):
    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "Y", "Co", "Cg"

    def from_rgb(self, image: np.ndarray) -> np.ndarray:
        image = image.copy()
        *wh, _ = image.shape
        r, g, b = _get_layers(image)
        y = (r + 2*g + b) / 4
        co = .5 + (r - b) / 2
        cg = .5 + (-r + 2*g - b) / 4
        return np.dstack((y, co, cg))

    def to_rgb(self, image: np.ndarray) -> np.ndarray:
        y, co, cg = _get_layers(image)
        co = co - .5
        cg = cg - .5
        r = y + co - cg
        g = y + cg
        b = y - co - cg
        return np.dstack((r, g, b))


class YCbCr601Space(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "Y", "Cb", "Cr"

    def name(self) -> str:
        return "YCbCr601"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        return _yuv_to_rgb(image, 0.299, 0.114)

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        return _rgb_to_yuv(image, 0.299, 0.114)


class YCbCr709Space(ColorSpace):

    @staticmethod
    def channels() -> tp.Tuple[str, str, str]:
        return "Y", "Cb", "Cr"

    def name(self) -> str:
        return "YCbCr709"

    @staticmethod
    def to_rgb(image: npt.NDArray) -> npt.NDArray:
        return _yuv_to_rgb(image, 0.2126, 0.0722)

    @staticmethod
    def from_rgb(image: npt.NDArray) -> npt.NDArray:
        return _rgb_to_yuv(image, 0.2126, 0.0722)


if __name__ == "__main__":
    print(RGBSpace().channels())
    print(RGBSpace().name())
