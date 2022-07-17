from functools import cached_property, cache
from imageio.v3 import imread
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
        return cv2.resize(self.square, (length, length), interpolation=cv2.INTER_AREA)

    @cached_property
    def average(self) -> np.ndarray:
        try:
            return self.averages[self.path]
        except KeyError:
            result: np.ndarray = self.square.mean((0, 1))
            self.averages[self.path] = result.tolist()
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
    def save_cache(cls, path="averages.yaml"):
        from yaml import dump
        with open(path, "w") as f:
            f.write(dump(cls.averages))

    @classmethod
    def load_cache(cls, path="averages.yaml"):
        from yaml import load, CLoader
        with open(path) as f:
            averages = load(f.read(), CLoader)

        for key, val in averages.items():
            averages[key] = np.array(val)

        cls.averages.update(averages)


if __name__ == '__main__':
    from pillow_heif import register_heif_opener

    register_heif_opener()
    for i in range(10):
        _ = Image("../input/IMG_20220625_194125.HEIC").average
    print(Image.__new__.cache_info())

    print(Image.averages)
    Image.save_cache()
    Image.load_cache()
    print(Image.averages)

    """
    buffer是一个property保证了图片的懒加载
    __new__的缓存保证了相同图片不会重复加载, 也不会重新计算均值
    
    实测大大加快了尤其是HEIF文件的加载速度
    
    但问题是pkl文件太大了, 现在50张图片能有500MB
    """
