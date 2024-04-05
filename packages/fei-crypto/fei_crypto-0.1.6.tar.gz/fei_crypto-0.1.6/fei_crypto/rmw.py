import os

from PIL import Image
from statistics import mean
from itertools import product
import typer


def rmw(file_path: str, colors: int = 3) -> str:
    img = Image.open(file_path)
    avg = take_color_avg(img, colors)
    width, height = img.size

    for pos in product(range(width), range(height)):
        if sum(img.getpixel(pos)[:3]) > 615 and avg > 381:
            img.putpixel(pos, (255, 255, 255))

        if sum(img.getpixel(pos)[:3]) < 150 and avg <= 381:
            img.putpixel(pos, (0, 0, 0))

    file_name, file_ext = os.path.splitext(file_path)
    new_file_name = file_name + '_rmw' + file_ext
    img.save(new_file_name)
    print(new_file_name)
    return new_file_name


def take_color_avg(img: Image, c: int) -> int:
    small_image = img.resize((80, 80))
    result = small_image.convert(
        "P", palette=Image.ADAPTIVE, colors=c
    )

    palette = result.getpalette()
    color_counts = sorted(result.getcolors(), reverse=True)
    colors = list()

    for i in range(c):
        palette_index = color_counts[i][1]
        dominant_color = palette[palette_index * 3: palette_index * 3 + 3]
        colors.append(tuple(dominant_color))

    color_sum = list(map(sum, colors))
    return mean(color_sum)


if __name__ == '__main__':
    typer.run(rmw)
