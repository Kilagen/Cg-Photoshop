import numpy as np
import numpy.typing as npt


class ImageHolder:
    def __init__(self) -> None:
        self.image: npt.NDArray = np.array([[[0, 0, 0]]])

    def set_image(self, image: npt.NDArray, scale: bool = False) -> None:
        if scale:
            image = image / 255
        self.image = np.clip(image, 0, 1)

    def get_image(self) -> npt.NDArray:
        return self.image.copy()
