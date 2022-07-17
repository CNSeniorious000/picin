from glob import glob
from picin import Image
from pillow_heif import register_heif_opener

register_heif_opener()

Image.load_cache()  # failed. cache miss.

for file in glob("input/*.HEIC")[:50]:
    print(Image(file).average)

Image.save_cache()
