from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import BadZipFile, ZipFile

from windows_setup import check_source, friendly_error, next_destination, validate_paths


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

    def test_checks_the_selected_archive_and_points_out_incompatible_files(self):
        with TemporaryDirectory() as scratch:
            root = Path(scratch)
            source = root / 'castl11a.zip'
            files = {f'CASTLE{part}.{kind}': b'game' for part in (1, 2) for kind in ('EXE', 'HLP')}
            originals = {name: {'size': len(data), 'sha256': sha256(data).hexdigest()}
                         for name, data in files.items()}
            (root / 'patches.json').write_text(json.dumps({'editions': [{'originals': originals}]}))
            with ZipFile(source, 'w') as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
            check_source(str(source), root)
            with ZipFile(source, 'w') as archive:
                for name, data in {**files, 'CASTLE2.EXE': b'modd'}.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(ValueError, 'castl11a.zip'):
                check_source(str(source), root)


if __name__ == '__main__':
    unittest.main()
