from os import environ
from pathlib import Path
import unittest

from title_art import brand, decode_rows, splash_resources


VANILLA = Path(environ.get('COTW_VANILLA', 'private-inputs'))


@unittest.skipUnless(all((VANILLA / f'CASTLE{part}.EXE').is_file() for part in (1, 2)),
                     'Set COTW_VANILLA to a folder containing the registered v1.1A games')
class TitleArtTests(unittest.TestCase):
    def test_both_chapters_keep_original_art_and_palette(self):
        for part in (1, 2):
            with self.subTest(part=part):
                data = (VANILLA / f'CASTLE{part}.EXE').read_bytes()
                painted = brand(data)
                self.assertEqual(len(data), len(painted))
                (old, old_chapter), (new, new_chapter) = splash_resources(data), splash_resources(painted)
                self.assertEqual(old_chapter, new_chapter)
                restored = bytearray(painted)
                self.assertEqual(old.offset, new.offset)
                self.assertEqual(old.body[40:104], new.body[40:104])
                original_rows = decode_rows(old.body)
                rows = zip(original_rows, decode_rows(new.body), strict=True)
                changes = [(y, original, replacement) for y, (previous, current) in enumerate(rows)
                           for original, replacement in zip(previous, current, strict=True)
                           if original != replacement]
                self.assertGreater(len(changes), 40)
                self.assertTrue(all(210 <= y < 230 and original == 0 for y, original, _ in changes))
                self.assertEqual({pixel for _, _, pixel in changes}, {3, 11, 15})
                restored[old.offset:old.offset + len(old.body)] = old.body
                self.assertEqual(bytes(restored), data)
