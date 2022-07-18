from picin import Image, BigImage
from imageio.v3 import imwrite

Image.load_cache()


def main():
    img = BigImage("1.png", 20, 20, "input", 13, 4, 2)
    # Image.save_cache()
    img.process()
    imwrite("output.png", img.buffer)


if __name__ == '__main__':
    main()
