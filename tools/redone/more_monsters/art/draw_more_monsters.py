"""Draw original 32-pixel icons for More Monsters v1.0."""

from pathlib import Path

from PIL import Image, ImageDraw

DESTINATION = Path(__file__).resolve().parent
from draw_bestiary import (BLACK, GRAY, MAROON, OCHRE, SIZE, TRANSPARENT, YELLOW,
                           VGA, icon_dib)

# The unmodified games use this darker sixteen-color variant for Giant Scorpion.
SCORPION_PALETTE = (
    (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
    (0, 0, 128), (128, 0, 128), (0, 128, 128), (128, 128, 128),
    (192, 192, 192), *VGA[9:],
)

SILVER, GREEN, PURPLE, BLUE, CYAN, WHITE, RED, NAVY = 7, 2, 5, 12, 14, 15, 9, 4


def black_ant():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)
    for leg in (
        ((12, 17), (10, 13), (7, 11), (5, 12)),
        ((14, 16), (14, 11), (11, 8), (8, 8)),
        ((17, 15), (19, 10), (17, 7), (14, 7)),
        ((12, 18), (11, 22), (11, 26), (8, 28)),
        ((14, 18), (16, 21), (16, 25), (14, 28)),
        ((17, 16), (22, 19), (22, 23), (19, 25)),
    ):
        draw.line(leg, fill=BLACK)
        draw.point(leg[1], fill=GRAY)
    draw.line(((15, 17), (20, 14)), fill=BLACK, width=3)
    draw.polygon(((20, 12), (22, 9), (26, 8), (29, 9), (31, 11), (31, 14),
                  (28, 17), (24, 18), (21, 16)), fill=BLACK)
    draw.line(((22, 12), (24, 10), (27, 10), (28, 11)), fill=GRAY)
    draw.point(((25, 11), (29, 13), (26, 15), (24, 16)), fill=GRAY)
    draw.polygon(((10, 16), (13, 14), (17, 14), (19, 16), (18, 19), (14, 21),
                  (11, 20)), fill=BLACK)
    draw.line(((12, 17), (14, 16), (16, 16)), fill=GRAY)
    draw.polygon(((5, 17), (8, 17), (11, 19), (11, 21), (8, 24), (5, 24),
                  (3, 22), (3, 19)), fill=BLACK)
    draw.line(((5, 18), (7, 18), (9, 19)), fill=GRAY)
    draw.point(((5, 20), (7, 22)), fill=GRAY)
    draw.line(((5, 17), (5, 14), (3, 12), (1, 12)), fill=BLACK)
    draw.line(((3, 19), (2, 17), (0, 17)), fill=BLACK)
    draw.line(((3, 21), (1, 22), (1, 24)), fill=BLACK)
    draw.line(((6, 23), (4, 26), (2, 26)), fill=BLACK)
    return sprite


def cave_spider():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)
    for leg in (
        ((16, 15), (9, 12), (8, 8), (3, 5)),
        ((18, 15), (13, 10), (14, 6), (11, 2)),
        ((20, 16), (19, 10), (21, 6), (20, 2)),
        ((22, 17), (24, 11), (28, 10), (30, 6)),
        ((14, 17), (7, 19), (4, 23), (1, 23)),
        ((17, 19), (10, 23), (9, 27), (5, 30)),
        ((19, 20), (16, 25), (18, 28), (15, 31)),
        ((22, 20), (24, 23), (25, 28), (29, 30)),
    ):
        draw.line(leg, fill=BLACK, width=2)
        draw.line(leg[1:3], fill=GRAY)

    draw.polygon(((6, 12), (9, 9), (14, 9), (18, 11), (21, 15), (20, 19),
                  (17, 22), (12, 23), (7, 21), (4, 17), (4, 14)), fill=BLACK)
    draw.polygon(((6, 13), (9, 11), (13, 10), (17, 12), (19, 15), (19, 18),
                  (17, 20), (12, 22), (8, 20), (5, 17), (5, 14)), fill=MAROON)
    draw.line(((6, 14), (8, 12), (11, 11), (13, 11)), fill=GRAY)
    draw.point(((7, 15), (8, 17), (9, 19), (10, 15), (11, 17), (11, 20),
                (13, 14), (13, 18), (14, 20), (15, 16), (16, 19), (17, 15)), fill=BLACK)
    draw.point(((9, 13), (12, 12), (14, 13), (16, 14), (12, 16)), fill=OCHRE)
    draw.polygon(((19, 14), (22, 14), (25, 16), (26, 20), (24, 23), (21, 23),
                  (18, 21), (17, 17)), fill=BLACK)
    draw.line(((19, 16), (21, 15), (23, 16), (24, 17)), fill=GRAY)
    draw.point(((24, 18), (24, 21)), fill=YELLOW)
    draw.line(((25, 18), (28, 18), (29, 20), (28, 21)), fill=BLACK)
    draw.line(((24, 22), (27, 24), (29, 23)), fill=BLACK)
    return sprite


def leech():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)
    draw.polygon(((24, 4), (28, 4), (30, 7), (30, 10), (28, 13), (25, 15),
                  (21, 16), (17, 16), (13, 17), (11, 19), (11, 21), (14, 24),
                  (17, 24), (19, 23), (22, 24), (22, 27), (19, 29), (14, 30),
                  (9, 29), (5, 26), (3, 22), (3, 18), (5, 14), (9, 11),
                  (14, 10), (19, 10), (22, 9), (23, 7)), fill=BLACK)
    for band in (
        ((24, 9), (23, 12), (23, 14)), ((22, 10), (20, 13), (20, 14)),
        ((18, 11), (16, 13), (16, 15)), ((15, 11), (13, 13), (13, 15)),
        ((12, 12), (10, 14), (10, 16)), ((9, 13), (7, 15), (7, 17)),
        ((5, 17), (7, 18), (9, 18)), ((4, 20), (7, 21), (9, 21)),
        ((5, 23), (8, 24), (10, 23)), ((7, 26), (10, 26), (12, 25)),
        ((10, 28), (13, 27), (14, 25)), ((14, 29), (16, 27), (17, 25)),
        ((18, 28), (19, 26), (19, 25)),
    ):
        draw.line(band, fill=OCHRE)
    draw.point(((22, 10), (18, 11), (15, 11), (12, 12), (9, 13), (7, 15),
                (5, 17), (4, 20), (5, 23), (7, 26)), fill=GRAY)
    draw.polygon(((23, 5), (25, 3), (29, 3), (31, 5), (31, 9), (29, 12),
                  (26, 13), (23, 11), (22, 8)), fill=MAROON, outline=BLACK)
    draw.polygon(((26, 5), (29, 5), (30, 7), (29, 9), (27, 11), (25, 10),
                  (24, 8)), fill=BLACK)
    draw.point(((30, 9), (27, 12)), fill=OCHRE)
    draw.point(((24, 6), (28, 4)), fill=GRAY)
    draw.point(((27, 7), (26, 9)), fill=MAROON)
    return sprite


def export_sprite(name, color, palette=SCORPION_PALETTE):
    mono = color.copy()
    mono.putdata([TRANSPARENT if value == TRANSPARENT else int(value in (SILVER, GRAY, YELLOW, CYAN, WHITE))
                  for value in color.tobytes()])
    mono_dib = icon_dib(mono, 1)
    (DESTINATION / f'{name}.mono.dib').write_bytes(mono_dib)

    if palette is SCORPION_PALETTE:
        color = color.copy()
        color.putdata(color.tobytes().translate(bytes.maketrans(b'\x07\x08', b'\x08\x07')))
    base_dib = icon_dib(color, 4)
    palette_bytes = bytes(value for red, green, blue in palette for value in (blue, green, red, 0))
    color_dib = base_dib[:40] + palette_bytes + base_dib[104:]
    (DESTINATION / f'{name}.color.dib').write_bytes(color_dib)
    preview = Image.new('RGBA', (SIZE, SIZE))
    preview.putdata([(0, 0, 0, 0) if value == TRANSPARENT else (*palette[value], 255)
                     for value in color.tobytes()])
    preview.save(DESTINATION / f'{name}.color.png')

def main():
    sprites = (('giant-black-ant', black_ant(), VGA),
               ('giant-cave-spider', cave_spider(), SCORPION_PALETTE),
               ('giant-leech', leech(), SCORPION_PALETTE))
    for name, color, palette in sprites:
        export_sprite(name, color, palette)


if __name__ == '__main__':
    main()
