"""Add native Win16 inventory icon variants with visible rarity brackets."""

from dataclasses import dataclass, replace
from struct import pack, pack_into, unpack_from


RT_ICON = 0x8003
RT_GROUP_ICON = 0x800E
RARITY_COLORS = {
    1: ((0x00, 0x00, 0xFF),),
    2: ((0xFF, 0xFF, 0x00),),
    # Two orange shades also distinguish the mark on 16-color VGA by dithering.
    3: ((0xFF, 0x78, 0x00), (0xFF, 0xAA, 0x00)),
}
# All weapon subtype icons and armor class icons, for each native condition.
GEAR_ICONS = (
    0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x6C, 0x6D, 0x6E, 0x6F, 0x70,
    0x85, 0x86, 0x89, 0x8A, 0x95, 0x96, 0x97, 0xB3, 0xB4, 0xB5,
    0xB6, 0xB7, 0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF,
    0xC0, 0xC1,
)


@dataclass(frozen=True)
class Resource:
    offset: int
    flags: int
    identity: int
    handle: int
    usage: int
    body: bytes


def _word(data, offset):
    return unpack_from('<H', data, offset)[0]


def _align(value, size):
    return (value + size - 1) & -size


def loot_icon_mapping():
    return {(native, tier): 0x0300 + 3 * index + tier - 1
            for index, native in enumerate(GEAR_ICONS)
            for tier in RARITY_COLORS}


def _add_corner_marks(source, colors):
    if unpack_from('<IiiHHI', source) != (40, 32, 64, 1, 4, 0):
        raise ValueError('Expected an uncompressed 32-by-32 4bpp icon')
    if source[40:44] != b'\0' * 4 or len(source) < 744:
        raise ValueError('Unexpected icon palette or mask')

    palette_end = 104
    mask_start = 616
    occupied = set()
    used_colors = set()
    for pos in range(1024):
        pixel = source[palette_end + pos // 2]
        color = pixel >> 4 if pos % 2 == 0 else pixel & 15
        if color or not source[mask_start + pos // 8] & (0x80 >> (pos % 8)):
            occupied.add(pos)
            used_colors.add(color)

    icon = bytearray(source)
    free = [index for index in range(1, 16) if index not in used_colors]
    if len(free) < len(colors):
        raise ValueError('Icon has too few available palette slots')
    for index, (red, green, blue) in zip(free, colors):
        icon[40 + index * 4:44 + index * 4] = bytes((blue, green, red, 0))

    # Four thick corners plus a low stripe keep color in the available part
    # of a paper-doll icon when a long name pushes its upper edge out of view.
    # In the bottom-up bitmap, row zero is the edge nearest the item name.
    for y in range(32):
        row_edge = min(y, 31 - y)
        for x in range(32):
            column_edge = min(x, 31 - x)
            bracket = (row_edge < 6 and column_edge < 11
                       or column_edge < 6 and row_edge < 11)
            bottom = y < 6 and 8 <= x <= 23
            pos = y * 32 + x
            if pos in occupied or not (bracket or bottom):
                continue
            accent = (0 < row_edge < 5 and 0 < column_edge < 10
                      or 0 < column_edge < 5 and 0 < row_edge < 10
                      or bottom and 0 < y < 5)
            color = free[(x + y) % len(colors)] if accent else 0
            xor_byte = palette_end + pos // 2
            shift = 4 if pos % 2 == 0 else 0
            icon[xor_byte] = (icon[xor_byte] & ~(15 << shift)) | (color << shift)
            icon[mask_start + pos // 8] &= ~(0x80 >> (pos % 8))
    return bytes(icon)


def _read_resources(executable, table_offset, table_end):
    shift = _word(executable, table_offset)
    cursor = table_offset + 2
    types = {}
    while (kind := _word(executable, cursor)):
        if not kind & 0x8000 or kind in types:
            raise ValueError('Unexpected named or duplicate resource type')
        count, reserved = unpack_from('<HI', executable, cursor + 2)
        cursor += 8
        records = {}
        for _ in range(count):
            offset, length, flags, identity, handle, usage = unpack_from('<6H', executable, cursor)
            cursor += 12
            first = offset << shift
            last = first + (length << shift)
            if identity in records or last > len(executable):
                raise ValueError('Invalid resource record')
            records[identity] = Resource(first, flags, identity, handle, usage, executable[first:last])
        types[kind] = reserved, records
    return types, executable[cursor + 2:table_end]


def _add_variants(types, mapping):
    icons = types[RT_ICON][1]
    groups = types[RT_GROUP_ICON][1]
    for (source, tier), identity in mapping.items():
        group = groups[0x8000 | source]
        if (_word(group.body, 4), _word(group.body, 26)) != (2, 4):
            raise ValueError(f'Unexpected icon group {source:#x}')
        original = icons[0x8000 | _word(group.body, 32)]
        new_identity = 0x8000 | identity
        if new_identity in groups or new_identity in icons:
            raise ValueError(f'Icon resource ID already allocated: {identity:#x}')
        descriptor = bytearray(group.body)
        pack_into('<H', descriptor, 32, identity)
        sprite = _add_corner_marks(original.body, RARITY_COLORS[tier])
        groups[new_identity] = replace(group, offset=-1, identity=new_identity, body=bytes(descriptor))
        icons[new_identity] = replace(original, offset=-1, identity=new_identity, body=sprite)


def add_loot_icons(executable: bytes, part: int):
    """Return an updated NE image and the (native icon, rarity) lookup table.

    Call after all code segments have been written. Move the resource block past
    code and use 32-byte resource sectors to fit both titles with the additions.
    """
    mapping = loot_icon_mapping()
    return repack_resources(executable, part, 2 * len(mapping),
                            lambda types: _add_variants(types, mapping)), mapping


def repack_resources(executable, part, additional_records, edit):
    """Repack the NE resource directory after appending resources."""
    ne = unpack_from('<I', executable, 0x3C)[0]
    if (executable[:2], executable[ne:ne + 2]) != (b'MZ', b'NE'):
        raise ValueError('Expected a Windows NE executable')
    if _word(executable, ne + 0x0E) != {1: 32, 2: 28}[part]:
        raise ValueError('Unexpected program or title')
    table_start = ne + _word(executable, ne + 0x24)
    table_end = ne + _word(executable, ne + 0x26)
    types, resource_names = _read_resources(executable, table_start, table_end)
    original = sorted((item for _, records in types.values() for item in records.values()),
                      key=lambda item: item.offset)
    resource_start = original[0].offset
    resource_end = original[-1].offset + len(original[-1].body)
    if any(item.offset + len(item.body) != following.offset
           for item, following in zip(original, original[1:])):
        raise ValueError('The original resource block is not contiguous')

    edit(types)
    new_entries_size = additional_records * 12
    segment_paragraph = 1 << _word(executable, ne + 0x32)
    header_growth = _align(new_entries_size, segment_paragraph)
    new_table_end = table_end + header_growth
    result = bytearray(executable[:table_start])
    result.extend(b'\0' * (new_table_end - table_start))
    result.extend(executable[table_end:resource_start])
    result.extend(executable[resource_end:])

    def move_offset(offset):
        if table_end <= offset < resource_start:
            return offset + header_growth
        if offset >= resource_end:
            return offset + header_growth - (resource_end - resource_start)
        raise ValueError(f'Unexpected non-resource offset {offset:#x}')

    # Relative NE header table pointers and the absolute nonresident-name offset.
    for position in (0x04, 0x26, 0x28, 0x2A):
        before = _word(executable, ne + position)
        pack_into('<H', result, ne + position, move_offset(ne + before) - ne)
    nonresident = unpack_from('<I', executable, ne + 0x2C)[0]
    pack_into('<I', result, ne + 0x2C, move_offset(nonresident))

    # Main code, DGROUP, and the linker-specified Windows fast-load area.
    segments = ne + _word(executable, ne + 0x22)
    count = _word(executable, ne + 0x1C)
    for position in (*range(segments, segments + count * 8, 8), ne + 0x38):
        sector = _word(executable, position)
        if sector:
            new_offset = move_offset(sector * segment_paragraph)
            if new_offset % segment_paragraph:
                raise ValueError('Misaligned segment offset')
            pack_into('<H', result, position, new_offset // segment_paragraph)

    shift = 5
    quantum = 1 << shift
    result.extend(b'\0' * (_align(len(result), quantum) - len(result)))
    table = bytearray(pack('<H', shift))
    for kind, (reserved, records) in types.items():
        table.extend(pack('<HHI', kind, len(records), reserved))
        for item in records.values():
            size = _align(len(item.body), quantum)
            identity = item.identity if item.identity & 0x8000 else item.identity + new_entries_size
            table.extend(pack('<6H', len(result) >> shift, size >> shift,
                              item.flags, identity, item.handle, item.usage))
            result.extend(item.body)
            result.extend(b'\0' * (size - len(item.body)))
    table.extend(b'\0\0' + resource_names)
    result[table_start:table_start + len(table)] = table
    return bytes(result)
