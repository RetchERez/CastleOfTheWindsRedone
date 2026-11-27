"""Indexed designs for the vermin, animals, reptiles and elementals."""

from PIL import Image, ImageDraw

from draw_more_monsters import (BLACK, BLUE, CYAN, GRAY, GREEN, MAROON, NAVY, OCHRE, RED,
                                SILVER, SIZE, TRANSPARENT, WHITE, YELLOW, export_sprite)
from draw_bestiary import TEAL, beetle, centipede


def blank():
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    return sprite, ImageDraw.Draw(sprite)


def giant_centipede():
    sprite = centipede()
    draw = ImageDraw.Draw(sprite)
    draw.line(((4,13),(2,13),(1,14),(2,15)),fill=BLACK)
    draw.line(((4,16),(3,18),(1,18),(1,17)),fill=BLACK)
    draw.point(((2,14),(2,17)),fill=MAROON)
    return sprite


def giant_beetle():
    sprite = beetle()
    pixels = sprite.load()
    for y in range(SIZE):
        for x in range(SIZE):
            value = pixels[x,y]
            if value == TEAL:
                pixels[x,y] = OCHRE if (x + 2*y) % 5 < 2 else BLACK
            if value == CYAN:
                pixels[x,y] = OCHRE
    return sprite


def toad():
    sprite, draw = blank()
    draw.polygon(((2,21),(5,15),(10,14),(14,17),(13,24),(9,27),(4,27),(1,26)),fill=GREEN,outline=BLACK)
    draw.polygon(((17,17),(23,17),(27,22),(28,25),(25,27),(19,27),(18,24)), fill=OCHRE,outline=BLACK)
    draw.polygon(((5,20),(7,14),(11,12),(15,11),(18,12),(20,10),(25,10),(28,12),
                  (30,15),(30,20),(28,22),(23,23),(18,26),(10,25),(6,23)),fill=OCHRE,outline=BLACK)
    draw.polygon(((17,19),(23,20),(29,17),(29,20),(27,22),(23,22),(18,23),(14,23)),fill=SILVER)
    draw.line(((17,19),(22,20),(26,19),(30,17)),fill=BLACK)
    draw.line(((6,23),(8,22),(10,24),(9,25)),fill=GREEN)
    draw.ellipse((20,11,24,15),fill=YELLOW,outline=BLACK)
    draw.point((22,13),fill=BLACK)
    draw.point(((26,14),(28,16)),fill=BLACK)
    draw.point(((8,17),(10,15),(12,17),(14,14),(15,16),(15,20),(18,16),(11,21)),fill=GREEN)
    draw.point(((9,17),(13,15),(15,17),(16,20)),fill=GRAY)
    draw.line(((23,26),(25,27),(28,26),(30,26)),fill=BLACK)
    return sprite


def slime():
    sprite, draw = blank()
    draw.polygon(((1, 23), (3, 21), (6, 20), (7, 17), (11, 15), (13, 12),
                  (16, 11), (19, 13), (20, 15), (23, 15), (25, 17), (25, 20),
                  (28, 21), (31, 23), (30, 25), (27, 26), (24, 28), (18, 28),
                  (16, 27), (13, 29), (8, 29), (6, 27), (3, 27), (0, 25)),
                 fill=BLACK)
    draw.line(((9, 19), (11, 17), (13, 16), (15, 14), (17, 14)), fill=WHITE)
    draw.line(((22, 17), (23, 18), (23, 19)), fill=WHITE)
    draw.point((7, 21), fill=WHITE)
    return sprite


def rat():
    sprite, draw = blank()
    draw.line(((12,20),(8,21),(5,20),(2,18),(1,15),(1,12),(3,10)),fill=BLACK,width=4)
    draw.line(((12,20),(8,21),(5,20),(2,18),(1,15),(1,12),(3,10)),fill=MAROON,width=2)
    draw.line(((2,15),(2,12),(3,10)),fill=GRAY)
    draw.polygon(((7,19),(9,15),(12,12),(17,11),(21,12),(23,14),(26,14),(28,16),
                  (28,18),(31,20),(30,22),(26,23),(23,22),(19,23),(15,25),(10,24),(8,22)),
                 fill=MAROON,outline=BLACK)
    draw.polygon(((11,20),(14,20),(17,24),(17,26),(12,27),(10,26),(12,25),(10,23)),fill=MAROON,outline=BLACK)
    draw.polygon(((21,20),(25,21),(25,24),(28,25),(27,26),(23,26),(22,24)),fill=MAROON,outline=BLACK)
    draw.ellipse((22,11,27,16),fill=MAROON,outline=BLACK)
    draw.line(((23,13),(25,12)),fill=GRAY)
    draw.line(((12,14),(15,13),(19,13),(21,14)),fill=OCHRE)
    draw.line(((9,18),(13,16),(16,16)),fill=GRAY)
    draw.point(((12,18),(16,15),(17,18),(20,16),(20,19),(22,20)),fill=BLACK)
    draw.point((26,17),fill=YELLOW)
    draw.point(((29,21),(30,21),(29,22)),fill=WHITE)
    return sprite


WOLVES = (
    ('dire-wolf', ((13,16),(8,16),(4,19),(1,18)), 9,16, 19, 14, 3, BLACK, GRAY, SILVER, WHITE),
    ('frost-hound', ((12,17),(7,16),(3,13),(1,13)), 10,18, 18, 15, 5, SILVER, GRAY, WHITE, NAVY),
    ('hell-hound', ((11,14),(7,12),(5,8),(5,5),(2,7)), 8,15, 21, 14, 4, BLACK, MAROON, RED, YELLOW),
)


def canine(name, tail, rear, chest, fore, muzzle_y, ear, hair, shadow, light, eye):
    sprite, draw = blank()
    draw.line(tail,fill=BLACK,width=4)
    draw.line(tail,fill=shadow,width=2)
    for x, y, dx in ((rear,20,-3), (rear+4,21,1), (fore-1,20,3), (fore+3,20,-1)):
        path = ((x,y),(x+1,y+4),(x+dx,27),(x+dx+2,28))
        draw.line(path,fill=BLACK,width=3)
        draw.line(path,fill=shadow)
    points = ((rear-3,16),(rear,13),(rear+3,13),(chest-2,14),(chest+1,11),(fore+1,11),
              (fore+3,12-ear),(fore+5,12-ear+3),(fore+7,13),(fore+8,muzzle_y+1),
              (30,muzzle_y+2),(30,muzzle_y+5),(28,muzzle_y+7),(fore+5,muzzle_y+7),
              (fore+1,22),(chest-3,23),(rear+1,22),(rear-2,21))
    draw.polygon(points,fill=hair,outline=BLACK)
    draw.line(((rear-1,15),(rear+2,15),(chest-3,16),(chest-1,14),(fore+1,13)),fill=shadow)
    draw.line(((chest-2,18),(chest,20),(fore-2,20)),fill=light)
    draw.line(((fore+3,14),(fore+5,13),(fore+7,14)),fill=shadow)
    draw.point((fore+5,15),fill=eye)
    if name == 'dire-wolf':
        draw.line(((fore+6,18),(fore+8,18),(29,17)),fill=GRAY)
        draw.point((29,19),fill=WHITE)
    if name == 'frost-hound':
        draw.line(((fore+6,17),(fore+8,17),(29,18),(29,19),(fore+5,20)),fill=WHITE)
        draw.line(((rear+1,16),(rear+4,16),(rear+6,17)),fill=WHITE)
        draw.point(((fore+4,18),(rear+4,20)),fill=CYAN)
    if name == 'hell-hound':
        draw.line(((fore+4,18),(fore+6,19),(29,18)),fill=RED)
        draw.point(((fore+6,18),(28,19),(fore+4,15)),fill=YELLOW)
        draw.line(((rear+1,17),(rear+3,18),(rear+5,17)),fill=MAROON)
        draw.line(((chest,18),(chest+1,20),(fore-1,20)),fill=MAROON)
    return sprite


def gargoyle():
    sprite, draw = blank()
    for wing in (
        ((13,19),(8,18),(5,15),(2,16),(2,11),(4,7),(4,2),(9,6),(11,10),(16,15)),
        ((20,17),(21,10),(25,6),(29,2),(28,8),(30,13),(29,16),(26,14),(24,16)),
    ):
        draw.polygon(wing,fill=GRAY,outline=BLACK)
    draw.line(((4,3),(5,9),(8,12),(8,17)),fill=SILVER)
    draw.line(((28,4),(26,9),(26,14)),fill=SILVER)
    draw.line(((4,11),(6,13),(5,15)),fill=BLACK)
    draw.line(((10,11),(10,15),(13,16)),fill=BLACK)
    draw.polygon(((9,21),(12,16),(17,13),(22,15),(24,19),(23,23),(21,26),
                  (25,27),(26,29),(20,30),(17,28),(17,25),(14,25),(12,28),(8,30),
                  (4,29),(7,26),(7,24)),fill=GRAY,outline=BLACK)
    draw.polygon(((14,13),(14,9),(16,10),(19,10),(22,8),(22,13),(21,16),(17,16)),fill=GRAY,outline=BLACK)
    draw.line(((17,12),(19,12),(20,13)),fill=BLACK)
    draw.point(((17,13),(20,13)),fill=WHITE)
    draw.line(((15,17),(14,20),(11,22),(9,26)),fill=SILVER)
    draw.line(((22,18),(20,21),(21,23)),fill=SILVER)
    draw.line(((10,23),(13,23),(14,21)),fill=BLACK)
    draw.point(((17,19),(16,21),(16,23),(19,25),(8,28),(24,28)),fill=BLACK)
    draw.line(((10,26),(5,26),(2,24),(1,21)),fill=BLACK,width=2)
    draw.line(((10,26),(5,26),(2,24),(1,21)),fill=GRAY)
    return sprite


def basilisk():
    sprite, draw = blank()
    draw.line(((12,22),(7,21),(3,18),(1,14),(2,10),(4,8)),fill=BLACK,width=4)
    draw.line(((12,22),(7,21),(3,18),(1,14),(2,10),(4,8)),fill=GREEN,width=2)
    for leg in (((10,22),(8,26),(4,27)),((14,21),(14,27),(11,29)),
                ((21,20),(23,25),(19,28)),((24,19),(27,22),(29,25))):
        draw.line(leg,fill=BLACK,width=3)
        draw.line(leg,fill=OCHRE)
    draw.polygon(((6,19),(9,16),(11,16),(12,12),(14,15),(16,14),(17,10),(19,13),
                  (20,13),(22,9),(23,12),(26,11),(29,13),(31,16),(31,19),(29,20),
                  (24,20),(22,22),(16,24),(10,23),(6,22)),fill=GREEN,outline=BLACK)
    draw.line(((10,20),(13,18),(17,17),(21,16),(24,15)),fill=OCHRE)
    draw.line(((9,22),(14,22),(18,21),(23,20)),fill=BLACK)
    draw.line(((25,18),(28,18),(30,17)),fill=BLACK)
    draw.point(((24,14),(25,14)),fill=YELLOW)
    draw.point(((12,17),(15,19),(19,18),(22,15),(28,15)),fill=BLACK)
    return sprite


def cockatrice():
    sprite, draw = blank()
    tail = ((12,19),(8,18),(5,16),(3,12),(3,9),(5,7),(7,7),(9,10),(9,12),(7,13),(6,12))
    draw.line(tail,fill=BLACK,width=4)
    draw.line(tail,fill=GREEN,width=2)
    draw.line(((5,8),(7,8),(8,10)),fill=OCHRE)
    for leg in (((16,23),(15,26),(16,28),(12,29)),((20,22),(21,25),(19,28),(22,29))):
        draw.line(leg,fill=BLACK,width=3)
        draw.line(leg,fill=OCHRE)
    draw.polygon(((11,16),(15,17),(18,15),(19,12),(19,8),(21,6),(24,6),(26,8),
                  (26,11),(29,12),(27,14),(24,14),(23,19),(21,23),(17,25),(13,24),(10,21)),
                 fill=MAROON,outline=BLACK)
    draw.polygon(((12,17),(14,15),(17,16),(20,17),(20,20),(18,22),(15,22),(12,20)),fill=OCHRE,outline=BLACK)
    draw.line(((13,18),(17,18),(18,19),(16,21)),fill=MAROON)
    draw.polygon(((20,7),(20,4),(22,5),(23,2),(24,5),(26,4),(26,7)),fill=RED,outline=BLACK)
    draw.line(((21,8),(24,8),(25,9),(25,11)),fill=OCHRE)
    draw.point((24,10),fill=YELLOW)
    draw.point(((25,14),(25,15),(26,14)),fill=RED)
    draw.line(((26,12),(28,12)),fill=OCHRE)
    return sprite


def lindworm():
    sprite, draw = blank()
    outer = ((27,11),(24,14),(17,15),(10,13),(6,14),(3,17),(3,22),(8,26),(15,27),
             (22,26),(26,22),(24,19),(18,19),(13,21),(8,21))
    draw.line(outer,fill=BLACK,width=6)
    draw.line(outer,fill=GREEN,width=4)
    draw.line(((4,17),(7,15),(11,15),(15,17),(20,17),(24,16)),fill=OCHRE)
    draw.line(((5,22),(9,24),(14,25),(21,24),(24,22)),fill=OCHRE)
    draw.line(((19,20),(15,22),(10,22),(7,21)),fill=OCHRE)
    draw.point(((9,17),(15,15),(22,15),(11,26),(17,26),(22,25),(21,20),(16,21)),fill=BLACK)
    draw.polygon(((24,11),(24,7),(26,5),(29,5),(31,7),(31,10),(29,11),
                  (27,13),(24,13)),fill=GREEN,outline=BLACK)
    draw.line(((25,7),(24,5),(23,4)),fill=OCHRE)
    draw.line(((28,6),(29,3),(30,4)),fill=OCHRE)
    draw.point((28,8),fill=YELLOW)
    draw.line(((29,10),(31,9)),fill=BLACK)
    return sprite


def wyvern(greater):
    sprite, draw = blank()
    if greater:
        tail = ((17,18),(13,22),(9,24),(5,24),(2,22),(2,17),(5,15),(7,17),(6,19))
        wing = ((15,20),(13,14),(8,10),(3,10),(6,7),(5,2),(10,5),(14,4),(15,8),
                (20,8),(19,13),(21,17))
        ribs = (((6,4),(9,9),(14,13),(17,18)),((13,5),(14,11),(17,17)))
        upper, under = OCHRE, MAROON
    else:
        tail = ((15,19),(12,22),(8,24),(5,22),(4,19),(2,17))
        wing = ((15,22),(11,18),(10,14),(6,12),(7,8),(10,10),(12,7),(14,11),
                (17,11),(17,14),(20,15),(19,19))
        ribs = (((8,10),(11,14),(15,19)),((12,8),(13,13),(17,18)))
        upper, under = MAROON, OCHRE
    draw.line(tail,fill=BLACK,width=5 if greater else 3)
    draw.line(tail,fill=upper,width=3 if greater else 1)
    draw.polygon(wing,fill=under,outline=BLACK)
    for rib in ribs:
        draw.line(rib,fill=upper)
    for leg in (((17,22),(16,26),(18,28),(15,30)),((21,21),(22,25),(24,27),(22,29))):
        draw.line(leg,fill=BLACK,width=3)
        draw.line(leg,fill=under)
    draw.polygon(((12,19),(15,16),(20,16),(22,13),(22,9),(25,7),(28,7),(30,9),
                  (31,11),(30,13),(27,14),(25,13),(24,17),(23,20),(20,24),(16,24),(13,22)),
                 fill=upper,outline=BLACK)
    draw.line(((16,19),(19,18),(22,18),(24,15)),fill=under)
    draw.line(((15,21),(18,22),(21,21)),fill=under)
    draw.line(((27,12),(30,11)),fill=BLACK)
    draw.point(((26,10),(29,12)),fill=YELLOW if greater else WHITE)
    if greater:
        draw.line(((23,9),(22,6),(20,5)),fill=BLACK,width=2)
        draw.line(((25,8),(25,6),(27,4)),fill=BLACK,width=2)
    else:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return sprite


def lightning():
    sprite, draw = blank()
    shape = ((17,1),(28,1),(21,8),(25,8),(19,14),(23,14),(14,21),(18,21),
             (3,31),(9,22),(5,22),(14,15),(9,15),(16,9),(11,9))
    draw.polygon(shape,fill=YELLOW,outline=BLUE)
    draw.line(((18,2),(24,2),(18,8),(19,9),(15,13),(18,13),(13,18),
               (15,18),(10,23),(8,25)),fill=WHITE,width=2)
    draw.point(((21,4),(17,11),(18,15),(10,20)),fill=CYAN)
    return sprite


def smoke():
    sprite, draw = blank()
    draw.polygon(((7,27),(3,26),(1,23),(1,20),(4,16),(8,15),(7,11),(9,9),(12,9),
                  (11,6),(13,3),(17,1),(23,2),(26,5),(26,8),(24,11),(23,12),(28,13),
                  (30,16),(30,19),(28,22),(26,23),(27,26),(25,29),(21,30),(16,28),(12,29)),
                 fill=BLACK,outline=BLACK)
    for curl in (
        ((13,8),(13,6),(17,3),(21,3),(24,5),(23,8),(19,9),(17,7)),
        ((10,11),(13,11),(15,13),(13,16),(11,16)),
        ((17,13),(18,11),(22,11),(22,13),(24,14),(27,15),(28,17),(26,20),(23,20)),
        ((4,19),(7,17),(10,17),(12,20),(10,22),(8,21)),
        ((4,24),(7,25),(11,24),(14,25),(16,26),(19,27),(24,27),(25,25),(23,23)),
        ((14,21),(15,19),(18,18),(21,19),(20,22),(18,21)),
    ):
        draw.line(curl,fill=GRAY,width=2)
    draw.point((17,15),fill=RED)
    return sprite


def main():
    designs = (
        ('giant-centipede', giant_centipede()), ('giant-beetle', giant_beetle()),
        ('giant-toad', toad()), ('black-slime', slime()), ('dire-rat', rat()),
        ('gargoyle', gargoyle()), ('basilisk', basilisk()), ('cockatrice', cockatrice()),
        ('lindworm', lindworm()), ('lesser-wyvern', wyvern(False)), ('greater-wyvern', wyvern(True)),
        ('lightning-elemental', lightning()), ('smoke-elemental', smoke()),
    )
    for name, sprite in designs:
        export_sprite(name, sprite)
    for profile in WOLVES:
        export_sprite(profile[0], canine(*profile))


if __name__ == '__main__':
    main()
