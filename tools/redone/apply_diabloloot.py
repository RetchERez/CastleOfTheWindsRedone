"""Install a Castle of the Winds Redone patch into a new folder."""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import time
import zipfile

MAGIC = b'COTWDL2\0'
LITERAL = 0xFFFFFFFF


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apply_delta(original, patch):
    if len(patch) < 16 or not patch.startswith(MAGIC):
        raise ValueError('Unrecognized DiabloLoot patch')
    output_size, ranges = struct.unpack_from('<II', patch, 8)
    if not len(original) <= output_size <= 2_000_000:
        raise ValueError('Invalid patched executable size')
    result = bytearray()
    cursor = 16
    for _ in range(ranges):
        if cursor + 8 > len(patch):
            raise ValueError('Truncated DiabloLoot patch')
        source, length = struct.unpack_from('<II', patch, cursor)
        cursor += 8
        if not length or len(result) + length > output_size:
            raise ValueError('Invalid change range in DiabloLoot patch')
        if source == LITERAL:
            if cursor + length > len(patch):
                raise ValueError('Truncated literal in DiabloLoot patch')
            result.extend(patch[cursor:cursor + length])
            cursor += length
        else:
            if source + length > len(original):
                raise ValueError('Invalid source range in DiabloLoot patch')
            result.extend(original[source:source + length])
    if cursor != len(patch) or len(result) != output_size:
        raise ValueError('Unexpected DiabloLoot patch length')
    return bytes(result)


def collect_game_files(source, expected):
    if source.is_dir():
        index = {}
        files = list(source.iterdir())
        for folder in source.glob('Part [12] - *'):
            if folder.is_dir():
                files.extend(folder.iterdir())
        for candidate in files:
            name = candidate.name.upper()
            if name in expected and candidate.is_file():
                if name in index or candidate.stat().st_size not in expected[name]:
                    raise ValueError(f'Unexpected or duplicate input {name}')
                index[name] = candidate.read_bytes()
    else:
        index = {}
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                name = Path(info.filename.replace('\\', '/')).name.upper()
                if not info.is_dir() and name in expected:
                    if name in index or info.file_size not in expected[name]:
                        raise ValueError(f'Unexpected or duplicate ZIP member {name}')
                    index[name] = archive.read(info)
    if missing := expected.keys() - index.keys():
        raise ValueError('Missing ' + ', '.join(sorted(missing)))
    return index


def install(source, target, release, theme=None):
    from theme_install import CLASSIC_FILE, THEME_NAMES, theme_output

    if target.exists():
        raise FileExistsError(f'Choose a new output folder. This folder already exists: {target}')
    manifest = json.loads((release / 'patches.json').read_text(encoding='utf-8'))
    expected = {}
    for edition in manifest['editions']:
        for name, info in edition['originals'].items():
            expected.setdefault(name, set()).add(info['size'])
    originals = collect_game_files(source, expected)
    hashes = {name: digest(data) for name, data in originals.items()}
    edition = next((candidate for candidate in manifest['editions']
                    if all(hashes[name] == info['sha256']
                           for name, info in candidate['originals'].items())), None)
    if edition is None:
        raise ValueError('Use clean Win16 v1.1A files or files installed by the other Redone patch')

    game_files = {}
    for game in edition['parts']:
        name = game['executable']
        patch = (release / game['patch']).read_bytes()
        data = apply_delta(originals[name], patch)
        if digest(data) != game['sha256']:
            raise ValueError(f'{name} failed its final integrity check')
        files = {name: data, game['help']: originals[game['help']]}
        if theme in ('warm', 'dark'):
            files[Path(name).stem + ' ' + CLASSIC_FILE] = data
            files[name] = theme_output(data, theme, release, apply_delta)
        game_files[game['folder']] = files

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.cotw-redone-', dir=target.parent) as temporary:
        stage = Path(temporary) / 'install'
        stage.mkdir()
        for folder, files in game_files.items():
            directory = stage / folder
            directory.mkdir()
            for name, data in files.items():
                (directory / name).write_bytes(data)
        if theme is not None:
            (stage / 'Interface Theme.txt').write_text(THEME_NAMES[theme] + '\n', encoding='utf-8')
        # Windows can briefly keep freshly written executables open for scanning.
        for delay in (0, 0.05, 0.1, 0.2, 0.4, 0.8):
            if delay:
                time.sleep(delay)
            if target.exists():
                raise FileExistsError(f'The output folder was created during installation: {target}')
            try:
                stage.rename(target)
                break
            except PermissionError as error:
                if getattr(error, 'winerror', None) not in (5, 32) or delay == 0.8:
                    raise


def main():
    from theme_install import THEME_NAMES, set_theme

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path, help='castl11a.zip, its extracted folder, or the other patch output')
    parser.add_argument('output', type=Path, nargs='?', help='a new folder for both patched games')
    parser.add_argument('--theme', choices=THEME_NAMES)
    parser.add_argument('--change-theme', action='store_true', help='change or restore the selected installation')
    args = parser.parse_args()
    try:
        assets = Path(__file__).resolve().parent
        if args.change_theme:
            if args.output or not args.theme:
                parser.error('--change-theme requires an installation folder and --theme')
            set_theme(args.original, args.theme, assets, apply_delta)
        elif args.output:
            theme = args.theme
            if theme is None and (assets / 'interface.json').is_file():
                theme = json.loads((assets / 'interface.json').read_bytes())['default_theme']
            install(args.original, args.output, assets, theme)
        else:
            parser.error('Supply an output folder, or use --change-theme with --theme')
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Castle of the Winds Redone: {error}\n')
    print(f'Both games are ready in {(args.output or args.original).resolve()}')


if __name__ == '__main__':
    main()
