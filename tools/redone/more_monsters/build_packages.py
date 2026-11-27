"""Prepare the More Monsters and All-in-One patch packages."""
import argparse
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from build_bestiary import build
from make_patches import write_release

ROOT = Path(__file__).resolve().parents[3]


def build_packages(vanilla, stable, destination, previous_monsters=None, previous_preview=None,
                   diabloloot=None, black_background=None):
    with TemporaryDirectory(prefix='cotw-monsters-') as scratch:
        monsters = Path(scratch) / 'more-monsters'
        stacked = Path(scratch) / 'stacked'
        for folder, source in ((monsters, vanilla), (stacked, stable)):
            folder.mkdir()
            for part in (1, 2):
                name = f'CASTLE{part}.EXE'
                (folder / name).write_bytes(build(source / name, part))
        standalone_sources = [
            (vanilla, monsters, ''),
            (stable, stacked, '-stack'),
        ]
        combined_sources = [
            (vanilla, stacked, ''),
            (stable, stacked, '-from-current-all-in-one'),
            (monsters, stacked, '-from-more-monsters'),
        ]
        if previous_monsters:
            standalone_sources.append((previous_monsters, monsters, '-from-early-monsters'))
            combined_sources.append((previous_monsters, stacked, '-from-early-monsters'))
        if previous_preview:
            standalone_sources.append((previous_preview, stacked, '-from-preview'))
            combined_sources.append((previous_preview, stacked, '-from-preview'))
        for source, suffix in ((diabloloot, '-from-diabloloot'), (black_background, '-from-background')):
            if source:
                combined_sources.append((source, stacked, suffix))
        write_release(vanilla, standalone_sources, destination / 'more-monsters')
        write_release(vanilla, combined_sources, destination / 'all-in-one-full')
    for name in ('more-monsters', 'all-in-one-full'):
        copyfile(ROOT / 'mods' / name / 'README.md', destination / name / 'README.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('vanilla', type=Path, help='clean Win16 v1.1A directory containing both EXEs and HLPs')
    parser.add_argument('stable', type=Path, help='directory containing both tested All-in-One v1.1 EXEs')
    parser.add_argument('destination', type=Path)
    parser.add_argument('--previous-monsters', type=Path, help='More Monsters v0.1 installed EXEs')
    parser.add_argument('--previous-preview', type=Path, help='All-in-One v1.2 Preview installed EXEs')
    parser.add_argument('--diabloloot', type=Path, help='DiabloLoot v1.2 installed EXEs')
    parser.add_argument('--black-background', type=Path, help='Black Background v1.0 installed EXEs')
    args = parser.parse_args()
    if args.destination.exists():
        parser.error('Choose a new destination directory')
    build_packages(args.vanilla, args.stable, args.destination, args.previous_monsters,
                   args.previous_preview, args.diabloloot, args.black_background)
