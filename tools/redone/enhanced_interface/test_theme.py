"""Verify deterministic Classic and scoped theme patches for audited chapters."""

from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from theme import Executable, THEMES, build, window_targets


class ThemeTest(unittest.TestCase):
    def test_compatible_inputs(self):
        with TemporaryDirectory() as scratch:
            scratch = Path(scratch)
            for part in (1, 2):
                name = f'CASTLE{part}.EXE'
                for source in (ORIGINAL / name, next(ALL_IN_ONE.glob(f'Part {part} -*/{name}'))):
                    for theme in THEMES:
                        with self.subTest(part=part, source=source, theme=theme):
                            original = Executable(source)
                            payload = build(source, part, theme, ASSEMBLER)
                            if theme == 'classic':
                                self.assertEqual(payload, original.data)
                                continue
                            destination = scratch / name
                            destination.write_bytes(payload)
                            updated = Executable(destination)
                            for old, new in zip(original.resources(), updated.resources(), strict=True):
                                self.assertEqual(old[:2], new[:2])
                                self.assertEqual(new[2][:len(old[2])], old[2])
                                self.assertFalse(any(new[2][len(old[2]):]))
                            self.assertEqual(updated.segments[original.dgroup].data, original.segments[original.dgroup].data)
                            self.assertEqual(updated.segments[2].data[0x5d:0x60], bytes.fromhex('90 0e e8'))
                            self.assertNotIn(0x5e, updated.segments[2].relocations)
                            self.assertEqual(updated.ne[0x37] & 8, 0)
                            primary = {2, 4, 5} if part == 1 else {2, 25, 26}
                            for segment in original.segments:
                                if segment not in primary | window_targets(original, part).keys():
                                    self.assertEqual(original.segments[segment].data, updated.segments[segment].data)

    def test_reject_unknown_artifact(self):
        with TemporaryDirectory() as scratch:
            source = Path(scratch) / 'CASTLE1.EXE'
            source.write_bytes((ORIGINAL / source.name).read_bytes() + b'\0')
            with self.assertRaisesRegex(ValueError, 'supported Chapter I'):
                build(source, 1, 'warm', ASSEMBLER)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('all_in_one', type=Path)
    parser.add_argument('assembler')
    args = parser.parse_args()
    ORIGINAL, ALL_IN_ONE, ASSEMBLER = args.original, args.all_in_one, args.assembler
    unittest.main(argv=[__file__], verbosity=2)
