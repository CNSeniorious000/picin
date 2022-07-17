from functools import cached_property, cache
from imageio.v3 import imread
import numpy as np
import cv2


class Image:
    images = {}

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

    @staticmethod
    def get_square(self: "Image"):
        try:
            return self.images[self]
        except KeyError:
            h, w = self.buffer.shape[:2]
            if h > w:
                y = (h - w) // 2
                result = self.buffer[y:y + w]
            elif w > h:
                x = (w - h) // 2
                result = self.buffer[:, x:x + h]
            else:
                result = self.buffer
            self.images[self] = result
            return result

    @cached_property
    def square(self) -> np.ndarray:
        return self.get_square(self)

    @cache
    def resized(self, length):
        return cv2.resize(self.square, (length, length), interpolation=cv2.INTER_AREA)

    @cached_property
    def average(self) -> np.ndarray:
        return self.square.mean((0, 1))

    def distance(self, color):
        return sum((self.average - color) ** 2) ** 0.5

    def __eq__(self, other):
        return isinstance(other, Image) and self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def __repr__(self):
        return f"<Image from {self.path!r}>"

    @classmethod
    def save_cache(cls, path="cache.pkl", slim=True):
        if slim:
            for image in cls.images:
                if hasattr(image, "buffer"):
                    del image.buffer  # original image

        from pickle import dumps
        from blosc2 import compress
        with open(path, "wb") as f:
            f.write(compress(dumps(cls.images), 1, cname="lz4hc"))

    @classmethod
    def load_cache(cls, path="cache.pkl"):
        from pickle import loads
        from blosc2 import decompress
        with open(path, "rb") as f:
            cls.images = loads(decompress(f.read()))


if __name__ == '__main__':
    from pillow_heif import register_heif_opener

    register_heif_opener()
    for i in range(10):
        print(len(Image.images), end=" ")
        _ = Image("../input/IMG_20220625_194125.HEIC").average
    print(Image.__new__.cache_info())

    Image.save_cache()

    """
    buffer是一个property保证了图片的懒加载
    get_square的缓存保证了相同图片不会重新resize
    __new__的缓存保证了相同图片不会重复加载, 也不会重新计算均值
    
    最后, 持久化缓存保证不带有原图
    
    实测大大加快了尤其是HEIF文件的加载速度
    
    但问题是pkl文件太大了, 现在50张图片能有500MB
    """
