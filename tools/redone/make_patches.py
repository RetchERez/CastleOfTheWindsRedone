"""Generate the portable DiabloLoot patch set from tested binaries."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import shutil
import struct

from apply_diabloloot import LITERAL, MAGIC, apply_delta, digest


def make_delta(original, patched):
    # Reference the bytes from the user's original file even when resource
    # relocation moves them to a new offset. Only new data travels as literals.
    anchor = 32
    blocks = defaultdict(list)
    for source in range(0, len(original) - anchor + 1, 16):
        blocks[original[source:source + anchor]].append(source)

    patch = bytearray(MAGIC + struct.pack('<II', len(patched), 0))
    literal_start = 0
    ranges = 0
    offset = 0
    previous_shift = 0
    while offset + anchor <= len(patched):
        block = patched[offset:offset + anchor]
        preferred = offset + previous_shift
        if preferred >= 0 and original[preferred:preferred + anchor] == block:
            source = preferred
        else:
            candidates = blocks.get(block)
            if not candidates:
                offset += 1
                continue
            source = candidates[0]
        if literal_start < offset:
            patch.extend(struct.pack('<II', LITERAL, offset - literal_start))
            patch.extend(patched[literal_start:offset])
            ranges += 1

        length = anchor
        limit = min(len(original) - source, len(patched) - offset)
        while length + 256 <= limit and original[source + length:source + length + 256] == patched[offset + length:offset + length + 256]:
            length += 256
        while length < limit and original[source + length] == patched[offset + length]:
            length += 1
        patch.extend(struct.pack('<II', source, length))
        ranges += 1
        previous_shift = source - offset
        offset += length
        literal_start = offset

    if literal_start < len(patched):
        patch.extend(struct.pack('<II', LITERAL, len(patched) - literal_start))
        patch.extend(patched[literal_start:])
        ranges += 1
    struct.pack_into('<I', patch, 12, ranges)
    if apply_delta(original, patch) != patched:
        raise ValueError('Patch round trip did not reproduce the verified executable')
    return bytes(patch)


def write_release(vanilla, editions, output):
    manifest = {'editions': []}
    output.mkdir(parents=True, exist_ok=False)
    for input_folder, tested, suffix in editions:
        edition = {'originals': {}, 'parts': []}
        manifest['editions'].append(edition)
        for number, chapter in ((1, 'A Question of Vengeance'), (2, "Lifthransir's Bane")):
            name = f'CASTLE{number}.EXE'
            help_name = f'CASTLE{number}.HLP'
            original = (input_folder / name).read_bytes()
            patched = (tested / name).read_bytes()
            help_data = (vanilla / help_name).read_bytes()
            for filename, data in ((name, original), (help_name, help_data)):
                edition['originals'][filename] = {'size': len(data), 'sha256': digest(data)}
            patch_name = f'CASTLE{number}{suffix}.dlpatch'
            (output / patch_name).write_bytes(make_delta(original, patched))
            edition['parts'].append({'executable': name, 'help': help_name,
                                     'folder': f'Part {number} - {chapter}',
                                     'sha256': digest(patched), 'patch': patch_name})
    (output / 'patches.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(Path(__file__).with_name('apply_diabloloot.py'), output / 'apply_redone.py')


def make_release(vanilla, first, other, combined, output):
    write_release(vanilla, ((vanilla, first, ''), (other, combined, '-stack')), output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('vanilla', 'first', 'other', 'combined', 'output'):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    make_release(args.vanilla, args.first, args.other, args.combined, args.output)
