from picin import Image, BigImage
from imageio.v3 import imwrite

Image.load_cache()


def process(filename, i, bs, ss):
    img = BigImage(filename, bs, ss, "input", 13, 4, 2)
    img.process()
    imwrite(f"output/{i}.png", img.buffer)
