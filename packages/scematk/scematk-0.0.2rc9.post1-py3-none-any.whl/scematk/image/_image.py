from abc import ABC, abstractmethod
from dask.array import Array
import matplotlib.pyplot as plt
import numpy as np
from typing import List

class Image(ABC):
    def __init__(self, image: Array, info: dict, channel_names: List[str]) -> None:
        assert isinstance(image, Array), "image must be a dask array"
        assert image.ndim in [2, 3], "image must be 2D or 3D"
        assert isinstance(info, dict), "info must be a dictionary"
        if isinstance(channel_names, str):
            channel_names = [channel_names]
        assert isinstance(channel_names, list), "channel_names must be a list"
        assert all(isinstance(name, str) for name in channel_names), "all channel names must be strings"
        if image.ndim == 3:
            assert len(channel_names) == image.shape[2], "number of channel names must match number of channels in image"
        else:
            assert len(channel_names) == 1, "number of channel names must match number of channels in image"
        self.image = image
        self.info = info
        self.ndim = image.ndim
        self.shape = image.shape
        self.dtype = str(image.dtype)
        if 'mpp' in self.info:
            self.mpp = self.info['mpp']
        elif 'mpp-x' in self.info and 'mpp-y' in self.info:
            if self.info['mpp-x'] == self.info['mpp-y']:
                self.mpp = self.info['mpp-x']
        else:
            self.mpp = None
        self.channel_names = channel_names

    def persist(self):
        return self.image.persist()

    def compute(self):
        return self.image.compute()

    def rechunk(self, chunks: tuple):
        assert isinstance(chunks, tuple), "chunks must be a tuple"
        assert all(isinstance(chunk, int) for chunk in chunks), "all elements of chunks must be integers"
        assert len(chunks) == self.ndim, "length of chunks must match number of dimensions in image"
        assert all(chunk > 0 for chunk in chunks), "all elements of chunks must be positive"
        if self.ndim == 3:
            assert chunks[2] == len(self.channel_names), "third element of chunks must match number of channels in image"
        self.image = self.image.rechunk(chunks)

    def read_region(self, y_min: int, x_min: int, y_len: int, x_len: int, pad: bool = False):
        assert isinstance(y_min, int), "y_min must be an integer"
        assert isinstance(x_min, int), "x_min must be an integer"
        assert isinstance(y_len, int), "y_len must be an integer"
        assert isinstance(x_len, int), "x_len must be an integer"
        assert isinstance(pad, bool), "pad must be a boolean"
        assert y_min >= 0, "y_min must be non-negative"
        assert x_min >= 0, "x_min must be non-negative"
        assert y_len > 0, "y_len must be positive"
        assert x_len > 0, "x_len must be positive"
        assert y_min + y_len <= self.shape[0] or pad, "y_min + y_len must be less than or equal to the height of the image if image is not padded"
        assert x_min + x_len <= self.shape[1] or pad, "x_min + x_len must be less than or equal to the width of the image if image is not padded"
        y_max = min(y_min+y_len, self.shape[0])
        x_max = min(x_min+x_len, self.shape[1])
        region = self.image[y_min:y_max, x_min:x_max].compute()
        if pad and region.shape[:2] != (y_len, x_len):
            pad_y = y_len - region.shape[0]
            pad_x = x_len - region.shape[1]
            if self.ndim == 2:
                region = np.pad(region, ((0, pad_y), (0, pad_x)), mode='constant', constant_values=0)
            elif self.ndim == 3:
                region = np.pad(region, ((0, pad_y), (0, pad_x), (0, 0)), mode='constant', constant_values=0)
        return region

    def show_region(self, y_min: int, x_min: int, y_len: int, x_len:int, pad: bool = False):
        region = self.read_region(y_min, x_min, y_len, x_len, pad)
        plt.imshow(region, cmap='gray' if self.ndim == 2 or len(self.channel_names) == 1 else None)
        plt.axis('off')
        plt.show()

    @abstractmethod
    def show_thumb(self):
        pass
