"""Build More Monsters for the two Win16 v1.1A games."""
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
from creature_icons import add_creature_icons
from roster import for_title
from room_protection import capture_code, selector_source


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
    rng: int
    actor_list: int
    map_count: int


TITLES = {
    1: Title('e90d202717882449196cc087bc2231d2c94a17a553c4b5dfa4c91ed4c718c3b0',
             19, 13, 20, 0x670, 0x70a, 0xa96, 0x4504, 0xeba, 0x137b,
             0x4b, 0x4eb2, 0x4eba, 22),
    2: Title('a056ac0947c967a26e6c5ece67893b7f6562611ef08736f87ab1d96c2d05da2e',
             16, 10, 17, 0xaf0, 0xc32, 0x11b8, 0x4765, 0x191a, 0x1ddb,
             0x89, 0x4fca, 0x4fd2, 28),
}
ALL_IN_ONE = {
    1: '49247755f470b544ba94fbbf90ab016bc681c5b3964b3b82de5c68d8cc7f9071',
    2: '6eeb093e12c3e5a0b4264708d53f74ed73b238c52de0b12fafada7656d421a7f',
}
FIRST_TEXT = 0x437
FIRST_HIGH_TEXT = 300
STATS = 0xbd
STAT_BYTES = 18
STAT_REFS = {
    1: (0x0896, 0x0D95, 0x0F67, 0x1162, 0x2089, 0x21E9, 0x2C26, 0x2C2B,
        0x2C62, 0x2C8C, 0x2CB2, 0x2CD8, 0x2CFE, 0x2D30, 0x31C2, 0x3439),
    2: (0x1164, 0x15CF, 0x1BAD, 0x1D80, 0x202D, 0x2228, 0x2538, 0x27AC, 0x2A86,
        0x2D70, 0x3094, 0x4249, 0x43A9, 0x50F0, 0x50F5, 0x512C, 0x5156, 0x517C,
        0x51A2, 0x51C8, 0x51FA, 0x5696, 0x590D),
}
ACTOR_REFS = {1: (0x1C65, 0x30C1), 2: (0x3E25, 0x5595)}
TURN_REFS = {1: (0x07e2, 0x0874, 0x0c6a, 0x1f55, 0x2016),
             2: (0x101c, 0x1142, 0x1a34, 0x4115, 0x41d6)}
SLOW_PARAMS = {1: (17, 0x4d16, 0x4e1e, 0x4ce6), 2: (14, 0x4e1c, 0x4f1e, 0x4dec)}


def write_strings(executable, title, creatures):
    names = [creature.name.encode('ascii') + b'\0' for creature in creatures]
    segment = executable.segments[title.strings]
    body = bytearray(segment.data.ljust(segment.allocation, b'\0'))
    table_size = 2 * (FIRST_TEXT - FIRST_HIGH_TEXT)
    first_pointer = title.text_index + 2 * FIRST_HIGH_TEXT
    new_index = len(body) - 2 * FIRST_HIGH_TEXT
    body.extend(segment.data[first_pointer:first_pointer + table_size])
    name_offset = len(body) + 2 * len(names)
    for name in names:
        body.extend(pack('<H', name_offset))
        name_offset += len(name)
    body.extend(b''.join(names))
    for offset in (0x20, 0x38):
        if word(body, offset) != title.text_index:
            raise ValueError('Unexpected native string index instruction')
        pack_into('<H', body, offset, new_index)
    return body


def native_definitions(exe, title, part):
    actor, spawn, strings = (exe.segments[index].data
                             for index in (title.actor, title.spawn, title.strings))
    low_text = {1: 0x4594, 2: 0x47F5}[part]
    definitions = {}
    for identity in range(title.first_id):
        name_id = word(actor, title.names + 2 * identity) & 0x3fff
        offset = word(spawn, title.pointers + 2 * identity)
        if not name_id or not offset:
            continue
        lookup = title.text_index if name_id >= FIRST_HIGH_TEXT else low_text
        start = word(strings, lookup + 2 * name_id)
        name = strings[start:strings.index(0, start)].decode('cp1252').casefold()
        hp = word(spawn, offset + 2)
        rolls = word(spawn, offset + 4)
        attack_count = spawn[offset + 0x12]
        if not hp or rolls > 15 or attack_count > 8:
            continue
        stats_at = STATS + STAT_BYTES * identity
        definitions[name] = (actor[stats_at:stats_at + STAT_BYTES],
                             spawn[offset:offset + 0x22 + 4 * attack_count])
    return definitions


def scaled_attack(source, percent):
    attack = bytearray(source)
    sides = attack[3] >> 4
    sides = max(1, min(15, (sides * percent + 50) // 100))
    attack[3] = (sides << 4) | (attack[3] & 15)
    return attack


def attacks(template):
    return [template[index:index + 4] for index in range(0x22, len(template), 4)]


def creature_rows(definitions, creature, identity, earlier):
    number = creature.logical_id
    if number == 39:
        pristine_stats, pristine = earlier[38]
    else:
        pristine_stats, pristine = definitions[creature.anchor.casefold()]
    stats = bytearray(pristine_stats)
    body = bytearray(pristine[:0x22])
    body[1] = identity
    base_hp, rolls = word(pristine, 2), word(pristine, 4)
    hp = max(1, ((2 * base_hp + 5 * rolls) * creature.hp_pct + 100 - 500 * rolls) // 200)
    body[6] = max(1, (body[6] * creature.speed_pct + 50) // 100)
    slots = attacks(pristine)
    safe_bites = [slot for slot in slots if word(slot, 1) in (0, 0x28, 0x2a)]
    if not safe_bites:
        safe_bites = [bytes((4, 0, 0, 0x71))]
    selected = [scaled_attack(max(safe_bites, key=lambda slot: (slot[0], slot[3])),
                              creature.damage_pct)]
    if number == 1:
        # Preserve the published preview's encounter balance.
        hp, body[6] = 5, 60
        selected = [bytes.fromhex('022a0041'), bytes.fromhex('020a0031')]
    elif number == 2:
        hp, body[6] = 12, 38
        selected = [bytes.fromhex('022a0061')]
    elif number in (4, 28, 30, 31, 32):
        selected.append(bytes.fromhex('020a0031'))
    elif number in (6, 12, 16):
        arrow = next(slot for slot in attacks(definitions['bandit'][1]) if slot[1] & 1)
        selected.append(scaled_attack(arrow, creature.damage_pct))
    elif number in (7, 27):
        selected.append(bytes.fromhex('02450041' if number == 7 else '04030061'))
    elif number == 10:
        selected = [scaled_attack(next(slot for slot in slots if word(slot, 1) == 6),
                                  creature.damage_pct)]
        # Black Slime takes half physical damage in place of the Slime's immunity.
        pack_into('<H', stats, 0x0a, (word(stats, 0x0a) & ~0x0010) | 0x4000)
    elif number in (34, 35, 36, 37, 38, 39, 40):
        element = {34: 4, 35: 2, 36: 8, 37: 2, 38: 4, 39: 2, 40: 2}[number]
        selected[0][1:3] = bytes((element, 0))
        if number in (34, 35, 36, 38, 39, 40):
            resistance = {2: 0x0400, 4: 0x0800, 8: 0x1000}[element]
            pack_into('<H', stats, 0x0a, (word(stats, 0x0a) & ~0x3c0f) | resistance)
    if number in (12, 24, 25):
        body[0] = 9
        undead = definitions['skeleton'][0]
        stats[8:] = undead[8:]
    if number in (30, 31, 32):
        body[0] = 3
        stats[8:] = definitions['large snake'][0][8:]
    if creature.role == 'Armored':
        pack_into('<H', stats, 2, word(stats, 2) + 1)
    pack_into('<H', stats, 6, creature.xp)
    pack_into('<H', body, 2, hp)
    pack_into('<H', body, 8, 6)           # native copper; roster controls frequency
    body[0x12:0x15] = bytes((len(selected), 0, 1))
    body[0x1e:0x22] = b'\0\0\0\0'    # drop inherited spells, summoning and gating
    if number in (7, 27):
        body[0x20] = 3                  # at most three ranged casts
    if number == 27:
        body[0x21] = 1                  # at most one non-stacking Slow each lifespan
    return bytes(stats), bytes(body) + b''.join(selected)


def assemble(reference, origin, constants, tables=''):
    constants = {'BLOB_ORIGIN': origin, **constants}
    if nasm := shutil.which('nasm'):
        cmd = [nasm]
    else:
        raise RuntimeError('Install NASM and add it to PATH to assemble More Monsters')
    with TemporaryDirectory(dir=HERE) as tmp:
        asmpath = Path(tmp) / 'spawn.asm'
        binary = Path(tmp) / 'spawn.bin'
        asmpath.write_text(reference.read_text(encoding='utf-8') + '\n' + tables, encoding='utf-8')
        subprocess.run(cmd + ['-f', 'bin', '-w+error', *[f'-D{k}={v}' for k,v in constants.items()],
                              '-o', binary.relative_to(HERE).as_posix(), asmpath.relative_to(HERE).as_posix()],
                       cwd=HERE, check=True)
        return binary.read_bytes()


def spawn_payload(exe, title, part, origin, actor_data, creatures):
    if part == 1:
        probability = {4: 26, 5: 26, 6: 38, 11: 38, 12: 38, 13: 38,
                       **dict.fromkeys(range(14, 20), 51)}
        early, middle = (4, 5), (6, 11, 12, 13)
    else:
        probability = {**dict.fromkeys(range(3, 7), 38), **dict.fromkeys(range(7, 13), 51),
                       **dict.fromkeys(range(13, 27), 64)}
        early, middle = (3, 4, 5), (6, 7, 8, 9)
    floor_ids = range(title.map_count)
    tables = (
        ('floor_probability', 'db', [probability.get(floor, 0) for floor in floor_ids]),
        ('floor_total', 'db', [2 if f in early else 3 if f in middle else 4 for f in floor_ids]),
        ('floor_risk', 'db', [1 if f in early else 2 if f in middle else 3 for f in floor_ids]),
        ('floor_weights', 'db', [c.weight(part, floor) for floor in floor_ids for c in creatures]),
        ('species_flags', 'db', [c.behavior for c in creatures]),
        ('species_min_xp', 'db', [max(2, (c.xp * 3 + 4) // 5) for c in creatures]),
        ('species_max_xp', 'db', [min(255, max(16, c.xp * 2 + 6)) for c in creatures]),
        ('species_copper', 'db', [c.copper_chance for c in creatures]),
        ('stock_xp', 'dw', [word(actor_data, STATS + STAT_BYTES * i + 6) for i in range(title.first_id)]),
    )
    declarations = '\n'.join(f'{name}: {size} ' + ','.join(map(str, values)) for name, size, values in tables)
    constants = {'FIRST_ID': title.first_id, 'SPECIES_COUNT': len(creatures),
                 'RNG_STATE': title.rng, 'MAP_COUNT': title.map_count, 'ACTOR_LIST': title.actor_list,
                 'FACTORY_CONTINUE': title.hook + 5, 'PRISONER_FLAG': 0x4e3a if part == 2 else 0}
    return assemble(HERE / 'spawn.asm', origin, constants, declarations + selector_source(exe, part))


def append_code(patched, exe, title, actor, fixups, strings, spawn, room, stacked):
    # The stable All-in-One has a large resource tail. Append the segments
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
    patched = relocate_segment(patched, title.actor, actor, fixups)
    patched = relocate_segment(patched, title.strings, strings, {})
    patched = relocate_segment(patched, title.spawn, spawn, {})
    section, body = room
    patched = relocate_segment(patched, section, body, {})
    if stacked:
        layout = bytearray(patched)
        layout.extend(bytes((-len(layout)) % (1 << shift)))
        distance = (len(layout) - start) >> shift
        for pointer in pointers:
            pack_into('<H', layout, pointer, word(layout, pointer) + distance)
        layout.extend(resources)
        patched = layout
    return patched


def patch_word(body, offset, original, replacement):
    if word(body, offset) != original:
        raise ValueError(f'Unexpected operand at {offset:#x}')
    pack_into('<H', body, offset, replacement)


def install_actor_tables(actor, spawn, segments, title, part, creatures, definitions):
    actor_source, spawn_source = segments
    stats = bytearray(actor_source[STATS:STATS + STAT_BYTES * title.first_id])
    icons = bytearray(actor_source[title.portraits:title.portraits + 2 * title.first_id])
    names = bytearray(actor_source[title.names:title.names + 2 * title.first_id])
    pointers = bytearray(spawn_source[title.pointers:title.pointers + 2 * title.first_id])
    earlier = {}
    for index, creature in enumerate(creatures):
        fields, template = creature_rows(definitions, creature, title.first_id + index, earlier)
        earlier[creature.logical_id] = fields, template
        stats.extend(fields)
        icons.extend(pack('<H', creature.portrait))
        names.extend(pack('<H', FIRST_TEXT + index))
        pointers.extend(pack('<H', len(spawn)))
        spawn.extend(template)

    stats_at = len(actor)
    icons_at = stats_at + len(stats)
    names_at = icons_at + len(icons)
    actor.extend(stats + icons + names)
    for reference in STAT_REFS[part]:
        offset = word(actor, reference) - STATS
        if offset not in range(0, 18, 2) and offset != 5:
            raise ValueError(f'Invalid stock stats field {offset} at {reference:#x}')
        pack_into('<H', actor, reference, stats_at + offset)
    icon_ref, name_ref = ACTOR_REFS[part]
    patch_word(actor, icon_ref, title.portraits, icons_at)
    patch_word(actor, name_ref, title.names, names_at)
    patch_word(spawn, 0x17, title.pointers, len(spawn))
    spawn.extend(pointers)


def install_turn_hooks(part, actor, title, creatures):
    turn, native_turn, regen, ranged, melee = TURN_REFS[part]
    effects, slow_stat, queue, overflow = SLOW_PARAMS[part]
    slow_type = next((title.first_id + i for i, c in enumerate(creatures) if c.logical_id == 27), -1)
    table = 'turn_behavior: db ' + ','.join(str(creature.behavior) for creature in creatures) + '\n'
    data = bytearray(assemble(HERE / 'actor.asm', len(actor),
                              {'FIRST_ID': title.first_id, 'SPECIES_COUNT': len(creatures),
                               'NATIVE_TURN': native_turn, 'NATIVE_REGEN': regen,
                               'SLOW_TYPE': slow_type, 'PLAYER_SLOW': slow_stat,
                               'SLOW_QUEUE': queue, 'SLOW_OVERFLOW': overflow}, table))
    fixups = {}
    if slow_type != -1:
        for entry in (0, 0x070a):
            marker = b'\x9a' + pack('<HH', entry, 0xfffe)
            position = data.index(marker) + 3
            fixups[len(actor) + position] = effects
            data[position:position + 2] = b'\xff\xff'
    if actor[turn:turn + 3] != b'\xe8' + pack('<H', (native_turn - turn - 3) & 0xffff):
        raise ValueError('Native turn call did not match')
    if actor[ranged:ranged + 4] != bytes.fromhex('837ef400'):
        raise ValueError('Native ranged action did not match')
    if actor[melee:melee + 5] != bytes.fromhex('8a44132ae4'):
        raise ValueError('Native melee selection did not match')
    for offset, entry in ((turn, word(data, 0)), (ranged, word(data, 2)), (melee, word(data, 4))):
        actor[offset:offset + 3] = b'\xe8' + pack('<H', (entry - offset - 3) & 0xffff)
    actor[ranged + 3] = 0x90
    actor.extend(data)
    return fixups


def build(source, part):
    exe = Executable(source)
    title = TITLES[part]
    base_hash = sha256(exe.data).hexdigest()
    stacked = base_hash == ALL_IN_ONE[part]
    if not stacked and base_hash != title.clean_hash:
        raise ValueError('Expected an original Win16 v1.1A or All-in-One v1.1 executable')
    spawn = exe.segments[title.spawn]
    actor = exe.segments[title.actor]
    creatures = for_title(part)
    actor_body = bytearray(actor.data.ljust(actor.allocation, b'\0'))
    spawn_body = bytearray(spawn.data.ljust(spawn.allocation, b'\0'))
    install_actor_tables(actor_body, spawn_body, (actor.data, spawn.data), title, part, creatures,
                         native_definitions(exe, title, part))
    fixups = install_turn_hooks(part, actor_body, title, creatures)
    if spawn_body[title.marker:title.marker + 7] != bytes.fromhex('b8ffff50502bc0'):
        raise ValueError('Ordinary spawn argument check failed')
    spawn_body[title.marker:title.marker + 7] = bytes.fromhex('6aff6afe2bc090')
    native_factory = b'\x57\x0e\xe8' + pack('<H', (-title.hook - 5) & 0xffff)
    if spawn_body[title.hook:title.hook + 5] != native_factory:
        raise ValueError('Native creature constructor signature did not match')
    added = spawn_payload(exe, title, part, len(spawn_body), actor.data, creatures)
    entry = word(added, 0)
    if not len(spawn_body) < entry < len(spawn_body) + len(added):
        raise ValueError('Invalid creature hook entry')
    spawn_body[title.hook:title.hook + 5] = b'\xe9' + pack('<H', (entry - title.hook - 3) & 0xffff) + b'\x90\x90'
    spawn_body.extend(added)
    patched = bytearray(exe.data)
    patched = append_code(patched, exe, title, actor_body, fixups,
                          write_strings(exe, title, creatures), spawn_body,
                          capture_code(exe, part, assemble), stacked)
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
