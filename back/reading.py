from dataclasses import dataclass
import typing as tp
from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt


class ImageReader(ABC):
    @abstractmethod
    def read(self, stream: tp.BinaryIO) -> npt.NDArray:
        pass


@dataclass
class PNMMetaData:
    height: int
    width: int


class PNMReader(ImageReader):

    def read(self, stream: tp.BinaryIO) -> npt.NDArray:
        try:
            meta = self.read_meta(stream)
        except AssertionError:
            raise Exception("Broken file")
        arr = np.frombuffer(stream.read(), dtype=np.uint8)
        return self.reshape(meta, arr / 255)

    @staticmethod
    @abstractmethod
    def reshape(metadata, arr: npt.NDArray) -> npt.NDArray:
        pass

    @staticmethod
    def read_meta(stream: tp.BinaryIO) -> PNMMetaData:
        s = stream.readline()
        assert s.count(b' ') == 1 and s.endswith(b'\n')

        width, height = s.rstrip(b'\n').decode().split()
        assert width.isnumeric() and height.isnumeric()

        s = stream.readline().rstrip(b'\n').decode()
        assert s.isnumeric()

        return PNMMetaData(int(height), int(width))


class P5Reader(PNMReader):
    @staticmethod
    def reshape(metadata, arr: npt.NDArray) -> npt.NDArray:
        height, width = metadata.height, metadata.width
        assert arr.size == height * width, "Invalid image size"
        return arr.reshape((height, width, 1)).repeat(3, axis=2)


class P6Reader(PNMReader):
    @staticmethod
    def reshape(metadata, arr: npt.NDArray) -> npt.NDArray:
        height, width = metadata.height, metadata.width
        assert arr.size == height * width * 3, "Invalid image size"
        return arr.reshape((height, width, 3))


def match(header: bytes, stream: tp.BinaryIO) -> npt.NDArray:
    if header == b"P6":
        return P6Reader().read(stream)
    if header == b"P5":
        return P5Reader().read(stream)
    else:
        raise Exception("Unknown image format")


def read_image(path: str) -> npt.NDArray:
    with open(path, "rb") as stream:
        header = stream.readline().rstrip(b'\n')
        return match(header, stream)
