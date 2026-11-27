"""Draw the two original monster sprites and export native Win16 icon DIBs."""

from pathlib import Path
from struct import pack

from PIL import Image, ImageDraw

SIZE = 32
TRANSPARENT = 16
VGA = (
    (0, 0, 0), (191, 0, 0), (0, 191, 0), (191, 191, 0),
    (0, 0, 191), (191, 0, 191), (0, 191, 191), (192, 192, 192),
    (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255),
)
BLACK, MAROON, OCHRE, TEAL, GRAY, YELLOW, CYAN = 0, 1, 3, 6, 8, 11, 14


def centipede():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)

    # Paired articulated legs. The body covers the roots of each leg.
    for near, far in [
        ([(8, 15), (5, 16), (3, 19), (3, 21)], [(8, 15), (10, 12), (10, 9)]),
        ([(9, 17), (7, 19), (7, 22), (6, 23)], [(9, 17), (12, 15), (13, 12)]),
        ([(11, 19), (10, 22), (10, 25), (8, 27)], [(11, 19), (13, 17), (16, 16)]),
        ([(13, 21), (13, 24), (11, 28)], [(13, 21), (14, 17), (16, 14)]),
        ([(16, 21), (16, 25), (14, 28)], [(16, 21), (16, 18), (18, 15)]),
        ([(18, 20), (19, 23), (18, 27)], [(18, 20), (18, 16), (17, 13)]),
        ([(20, 18), (22, 21), (22, 24)], [(20, 18), (20, 14), (19, 12)]),
        ([(22, 16), (24, 18), (25, 21)], [(22, 16), (22, 12), (21, 10)]),
        ([(24, 15), (27, 17), (28, 19)], [(24, 15), (25, 12), (24, 10)]),
        ([(26, 15), (29, 16), (30, 18)], [(26, 15), (28, 13), (28, 11)]),
    ]:
        draw.line(near, fill=BLACK)
        draw.line(far, fill=MAROON)

    draw.polygon([(6, 12), (9, 13), (11, 17), (13, 18), (16, 18), (19, 16),
                  (22, 13), (25, 12), (28, 13), (29, 14), (28, 15), (25, 15),
                  (23, 17), (21, 19), (19, 21), (17, 23), (12, 23), (9, 21),
                  (6, 18), (4, 15), (4, 13)], fill=MAROON, outline=BLACK)
    for ridge in [
        [(8, 13), (7, 15), (6, 16)], [(10, 16), (9, 17), (7, 18)],
        [(12, 18), (11, 20), (10, 21)], [(14, 19), (13, 22)],
        [(17, 18), (16, 22)], [(19, 17), (19, 20)],
        [(21, 15), (21, 18)], [(23, 14), (23, 16)], [(25, 13), (25, 14)],
    ]:
        draw.line(ridge, fill=OCHRE)

    draw.polygon([(4, 11), (7, 11), (9, 13), (8, 16), (5, 17), (3, 15),
                  (3, 12)], fill=MAROON, outline=BLACK)
    draw.line([(4, 12), (6, 12), (7, 13)], fill=OCHRE)
    draw.point([(4, 13), (4, 15), (8, 14), (11, 18), (14, 19), (17, 19), (21, 16)], fill=YELLOW)
    draw.line([(4, 11), (3, 9), (1, 8)], fill=BLACK)
    draw.line([(3, 13), (2, 12), (1, 12), (0, 11)], fill=BLACK)
    draw.line([(3, 15), (2, 15), (1, 16)], fill=BLACK)
    return sprite


def beetle():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)

    for leg in [
        [(10, 18), (7, 15), (5, 15), (3, 17)], [(13, 14), (10, 10), (6, 9), (4, 11)],
        [(19, 10), (17, 6), (13, 4), (10, 5)], [(13, 22), (14, 26), (12, 29)],
        [(19, 20), (21, 23), (20, 27), (17, 30)], [(24, 16), (28, 19), (28, 23), (26, 26)],
    ]:
        draw.line(leg, fill=BLACK, width=2)
    draw.line([(7, 15), (6, 15)], fill=GRAY)
    draw.line([(10, 10), (7, 9)], fill=GRAY)
    draw.line([(17, 6), (13, 4)], fill=GRAY)
    draw.point([(14, 26), (21, 23), (28, 19)], fill=GRAY)

    draw.polygon([(13, 12), (18, 7), (21, 6), (25, 6), (28, 8), (29, 11),
                  (29, 15), (27, 19), (24, 22), (20, 24), (16, 24), (12, 21),
                  (11, 16)], fill=BLACK)
    draw.polygon([(13, 14), (17, 9), (21, 7), (24, 7), (27, 9), (28, 11),
                  (28, 15), (26, 19), (22, 22), (19, 23), (16, 22), (13, 20),
                  (12, 17)], fill=TEAL)
    draw.line([(14, 15), (16, 14), (19, 13), (23, 11), (26, 9), (27, 8)], fill=BLACK, width=2)
    draw.line([(16, 11), (18, 9), (21, 8), (23, 8)], fill=CYAN)
    for x, y in [(17, 11), (19, 10), (21, 9), (20, 16), (22, 15), (24, 14), (26, 13),
                 (26, 15), (25, 17), (23, 19), (21, 20), (19, 21), (17, 20)]:
        draw.point((x, y), fill=BLACK)
    draw.line([(26, 12), (25, 13), (24, 14)], fill=GRAY)

    draw.polygon([(11, 14), (13, 14), (16, 17), (18, 21), (16, 23), (13, 25),
                  (9, 22), (8, 18)], fill=BLACK)
    draw.line([(10, 17), (12, 16), (14, 18)], fill=TEAL, width=2)
    draw.line([(11, 18), (14, 20), (14, 22)], fill=TEAL)
    draw.point([(13, 18), (15, 21)], fill=GRAY)

    draw.polygon([(7, 18), (9, 18), (12, 21), (12, 24), (10, 26), (7, 26),
                  (5, 24), (5, 21)], fill=BLACK)
    draw.line([(6, 21), (7, 20), (9, 21), (10, 23), (9, 24)], fill=TEAL)
    draw.point([(6, 22), (9, 24)], fill=YELLOW)
    draw.line([(6, 24), (5, 26), (2, 26), (1, 25)], fill=BLACK)
    draw.line([(8, 25), (7, 28), (5, 29), (4, 28)], fill=BLACK)
    draw.line([(5, 21), (3, 21), (2, 20), (2, 18)], fill=BLACK)
    draw.line([(10, 26), (10, 29), (9, 30)], fill=BLACK)
    return sprite


def monochrome(sprite):
    mono = sprite.copy()
    mono.putdata([TRANSPARENT if value == TRANSPARENT else int(value in (GRAY, YELLOW, CYAN))
                  for value in sprite.tobytes()])
    return mono


def icon_dib(sprite, depth):
    colors = VGA if depth == 4 else ((0, 0, 0), (255, 255, 255))
    bytes_per_row = SIZE * depth // 8
    xor = bytearray(SIZE * bytes_per_row)
    mask = bytearray(SIZE * SIZE // 8)
    for y in range(SIZE):
        source_y = SIZE - 1 - y
        for x in range(SIZE):
            value = sprite.getpixel((x, source_y))
            if value == TRANSPARENT:
                mask[y * (SIZE // 8) + x // 8] |= 128 >> (x % 8)
            else:
                xor[y * bytes_per_row + x * depth // 8] |= value << (8 - depth - x * depth % 8)
    header = pack('<IiiHHIIIIII', 40, SIZE, 2 * SIZE, 1, depth, 0,
                  len(xor) + len(mask), 0, 0, 0, 0)
    palette = bytes(value for red, green, blue in colors for value in (blue, green, red, 0))
    return header + palette + xor + mask


def to_rgba(sprite, depth):
    colors = VGA if depth == 4 else ((0, 0, 0), (255, 255, 255))
    canvas = Image.new('RGBA', (SIZE, SIZE))
    canvas.putdata([(0, 0, 0, 0) if value == TRANSPARENT else (*colors[value], 255)
                    for value in sprite.tobytes()])
    return canvas


def main():
    destination = Path(__file__).parent
    for name, color in [('giant-centipede', centipede()), ('giant-beetle', beetle())]:
        for kind, sprite, depth in [('color', color, 4), ('mono', monochrome(color), 1)]:
            (destination / f'{name}.{kind}.dib').write_bytes(icon_dib(sprite, depth))
            to_rgba(sprite, depth).save(destination / f'{name}.{kind}.png')


if __name__ == '__main__':
    main()
