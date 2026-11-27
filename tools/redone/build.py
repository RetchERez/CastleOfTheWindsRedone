"""Build DiabloLoot executables from the verified Win16 v1.1A files."""

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parent
WORK = SOURCE.parent
sys.path.insert(0, str(WORK))
from ne_research import Executable
from ne_patch import relocate_segment


@dataclass(frozen=True)
class Game:
    digest: str
    shop: int
    stock_new: int
    stock_refill: int
    reward: int
    reward_start: int
    lethal_return: int
    floor_append: int
    rng: tuple[int, int]
    factory: tuple[int, int]
    formatter: tuple[int, int]
    new_name: tuple[int, int]
    add_attribute: int
    depth_table: int
    icon_select: int
    instance_cell: int
    successful_equip: int
    map_painter: int
    unexplored_brush: int
    white_brush: int


GAMES = {
    1: Game('e90d202717882449196cc087bc2231d2c94a17a553c4b5dfa4c91ed4c718c3b0',
            18, 0x08C3, 0x0A7E, 9, 0x1645, 0x1578, 0x17F8,
            (12, 0x0314), (14, 0x07C2), (16, 0x0808), (13, 0x51D4), 0x0B7C, 0x3D88,
            0x1175, 0x3D28, 0x137A, 21, 0x060A, 0x3CE2),
    2: Game('a056ac0947c967a26e6c5ece67893b7f6562611ef08736f87ab1d96c2d05da2e',
            15, 0x09CE, 0x0B71, 6, 0x1669, 0x159C, 0x181C,
            (9, 0x031A), (11, 0x07C0), (13, 0x0808), (10, 0x5442), 0x0B7A, 0x3D98,
            0x117F, 0x3D38, 0x1390, 18, 0x0640, 0x3CF2),
}


def assembler_command():
    if nasm := shutil.which('nasm'):
        return [nasm]
    raise RuntimeError('Install NASM and add it to PATH to assemble the patch')


def assemble(module, origin, definitions, export_count, append_asm=''):
    with tempfile.TemporaryDirectory(dir=SOURCE) as stage:
        destination = Path(stage, 'payload.bin')
        command = assembler_command()
        options = {**definitions, 'BLOB_ORIGIN': origin}
        command += ['-f', 'bin', '-w+error']
        command += [f'-D{name}={value}' for name, value in options.items()]
        input_name = module
        if append_asm:
            augmented = Path(stage, 'payload.asm')
            augmented.write_text((SOURCE / module).read_text(encoding='utf-8') + append_asm,
                                 encoding='utf-8')
            input_name = augmented.relative_to(SOURCE).as_posix()
        command += ['-o', destination.relative_to(SOURCE).as_posix(), input_name]
        subprocess.run(command, cwd=SOURCE, check=True)
        payload = bytearray(destination.read_bytes())
    exports = struct.unpack_from('<' + 'H' * export_count, payload)
    if any(not origin + 2 * export_count <= address < origin + len(payload) for address in exports):
        raise ValueError(f'Invalid export in {module}')

    selectors = {}
    imports = {}
    for offset in range(export_count * 2, len(payload) - 4):
        if payload[offset] != 0x9A:
            continue
        marker = payload[offset + 4]
        if marker == 0xDA and 1 <= payload[offset + 3] <= 32:
            selectors[origin + offset + 3] = payload[offset + 3]
            payload[offset + 3:offset + 5] = b'\xff\xff'
        elif marker == 0xE1 and payload[offset + 1:offset + 3] == b'\xff\xff':
            imports[origin + offset + 1] = (1, payload[offset + 3])
            payload[offset + 3:offset + 5] = b'\0\0'
    return bytes(payload), exports, selectors, imports


def redirect(body, offset, expected, destination):
    if body[offset:offset + len(expected)] != expected:
        raise ValueError(f'Unexpected instruction bytes at {offset:#06x}')
    rel = (destination - offset - 3) & 0xFFFF
    body[offset:offset + len(expected)] = b'\xe9' + struct.pack('<H', rel) + b'\x90' * (len(expected) - 3)


def with_map_background(exe, game, black=True):
    map_code = exe.segments[game.map_painter]
    unseen = map_code.file_offset + game.unexplored_brush
    source_brush = game.white_brush if black else game.white_brush + 6
    output_brush = game.white_brush + 6 if black else game.white_brush
    expected = b'\xff\x36' + struct.pack('<H', source_brush)
    if exe.data[unseen:unseen + 4] != expected:
        raise ValueError('Unexpected unexplored-map brush')
    patched = bytearray(exe.data)
    struct.pack_into('<H', patched, unseen + 2, output_brush)
    return bytes(patched)


def build(source, game, color_icons=True):
    exe = Executable(source)
    if hashlib.sha256(exe.data).hexdigest() != game.digest:
        raise ValueError(f'{source.name} must be unmodified Win16 v1.1A')

    shared = {
        'RNG_SEGMENT': game.rng[0], 'RNG_OFFSET': game.rng[1],
        'ITEM_SEGMENT': game.factory[0], 'ITEM_FACTORY': game.factory[1],
        'NAME_SEGMENT': game.formatter[0], 'NAME_FORMATTER': game.formatter[1],
        'STRING_SEGMENT': game.new_name[0], 'MAKE_NAME': game.new_name[1],
        'ADD_ATTRIBUTE': game.add_attribute,
        'DEPTH_TABLE': game.depth_table,
    }
    shop = exe.segments[game.shop]
    shop_body = bytearray(shop.data.ljust(shop.allocation, b'\0'))
    payload, labels, selectors, imports = assemble('shop.asm', len(shop_body), {
        **shared, 'STOCK_INIT_CONTINUE': game.stock_new + 4,
        'STOCK_RESTOCK_CONTINUE': game.stock_refill + 4,
    }, 3)
    tab = bytes.fromhex('8bf00bf6')
    redirect(shop_body, game.stock_new, tab, labels[0])
    redirect(shop_body, game.stock_refill, tab, labels[1])
    shop_body.extend(payload)
    patched = relocate_segment(exe.data, game.shop, shop_body, selectors, imports)

    reward = exe.segments[game.reward]
    reward_body = bytearray(reward.data.ljust(reward.allocation, b'\0'))
    payload, labels, selectors, imports = assemble('reward.asm', len(reward_body), {
        **shared, 'SHOP_SEGMENT': game.shop, 'ENHANCE_OFFSET': labels[2],
        'LETHAL_RETURN': game.lethal_return, 'FLOOR_APPEND': game.floor_append,
        'REWARD_CONTINUE': game.reward_start + 5,
    }, 1)
    redirect(reward_body, game.reward_start, bytes.fromhex('8a45162ae4'), labels[0])
    reward_body.extend(payload)
    patched = relocate_segment(patched, game.reward, reward_body, selectors, imports)

    names = exe.segments[game.formatter[0]]
    names_body = bytearray(names.data.ljust(names.allocation, b'\0'))
    payload, labels, selectors, imports = assemble('hidden_name.asm', len(names_body), {
        'NAME_CONTINUE': 0x082E,
        'NAME_EPILOGUE': 0x0E3C,
    }, 2)
    redirect(names_body, 0x082A, bytes.fromhex('f6470901'), labels[0])
    redirect(names_body, 0x0E38, bytes.fromhex('5e5f4d4d'), labels[1])
    names_body.extend(payload)
    patched = relocate_segment(patched, names.index, names_body, selectors, imports)

    mapping = {}
    if color_icons:
        from color_resources import add_loot_icons, loot_icon_mapping
        mapping = loot_icon_mapping()
    table = '\nrarity_icons:\n'
    for source_icon in sorted({key[0] for key in mapping}):
        icons = [mapping[source_icon, tier] for tier in (1, 2, 3)]
        table += '    dw ' + ', '.join(map(str, [source_icon, *icons])) + '\n'
    table += '    dw 0\n'

    ui = exe.segments[game.factory[0]]
    ui_body = bytearray(ui.data.ljust(ui.allocation, b'\0'))
    payload, labels, selectors, imports = assemble('item_ui.asm', len(ui_body), {
        'HINSTANCE_CELL': game.instance_cell, 'ICON_CONTINUE': game.icon_select + 4,
        'EQUIP_CONTINUE': game.successful_equip + 4,
    }, 2, table)
    redirect(ui_body, game.icon_select, b'\xff\x36' + struct.pack('<H', game.instance_cell), labels[0])
    redirect(ui_body, game.successful_equip, bytes.fromhex('f6440901'), labels[1])
    ui_body.extend(payload)
    patched = relocate_segment(patched, ui.index, ui_body, selectors, imports)

    if color_icons:
        part = 1 if game is GAMES[1] else 2
        patched, installed_mapping = add_loot_icons(patched, part)
        if mapping != installed_mapping:
            raise ValueError('Compiled and installed rarity icon IDs disagree')
    return patched


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='directory containing the original EXEs')
    parser.add_argument('output', type=Path, help='separate directory for processed EXEs')
    parser.add_argument('--curse-preview', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.output.resolve() == args.input.resolve():
        parser.error('Select different input and output directories')
    args.output.mkdir(parents=True, exist_ok=True)
    built = {}
    for part, game in GAMES.items():
        name = f'CASTLE{part}.EXE'
        built[name] = build(args.input / name, game, not args.curse_preview)
    for name, contents in built.items():
        (args.output / name).write_bytes(contents)
        print(name, len(contents), hashlib.sha256(contents).hexdigest())


if __name__ == '__main__':
    main()
