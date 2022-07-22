from pillow_heif import register_heif_opener
from alive_progress import alive_it
from random import shuffle, choices
from itertools import product
from picin.core import *
from math import dist
import numpy as np


class BigImage:
    register_heif_opener()

    def __init__(self, filename, bs, ss, directory, random_num, r, r_min):
        self.image: np.ndarray = imread(filename)
        self.block_size = bs
        self.square_size = ss
        self.random_num: str = random_num
        self.r: int = r
        self.r_min: int = r_min
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

        self.ny = ny = self.h // bs
        self.nx = nx = self.w // bs
        self.buffer = np.empty((ss * ny, ss * nx, 3), np.uint8)

        ny += r + r
        nx += r + r
        self.log: list[list[Image | None]] = [[None] * nx for _ in range(ny)]

    def weight(self, i, j, image: Image):
        log, r, r_min = self.log, self.r, self.r_min
        i, j = i + r, j + r

        tmp = 0
        for ii in range(i - r, i + r):
            for jj in range(j - r, j + r):
                if log[ii][jj] == image:
                    d = dist((ii, jj), (i, j))
                    if d <= r_min:
                        return 0
                    else:
                        tmp += 1 / d
        return 1 / tmp if tmp else r * 1.45

    def choose(self, i, j) -> Image:
        bs = self.block_size
        y = i * bs
        x = j * bs
        average = self.image[y:y + bs, x:x + bs].mean((0, 1))

        distances = {image.distance(average): image for image in self.assets}  # 方差
        choose_from = sorted(distances)[:self.random_num]
        weight_map = [self.weight(i, j, distances[key]) for key in choose_from]
        result = distances[choices(choose_from, weight_map)[0]]

        self.log[i + self.r][j + self.r] = result

        return result

    def process(self):
        bs, ss, ny, nx = self.block_size, self.square_size, self.ny, self.nx

        locations = list(product(range(ny), range(nx)))
        shuffle(locations)

        for i, j in alive_it(locations):
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
        # Image.show(self)
