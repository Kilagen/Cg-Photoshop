from abc import abstractmethod

import numpy as np
import numpy.typing as npt
import typing as tp

from .autocorrection import get_histograms


class Filter:
    @abstractmethod
    def apply_to(self, image: npt.NDArray) -> npt.NDArray:
        pass

    @staticmethod
    def name() -> str:
        pass


class KernelFilter(Filter):
    def __init__(self, radius: int = 1):
        self.radius = radius

    def apply_to(self, image: npt.NDArray) -> npt.NDArray:
        height, width, layers = np.shape(image)
        kernel = self.get_kernel()
        padded_image = np.pad(
            image,
            (
                (self.radius, self.radius),
                (self.radius, self.radius),
                (0, 0)
            )
        )

        res_image = np.zeros_like(image)
        for x in range(height):
            for y in range(width):
                window = padded_image[x: x + self.radius*2 + 1, y: y + self.radius*2 + 1]
                res_image[x, y] = self.apply_kernel(window, kernel)
        return res_image

    @abstractmethod
    def apply_kernel(self, window: npt.NDArray, kernel: npt.NDArray):
        pass

    @abstractmethod
    def get_kernel(self) -> npt.NDArray:
        pass


class BoxBlurFilter(KernelFilter):

    def __init__(self, radius: int = 1):
        super().__init__(radius)

    def get_kernel(self) -> npt.NDArray:
        return np.ones((self.radius*2 + 1, self.radius*2 + 1, 1))

    def apply_kernel(self, window: npt.NDArray, kernel: npt.NDArray):
        return np.mean(kernel * window, axis=(0, 1))

    @staticmethod
    def name() -> str:
        return "Box Blur"


class SobelFilter(KernelFilter):
    def __init__(self):
        super().__init__(1)

    def apply_kernel(self, window: npt.NDArray, kernel: npt.NDArray):
        r, g, b = window[:, :, 0], window[:, :, 1], window[:, :, 2]
        y = 0.2989 * r + 0.5870 * g + 0.1140 * b
        gy = np.sum(kernel * y, axis=(0, 1))
        gx = np.sum(kernel.T * y, axis=(0, 1))
        g = (gx**2 + gy**2) ** .5
        return np.dstack((g, g, g))

    def get_kernel(self) -> npt.NDArray:
        return np.array(
            [
                [ 1,  2,  1],
                [ 0,  0,  0],
                [-1, -2, -1]
            ]
        )

    @staticmethod
    def name() -> str:
        return "Sobel"


class ThresholdFilter(Filter):
    def __init__(self, threshold1: float = 0.1, threshold2: tp.Optional[float] = 0.1):
        assert 0 < threshold1 < 1
        if threshold2 is not None:
            assert 0 < threshold2 < 1
        else:
            threshold2 = threshold1
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    def apply_to(self, image: npt.NDArray) -> npt.NDArray:
        r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        bw_image = 0.2989 * r + 0.5870 * g + 0.1140 * b
        bw_image[bw_image <= self.threshold1] = 0.0
        bw_image[(self.threshold1 < bw_image) & (bw_image <= self.threshold2)] = 0.5
        bw_image[self.threshold2 < bw_image] = 1.0
        return np.dstack((bw_image, bw_image, bw_image))

    @staticmethod
    def name() -> str:
        return "Threshold"


class GaussianFilter(KernelFilter):
    def __init__(self, sigma: float = 1.0):
        assert 0.1 <= sigma <= 12
        radius = int(np.ceil(3*sigma))
        super().__init__(radius)
        self.sigma = sigma

    def apply_kernel(self, window: npt.NDArray, kernel: npt.NDArray):
        return np.sum(kernel * window, axis=(0, 1))

    def get_kernel(self) -> npt.NDArray:
        kernel_size = 2 * self.radius + 1
        x, y = np.meshgrid(np.linspace(-1, 1, kernel_size),
                           np.linspace(-1, 1, kernel_size))

        # lower normal part of gaussian
        normal = 1 / (2.0 * np.pi * self.sigma ** 2)

        # Calculating Gaussian filter
        gauss = np.exp(-(x ** 2 + y ** 2) / (2.0 * self.sigma ** 2)) * normal
        gauss /= gauss.sum()
        return gauss.reshape((kernel_size, kernel_size, 1))

    @staticmethod
    def name() -> str:
        return "Gaussian Blur"


class MedianFilter(KernelFilter):
    def apply_kernel(self, window: npt.NDArray, kernel: npt.NDArray):
        return np.median(window, axis=(0, 1))

    def get_kernel(self) -> npt.NDArray:
        return np.array([0])

    @staticmethod
    def name() -> str:
        return "Median Filter"


class UnsharpMaskingFilter(Filter):
    def __init__(self, amount: float = 1.0, sigma: float = 1.0):
        assert 0.0 < amount < 5.0
        assert 0.1 <= sigma <= 12
        self.sigma = sigma
        self.amount = amount
        self.gaussian_filter = GaussianFilter(sigma=sigma)

    def apply_to(self, image: npt.NDArray) -> npt.NDArray:
        blurred_image = self.gaussian_filter.apply_to(image)
        return image + (image - blurred_image) * self.amount

    @staticmethod
    def name() -> str:
        return "Unsharp Masking"


class OtsuThresholdFilter(Filter):

    def apply_to(self, image: npt.NDArray) -> npt.NDArray:
        r, g, b = image[:, :, 0:1], image[:, :, 1:2], image[:, :, 2:3]
        bw_image = 0.2989 * r + 0.5870 * g + 0.1140 * b
        histogram = get_histograms(np.round(bw_image * 255).astype(int))[0]
        histogram = histogram / histogram.sum()
        Q = histogram.cumsum()
        bins = np.arange(256)
        fn_min = np.inf
        thresh = -1
        for i in range(1, 256):
            p1, p2 = histogram[:i], histogram[i:]
            q1, q2 = Q[i], Q[255] - Q[i]
            if q1 < 1e-6 or q2 < 1e-6:
                continue
            b1, b2 = bins[:i], bins[i:]

            m1, m2 = np.sum(p1 * b1) / q1, np.sum(p2 * b2) / q2
            v1, v2 = np.sum(((b1 - m1) ** 2) * p1) / q1, np.sum(((b2 - m2) ** 2) * p2) / q2
            fn = v1 * q1 + v2 * q2
            if fn < fn_min:
                fn_min = fn
                thresh = i
        thresh /= 255
        bw_image = bw_image[:, :, 0]
        bw_image[bw_image < thresh] = 0
        bw_image[bw_image >= thresh] = 1
        return np.dstack((bw_image, bw_image, bw_image))

    @staticmethod
    def name() -> str:
        return "Otsu Threshold Filter"



class ContrastAdaptiveShapreningFilter(Filter):
    pass


class CannyEdgeDetectorFilter(Filter):
    pass
