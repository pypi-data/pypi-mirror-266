from ._image import Image
from dask.array import Array
import dask.array as da
import matplotlib.pyplot as plt
from typing import List

class UByteImage(Image):
    def __init__(self, image: Array, info: dict, channel_names: List[str]) -> None:
        super().__init__(image, info, channel_names)
        assert self.dtype == 'uint8', "image must be of type uint8"
        if self.ndim == 2:
            self.image = da.expand_dims(self.image, axis=-1)
        self.ndim = self.image.ndim
        self.shape = self.image.shape

    def get_thumb(self, target_size: int = 512):
        assert isinstance(target_size, int), "target_size must be an integer"
        assert target_size > 0, "target_size must be greater than 0"
        coarsen_factor = max([s // target_size for s in self.shape])
        if coarsen_factor == 0:
            coarsen_factor = 1
        image = self.image
        if self.shape[2] == 3:
            thumb = da.coarsen(da.mean, image, {0: coarsen_factor, 1: coarsen_factor, 2:1}, trim_excess=True)
            thumb = thumb.astype('uint8')
        elif self.shape[2] == 1:
            thumb = da.coarsen(da.mean, image, {0: coarsen_factor, 1: coarsen_factor}, trim_excess=True)
            thumb = thumb.astype('uint8')
        else:
            raise NotImplementedError("Only 1 or 3 channel images are supported")
        return thumb.compute()

    def show_thumb(self, target_size: int = 512):
        thumb = self.get_thumb(target_size)
        plt.imshow(thumb, cmap='gray' if self.shape[2] == 1 else None)
        plt.axis('off')
        plt.show()