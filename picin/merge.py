from picin.core import *
import numpy as np
from pillow_heif import register_heif_opener
from alive_progress import alive_it
from itertools import product


class BigImage:
    register_heif_opener()

    def __init__(self, filename, bs, ss, directory, strategy):
        self.image: np.ndarray = imread(filename)
        self.block_size = bs
        self.square_size = ss
        self.strategy: str = strategy
        self.assets = [Image(path) for path in image_paths(directory)]

        for path in alive_it(image_paths(directory)):
            image = Image(path)
            try:
                # noinspection PyStatementEffect
                image.average
                # image.resized(ss)
                # image.delete_buffer()
            except OSError as err:
                print(err)
                print(image)
                print(image.path)

        h, w = self.image.shape[:2]  # cropping

        if y := h % bs:
            self.h = h - y
            y //= 2
            self.image = self.image[y: y + self.h]
        else:
            self.h = h

        if x := w % bs:
            self.w = w - x
            x //= 2
            self.image = self.image[:, x: x + self.w]
        else:
            self.w = w

        ny = self.h // bs
        nx = self.w // bs

        self.buffer = np.empty((ss * ny, ss * nx, 3), np.uint8)

        self.log = [[None] * (nx + 2) for _ in range(ny + 2)]

    def choose(self, i, j) -> Image:
        bs = self.block_size
        y = i * bs
        x = j * bs
        average = self.image[y:y + bs, x:x + bs].mean((0, 1))

        log = self.log

        i += 1
        j += 1
        neighbors = {log[i - 1][j], log[i + 1][j], log[i][j - 1], log[i][j + 1]}

        distances = {image.distance(average): image
                     for image in self.assets if image not in neighbors}

        if self.strategy == "nearest":
            minimum = min(distances)
            result = distances[minimum]
        elif self.strategy.startswith("random"):
            from random import choice
            n = int(self.strategy.removeprefix("random-"))
            result = distances[choice(sorted(distances)[:n])]
        else:
            raise NotImplementedError

        log[i][j] = result

        return result

    def process(self):
        bs = self.block_size
        ss = self.square_size

        ny = self.h // bs
        nx = self.w // bs

        for i, j in alive_it(product(range(ny), range(nx)), ny * nx):
            y = i * ss
            x = j * ss
            chosen = self.choose(i, j).resized(ss)
            try:
                self.buffer[y:y + ss, x:x + ss] = chosen
            except ValueError as err:
                assert "could not broadcast input array" in err.args[0]
                self.buffer[y:y + ss, x:x + ss, 0] = chosen
                self.buffer[y:y + ss, x:x + ss, 1] = chosen
                self.buffer[y:y + ss, x:x + ss, 2] = chosen

        # noinspection PyTypeChecker
        Image.show(self)
