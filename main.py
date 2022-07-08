from glob import glob
from picin import Image
from pillow_heif import register_heif_opener

register_heif_opener()

for file in glob("input/*.HEIC"):
    Image(file).show()
