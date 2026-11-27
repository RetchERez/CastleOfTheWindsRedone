"""Indexed designs for the humanoid members of the expanded bestiary."""

from dataclasses import dataclass

from PIL import Image, ImageDraw

from draw_more_monsters import (BLACK, CYAN, GRAY, GREEN, MAROON, NAVY, OCHRE, PURPLE,
                                RED, SILVER, SIZE, TRANSPARENT, WHITE, YELLOW, export_sprite)


@dataclass(frozen=True)
class Figure:
    slug: str
    height: int
    width: int
    skin: int
    cloth: int
    trim: int
    head: str
    weapon: str
    shield: str = ''
    cloak: bool = False
    reverse: bool = False


FIGURES = (
    Figure('goblin-archer', 21, 4, GREEN, OCHRE, MAROON, 'goblin', 'bow'),
    Figure('goblin-shaman', 24, 4, GREEN, MAROON, OCHRE, 'goblin', 'staff', cloak=True, reverse=True),
    Figure('kobold-warrior', 20, 5, OCHRE, MAROON, SILVER, 'kobold', 'spear', 'wood'),
    Figure('skeleton-archer', 26, 4, WHITE, SILVER, GRAY, 'skull', 'bow', reverse=True),
    Figure('skeleton-warrior', 27, 5, WHITE, SILVER, GRAY, 'skull', 'sword', 'buckler'),
    Figure('ghoul', 23, 5, GRAY, BLACK, MAROON, 'ghoul', 'claws'),
    Figure('orc-warrior', 26, 7, OCHRE, MAROON, GRAY, 'orc', 'axe', reverse=True),
    Figure('orc-archer', 25, 7, OCHRE, GREEN, MAROON, 'orc', 'bow'),
    Figure('black-dwarf', 21, 7, OCHRE, GRAY, SILVER, 'dwarf', 'hammer'),
    Figure('bandit-swordsman', 27, 5, OCHRE, MAROON, OCHRE, 'hood', 'sword', cloak=True, reverse=True),
    Figure('animated-suit-of-armor', 28, 7, BLACK, SILVER, WHITE, 'hollow', 'sword'),
    Figure('draugr', 26, 6, SILVER, NAVY, GRAY, 'iron', 'short-sword', 'iron'),
    Figure('barrow-draugr', 27, 6, GRAY, MAROON, OCHRE, 'bronze', 'axe', 'dark', cloak=True, reverse=True),
    Figure('fallen-knight', 29, 7, BLACK, GRAY, SILVER, 'fallen', 'sword', 'broken'),
    Figure('dark-sorcerer', 28, 5, OCHRE, PURPLE, GRAY, 'human', 'staff', cloak=True),
    Figure('lesser-fire-devil', 23, 5, MAROON, RED, OCHRE, 'devil', 'claws', reverse=True),
)


def draw_head(draw, figure, x, y):
    kind = figure.head
    width = 3 if figure.width < 6 else 4
    skin = figure.skin
    draw.polygon(((x-width,y+2),(x-width+1,y),(x+width-1,y),(x+width,y+2),
                  (x+width,y+5),(x+2,y+7),(x-2,y+7),(x-width,y+5)), fill=skin, outline=BLACK)
    if kind in ('goblin', 'orc', 'kobold'):
        ear = 7 if kind == 'orc' else 5
        draw.polygon(((x-width,y+2),(x-ear,y+1),(x-ear+1,y+4),(x-2,y+5)), fill=skin, outline=BLACK)
        draw.polygon(((x+width-1,y+2),(x+ear,y),(x+ear-1,y+3),(x+2,y+5)), fill=skin, outline=BLACK)
        draw.point(((x-1,y+3),(x+2,y+3)), fill=YELLOW)
        draw.line(((x,y+5),(x+2,y+5)), fill=BLACK)
        if kind == 'orc':
            draw.point(((x-1,y+5),(x+3,y+5)), fill=WHITE)
        if kind == 'kobold':
            draw.line(((x+2,y+4),(x+5,y+5),(x+4,y+6),(x+1,y+6)), fill=skin)
            draw.point((x+5,y+5), fill=BLACK)
    elif kind == 'skull':
        draw.line(((x-2,y+3),(x+2,y+3)), fill=BLACK)
        draw.point(((x,y+3),(x-1,y+2),(x+1,y+2)), fill=WHITE)
        draw.point(((x,y+4),(x-1,y+6),(x+1,y+6)), fill=BLACK)
    elif kind in ('dwarf', 'iron', 'bronze', 'hollow', 'fallen'):
        helm = {'dwarf':GRAY,'iron':GRAY,'bronze':OCHRE,'hollow':SILVER,'fallen':GRAY}[kind]
        top = WHITE if kind == 'hollow' else SILVER
        draw.polygon(((x-width-1,y+3),(x-width,y+1),(x-2,y-1),(x+2,y-1),(x+width,y+1),
                      (x+width+1,y+3),(x+width,y+5),(x-width,y+5)), fill=helm, outline=BLACK)
        draw.line(((x-2,y),(x+1,y),(x+2,y+1)), fill=top)
        draw.line(((x-width+1,y+3),(x+width-1,y+3)), fill=BLACK)
        if kind in ('dwarf', 'bronze', 'iron'):
            draw.line(((x,y+2),(x,y+5)), fill=helm)
            draw.point((x+2,y+3), fill=WHITE if kind != 'dwarf' else OCHRE)
        if kind == 'dwarf':
            draw.polygon(((x-4,y+4),(x-2,y+5),(x+3,y+4),(x+4,y+6),(x+1,y+8),(x-2,y+7)), fill=BLACK)
            draw.point((x+1,y+6), fill=GRAY)
        if kind == 'fallen':
            draw.line(((x+2,y),(x+3,y+2),(x+2,y+4),(x+3,y+6)), fill=BLACK)
        if kind == 'hollow':
            draw.line(((x-2,y+5),(x+2,y+5)), fill=GRAY)
    elif kind == 'hood':
        draw.polygon(((x-5,y+3),(x-3,y),(x+1,y-2),(x+4,y),(x+5,y+5),(x+3,y+7),
                      (x-3,y+7)), fill=MAROON, outline=BLACK)
        draw.line(((x-1,y+2),(x+2,y+2),(x+2,y+5),(x,y+5)), fill=OCHRE)
        draw.point((x+1,y+3), fill=BLACK)
    elif kind == 'devil':
        draw.line(((x-3,y+2),(x-5,y),(x-5,y-2)), fill=MAROON, width=2)
        draw.line(((x+2,y+1),(x+4,y),(x+4,y-3)), fill=MAROON, width=2)
        draw.point(((x-2,y+3),(x+2,y+3)), fill=YELLOW)
        draw.line(((x-1,y+6),(x+2,y+5)), fill=BLACK)
    else:
        draw.line(((x-width+1,y+1),(x+width-1,y+1)), fill=BLACK)
        draw.line(((x-2,y+3),(x-1,y+3)), fill=BLACK)
        draw.point(((x+2,y+3),(x+1,y+5)), fill=BLACK)
        if kind == 'ghoul':
            draw.line(((x-2,y+6),(x+1,y+6)), fill=WHITE)


def draw_weapon(draw, kind, x, y):
    if kind == 'bow':
        draw.line(((x-2,y-8),(x+1,y-6),(x+3,y-2),(x+3,y+2),(x+1,y+6),(x-2,y+8)),
                  fill=BLACK, width=2)
        draw.line(((x-2,y-8),(x+1,y-5),(x+2,y-1),(x+2,y+2),(x,y+6),(x-2,y+8)), fill=OCHRE)
        draw.line(((x-2,y-7),(x-2,y+7)), fill=GRAY)
        draw.line(((x-7,y),(x+5,y)), fill=SILVER)
        draw.point(((x+4,y-1),(x+4,y+1)), fill=WHITE)
    elif kind in ('sword', 'short-sword'):
        blade = 13 if kind == 'sword' else 10
        draw.polygon(((x-2,y-3),(x-1,y-blade+2),(x+1,y-blade),(x+2,y-blade+3),
                      (x+1,y-3)), fill=SILVER, outline=BLACK)
        draw.line(((x,y-4),(x+1,y-blade+2)), fill=WHITE)
        draw.line(((x-3,y-3),(x+3,y-3)), fill=BLACK)
        draw.line(((x,y-2),(x,y+3)), fill=OCHRE)
    elif kind == 'axe':
        draw.line(((x-2,y+7),(x+1,y-10)), fill=BLACK, width=2)
        draw.line(((x-2,y+7),(x+1,y-10)), fill=OCHRE)
        draw.polygon(((x-3,y-10),(x+1,y-8),(x+4,y-9),(x+5,y-6),(x+4,y-3),
                      (x+1,y-5),(x-3,y-5)), fill=SILVER, outline=BLACK)
        draw.line(((x+4,y-8),(x+4,y-5)), fill=WHITE)
    elif kind == 'hammer':
        draw.line(((x-2,y+6),(x+1,y-7)), fill=BLACK, width=2)
        draw.line(((x-2,y+6),(x+1,y-7)), fill=OCHRE)
        draw.rectangle((x-4,y-10,x+4,y-5), fill=GRAY, outline=BLACK)
        draw.line(((x-3,y-9),(x+3,y-9)), fill=SILVER)
    elif kind == 'staff':
        draw.line(((x-2,y+12),(x,y-13),(x-2,y-14),(x-3,y-12)), fill=BLACK, width=2)
        draw.line(((x-2,y+10),(x,y-12),(x-2,y-13)), fill=OCHRE)
    elif kind == 'spear':
        draw.line(((x-5,y+8),(x+4,y-11)), fill=BLACK, width=2)
        draw.line(((x-5,y+8),(x+4,y-10)), fill=OCHRE)
        draw.polygon(((x+3,y-13),(x+6,y-15),(x+5,y-10),(x+3,y-9)), fill=SILVER, outline=BLACK)


def draw_shield(draw, kind, x, y):
    if kind == 'broken':
        draw.polygon(((x-4,y-5),(x+3,y-5),(x+2,y-2),(x+4,y-1),(x+3,y+3),
                      (x,y+6),(x-4,y+3)), fill=GRAY, outline=BLACK)
        draw.line(((x+2,y-2),(x-1,y),(x+1,y+1),(x,y+4)), fill=BLACK)
        draw.line(((x-3,y-3),(x-3,y+2)), fill=SILVER)
        return
    if kind == 'buckler':
        box = (x-3,y-4,x+3,y+3)
    else:
        box = (x-5,y-5,x+5,y+5)
    color = {'wood':MAROON,'buckler':GRAY,'iron':GRAY,'dark':BLACK}[kind]
    draw.ellipse(box, fill=color, outline=GRAY if kind == 'dark' else BLACK)
    draw.line(((x-2,y-3),(x-3,y-1)), fill=OCHRE if kind in ('wood','dark') else SILVER)
    draw.rectangle((x-1,y-1,x+1,y+1), fill=GRAY if kind == 'dark' else SILVER, outline=BLACK)


def humanoid(figure):
    sprite = Image.new('P', (SIZE, SIZE), TRANSPARENT)
    draw = ImageDraw.Draw(sprite)
    head_y = 30 - figure.height
    x = 13 if figure.weapon == 'bow' else 15
    leg_y = max(head_y + 13, 21)
    shoulders_y = head_y + 8
    hip = figure.width - 1
    skeleton = figure.head == 'skull'
    armored = figure.head in ('fallen', 'hollow', 'iron', 'bronze', 'dwarf')

    if figure.head == 'devil':
        draw.line(((x-3,leg_y),(7,25),(5,28),(3,27)), fill=BLACK, width=3)
        draw.line(((x-3,leg_y),(7,25),(5,28),(3,27)), fill=MAROON)
        draw.polygon(((3,25),(1,27),(3,29)), fill=MAROON, outline=BLACK)
    if figure.cloak:
        draw.polygon(((x-3,shoulders_y-1),(x+3,shoulders_y-1),(x+figure.width,23),
                      (x+figure.width+1,28),(x+3,27),(x+1,29),(x-2,28),(x-5,30),
                      (x-figure.width-2,28)), fill=figure.cloth, outline=BLACK)
        draw.line(((x-2,shoulders_y+1),(x-3,21),(x-6,27)), fill=figure.trim)
        draw.line(((x+2,14),(x+4,24),(x+4,26)), fill=BLACK)
    if skeleton:
        for path in (((x-2,leg_y),(x-4,25),(x-4,29),(x-6,30)),
                     ((x+2,leg_y),(x+3,25),(x+2,29),(x+5,30))):
            draw.line(path, fill=BLACK, width=3)
            draw.line(path, fill=WHITE)
            draw.point(path[1], fill=SILVER)
    elif figure.head != 'human':
        for direction in (-1,1):
            attach = x + direction * (hip-2)
            knee = x + direction * (hip-1)
            foot = x + direction * (hip+1)
            draw.polygon(((attach-2,leg_y),(attach+2,leg_y),(knee+2,26),(knee+1,28),
                          (foot+1 if direction==1 else foot-1,29),
                          (foot+1 if direction==1 else foot-1,30),(knee-2,30),(knee-2,27)),
                         fill=figure.cloth if armored else BLACK, outline=BLACK)
            draw.line(((attach,leg_y+2),(knee,27)), fill=figure.trim)

    if figure.weapon == 'bow':
        front_hand = (23, shoulders_y+2)
        far_hand = (20, shoulders_y+4)
    elif figure.weapon == 'claws':
        front_hand = (x+figure.width+5, min(29,shoulders_y+13))
        far_hand = (x-figure.width-4, min(29,shoulders_y+12))
    else:
        front_hand = (25, shoulders_y+4)
        far_hand = (x-figure.width-3, shoulders_y+8)
    upper_color = WHITE if skeleton else figure.skin if not armored else figure.cloth
    for path in (((x-hip,shoulders_y),(x-figure.width-2,shoulders_y+4),far_hand),
                 ((x+hip,shoulders_y),(x+figure.width+2,shoulders_y+3),front_hand)):
        draw.line(path, fill=BLACK, width=3 if skeleton else 5)
        draw.line(path, fill=upper_color, width=1 if skeleton else 3)
        draw.point(path[1], fill=figure.trim)
    if figure.weapon == 'claws':
        for hand in (front_hand,far_hand):
            for dx in (-2,0,2):
                draw.line((hand,(hand[0]+dx,min(31,hand[1]+3))), fill=upper_color)

    if skeleton:
        draw.line(((x,shoulders_y-1),(x,leg_y+1)), fill=BLACK, width=4)
        draw.line(((x,shoulders_y-1),(x,leg_y+1)), fill=WHITE)
        for dy in (0,2,4,6):
            draw.line(((x-hip,shoulders_y+dy),(x-hip+1,shoulders_y+dy+1),
                       (x+hip-1,shoulders_y+dy+1),(x+hip,shoulders_y+dy)), fill=WHITE)
        draw.line(((x-2,leg_y),(x+2,leg_y)), fill=SILVER)
    else:
        if figure.cloak:
            shape = ((x-hip,shoulders_y-1),(x+hip,shoulders_y-1),(x+hip-1,leg_y-1),
                     (x+hip+2,28),(x+2,29),(x,27),(x-3,29),(x-hip-1,28),(x-hip,leg_y))
        else:
            shape = ((x-hip,shoulders_y-1),(x+hip,shoulders_y-1),(x+hip+1,shoulders_y+2),
                     (x+hip-1,leg_y),(x-hip+1,leg_y),(x-hip-1,shoulders_y+2))
        draw.polygon(shape, fill=figure.cloth, outline=BLACK)
        draw.line(((x-hip+1,shoulders_y+1),(x,shoulders_y+3),
                   (x+hip-1,shoulders_y+1)), fill=figure.trim)
        draw.line(((x-hip+2,leg_y-2),(x+hip-2,leg_y-2)), fill=BLACK)
        draw.rectangle((x-1,leg_y-2,x,leg_y-1), fill=figure.trim)
        if figure.head == 'hollow':
            draw.line(((x-4,shoulders_y+4),(x,shoulders_y+6),(x+4,shoulders_y+4)), fill=GRAY)
        if figure.head == 'ghoul':
            draw.point(((x-3,leg_y),(x-1,leg_y+1),(x+3,leg_y)), fill=GRAY)
        if figure.head == 'devil':
            draw.point(((x-2,shoulders_y+3),(x+2,shoulders_y+3),(x,leg_y-4)), fill=OCHRE)

    draw_head(draw, figure, x-2 if figure.head == 'ghoul' else x, head_y)
    draw_weapon(draw, figure.weapon, *front_hand)
    if figure.shield:
        draw_shield(draw, figure.shield, far_hand[0]+1, far_hand[1]-2)
    if figure.reverse:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return sprite


TROLLS = (
    ('forest-troll', 4, 3, 2, GREEN, OCHRE, GRAY),
    ('cave-troll', 2, 4, 0, GRAY, MAROON, OCHRE),
    ('stone-troll', 7, 5, 1, GRAY, SILVER, BLACK),
    ('frost-troll', 1, 2, 3, SILVER, NAVY, WHITE),
    ('fire-troll', 3, 3, 1, MAROON, OCHRE, RED),
)


def troll(name, head_y, breadth, arm_raise, skin, shadow, light):
    sprite = Image.new('P',(SIZE,SIZE),TRANSPARENT)
    draw = ImageDraw.Draw(sprite)
    shoulder = 7 - breadth
    for side in (0,1):
        def face(point):
            return (31-point[0], point[1]) if side else point

        arm = ((shoulder+1,head_y+7),(shoulder+4,head_y+6),(shoulder+5,head_y+10),
               (shoulder+3,17),(shoulder+3,23-arm_raise),(shoulder+1,27-arm_raise),
               (shoulder-2,27-arm_raise),(shoulder-2,23-arm_raise),(shoulder-1,17),(shoulder-1,head_y+10))
        draw.polygon(tuple(map(face,arm)),fill=skin,outline=BLACK)
        draw.line(tuple(map(face,((shoulder,head_y+11),(shoulder,18),(shoulder-1,22-arm_raise)))),fill=light)
        draw.line(tuple(map(face,((shoulder+3,17),(shoulder+2,22-arm_raise),(shoulder+1,25-arm_raise)))),fill=shadow)
        draw.line(tuple(map(face,((shoulder,25-arm_raise),(shoulder,27-arm_raise)))),fill=BLACK)
        leg = ((10-breadth//2,20),(15,20),(15,26),(13,29),(13,31),
               (7,31),(6,30),(7,29),(9,25))
        draw.polygon(tuple(map(face,leg)),fill=skin,outline=BLACK)
        draw.line(tuple(map(face,((12,24),(11,29),(8,30)))),fill=shadow)

    draw.polygon(((8-breadth//2,head_y+8),(12,head_y+5),(19,head_y+5),
                  (23+breadth//2,head_y+8),(23,21),(20,25),(16,24),(12,25),(8,22)),fill=skin,outline=BLACK)
    draw.polygon(((10,21),(15,22),(20,21),(21,24),(19,26),(16,24),(11,26)),fill=shadow,outline=BLACK)
    draw.line(((8,head_y+12),(12,head_y+10),(15,head_y+12)),fill=light)
    draw.line(((17,head_y+12),(20,head_y+10),(23,head_y+12)),fill=light)
    draw.line(((16,head_y+13),(16,head_y+16)),fill=shadow)
    draw.polygon(((12,head_y),(18,head_y),(21,head_y+3),(21,head_y+6),
                  (18,head_y+9),(13,head_y+8),(11,head_y+6),(10,head_y+3)),fill=skin,outline=BLACK)
    draw.line(((12,head_y+2),(15,head_y+2),(16,head_y+4),(18,head_y+2),(20,head_y+2)),fill=shadow)
    draw.point(((14,head_y+4),(18,head_y+4)),fill=YELLOW if skin != SILVER else NAVY)
    draw.line(((13,head_y+6),(18,head_y+6)),fill=BLACK)
    draw.point(((14,head_y+6),(17,head_y+6)),fill=WHITE)
    if name == 'forest-troll':
        draw.line(((10,head_y+3),(9,head_y+2),(8,head_y+2)),fill=GREEN)
        draw.point(((7,17),(10,19),(12,17),(21,18),(25,16),(24,23)),fill=OCHRE)
    if name == 'cave-troll':
        draw.line(((6,15),(7,17),(6,20)),fill=SILVER)
        draw.line(((24,14),(26,17),(25,19)),fill=SILVER)
    if name == 'stone-troll':
        for x,y in ((11,15),(18,16),(9,21),(21,22),(4,21),(26,21)):
            draw.line(((x-1,y+2),(x,y),(x+2,y+1)),fill=BLACK)
    if name == 'frost-troll':
        draw.polygon(((13,1),(15,0),(16,2),(18,0),(20,3),(17,3)),fill=WHITE)
        draw.line(((11,18),(14,20),(16,19),(20,18)),fill=WHITE)
        draw.point(((6,14),(24,14),(12,26),(19,27)),fill=CYAN)
    if name == 'fire-troll':
        draw.point(((7,14),(9,15),(10,14),(11,16),(19,16),(20,15),(23,15),(24,14),
                    (6,19),(7,20),(24,20),(26,19),(11,28),(20,28)),fill=YELLOW)
    return sprite


def main():
    for design in FIGURES:
        export_sprite(design.slug, humanoid(design))
    for profile in TROLLS:
        export_sprite(profile[0], troll(*profile))


if __name__ == '__main__':
    main()
