from abc import abstractmethod
import numpy as np
import typing as tp
import numpy.typing as npt


class OneDimensionScaler:
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def scale(self, image: npt.NDArray, width: int, offset: int = 0, **kwargs) -> npt.NDArray:
        pass


class Scaler:
    @staticmethod
    def scale(
            odscaler: OneDimensionScaler,
            image: npt.NDArray,
            height: int, width: int,
            h_offset: int = 0, w_offset: int = 0,
            **kwargs
    ) -> npt.NDArray:
        old_height, old_width, _ = image.shape
        height_scale = height / old_height
        width_scale = width / old_width
        if height_scale > width_scale:
            image = np.swapaxes(image, 0, 1)
            image = odscaler.scale(image, height, h_offset, **kwargs)
            image = np.swapaxes(image, 0, 1)
            image = odscaler.scale(image, width, w_offset, **kwargs)
        else:
            image = odscaler.scale(image, width, w_offset, **kwargs)
            image = np.swapaxes(image, 0, 1)
            image = odscaler.scale(image, height, h_offset, **kwargs)
            image = np.swapaxes(image, 0, 1)
        return image


class NearestScaler(OneDimensionScaler):
    def name(self) -> str:
        return "Nearest Neighbor"

    def scale(self, image: npt.NDArray, width: int, offset: int = 0, **kwargs) -> npt.NDArray:
        old_height, old_width, layers = np.shape(image)
        scale_coefficient = old_width / width

        target_positions = np.arange(width) * scale_coefficient - 1 / 2 + scale_coefficient / 2 + offset

        new_image = np.zeros((old_height, width, 3), dtype=image.dtype)
        for target_index, target_position in enumerate(target_positions):
            pos, residual = divmod(target_position, 1)
            # pos, rem = target_position // 1, target_position % 1
            neighbor_index = pos if residual < .5 else pos + 1
            neighbor_index = int(np.clip(neighbor_index, 0, old_width - 1))
            new_image[:, target_index, :] = image[:, neighbor_index, :]
        return new_image


class LinearScaler(OneDimensionScaler):
    def _get_kernel(self, position: float, radius: float, high: int) -> tp.Tuple[tp.Iterable[int], npt.NDArray]:
        _low = int(max(0, np.ceil(position - radius)))
        _high = int(min(high, np.floor(position + radius)))
        coefs = radius - np.abs(np.arange(_low, _high + 1) - position)
        return range(_low, _high + 1), coefs / np.sum(coefs)

    def name(self) -> str:
        return "Linear"

    def scale(self, image: npt.NDArray, width: int, offset: int = 0, **kwargs) -> npt.NDArray:
        old_height, old_width, layers = np.shape(image)
        scale_coefficient = old_width / width
        target_positions = np.arange(width) * scale_coefficient + (scale_coefficient - 1) / 2 + offset

        new_image = np.zeros((old_height, width, 3), dtype=image.dtype)
        for target_index, target_position in enumerate(target_positions):
            neighbors_index, coefs = self._get_kernel(
                position=target_position,
                radius=max(1, scale_coefficient),
                high=old_width-1)
            for layer in range(layers):
                new_image[:, target_index, layer] = image[:, neighbors_index, layer] @ coefs
        return new_image


class SplineScaler(OneDimensionScaler):
    def _get_kernel(
            self,
            position: float,
            radius: float,
            high: int,
            b: float,
            c: float
    ) -> tp.Tuple[tp.Iterable[int], npt.NDArray]:
        _low = int(max(0, np.ceil(position - radius*2)))
        _high = int(min(high, np.floor(position + radius*2)))
        dist = np.abs(np.arange(_low, _high + 1) - position) / radius
        coefs = np.zeros_like(dist)

        # 0 <= dist < 1
        mask = dist < 1
        c3 = 12 - 9*b - 6*c
        c2 = -18 + 12*b + 6*c
        c0 = 6 - 2*b
        coefs[mask] = c3 * dist[mask] ** 3 + c2 * dist[mask] ** 2 + c0

        # 1 <= dist < 2
        mask = (1 <= dist) & (dist < 2)
        c3 = -b - 6*c
        c2 = 6*b + 30*c
        c1 = -12*b - 48*c
        c0 = 8*b + 24 * c
        coefs[mask] = c3 * dist[mask] ** 3 + c2 * dist[mask] ** 2 + c1 * dist[mask] + c0

        return range(_low, _high + 1), coefs / np.sum(coefs)

    def name(self) -> str:
        return "Spline"

    def scale(self, image: npt.NDArray, width: int, offset: int = 0, **kwargs) -> npt.NDArray:
        b: float = kwargs["b"]
        c: float = kwargs["c"]
        assert 0 <= b <= 1, "Expected b in [0, 1]"
        assert 0 <= c <= 1, "Expected c in [0, 1]"
        old_height, old_width, layers = np.shape(image)
        scale_coefficient = old_width / width
        target_positions = np.arange(width) * scale_coefficient + (scale_coefficient - 1) / 2 + offset

        new_image = np.zeros((old_height, width, 3), dtype=image.dtype)
        for target_index, target_position in enumerate(target_positions):
            neighbors_index, coefs = self._get_kernel(
                position=target_position,
                radius=max(1, scale_coefficient),
                high=old_width-1,
                b=b, c=c)
            for layer in range(layers):
                new_image[:, target_index, layer] = image[:, neighbors_index, layer] @ coefs
        return new_image


class LanczosScaler(OneDimensionScaler):
    def _get_kernel(self, position: float, radius: float, high: int) -> tp.Tuple[tp.Iterable[int], npt.NDArray]:
        _low = int(max(0, np.ceil(position - radius*3)))
        _high = int(min(high, np.floor(position + radius*3)))
        dist = np.abs(np.arange(_low, _high + 1) - position) / radius
        mask = dist != 0
        coefs = np.zeros_like(dist)
        coefs[mask] = 3 * np.sin(np.pi*dist[mask]) * np.sin(np.pi*dist[mask]/3) / (np.pi*dist[mask])**2
        coefs[~mask] = 1

        return range(_low, _high + 1), coefs / np.sum(coefs)

    def name(self) -> str:
        return "Lanczos3"

    def scale(self, image: npt.NDArray, width: int, offset: int = 0, **kwargs) -> npt.NDArray:
        old_height, old_width, layers = np.shape(image)
        scale_coefficient = old_width / width
        target_positions = np.arange(width) * scale_coefficient + (scale_coefficient - 1) / 2 + offset

        new_image = np.zeros((old_height, width, 3), dtype=image.dtype)
        for target_index, target_position in enumerate(target_positions):
            neighbors_index, coefs = self._get_kernel(
                position=target_position,
                radius=max(1, scale_coefficient),
                high=old_width-1
            )
            for layer in range(layers):
                new_image[:, target_index, layer] = image[:, neighbors_index, layer] @ coefs
        return new_image
