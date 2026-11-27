"""Produce deterministic theme manifests and patch payloads from audited images."""

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from zlib import crc32

from theme import build
from make_patches import make_delta, write_release
from theme_install import THEME_NAMES, digest


def stage_interface(output, classic_folders, assembler='nasm', default_theme='warm'):
    output.mkdir(parents=True, exist_ok=True)
    if default_theme not in THEME_NAMES:
        raise ValueError('Unknown default theme')
    pairs = [(part, folder / f'CASTLE{part}.EXE') for folder in classic_folders for part in (1, 2)]
    aliases = {}
    for part, path in pairs:
        data = path.read_bytes()
        aliases[digest(data)] = (part, path, data)

    def create(source):
        identity, (part, path, before) = source
        variants = {}
        for theme in ('warm', 'dark'):
            result = build(path, part, theme, assembler)
            patch = make_delta(before, result)
            name = f'interface-{identity[:16]}-{theme}.dlpatch'
            (output / name).write_bytes(patch)
            variants[theme] = {'patch': name, 'patch_sha256': digest(patch),
                               'sha256': digest(result), 'crc32': f'{crc32(result):08X}'}
        return identity, variants

    with ThreadPoolExecutor(max_workers=4) as executor:
        variants = dict(executor.map(create, sorted(aliases.items())))
    index = {'default_theme': default_theme, 'bases': variants}
    (output / 'interface.json').write_text(json.dumps(index, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return index


def write_readme(output, classic_folders, index, project='Enhanced Interface'):
    entries = [
        'Castle of the Winds I & II: Redone', project, 'By RetchERezzed', '',
        'Close both games before installing or changing the theme.', '',
        '1. Open Windows Setup and select the original registered v1.1A ZIP or a compatible game folder.',
        '2. Choose a new destination and select Warm Stone, Dark Slate or Classic.',
        '3. Install both games, then open the adventure you want to play in a Win16 runtime.', '',
        'Classic restores the executable for your existing mod setup byte for byte. Warm Stone',
        'and Dark Slate keep the same dungeon graphics, saves and game rules.', '',
        'To change or remove the theme, reopen Setup and select the installed game folder.',
        'Check Change the theme in an existing installation. Select Classic to remove the theme.',
        'Keep the local Classic.bin files. Setup uses them to restore the original game design and mods.',
        'Theme changes leave your save files in place. DOS and Windows Help retain their native styling.', '',
        'Executable CRC32 checksums', '',
    ]
    if index['default_theme'] == 'classic':
        entries.insert(11, 'All-in-One defaults to Classic. Choose Warm Stone or Dark Slate to enable the add-on.')
    for label, folder in classic_folders.items():
        for part in (1, 2):
            name = f'CASTLE{part}.EXE'
            before = (folder / name).read_bytes()
            values = index['bases'][digest(before)]
            entries.append(f"{label} {name}: Classic {crc32(before):08X}, "
                           f"Warm Stone {values['warm']['crc32']}, Dark Slate {values['dark']['crc32']}")
    entries.extend(('', 'The interface.json manifest contains full SHA-256 hashes.', ''))
    (output / 'README.txt').write_text('\n'.join(entries), encoding='utf-8', newline='\r\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('original', type=Path)
    parser.add_argument('supported', type=Path, nargs='*')
    parser.add_argument('--assembler', default='nasm')
    options = parser.parse_args()
    bases = {folder.name: folder for folder in (options.original, *options.supported)}
    write_release(options.original, [(path, path, f'-base-{i}') for i, path in enumerate(bases.values())],
                  options.destination)
    index = stage_interface(options.destination, bases.values(), options.assembler)
    write_readme(options.destination, bases, index)
