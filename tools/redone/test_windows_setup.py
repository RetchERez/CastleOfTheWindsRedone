from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import BadZipFile

from windows_setup import friendly_error, next_destination, validate_paths


class SetupPathsTests(unittest.TestCase):
    def test_finds_next_unused_destination(self):
        with TemporaryDirectory() as scratch:
            root = Path(scratch)
            (root / 'Black Background').mkdir()
            (root / 'Black Background (2)').touch()
            self.assertEqual(next_destination(root, 'Black Background'), root / 'Black Background (3)')

    def test_accepts_pasted_paths_with_quotes_spaces_and_apostrophes(self):
        with TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root / "Player's Original.zip"
            source.touch()
            target = root / 'My Redone'
            self.assertEqual(validate_paths(f'"{source}"', f' "{target}" '), (source, target))

    def test_rejects_a_missing_source_or_an_existing_destination(self):
        with TemporaryDirectory() as scratch:
            root = Path(scratch)
            with self.assertRaisesRegex(ValueError, 'Choose the original'):
                validate_paths('', str(root / 'new'))
            with self.assertRaisesRegex(ValueError, 'already exists'):
                validate_paths(str(root), str(root))

    def test_explains_an_invalid_zip(self):
        self.assertIn('ZIP', friendly_error(BadZipFile('bad')))
        self.assertIn('v1.1A', friendly_error(BadZipFile('bad')))


if __name__ == '__main__':
    unittest.main()
