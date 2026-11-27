"""Build all three installer directories from a clean Win16 v1.1A game folder."""

import argparse
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from build import Executable, GAMES, build, with_map_background
from make_patches import write_release

ROOT = Path(__file__).resolve().parents[2]


def build_mods(vanilla, destination, previous_loot=None, previous_combined=None):
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
        loot_editions = [(vanilla, loot, ''), (black, combined, '-stack')]
        black_editions = [(vanilla, black, ''), (loot, combined, '-stack')]
        combined_editions = [
            (vanilla, combined, ''),
            (loot, combined, '-from-diabloloot'),
            (black, combined, '-from-black-background'),
        ]
        if previous_loot and previous_combined:
            for part, game in GAMES.items():
                name = f'CASTLE{part}.EXE'
                expected = with_map_background(Executable(previous_loot / name), game)
                if expected != (previous_combined / name).read_bytes():
                    raise ValueError('The previous combined files must match the previous DiabloLoot plus Black Background')
            loot_editions.extend([
                (previous_loot, loot, '-upgrade-loot'),
                (previous_combined, combined, '-upgrade-combined'),
            ])
            black_editions.append((previous_loot, previous_combined, '-stack-previous'))
            combined_editions.extend([
                (previous_loot, combined, '-upgrade-loot'),
                (previous_combined, combined, '-upgrade-combined'),
            ])
        for name, editions in (
            ('diabloloot', loot_editions),
            ('black-background', black_editions),
            ('all-in-one', combined_editions),
        ):
            write_release(vanilla, editions, destination / name)
    for name in ('diabloloot', 'black-background', 'all-in-one'):
        copyfile(ROOT / 'mods' / name / 'README.md', destination / name / 'README.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vanilla', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--previous-loot', type=Path, help='directory with the previous standalone DiabloLoot EXEs')
    parser.add_argument('--previous-combined', type=Path, help='directory with the previous All-in-One EXEs')
    args = parser.parse_args()
    if args.destination.exists():
        parser.error('Choose a new destination directory')
    if bool(args.previous_loot) != bool(args.previous_combined):
        parser.error('Supply both previous build directories when including upgrades')
    build_mods(args.vanilla, args.destination, args.previous_loot, args.previous_combined)
