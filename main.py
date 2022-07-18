from picin import Image, BigImage

Image.load_cache()  # failed. cache miss.

img = BigImage("100.png", 20, "input")

# Image.save_cache()

img.process()
