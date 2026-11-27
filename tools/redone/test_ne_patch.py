from pathlib import Path
import os
import struct
import sys
import tempfile
import unittest

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK))
from ne_research import Executable
from ne_patch import relocate_segment

VANILLA = Path(os.environ.get('COTW_VANILLA', 'private-inputs'))

@unittest.skipUnless(all((VANILLA / f'CASTLE{part}.EXE').is_file() for part in (1, 2)),
                     'Set COTW_VANILLA to a directory containing both clean Win16 executables')
class RelocationTests(unittest.TestCase):
    def test_added_import_resolves_to_the_original_kernel_module(self):
        source = Executable(VANILLA / 'CASTLE1.EXE')
        with tempfile.TemporaryDirectory() as tmp:
            segment = source.segments[18]
            start = len(segment.data)
            binary = relocate_segment(source.data, 18, segment.data + b'\x9a\xff\xff\0\0\xcb',
                                      {}, {start + 1: (1, 5)})
            path = Path(tmp) / 'import.exe'
            path.write_bytes(binary)
            patched = Executable(path)
            self.assertIn((18, start, ('KERNEL', 5)), patched.calls())

    def test_expanded_segment_preserves_loader_fixups_and_other_segments(self):
        for part, number, target in ((1, 20, 12), (2, 17, 9)):
            with self.subTest(part=part), tempfile.TemporaryDirectory() as tmp:
                source = Executable(VANILLA / f'CASTLE{part}.EXE')
                before = source.segments[number]
                # A new far call uses a selector relocation at operand byte 3.
                patch_pos = len(before.data)
                expanded = before.data + bytes.fromhex('9a1403ffffcb')
                result = relocate_segment(source.data, number, expanded, {patch_pos + 3: target})
                result_path = Path(tmp) / 'patched.exe'
                result_path.write_bytes(result)
                patched = Executable(result_path)
                after = patched.segments[number]
                self.assertEqual(after.data, expanded)
                self.assertGreaterEqual(after.allocation, len(expanded))
                self.assertGreaterEqual(after.file_offset, len(source.data))
                self.assertEqual(after.relocations, {**before.relocations, patch_pos + 3: (2, (target, 0))})
                self.assertIn((number, patch_pos, (target, 0x314)), patched.calls())
                self.assertEqual(list(source.resources()), list(patched.resources()))
                for other in source.segments.keys() - {number}:
                    self.assertEqual(source.segments[other], patched.segments[other])

    def test_refuses_a_segment_base_that_overflows_the_file_sector_field(self):
        source = Executable(VANILLA / 'CASTLE2.EXE')
        alignment = struct.unpack_from('<H', source.ne, 0x32)[0]
        padded = source.data.ljust(0x10000 << alignment, b'\0')
        with self.assertRaisesRegex(ValueError, 'sector'):
            relocate_segment(padded, 17, source.segments[17].data, {})


if __name__ == '__main__':
    unittest.main()
