from abc import abstractmethod
from typing import BinaryIO
import numpy as np


class ImageSaver:
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def save(self, arr: np.ndarray, stream: BinaryIO):
        pass


class P6Saver(ImageSaver):
    def name(self) -> str:
        return "P6"

    def save(self, arr: np.ndarray, stream: BinaryIO):
        stream.write(b'P6\n')
        stream.write(f"{arr.shape[1]} {arr.shape[0]}\n"
                     f"255\n".encode())
        stream.write(arr.tobytes())


class P5Saver(ImageSaver):
    def name(self) -> str:
        return "P5"

    def save(self, arr: np.ndarray, stream: BinaryIO):
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        arr = np.array(0.2989 * r + 0.5870 * g + 0.1140 * b, dtype=np.uint8)
        b = arr.tobytes()
        stream.write(b'P5\n')
        stream.write(f"{arr.shape[1]} {arr.shape[0]}\n"
                     f"255\n".encode())
        stream.write(b)
