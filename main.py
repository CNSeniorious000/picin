from picin import Image, BigImage
from imageio.v3 import imwrite

Image.load_cache()  # failed. cache miss.

img = BigImage("100.png", 30, 100, "input")

# Image.save_cache()

img.process()

imwrite("output.png", img.buffer)
