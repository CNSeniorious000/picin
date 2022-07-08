from functools import cached_property, cache
from imageio.v3 import imread
import numpy as np
import cv2


class Image:
    def __init__(self, path):
        self.buffer: np.ndarray = imread(path)

    def show(self):
        from matplotlib.pyplot import imshow, show
        imshow(self.buffer)
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

    @cache
    def resized(self, length):
        return cv2.resize(self.square, (length, length), interpolation=cv2.INTER_AREA)

    @cached_property
    def average(self) -> np.ndarray:
        return self.square.mean((0, 1))

    def distance(self, color):
        return sum((self.average - color) ** 2) ** 0.5
