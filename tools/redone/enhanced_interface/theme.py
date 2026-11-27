"""Build game-local Win16 color hooks for registered Castle of the Winds."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import struct
from subprocess import run
import sys
from tempfile import TemporaryDirectory
from zlib import crc32

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE.parents[1])]
from ne_patch import relocate_segment
from ne_research import Executable, word

PALETTE = json.loads((HERE / 'theme_palette.json').read_text(encoding='utf-8'))
THEMES = ('warm', 'dark', 'classic')
NE_FAST_LOAD = 0x08
SUPPORTED = {
    1: {
        'e90d202717882449196cc087bc2231d2c94a17a553c4b5dfa4c91ed4c718c3b0',
        '70c2762f0aa003105752f3709e47e83cccaef31f3ab4346f4a3dc36981b69451',
        'e1c23b146534c2dbc294c7db03c8d1c7394d3af5c62d46ba33d9b7deee7c0ace',
        '32224a578e73a0acd537f2f759fee6775ce240458dd8c69d95fe544b99366204',
        'c72cc531a40c34eb1d532f9836641468de84d96b2d6748c4e80291cabb0afa60',
        'd1966843fe93644f81f2d9fbee6268c6e90dd025c638646e3651316a2145a5b5',
        'e78e79849a716a444f12944f6fc1932e87c1eaae6d8766e0d15ad8242f0e253a',
        'e73c8df28cc05112c1a5569abaafc8a993419d52b123a36b85fc2191d77d4f52',
        '48298072d8f55241583f333ec6b9ec8a9b93eb5cab22d8c00bfbf999c9be104c',
        '6f27172eb8db55698264b92e1ad59fe02d6b37c8e4af41a4e824d21481027493',
        '0826621fd62d512e13ed69c1575cd918df2c721ea20f3d3e7042fcdf3e1823c5',
        'a1024efd622bec22c56bb16b13641f92053d8d4cc1bbdec8e17184c83588d69d',
        'af03ec8c67c81f08b3baac3d67c99336d938ce210eb42a1c37960d41911d4704',
        '3de71f5ddf5c488cf6c11a55dee6fb38e78ed028ee2c489d7ba07d087ab932ba',
    },
    2: {
        'a056ac0947c967a26e6c5ece67893b7f6562611ef08736f87ab1d96c2d05da2e',
        'f764c2e7f757197a5c2226665009818c7548d2a74e4c29f328342cf7b7b633bc',
        '14e096a51389318de6bec0ff6406336dc27057b5d08f883c7fe00033276603b1',
        '2117f2174f7d0406a70080c30b383f4ae88fc4aa053c57c899a7a45f9965dce5',
        '5030e740628e4f51b1f33a5aae286aa2bd84e7549158a31c7a159a26aeab2960',
        'ebbc6b68e54c01b6e2829125bdcdfa2f3f2ed5aeb8e7f91d53af8fda8ac2dee7',
        'd436d36d22c12b7a29e981a78b9a158b3008bc4a3585a6cdcf8ca66745b18fe4',
        'a24f0aa749bf5b79ca5424664af819ac5f6abf7840ed5592f72ce8d404e2c891',
        'd5a3b4530fff0b72784ee7c5aed62a1a3b8424020c211edf5afcde4387f2c0f5',
        '536584eb31022b1c697c2354e344be00892c6a67e255555d1d6c806b43b22a9d',
        '8485d052392d8331f911acc55072e174333bf9a863eaf23e0bf9e9e34f1bb186',
        '5c939196f2b0e7232e7f445e6424ac34fd497580174b782890df7cf559061eee',
        '062c0321edd842891b4d452af03ba204988b099e9798df640ecfdfb0de0a6010',
        '1febb45ece3322dd0ae185a1866750d5a83b286a42975d1badf6c278e9ebffd1',
    },
}
CLASS_IMPORTS = (('GDI', 66), ('USER', 57), ('GDI', 69), ('USER', 66), ('USER', 68), ('GDI', 80))
INVENTORY_IMPORTS = (
    ('GDI', 2), ('GDI', 9), ('USER', 85), ('GDI', 9), ('GDI', 2),
    ('GDI', 66), ('GDI', 45), ('GDI', 87), ('GDI', 45),
    ('GDI', 61), ('GDI', 45), ('GDI', 27), ('GDI', 45), ('GDI', 69),
    ('GDI', 45), ('GDI', 69), ('USER', 84), ('GDI', 66), ('USER', 81), ('GDI', 69),
    ('GDI', 80),
)
INVENTORY_TARGETS = (('USER', 85), ('GDI', 27), ('USER', 84))
DOLL_TARGET = ('GDI', 123)
DOLL_IMPORTS = (('GDI', 30), ('GDI', 175), ('GDI', 39), ('GDI', 123), ('GDI', 176))
DIALOG, FILL, DRAWTEXT, TEXTOUT = (('USER', 87), ('USER', 81), ('USER', 85), ('GDI', 33))
TABBED = ('USER', 196)
WINDOW_IMPORTS = {
    DIALOG: (('USER', 239), ('GDI', 69), ('GDI', 69), ('USER', 136), ('USER', 135),
             ('USER', 35), ('GDI', 9), ('GDI', 1), ('GDI', 66)),
    FILL: (('GDI', 66), ('USER', 81), ('GDI', 69)),
    DRAWTEXT: (('USER', 85),),
    TEXTOUT: (('GDI', 33),),
    TABBED: (('GDI', 90), ('GDI', 9), ('GDI', 1), ('USER', 196), ('GDI', 1), ('GDI', 9)),
}


def colorref(color):
    return int.from_bytes(bytes.fromhex(color), 'little')


def theme_values(theme):
    settings = PALETTE[theme]
    return {'MAIN': colorref(settings['main']), 'PANEL': colorref(settings['panel']), 'WELL': colorref(settings['well']),
            'INK': colorref(settings['text']), 'BORDER': colorref(settings['border']),
            'SECONDARY': colorref(settings['secondary']), 'ICON_BACKING': int(theme == 'dark'),
            'WARNING': colorref(settings['warning']), 'MAGIC': colorref(settings['magic']),
            'DOLL_GUIDES': colorref('92635C' if theme == 'warm' else 'C89686'),
            'PANEL_LOW': 0xc0c0c0 if theme == 'warm' else 0x808080,
            'WELL_LOW': 0xc0c0c0 if theme == 'warm' else 0x808080,
            'BORDER_LOW': 0, 'INK_LOW': 0, 'BACKING_LOW': 0xc0c0c0}


def assemble_blob(exe, filename, values, hook_names, import_names, assembler):
    if isinstance(assembler, str):
        assembler = ['wsl', '-d', 'Ubuntu', '--', assembler] if assembler.startswith('/') else [assembler]
    with TemporaryDirectory(dir=HERE) as temporary:
        output = Path(temporary) / 'theme.bin'
        arguments = [f'-D{name}={value}' for name, value in values.items()]
        run([*assembler, '-f', 'bin', '-w+error', *arguments, '-o',
             output.relative_to(HERE).as_posix(), filename], cwd=HERE, check=True)
        data = output.read_bytes()
    header = struct.unpack_from('<' + 'H' * (len(hook_names) + len(import_names)), data)
    hooks = dict(zip(hook_names, header[:len(hook_names)], strict=True))
    imports = {pos: (exe.imports.index(module), ordinal)
               for pos, (module, ordinal) in zip(header[len(hook_names):], import_names, strict=True) if pos}
    return data, hooks, imports


def assemble(exe, segment, theme, assembler):
    classes = segment.index == 2
    doll = segment.index in (4, 25)
    values = {**theme_values(theme), 'ORIGIN': len(segment.data),
              'CLASS_HOOK': int(classes), 'DOLL_HOOK': int(doll)}
    hook_names = (('USER', 57),) if classes else INVENTORY_TARGETS
    import_names = CLASS_IMPORTS if classes else INVENTORY_IMPORTS
    if doll:
        hook_names += (DOLL_TARGET,)
        import_names += DOLL_IMPORTS
    return assemble_blob(exe, 'theme.asm', values, hook_names, import_names, assembler)


def assemble_windows(exe, origin, part, theme, assembly, targets):
    values = {**theme_values(theme), 'ORIGIN': origin, 'WHITE_BRUSH': 0x3ce2 if part == 1 else 0x3cf2,
              'HAS_DIALOG': int(DIALOG in targets), 'HAS_FILL': int(FILL in targets),
              'HAS_DRAWTEXT': int(DRAWTEXT in targets), 'HAS_TEXTOUT': int(TEXTOUT in targets),
              'HAS_TABBED': int(TABBED in targets)}
    imports = tuple(api for target in targets for api in WINDOW_IMPORTS[target])
    if DRAWTEXT in targets or TEXTOUT in targets:
        imports += (('GDI', 2), ('GDI', 9), ('GDI', 9), ('GDI', 2))
    imports += (('GDI', 80), ('GDI', 80))
    return assemble_blob(exe, 'window_theme.asm', values, targets, imports, assembly)


def window_targets(exe, part):
    found = {}
    status = 10 if part == 1 else 7
    for segment, _, target in exe.calls():
        if (target == DIALOG or segment in (1, 2) and target in (FILL, DRAWTEXT, TEXTOUT)
                or segment == status and target in (DRAWTEXT, TABBED)):
            found.setdefault(segment, set()).add(target)
    return {segment: tuple(target for target in (DIALOG, FILL, DRAWTEXT, TEXTOUT, TABBED) if target in targets)
            for segment, targets in found.items()}


def moveable_tail(exe):
    """Separate the large graphics build's trailing NE resources from its code."""
    shift = word(exe.data, exe.resource_table)
    cursor = exe.resource_table + 2
    records = []
    while word(exe.data, cursor):
        count = word(exe.data, cursor + 2)
        cursor += 8
        for address in range(cursor, cursor + 12 * count, 12):
            sector, blocks = struct.unpack_from('<HH', exe.data, address)
            records.append((sector << shift, (sector + blocks) << shift, address))
        cursor += count * 12
    records.sort()
    first = records[0][0]
    if (records[-1][1] != len(exe.data) or cursor >= first
            or any(left[1] != right[0] for left, right in zip(records, records[1:]))):
        raise ValueError('Large build lacks a separate trailing resource block')
    for segment in exe.segments.values():
        end = segment.file_offset + len(segment.data)
        if segment.flags & 0x100:
            end += 2 + 8 * word(exe.data, end)
        if end > first:
            raise ValueError('An executable segment overlaps the graphics resources')
    header, = struct.unpack_from('<I', exe.data, 0x3c)
    names_end = struct.unpack_from('<I', exe.data, header + 0x2c)[0] + word(exe.ne, 0x20)
    preload_end = (word(exe.ne, 0x38) + word(exe.ne, 0x3a)) << word(exe.ne, 0x32)
    if max(names_end, preload_end) > first:
        raise ValueError('Executable tables overlap the graphics resources')
    return first, shift, records


def append_resources(exe, image, tail):
    start, alignment_shift, records = tail
    new_start = (len(image) + (1 << alignment_shift) - 1) & -(1 << alignment_shift)
    if ((records[-1][0] + new_start - start) >> alignment_shift) <= 0xffff:
        image.extend(bytes(new_start - len(image)))
        delta = (new_start - start) >> alignment_shift
        for _, _, address in records:
            struct.pack_into('<H', image, address, word(image, address) + delta)
        image.extend(exe.data[start:])
        return bytes(image)

    # Large earlier graphics builds used all available 16-bit resource
    # sectors. Re-align those resources without modifying their contents.
    while len(image) + len(exe.data) - start + len(records) * (1 << alignment_shift) > 0xffff << alignment_shift:
        alignment_shift += 1
    alignment = 1 << alignment_shift
    struct.pack_into('<H', image, exe.resource_table, alignment_shift)
    image.extend(bytes((-len(image)) % alignment))
    for old_start, old_end, address in records:
        size = old_end - old_start
        padded = (size + alignment - 1) & -alignment
        struct.pack_into('<HH', image, address, len(image) >> alignment_shift, padded >> alignment_shift)
        image.extend(exe.data[old_start:old_end])
        image.extend(bytes(padded - size))
    return bytes(image)


def redirect_imports(image, exe, segment, hooks):
    table = segment.file_offset + len(segment.data)
    result = bytearray(image)
    code = bytearray(segment.data)
    found = set()
    retained = bytearray()
    for offset in range(table + 2, table + 2 + 8 * word(image, table), 8):
        record = image[offset:offset + 8]
        source_type, relocation_type, first, module, ordinal = struct.unpack('<BBHHH', record)
        key = (exe.imports[module], ordinal) if (source_type, relocation_type) == (3, 1) else None
        if key not in hooks:
            retained.extend(record)
            continue
        linked = first
        while linked != 0xffff:
            if not linked or code[linked - 1] != 0x9a or segment.relocations[linked] != (3, key):
                raise ValueError(f'Expected far call at {segment.index}:{linked - 1:04x}')
            following = word(code, linked)
            relative = (hooks[key] - linked - 4) & 0xffff
            # Same five-byte instruction span, with the exact far return ABI.
            # NE movable segments use an entry-point index for a far fixup.
            # An assembler-local call avoids introducing a movable NE entry.
            code[linked - 1:linked + 4] = b'\x90\x0e\xe8' + struct.pack('<H', relative)
            linked = following
        found.add(key)
    if found != hooks.keys():
        raise ValueError(f'Unexpected native API fixups in segment {segment.index}: {found}')
    struct.pack_into('<H', result, table, len(retained) // 8)
    result[table + 2:table + 2 + len(retained)] = retained
    return result, code


def build(path, part, theme, assembler='nasm'):
    exe = Executable(path)
    if sha256(exe.data).hexdigest() not in SUPPORTED[part]:
        name = 'Chapter I' if part == 1 else 'Chapter II'
        raise ValueError(f'Expected a supported {name} executable')
    if theme == 'classic':
        return exe.data
    sector_limit = 0xffff << word(exe.ne, 0x32)
    primary = (2, 4, 5) if part == 1 else (2, 25, 26)
    windows = window_targets(exe, part)
    numbers = sorted(set(primary) | windows.keys())
    growth_bound = sum(len(exe.segments[number].data) + 4096 for number in numbers)
    tail = moveable_tail(exe) if len(exe.data) + growth_bound > sector_limit else None
    image = exe.data[:tail[0]] if tail else exe.data
    for number in numbers:
        segment = exe.segments[number]
        body, hooks, imports = assemble(exe, segment, theme, assembler) if number in primary else (b'', {}, {})
        if targets := windows.get(number):
            extra, window_hooks, window_imports = assemble_windows(
                exe, len(segment.data) + len(body), part, theme, assembler, targets)
            body += extra
            hooks.update(window_hooks)
            imports.update(window_imports)
        image, code = redirect_imports(image, exe, segment, hooks)
        if number == primary[1]:
            # Keep long equipment names below the existing 32-pixel icon.
            # The native clipped rectangle and full Inspect name still apply.
            if code[0x03c4:0x03c6] != b'\x73\x1f':
                raise ValueError('Unexpected equipment label rectangle branch')
            code[0x03c4] = 0xeb
        image = relocate_segment(image, number, code + body, {}, imports)
    # Segment 2 originally occupies the NE application's contiguous fast-load
    # region. It remains a preload segment, but the Windows 3.1 loader must
    # read its new file offset individually.
    image = bytearray(image)
    header, = struct.unpack_from('<I', image, 0x3c)
    image[header + 0x37] &= ~NE_FAST_LOAD
    struct.pack_into('<HH', image, header + 0x38, 0, 0)
    if not tail:
        return bytes(image)
    return append_resources(exe, image, tail)


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('part', type=int, choices=(1, 2))
    cli.add_argument('source', type=Path)
    cli.add_argument('destination', type=Path)
    cli.add_argument('--theme', choices=THEMES, default='warm')
    cli.add_argument('--assembler', default='nasm')
    args = cli.parse_args()
    contents = build(args.source, args.part, args.theme, args.assembler)
    with args.destination.open('xb') as output:
        output.write(contents)
    print(f'{args.destination.name} {args.theme}: CRC32 {crc32(contents):08X}, SHA-256 {sha256(contents).hexdigest()}')


if __name__ == '__main__':
    main()
