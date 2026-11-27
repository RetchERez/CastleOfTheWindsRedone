"""Prepare the More Monsters and All-in-One preview patch packages."""
import argparse
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from build_bestiary import build
from make_patches import write_release

ROOT = Path(__file__).resolve().parents[3]


def build_packages(vanilla, stable, destination):
    with TemporaryDirectory(prefix='cotw-monsters-') as scratch:
        monsters = Path(scratch) / 'more-monsters'
        stacked = Path(scratch) / 'stacked'
        for folder, source in ((monsters, vanilla), (stacked, stable)):
            folder.mkdir()
            for part in (1, 2):
                name = f'CASTLE{part}.EXE'
                (folder / name).write_bytes(build(source / name, part))
        write_release(vanilla, (
            (vanilla, monsters, ''),
            (stable, stacked, '-stack'),
        ), destination / 'more-monsters')
        write_release(vanilla, (
            (vanilla, stacked, ''),
            (stable, stacked, '-from-current-all-in-one'),
            (monsters, stacked, '-from-more-monsters'),
        ), destination / 'all-in-one-preview')
    for name in ('more-monsters', 'all-in-one-preview'):
        copyfile(ROOT / 'mods' / name / 'README.md', destination / name / 'README.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vanilla', type=Path, help='clean Win16 v1.1A directory containing both EXEs and HLPs')
    parser.add_argument('stable', type=Path, help='directory containing both tested All-in-One v1.1 EXEs')
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    if args.destination.exists():
        parser.error('Choose a new destination directory')
    build_packages(args.vanilla, args.stable, args.destination)
