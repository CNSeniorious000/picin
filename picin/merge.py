from picin.core import *
import numpy as np
from os import walk
from pillow_heif import register_heif_opener


class BigImage:
    register_heif_opener()

    def __init__(self, filename, block_size, directory):
        self.buffer: np.ndarray = imread(filename)
        self.block_size = block_size
        self.assets = [Image(path) for path in image_paths(directory)]

        w, h = self.buffer.shape[:2]  # cropping

        if y := self.h % block_size:
            self.h = h - y
            y //= 2
            self.buffer = self.buffer[y: y + h]
        else:
            self.h = h

        if x := self.w % block_size:
            self.w = w - x
            x //= 2
            self.buffer = self.buffer[..., x: x + w]
        else:
            self.w = w

    def best(self, i, j):
        bs = self.block_size
        y = i * bs
        x = j * bs
        average = np.mean(self.buffer[y:y + bs, x:x + bs])
        scores = {image.distance(average): image for image in self.assets}
        minimum = min(scores)
        choice = scores[minimum]
        return choice
