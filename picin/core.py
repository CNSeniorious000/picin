from functools import cached_property, cache
from imageio.v3 import imread
# from rich import print
import numpy as np
import cv2


class Image:
    averages = {}

    @cache
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, path):
        self.path = path

    @cached_property
    def buffer(self):
        return imread(self.path)

    def show(self, buffer: np.ndarray = None):
        from matplotlib.pyplot import imshow, show
        imshow(self.buffer if buffer is None else buffer)
        show()
        return self

    @cached_property
    def square(self) -> np.ndarray:
        h, w = self.buffer.shape[:2]
        if h > w:
            y = (h - w) // 2
            return self.buffer[y:y + w]
        elif w > h:
            x = (w - h) // 2
            return self.buffer[:, x:x + h]
        else:
            return self.buffer

    @cache
    def resized(self, length):
        result = cv2.resize(self.square, (length, length), interpolation=cv2.INTER_AREA)
        self.delete_buffer()
        return result

    # noinspection PyPropertyAccess
    def delete_buffer(self):
        del self.square, self.buffer  # optimize memory of no use

    @cached_property
    def average(self) -> np.ndarray:
        try:
            return self.averages[self.path]
        except KeyError:
            result: np.ndarray = self.square.mean((0, 1))
            # print(f"calculating average of {self}")
            self.averages[self.path] = result
            return result

    def distance(self, color):
        return sum((self.average - color) ** 2) ** 0.5

    def __eq__(self, other):
        return isinstance(other, Image) and self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return f"<Image from {self.path!r}>"

    @classmethod
    def save_cache(cls, path="averages.pkl"):
        from pickle import dumps
        from blosc2 import compress
        with open(path, "wb") as f:
            f.write(compress(dumps(cls.averages, 5)))

    @classmethod
    def load_cache(cls, path="averages.pkl"):
        from os.path import isfile
        if not isfile(path):
            return
        from pickle import loads
        from blosc2 import decompress
        with open(path, "rb") as f:
            cls.averages.update(loads(decompress(f.read())))


def image_paths(asset_dir):
    from glob import glob
    return sum([
        glob(f"{asset_dir}/*.HEIC"),
        glob(f"{asset_dir}/*.png"),
        glob(f"{asset_dir}/*.jpg")
    ], start=[])
