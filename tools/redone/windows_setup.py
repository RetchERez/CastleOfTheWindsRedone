"""Double-click installer for a single Castle of the Winds Redone package."""

import argparse
import json
import os
from pathlib import Path
from queue import Empty, Queue
import sys
from threading import Thread
import time
import tkinter as tk
from tkinter import filedialog, ttk
from zipfile import BadZipFile

from apply_diabloloot import apply_delta, install, read_install_source
from theme_install import THEME_INDEX, THEME_NAMES, set_theme

ASSETS = Path(__file__).resolve().with_name('redone-package')
SOURCE_PROMPT = 'For a new install, select the original Win16 v1.1A archive (castl11a.zip).'
SOURCE_READY = 'Both games and Help files verified. Check the destination and click Install.'


def next_destination(parent, name):
    candidate = parent / name
    number = 2
    while candidate.exists():
        candidate = parent / f'{name} ({number})'
        number += 1
    return candidate


def source_path(source_text):
    source_text = source_text.strip().strip('"')
    if not source_text:
        raise ValueError('Choose the original v1.1A ZIP (castl11a.zip) or game folder')
    source = Path(source_text).expanduser().resolve()
    if not source.exists():
        raise ValueError('Choose the original ZIP or an existing game folder')
    return source


def check_source(source_text, assets):
    read_install_source(source_path(source_text), assets)


def validate_paths(source_text, target_text):
    source = source_path(source_text)
    target_text = target_text.strip().strip('"')
    if not target_text:
        raise ValueError('Choose a destination folder')
    target = Path(target_text).expanduser().resolve()
    if target.exists():
        raise ValueError('The destination already exists. Choose a new folder so your files stay safe')
    if any(parent.is_file() for parent in target.parents):
        raise ValueError('Choose a destination under an existing drive or folder')
    return source, target


def friendly_error(error):
    if isinstance(error, BadZipFile):
        return 'That ZIP could not be opened. Select a fresh copy of castl11a.zip for Win16 v1.1A.'
    if isinstance(error, FileExistsError):
        return 'The destination already exists. Choose a new folder so your files stay safe.'
    if isinstance(error, PermissionError):
        return 'Windows could not save the files there. Try a new folder under Documents.'
    if isinstance(error, ValueError):
        message = str(error).rstrip('.')
        if message.startswith(('Missing ', 'Unexpected or duplicate ')):
            return f'{message}. Try the original castl11a.zip or choose the folder with both games and Help files.'
        return message + '.'
    if isinstance(error, OSError):
        return 'Setup could not read the source or write the destination. Check the paths and available disk space.'
    return 'Setup could not complete. Re-download the installer and try again.'


class SetupWindow:
    def __init__(self, root, settings, assets):
        self.root, self.assets = root, assets
        self.name = settings['name']
        self.folder_name = settings['folder']
        self.events = Queue()
        self.busy = False
        self.installed = None
        self.error = None
        self.rejected_source = None
        self.theme_names = {name: key for key, name in THEME_NAMES.items()}
        self.with_themes = (assets / THEME_INDEX).is_file()
        default_theme = settings.get('default_theme', 'classic')
        self.theme = tk.StringVar(value=THEME_NAMES[default_theme])
        self.manage_theme = tk.BooleanVar(value=False)

        root.title(f'{self.name} Setup')
        root.minsize(705, 505 if self.with_themes else 410)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        root.protocol('WM_DELETE_WINDOW', self.close)
        if (assets / 'redone.ico').is_file():
            root.iconbitmap(default=str(assets / 'redone.ico'))
        root.option_add('*Font', ('Segoe UI', 10))
        style = ttk.Style(root)
        style.configure('Step.TLabel', font=('Segoe UI', 11, 'bold'))
        style.configure('Muted.TLabel', foreground='#4f5360')
        style.configure('Status.TLabel', foreground='#2f455d')
        style.configure('Error.TLabel', foreground='#9b2121')

        header = tk.Frame(root, background='#202936', padx=24, pady=15)
        header.grid(row=0, column=0, sticky='ew')
        tk.Label(header, text='Castle of the Winds I & II: Redone', font=('Segoe UI', 19, 'bold'),
                 foreground='#ffffff', background='#202936', anchor='w').pack(fill='x')
        tk.Label(header, text=f'{self.name}  •  {settings["version"]}  •  Both chapters',
                 font=('Segoe UI', 10), foreground='#ead1a8', background='#202936',
                 anchor='w').pack(fill='x', pady=(4, 0))

        form = ttk.Frame(root, padding=(24, 16, 24, 14))
        form.grid(row=1, column=0, sticky='nsew')
        form.columnconfigure(0, weight=1)
        self.source = tk.StringVar()
        install_parent = Path.home() / 'Documents' / 'Castle of the Winds Redone'
        self.target = tk.StringVar(value=str(next_destination(install_parent, self.folder_name)))
        ttk.Label(form, text='1. Choose the game files', style='Step.TLabel').grid(
            row=0, column=0, columnspan=3, sticky='w')
        ttk.Label(form, text='Choose the original Win16 v1.1A ZIP (castl11a.zip) or a compatible Redone folder.\n'
                 'Using extracted originals? Choose the folder with CASTLE1.EXE, CASTLE2.EXE, and both .HLP files.',
                  style='Muted.TLabel').grid(row=1, column=0, columnspan=3, sticky='w', pady=(2, 5))

        self.source_entry = ttk.Entry(form, textvariable=self.source)
        self.source_entry.grid(row=2, column=0, sticky='ew')
        zip_button = ttk.Button(form, text='Choose ZIP…', command=self.select_zip)
        zip_button.grid(row=2, column=1, padx=(8, 0))
        folder_button = ttk.Button(form, text='Choose folder…', command=self.select_source_folder)
        folder_button.grid(row=2, column=2, padx=(8, 0))

        ttk.Label(form, text='2. Choose where to install', style='Step.TLabel').grid(
            row=3, column=0, columnspan=3, sticky='w', pady=(16, 0))
        ttk.Label(form, text='Setup creates a new folder for both games.', style='Muted.TLabel').grid(
            row=4, column=0, columnspan=3, sticky='w', pady=(2, 5))
        target_entry = ttk.Entry(form, textvariable=self.target)
        target_entry.grid(row=5, column=0, columnspan=2, sticky='ew')
        target_button = ttk.Button(form, text='Change folder…', command=self.select_destination)
        target_button.grid(row=5, column=2, padx=(8, 0))
        self.inputs = (self.source_entry, zip_button, folder_button, target_entry, target_button)
        self.status = tk.StringVar(value=SOURCE_PROMPT)
        status_row = 6
        if self.with_themes:
            ttk.Label(form, text='3. Choose an interface theme', style='Step.TLabel').grid(
                row=6, column=0, columnspan=3, sticky='w', pady=(16, 4))
            themes = ttk.Combobox(form, textvariable=self.theme, state='readonly',
                                  values=tuple(THEME_NAMES.values()), width=20)
            themes.grid(row=7, column=0, sticky='w')
            mode = ttk.Checkbutton(form, text='Change the theme in an existing installation',
                                   variable=self.manage_theme, command=self.change_mode)
            mode.grid(row=8, column=0, columnspan=3, sticky='w', pady=(6, 0))
            self.inputs += (themes, mode)
            self.theme_combo = themes
            self.destination_widgets = (target_entry, target_button)
            status_row = 9
        self.notice = ttk.Label(form, textvariable=self.status, wraplength=600,
                               style='Status.TLabel', justify='left')
        self.notice.grid(row=status_row, column=0, columnspan=3, sticky='we', pady=(16, 0))
        form.bind('<Configure>', lambda event: self.notice.configure(wraplength=max(240, event.width - 48)))

        footer = ttk.Frame(root, padding=(24, 0, 24, 16))
        footer.grid(row=2, column=0, sticky='ew')
        ttk.Button(footer, text='Runtime licenses', command=self.show_licenses).pack(side='left')
        self.action = ttk.Button(footer, text='Install', command=self.begin)
        self.action.pack(side='right')
        ttk.Button(footer, text='Close', command=self.close).pack(side='right', padx=(0, 8))
        root.bind('<Return>', lambda _event: self.action.invoke())
        self.source.trace_add('write', self.source_changed)
        self.target.trace_add('write', self.update_action)
        self.update_action()
        self.source_entry.focus_set()

    def update_action(self, *_args):
        manage = self.with_themes and self.manage_theme.get()
        source = self.source.get()
        ready = (not self.busy and bool(source.strip()) and
                 (manage or (source != self.rejected_source and bool(self.target.get().strip()))))
        if self.with_themes and not self.busy:
            for widget in self.destination_widgets:
                widget.configure(state='disabled' if manage else 'normal')
        if not self.installed:
            self.action.configure(text='Apply theme' if manage else 'Install')
        self.action.configure(state='normal' if ready or self.installed else 'disabled')

    def source_changed(self, *_args):
        self.error = self.rejected_source = None
        self.notice.configure(style='Status.TLabel')
        if self.with_themes and self.manage_theme.get():
            prompt = 'Choose the installed game folder, close both games, and click Apply theme.'
        else:
            prompt = 'Click Install to check the selected files and install both games.' if self.source.get().strip() else SOURCE_PROMPT
        self.status.set(prompt)
        self.update_action()

    def change_mode(self):
        if self.source.get().strip():
            self.select_source(self.source.get())
        else:
            self.source_changed()

    def select_source(self, selected):
        self.source.set(selected)
        if self.with_themes and self.manage_theme.get():
            return True
        try:
            check_source(selected, self.assets)
        except (BadZipFile, OSError, RuntimeError, ValueError) as error:
            self.rejected_source = selected
            self.show_error(error)
            self.update_action()
            return False
        self.status.set(SOURCE_READY)
        return True

    def select_zip(self):
        filename = filedialog.askopenfilename(parent=self.root, title='Choose the game ZIP',
                                             filetypes=[('ZIP archives', '*.zip'), ('All files', '*')])
        if filename:
            self.select_source(filename)

    def select_source_folder(self):
        folder = filedialog.askdirectory(parent=self.root, title='Choose the game files folder')
        if folder:
            self.select_source(folder)

    def select_destination(self):
        folder = filedialog.askdirectory(parent=self.root, title='Choose a parent folder for the new install')
        if folder:
            self.target.set(str(next_destination(Path(folder), self.folder_name)))

    def begin(self):
        if self.busy or self.installed:
            return
        manage = self.with_themes and self.manage_theme.get()
        theme = self.theme_names[self.theme.get()] if self.with_themes else None
        try:
            if manage:
                source = Path(self.source.get().strip().strip('"')).expanduser().resolve()
                if not source.is_dir():
                    raise ValueError('Choose the installed game folder and close both games first')
                target = source
            else:
                source, target = validate_paths(self.source.get(), self.target.get())
        except (ValueError, OSError, RuntimeError) as error:
            self.show_error(error)
            return
        self.busy = True
        self.error = None
        for widget in self.inputs:
            widget.configure(state='disabled')
        self.update_action()
        self.notice.configure(style='Status.TLabel')
        self.status.set('Checking the game files and installing both chapters…')
        Thread(target=self.run_install, args=(source, target, theme, manage), daemon=True).start()
        self.root.after(60, self.poll)

    def run_install(self, source, target, theme, manage):
        try:
            if manage:
                set_theme(source, theme, self.assets, apply_delta)
            else:
                install(source, target, self.assets, theme)
        except Exception as error:
            self.events.put((None, error))
        else:
            self.events.put((target, None))

    def poll(self):
        try:
            target, error = self.events.get_nowait()
        except Empty:
            self.root.after(60, self.poll)
            return
        self.busy = False
        if error:
            for widget in self.inputs:
                widget.configure(state='normal')
            if self.with_themes:
                self.theme_combo.configure(state='readonly')
            self.update_action()
            self.show_error(error)
            return
        self.installed = target
        self.status.set('Both chapters are ready. To play, open the matching EXE in a Win16 runtime.')
        self.action.configure(text='Open install folder', command=self.open_folder, state='normal')
        self.action.focus_set()

    def show_error(self, error):
        self.error = error
        self.notice.configure(style='Error.TLabel')
        self.status.set(friendly_error(error))

    def open_folder(self):
        try:
            os.startfile(self.installed)
        except OSError:
            self.notice.configure(style='Error.TLabel')
            self.status.set(f'Open this folder in File Explorer: {self.installed}')

    def show_licenses(self):
        window = tk.Toplevel(self.root)
        window.title('Bundled runtime licenses')
        window.geometry('640x420')
        window.transient(self.root)
        notice = tk.Text(window, wrap='word', padx=12, pady=12)
        scroll = ttk.Scrollbar(window, command=notice.yview)
        notice.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        notice.pack(side='left', fill='both', expand=True)
        for license_file in sorted((self.assets / 'Licenses').glob('*.txt')):
            notice.insert('end', license_file.stem + '\n\n')
            notice.insert('end', license_file.read_text(encoding='utf-8', errors='replace') + '\n\n')
        notice.configure(state='disabled')
        window.bind('<Escape>', lambda _event: window.destroy())

    def close(self):
        if not self.busy:
            self.root.destroy()


def verify_install(args, settings):
    """Exercise the frozen installer from tests without mapping a window."""
    root = None
    try:
        if args.ui:
            root = tk.Tk()
            root.withdraw()
            window = SetupWindow(root, settings, ASSETS)
            if args.theme and window.with_themes:
                window.theme.set(THEME_NAMES[args.theme])
            window.manage_theme.set(args.manage)
            window.update_action()
            assert str(window.action.cget('state')) == 'disabled'
            window.target.set(args.destination)
            if not window.select_source(args.source):
                assert str(window.action.cget('state')) == 'disabled'
                raise window.error
            assert str(window.action.cget('state')) == 'normal'
            if not args.manage:
                assert window.status.get() == SOURCE_READY
            window.action.invoke()
            deadline = time.monotonic() + 25
            while window.busy and time.monotonic() < deadline:
                root.update()
                time.sleep(0.02)
            if window.error:
                raise window.error
            if window.busy or not window.installed:
                raise RuntimeError('Setup did not complete in the allotted time')
            assert window.action.cget('text') == 'Open install folder'
        else:
            if args.manage:
                set_theme(Path(args.source), args.theme, ASSETS, apply_delta)
            else:
                source, target = validate_paths(args.source, args.destination)
                install(source, target, ASSETS, args.theme)
        report = {'success': True, 'edition': settings['name'], 'ui': args.ui}
        if args.theme:
            report['theme'] = args.theme
    except Exception as error:
        report = {'success': False, 'error': friendly_error(error), 'type': type(error).__name__}
    finally:
        if root:
            root.destroy()
    Path(args.verify).write_text(json.dumps(report, ensure_ascii=False), encoding='utf-8')
    return 0 if report['success'] else 1


def main():
    settings = json.loads((ASSETS / 'setup.json').read_text(encoding='utf-8'))
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('--verify', required=True)
        parser.add_argument('--source', required=True)
        parser.add_argument('--destination', required=True)
        parser.add_argument('--ui', action='store_true')
        parser.add_argument('--theme', choices=THEME_NAMES)
        parser.add_argument('--manage', action='store_true')
        return verify_install(parser.parse_args(), settings)
    root = tk.Tk()
    root.withdraw()
    SetupWindow(root, settings, ASSETS)
    root.update_idletasks()
    root.deiconify()
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
