"""Build the More Monsters prototype from the clean Win16 v1.1A games."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from struct import pack, pack_into
from tempfile import TemporaryDirectory
import argparse
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parent.parent)]
from ne_research import Executable, word
from ne_patch import relocate_segment
from creature_icons import CREATURE_ART, add_creature_icons


@dataclass(frozen=True)
class Title:
    clean_hash: str
    actor: int
    strings: int
    spawn: int
    portraits: int
    names: int
    pointers: int
    text_index: int
    hook: int
    marker: int
    first_id: int
    anchors: tuple
    rng: int
    actor_list: int
    floors: dict
    beetle_only: int
    map_count: int


TITLES = {
    1: Title('e90d202717882449196cc087bc2231d2c94a17a553c4b5dfa4c91ed4c718c3b0',
             19, 13, 20, 0x670, 0x70a, 0xa96, 0x4504, 0xeba, 0x137b,
             0x4b, (0x15, 0x3e), 0x4eb2, 0x4eba,
             {4: 26, 5: 26, 6: 38, 11: 38, 12: 38, 13: 38}, 13, 22),
    2: Title('a056ac0947c967a26e6c5ece67893b7f6562611ef08736f87ab1d96c2d05da2e',
             16, 10, 17, 0xaf0, 0xc32, 0x11b8, 0x4765, 0x191a, 0x1ddb,
             0x89, (0x1e, 0x68), 0x4fca, 0x4fd2, {3: 38, 4: 38, 5: 38}, 5, 28),
}
NAMES = (b'Giant Centipede\0', b'Giant Beetle\0')
ALL_IN_ONE = {
    1: '49247755f470b544ba94fbbf90ab016bc681c5b3964b3b82de5c68d8cc7f9071',
    2: '6eeb093e12c3e5a0b4264708d53f74ed73b238c52de0b12fafada7656d421a7f',
}
FIRST_TEXT = 0x437
FIRST_HIGH_TEXT = 300
STATS = 0xbd
STAT_BYTES = 18


def write_strings(executable, title):
    segment = executable.segments[title.strings]
    body = bytearray(segment.data.ljust(segment.allocation, b'\0'))
    table_size = 2 * (FIRST_TEXT - FIRST_HIGH_TEXT)
    first_pointer = title.text_index + 2 * FIRST_HIGH_TEXT
    new_index = len(body) - 2 * FIRST_HIGH_TEXT
    body.extend(segment.data[first_pointer:first_pointer + table_size])
    name_offset = len(body) + 2 * len(NAMES)
    for name in NAMES:
        body.extend(pack('<H', name_offset))
        name_offset += len(name)
    body.extend(b''.join(NAMES))
    for offset in (0x20, 0x38):
        if word(body, offset) != title.text_index:
            raise ValueError('Unexpected native string index instruction')
        pack_into('<H', body, offset, new_index)
    return body


def creature_rows(title, spawn, actors, index):
    anchor = title.anchors[index]
    start = word(spawn, title.pointers + anchor * 2)
    template_size = 0x22 + 4 * spawn[start + 0x12]
    actor_start = STATS + STAT_BYTES * anchor
    stats = bytearray(actors[actor_start:actor_start + STAT_BYTES])
    body = bytearray(spawn[start:start + template_size])
    body[1] = title.first_id + index
    if index == 0:
        pack_into('<H', body, 2, 5)       # 5–10 HP versus the viper's 8–13
        body[6] = 60                     # 60/50 native speed ratio
        if body[0x22:] != bytes.fromhex('022a0061020a0081'):
            raise ValueError('Unexpected viper attack template')
        body[0x25] = 0x41                # 1d4 physical bite instead of 1d6
        body[0x29] = 0x31                # poison magnitude 3 instead of 8
        pack_into('<H', stats, 6, 4)
    else:
        pack_into('<H', body, 2, 12)      # 12–17 HP versus the ant's 10–15
        body[6] = 38                     # slower than the ant's 50/50
        if body[0x22:] != bytes.fromhex('022a0081'):
            raise ValueError('Unexpected ant attack template')
        body[0x25] = 0x61                # 1d6 bite instead of 1d8
        pack_into('<H', stats, 2, word(stats, 2) + 1)
        pack_into('<H', stats, 6, 6)
    pack_into('<H', body, 8, 6)           # modest native copper, gated by spawn hook
    return stats, body


def spawn_payload(title, origin, actor_data):
    reference = HERE / 'spawn.asm'
    floors = [title.floors.get(index, 0) for index in range(title.map_count)]
    policies = []
    for index in range(title.first_id):
        xp = word(actor_data, STATS + STAT_BYTES * index + 6)
        policies.append(int(4 <= xp <= 16) | (int(6 <= xp <= 18) << 1))
    constants = {
        'BLOB_ORIGIN': origin, 'CANDIDATE_LIMIT': title.first_id,
        'RNG_STATE': title.rng, 'MAP_COUNT': title.map_count, 'ACTOR_LIST': title.actor_list,
        'FACTORY_CONTINUE': title.hook + 5, 'BEETLE_ONLY_FLOOR': title.beetle_only,
        'CENTIPEDE_ID': title.first_id, 'BEETLE_ID': title.first_id + 1,
    }
    if nasm := shutil.which('nasm'):
        cmd = [nasm]
    else:
        raise RuntimeError('Install NASM and add it to PATH to assemble More Monsters')
    with TemporaryDirectory(dir=HERE) as tmp:
        asmpath = Path(tmp) / 'spawn.asm'
        binary = Path(tmp) / 'spawn.bin'
        asmpath.write_text(reference.read_text(encoding='utf-8') +
                           '\nfloor_policy: db ' + ','.join(map(str, floors)) +
                           '\ncandidate_policy: db ' + ','.join(map(str, policies)) + '\n',
                           encoding='utf-8')
        subprocess.run(cmd + ['-f', 'bin', '-w+error', *[f'-D{k}={v}' for k,v in constants.items()],
                              '-o', binary.relative_to(HERE).as_posix(), asmpath.relative_to(HERE).as_posix()],
                       cwd=HERE, check=True)
        return binary.read_bytes()


def append_code(patched, exe, title, strings, spawn, stacked):
    # The stable All-in-One has a large resource tail. Append both segments
    # before that tail so their 16-bit sector offsets still fit the NE loader.
    if stacked:
        table = exe.resource_table
        shift = word(patched, table)
        cursor = table + 2
        pointers = []
        while word(patched, cursor):
            count = word(patched, cursor + 2)
            cursor += 8
            pointers.extend(range(cursor, cursor + 12 * count, 12))
            cursor += 12 * count
        start = min(word(patched, pointer) << shift for pointer in pointers)
        end = max((word(patched, pointer) + word(patched, pointer + 2)) << shift
                  for pointer in pointers)
        if end != len(patched):
            raise ValueError('Expected a separate All-in-One resource tail')
        for segment in exe.segments.values():
            last = segment.file_offset + len(segment.data)
            if segment.flags & 0x100:
                last += 2 + 8 * word(patched, last)
            if last > start:
                raise ValueError('A code segment overlaps the resource tail')
        resources = bytes(patched[start:])
        patched = patched[:start]
    patched = relocate_segment(patched, title.strings, strings, {})
    patched = relocate_segment(patched, title.spawn, spawn, {})
    if stacked:
        layout = bytearray(patched)
        layout.extend(bytes((-len(layout)) % (1 << shift)))
        distance = (len(layout) - start) >> shift
        for pointer in pointers:
            pack_into('<H', layout, pointer, word(layout, pointer) + distance)
        layout.extend(resources)
        patched = layout
    return patched


def build(source, part):
    exe = Executable(source)
    title = TITLES[part]
    base_hash = sha256(exe.data).hexdigest()
    stacked = base_hash == ALL_IN_ONE[part]
    if not stacked and base_hash != title.clean_hash:
        raise ValueError('Expected an original Win16 v1.1A or All-in-One v1.1 executable')
    spawn = exe.segments[title.spawn]
    actor = exe.segments[title.actor]
    actor_body = bytearray(actor.data)
    spawn_body = bytearray(spawn.data.ljust(spawn.allocation, b'\0'))
    for index, (_, portrait) in enumerate(CREATURE_ART):
        new_id = title.first_id + index
        stats_at = STATS + STAT_BYTES * new_id
        portrait_at = title.portraits + 2 * new_id
        name_at = title.names + 2 * new_id
        template_at = title.pointers + 2 * new_id
        if (any(actor_body[stats_at:stats_at + STAT_BYTES])
                or word(actor_body, portrait_at) or word(actor_body, name_at)
                or word(spawn_body, template_at)):
            raise ValueError('More Monsters would overwrite an existing actor definition')
        stats, template = creature_rows(title, spawn.data, actor.data, index)
        actor_body[stats_at:stats_at + STAT_BYTES] = stats
        pack_into('<H', actor_body, portrait_at, portrait)
        pack_into('<H', actor_body, name_at, FIRST_TEXT + index)
        pack_into('<H', spawn_body, template_at, len(spawn_body))
        spawn_body.extend(template)
    if spawn_body[title.marker:title.marker + 7] != bytes.fromhex('b8ffff50502bc0'):
        raise ValueError('Ordinary spawn argument check failed')
    spawn_body[title.marker:title.marker + 7] = bytes.fromhex('6aff6afe2bc090')
    native_factory = b'\x57\x0e\xe8' + pack('<H', (-title.hook - 5) & 0xffff)
    if spawn_body[title.hook:title.hook + 5] != native_factory:
        raise ValueError('Native creature constructor signature did not match')
    added = spawn_payload(title, len(spawn_body), actor.data)
    entry = word(added, 0)
    if not len(spawn_body) < entry < len(spawn_body) + len(added):
        raise ValueError('Invalid creature hook entry')
    spawn_body[title.hook:title.hook + 5] = b'\xe9' + pack('<H', (entry - title.hook - 3) & 0xffff) + b'\x90\x90'
    spawn_body.extend(added)
    patched = bytearray(exe.data)
    patched[actor.file_offset:actor.file_offset + len(actor_body)] = actor_body
    patched = append_code(patched, exe, title, write_strings(exe, title), spawn_body, stacked)
    return add_creature_icons(patched, part)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('originals', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.originals.resolve() == args.output.resolve():
        parser.error('Choose a destination separate from the originals')
    args.output.mkdir(parents=True, exist_ok=True)
    for part in TITLES:
        filename = f'CASTLE{part}.EXE'
        binary = build(args.originals / filename, part)
        (args.output / filename).write_bytes(binary)
        print(filename, sha256(binary).hexdigest())
