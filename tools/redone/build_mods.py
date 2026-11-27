"""Build all three installer directories from a clean Win16 v1.1A game folder."""

import argparse
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from build import Executable, GAMES, build, with_map_background
from make_patches import make_release, write_release

ROOT = Path(__file__).resolve().parents[2]


def build_mods(vanilla, destination):
    with TemporaryDirectory(prefix='cotw-build-') as temp:
        loot, black, combined = (Path(temp) / name for name in ('loot', 'black', 'combined'))
        for folder in (loot, black, combined):
            folder.mkdir()
        for part, game in GAMES.items():
            name = f'CASTLE{part}.EXE'
            source = Executable(vanilla / name)
            if sha256(source.data).hexdigest() != game.digest:
                raise ValueError(f'{name} must be the original Win16 v1.1A executable')
            (loot / name).write_bytes(build(vanilla / name, game))
            (black / name).write_bytes(with_map_background(source, game))
            (combined / name).write_bytes(with_map_background(Executable(loot / name), game))
        make_release(vanilla, loot, black, combined, destination / 'diabloloot')
        make_release(vanilla, black, loot, combined, destination / 'black-background')
        write_release(vanilla, (
            (vanilla, combined, ''),
            (loot, combined, '-from-diabloloot'),
            (black, combined, '-from-black-background'),
        ), destination / 'all-in-one')
    for name in ('diabloloot', 'black-background', 'all-in-one'):
        copyfile(ROOT / 'mods' / name / 'README.md', destination / name / 'README.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vanilla', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    if args.destination.exists():
        parser.error('Choose a new destination directory')
    build_mods(args.vanilla, args.destination)
