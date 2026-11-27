from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from theme_install import digest, set_theme


class LegacyTitleThemeTests(unittest.TestCase):
    def test_theme_changes_keep_the_redone_title_and_upgrade_old_backups(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            index = {'bases': {}, 'classic_upgrades': {}}

            def entry(name, data):
                (root / name).write_bytes(data)
                return {'patch': name, 'patch_sha256': digest(data), 'sha256': digest(data)}

            for chapter in (1, 2):
                old = f'old classic {chapter}'.encode()
                classic = f'redone classic {chapter}'.encode()
                dark = f'old dark {chapter}'.encode()
                (root / f'CASTLE{chapter}.EXE').write_bytes(dark)
                (root / f'CASTLE{chapter} Classic.bin').write_bytes(old)
                (root / f'CASTLE{chapter}.CWG').write_bytes(b'test save')
                index['classic_upgrades'][digest(old)] = entry(f'upgrade-{chapter}', classic)
                index['bases'][digest(old)] = {'dark': entry(f'old-dark-{chapter}', dark),
                                               'warm': entry(f'old-warm-{chapter}', old + b' warm')}
                index['bases'][digest(classic)] = {'warm': entry(f'new-warm-{chapter}', classic + b' warm')}
            (root / 'interface.json').write_text(json.dumps(index), encoding='utf-8')

            for theme, suffix in (('warm', b' warm'), ('classic', b'')):
                set_theme(root, theme, root, lambda original, patch: patch)
                for chapter in (1, 2):
                    classic = f'redone classic {chapter}'.encode()
                    self.assertEqual((root / f'CASTLE{chapter}.EXE').read_bytes(), classic + suffix)
                    self.assertEqual((root / f'CASTLE{chapter} Classic.bak').read_bytes(), classic)
                    self.assertFalse((root / f'CASTLE{chapter} Classic.bin').exists())
                    self.assertEqual((root / f'CASTLE{chapter}.CWG').read_bytes(), b'test save')
