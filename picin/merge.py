from picin.core import *
import numpy as np
from pillow_heif import register_heif_opener
from alive_progress import alive_it
from itertools import product


class BigImage:
    register_heif_opener()

    def __init__(self, filename, block_size, directory):
        self.buffer: np.ndarray = imread(filename)
        self.block_size = block_size
        self.assets = [Image(path) for path in image_paths(directory)]

        # print(len([image.average for image in alive_it(self.assets)]))
        for image in alive_it(self.assets):
            try:
                image.average
            except OSError as err:
                # OSError: image file is truncated
                print(err)
                print(image)
                print(image.path)
                from rich import inspect
                inspect(image)
                exit()

        h, w = self.buffer.shape[:2]  # cropping

        if y := h % block_size:
            self.h = h - y
            y //= 2
            self.buffer = self.buffer[y: y + self.h]
        else:
            self.h = h

        if x := w % block_size:
            self.w = w - x
            x //= 2
            self.buffer = self.buffer[:, x: x + self.w]
        else:
            self.w = w

    def best(self, y, x) -> Image:
        bs = self.block_size
        average = np.mean(self.buffer[y:y + bs, x:x + bs])
        scores = {image.distance(average): image for image in self.assets}
        minimum = min(scores)
        choice = scores[minimum]
        return choice

    def process(self):
        bs = self.block_size

        ny = self.h // bs
        nx = self.w // bs

        for i, j in alive_it(product(range(ny), range(nx)), ny * nx):
            y = i * bs
            x = j * bs
            self.buffer[y:y + bs, x:x + bs] = self.best(y, x).resized(bs)

        # noinspection PyTypeChecker
        Image.show(self)
