from main import *

for i in range(220):
    img = BigImage(f"output/part-2/input/{i}.png", 13, 13, "input", 13, 4, 2)
    img.process()
    imwrite(f"output/part-2/output/{i}.png", img.buffer)
