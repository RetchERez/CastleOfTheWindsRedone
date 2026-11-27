"""Build self-contained 64-bit Windows installers for the requested editions."""

import argparse
from importlib import metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

SOURCE = Path(__file__).resolve().parent
EDITIONS = {
    'diabloloot': ('DiabloLoot', 'v1.2'),
    'black-background': ('Black Background', 'v1.0'),
    'all-in-one': ('All-in-One', 'v1.1'),
    'diablo-loot': ('Diablo Loot', 'v1.1'),
    'more-monsters': ('More Monsters', 'v1.1'),
    'more-equipment': ('More Equipment', 'v1.1'),
    'graphics-overhaul': ('Graphics Overhaul', 'v1.1'),
    'all-in-one-full': ('All-in-One', 'v1.1'),
    'enhanced-interface': ('Enhanced Interface', 'v1.1'),
}


def bundle(package_root, destination, edition):
    name, version = EDITIONS[edition]
    asset_name = f'castle-of-the-winds-redone-{edition}-{version}-windows-setup'
    with TemporaryDirectory(prefix='cotw-setup-') as temporary:
        stage = Path(temporary)
        assets = stage / 'redone-package'
        assets.mkdir()
        package = package_root / edition
        for filename in [package / 'patches.json', *sorted(package.glob('*.dlpatch'))]:
            shutil.copyfile(filename, assets / filename.name)
        config = {'name': name, 'version': version, 'folder': name}
        if (theme_index := package / 'interface.json').is_file():
            shutil.copyfile(theme_index, assets / theme_index.name)
            shutil.copytree(SOURCE / 'theme_previews', assets / 'theme_previews')
            config['default_theme'] = json.loads(theme_index.read_bytes())['default_theme']
        (assets / 'setup.json').write_text(json.dumps({
            **config,
        }), encoding='utf-8')
        shutil.copyfile(SOURCE / 'redone.ico', assets / 'redone.ico')

        licenses = assets / 'Licenses'
        licenses.mkdir()
        shutil.copyfile(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python and Tcl Tk.txt')
        distribution = metadata.distribution('pyinstaller')
        copying = next(entry for entry in distribution.files if entry.name == 'COPYING.txt')
        shutil.copyfile(distribution.locate_file(copying), licenses / 'PyInstaller.txt')

        major, minor = (int(number) for number in version[1:].split('.'))
        version_file = stage / 'version.txt'
        version_file.write_text(f"""
VSVersionInfo(
  ffi=FixedFileInfo(filevers=({major}, {minor}, 0, 0), prodvers=({major}, {minor}, 0, 0),
                    mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'RetchERezzed'),
    StringStruct('FileDescription', 'Castle of the Winds Redone {name} Setup'),
    StringStruct('FileVersion', '{version[1:]}'),
    StringStruct('OriginalFilename', '{asset_name}.exe'),
    StringStruct('ProductName', 'Castle of the Winds I & II: Redone'),
    StringStruct('ProductVersion', '{version[1:]}')
  ])]), VarFileInfo([VarStruct('Translation', [1033, 1200])])]
)
""".strip(), encoding='utf-8')
        subprocess.run([
            sys.executable, '-m', 'PyInstaller', '--onefile', '--windowed', '--noupx',
            '--name', asset_name, '--icon', str(SOURCE / 'redone.ico'),
            '--version-file', str(version_file), '--add-data', f'{assets}:redone-package',
            '--distpath', str(destination), '--workpath', str(stage / 'work'),
            '--specpath', str(stage), str(SOURCE / 'windows_setup.py'),
        ], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages', type=Path, help='output of build_mods.py')
    parser.add_argument('destination', type=Path)
    parser.add_argument('--edition', choices=EDITIONS, action='append')
    args = parser.parse_args()
    if sys.platform != 'win32' or sys.maxsize <= 2**32:
        parser.error('Build the Windows setup on 64-bit Windows')
    args.destination.mkdir(parents=True, exist_ok=True)
    available = [edition for edition in EDITIONS
                 if (args.packages / edition / 'patches.json').is_file()]
    if not args.edition and not available:
        parser.error('No patch manifests found in the package directory')
    for edition in args.edition or available:
        bundle(args.packages.resolve(), args.destination.resolve(), edition)
