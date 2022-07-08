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

    def crop_to_square(self):
        h, w = self.buffer.shape[:2]
        if h > w:
            y = (h - w) // 2
            self.buffer = self.buffer[y:y + w]
        elif w > h:
            x = (w - h) // 2
            self.buffer = self.buffer[:, x:x + h]
        return self

    def fit(self, length):
        self.buffer = cv2.resize(self.buffer, (length, length), interpolation=cv2.INTER_AREA)
        return self

    def average(self) -> np.ndarray:
        return self.crop_to_square().buffer.mean(0).mean(0)

    def distance(self, color: np.ndarray):
        return sum((self.average() - color) ** 2)
