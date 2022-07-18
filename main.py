from picin import Image, BigImage
from imageio.v3 import imwrite

Image.load_cache()

img = BigImage("in.jpg", 18, 36, "input", "random-3")

# Image.save_cache()

img.process()

imwrite("output.png", img.buffer)
