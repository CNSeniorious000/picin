from imageio.v3 import imread
import numpy as np


class Image:
    def __init__(self, path):
        self.buffer: np.ndarray = imread(path)

    def crop_to_square(self):
        h, w = self.buffer.shape
        if h > w:
            y = (h - w) // 2
            self.buffer = self.buffer[y:y + w]
        elif w > h:
            x = (w - h) // 2
            self.buffer = self.buffer[:, x:x + h]
        return self
