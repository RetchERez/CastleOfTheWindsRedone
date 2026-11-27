from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk
import unittest

from windows_setup import SetupWindow


class ThemePreviewTest(unittest.TestCase):
    def setup_window(self, include_assets):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        assets = Path(folder.name)
        (assets / 'interface.json').write_text('{}', encoding='utf-8')
        if include_assets:
            copytree(Path(__file__).with_name('theme_previews'), assets / 'theme_previews')
        root = tk.Tk()
        self.addCleanup(root.destroy)
        root.withdraw()
        return SetupWindow(root, {'name': 'Test Setup', 'version': 'v1.1', 'folder': 'Preview QA',
                                  'default_theme': 'classic'}, assets)

    def test_previews_show_three_screenshots_and_apply_only_selected_theme(self):
        setup = self.setup_window(True)
        setup.theme.set('Warm Stone')
        preview = setup.show_theme_previews()
        setup.root.update_idletasks()
        self.assertEqual(preview.state(), 'withdrawn')
        self.assertIs(setup.show_theme_previews(), preview)
        tabs, = (child for child in preview.children.values() if isinstance(child, ttk.Notebook))
        self.assertEqual([tabs.tab(tab, 'text') for tab in tabs.tabs()], ['Compare', 'Classic', 'Warm Stone', 'Dark Slate'])
        self.assertEqual(tabs.tab(tabs.select(), 'text'), 'Compare')
        self.assertEqual([(picture.width(), picture.height()) for picture in preview.photos],
                         [(1008, 298), *([(640, 480)] * 3)])
        tabs.select(3)
        self.assertEqual(setup.theme.get(), 'Warm Stone')
        use = next(button for frame in preview.children.values() for button in frame.children.values()
                   if isinstance(button, ttk.Button) and button.cget('text') == 'Use Dark Slate')
        use.invoke()
        self.assertEqual(setup.theme.get(), 'Dark Slate')
        self.assertFalse(setup.manage_theme.get())
        self.assertFalse(preview.winfo_exists())

    def test_older_package_still_has_normal_theme_choices_without_screenshots(self):
        setup = self.setup_window(False)
        self.assertCountEqual(setup.theme_combo.cget('values'), ('Classic', 'Warm Stone', 'Dark Slate'))
        self.assertIsNone(setup.show_theme_previews())


if __name__ == '__main__':
    unittest.main()
