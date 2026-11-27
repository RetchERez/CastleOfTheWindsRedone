from collections import Counter
import os
from pathlib import Path
import unittest

from build import Executable
from color_resources import GEAR_ICONS, RARITY_COLORS, RT_GROUP_ICON, RT_ICON
from color_resources import _add_corner_marks, _word


def pixels(icon):
    for y in range(32):
        for x in range(32):
            index = y * 32 + x
            color = (icon[104 + index // 2] >> (4 if not index % 2 else 0)) & 15
            masked = bool(icon[616 + index // 8] & (0x80 >> (index % 8)))
            first = 40 + 4 * color
            yield (x, y), None if color == 0 and masked else (masked, tuple(icon[first:first + 3][::-1]))


VANILLA = Path(os.environ.get('COTW_VANILLA', 'private-inputs'))


@unittest.skipUnless(all((VANILLA / f'CASTLE{part}.EXE').is_file() for part in (1, 2)),
                     'Set COTW_VANILLA to the original Win16 executables')
class RarityMarkTests(unittest.TestCase):
    def test_each_icon_has_a_strong_lower_mark_and_keeps_the_original_art(self):
        for part in (1, 2):
            exe = Executable(VANILLA / f'CASTLE{part}.EXE')
            resources = {(kind, identity): data for kind, identity, data in exe.resources()}
            for identity in GEAR_ICONS:
                group = resources[RT_GROUP_ICON, 0x8000 | identity]
                original = resources[RT_ICON, 0x8000 | _word(group, 32)]
                for tier, colors in RARITY_COLORS.items():
                    with self.subTest(part=part, native_icon=identity, tier=tier):
                        added = Counter()
                        lower = Counter()
                        updated = _add_corner_marks(original, colors)
                        for ((_, y), before), (_, after) in zip(pixels(original), pixels(updated)):
                            if before:
                                self.assertEqual(before, after)
                            elif after and after[1] in colors:
                                self.assertFalse(after[0])
                                added[after[1]] += 1
                                if y < 9:
                                    lower[after[1]] += 1
                        self.assertGreaterEqual(sum(added.values()), 105)
                        self.assertGreaterEqual(sum(lower.values()), 42)
                        self.assertTrue(all(lower[color] >= 18 for color in colors))
