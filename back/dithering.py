from abc import abstractmethod

import numpy as np
import numpy.typing as npt
import typing as tp

BAYER_MATRIX = 1/64 * np.array(
    [
        [0, 32, 8, 40, 2, 34, 10, 42],
        [48, 16, 56, 24, 50, 18, 58, 26],
        [12, 44, 4, 36, 14, 46, 6, 38],
        [60, 28, 52, 20, 62, 30, 54, 22],
        [3, 35, 11, 43, 1, 33, 9, 41],
        [51, 19, 59, 27, 49, 17, 57, 25],
        [15, 47, 7, 39, 13, 45, 5, 37],
        [63, 31, 55, 23, 61, 29, 53, 21]
    ]
).reshape((8, 8, 1))


class ImageDitherer:
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _dither(self, image: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        pass

    def dither(self, image: npt.NDArray[np.float64], n_bits: int) -> npt.NDArray[np.float64]:
        image = np.clip(image, 0.0, 1.0)
        image *= 2 ** n_bits - 1
        image = self._dither(image)
        image /= 2 ** n_bits - 1
        image = np.clip(image, 0.0, 1.0)
        return image


class RandomDitherer(ImageDitherer):
    def name(self) -> str:
        return "Random"

    def _dither(self, image: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        height, width, depth = image.shape
        image += np.random.rand(height, width, 1) - .5
        return np.round(image)


class FloydSteinbergDitherer(ImageDitherer):
    def name(self) -> str:
        return "FloydSteinberg"

    def _dither(self, image: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        height, width, depth = np.shape(image)
        for i in range(height):
            for j in range(width):
                value = image[i, j, :]
                rounded = np.round(value)
                error = value - rounded
                error /= 16
                for (_i, _j), s in zip(
                        ((i+1, j+1), (i+1, j), (i+1, j-1), (i, j+1)),
                        (1, 5, 3, 7)
                ):
                    if 0 <= _i < height and 0 <= _j < width:
                        image[_i, _j, :] += error * s
                image[i, j, :] = rounded
        return image


class OrderedDitherer(ImageDitherer):
    def name(self) -> str:
        return "Ordered"

    def _dither(self, image: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        height, width, depth = np.shape(image)
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                block = image[i:i + 8, j:j + 8, :]
                block, residuals = np.divmod(block, 1)
                if i >= height - 8 or j >= width - 8:
                    block[residuals > BAYER_MATRIX[: height - i, : width - j, :]] += 1
                else:
                    block[residuals > BAYER_MATRIX] += 1
                image[i:i + 8, j:j + 8, :] = block
        return image


class AtkinsonDitherer(ImageDitherer):
    def name(self) -> str:
        return "Atkinson"

    def _dither(self, image: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        height, width, depth = np.shape(image)
        for i in range(height):
            for j in range(width):
                value = image[i, j, :]
                rounded = np.round(value)
                error = value - rounded
                error /= 8
                for _i, _j in (
                        (i, j+1),
                        (i, j+2),
                        (i+1, j-1),
                        (i+1, j),
                        (i+1, j+1),
                        (i+2, j)
                ):
                    if 0 <= _i < height and 0 <= _j < width:
                        image[_i, _j, :] += error
                image[i, j, :] = rounded
        return image
