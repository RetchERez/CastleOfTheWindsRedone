"""Add Redone lettering to the original Win16 title bitmap."""

from hashlib import sha256
from struct import pack_into, unpack_from

from color_resources import _read_resources, _word


ORIGINAL_SPLASH = 'f98278467f58ed28aaa836899719a3dc29d1c5a124c801ef33b7bc53687d7181'


GLYPHS = {
    'R': ('####.', '.#..#', '.#..#', '.###.', '.#.#.', '.#..#', '##..#'),
    'E': ('#####', '.#..#', '.#.#.', '.###.', '.#.#.', '.#..#', '#####'),
    'D': ('####.', '.#..#', '.#..#', '.#..#', '.#..#', '.#..#', '####.'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'N': ('##..#', '.##.#', '.##.#', '.#.##', '.#.##', '.#..#', '##..#'),
    'B': ('####.', '.#..#', '.#..#', '.###.', '.#..#', '.#..#', '####.'),
    'y': ('.....', '.....', '#...#', '#...#', '.####', '....#', '.###.'),
    'e': ('.....', '.....', '.###.', '#...#', '#####', '#....', '.###.'),
    't': ('..#..', '..#..', '.####', '..#..', '..#..', '..#..', '...##'),
    'c': ('.....', '.....', '.###.', '#...#', '#....', '#...#', '.###.'),
    'h': ('#....', '#....', '#.##.', '##..#', '#...#', '#...#', '#...#'),
    ' ': ('.....',) * 7,
}


def decode_rows(body):
    size, width, height, planes, depth, compression = unpack_from('<IiiHHI', body)
    if (size, planes, depth, compression) != (40, 1, 4, 2) or (width, height) not in ((441, 230), (425, 106)):
        raise ValueError('Unexpected splash bitmap dimensions or format')
    rows = [bytearray(width) for _ in range(height)]
    x = y = 0
    pos = 104
    end = pos + unpack_from('<I', body, 20)[0]
    while pos + 2 <= end:
        count, color = body[pos:pos + 2]
        pos += 2
        if count:
            pixels = bytes((color >> 4, color & 15))
            row = (pixels * ((count + 1) // 2))[:count]
        elif color == 0:
            x, y = 0, y + 1
            continue
        elif color == 1:
            return rows[::-1]
        elif color == 2:
            dx, dy = body[pos:pos + 2]
            x, y, pos = x + dx, y + dy, pos + 2
            continue
        else:
            count = color
            size = (count + 1) // 2
            row = bytes(channel for packed in body[pos:pos + size] for channel in (packed >> 4, packed & 15))[:count]
            pos += size + size % 2
        if y >= height or x + count > width or len(row) != count:
            raise ValueError('Splash bitmap row exceeds its declared dimensions')
        rows[y][x:x + count] = row
        x += count
    raise ValueError('Missing splash bitmap end marker')


def alternating_length(row, start):
    end = min(len(row), start + 255)
    if end - start < 3:
        return end - start
    for pos in range(start + 2, end):
        if row[pos] != row[start + (pos - start) % 2]:
            return pos - start
    return end - start


def encode_rows(rows):
    stream = bytearray()
    for row in reversed(rows):
        x = 0
        while x < len(row):
            count = alternating_length(row, x)
            if count > 3 or x + count == len(row):
                stream.extend((count, row[x] << 4 | row[x + (count > 1)]))
                x += count
                continue
            end = x + count
            while end < min(x + 254, len(row)) and alternating_length(row, end) < 4:
                end += 1
            literals = row[x:end]
            if len(literals) < 3:
                stream.extend((count, row[x] << 4 | row[x + 1]))
                x += count
                continue
            stream.extend((0, len(literals)))
            if len(literals) % 2:
                literals.append(0)
            packed = bytes(a << 4 | b for a, b in zip(literals[::2], literals[1::2], strict=True))
            stream.extend(packed)
            if len(packed) % 2:
                stream.append(0)
            x = end
        stream.extend((0, 0))
    stream.extend((0, 1))
    return stream


def letter(rows, text, left, top, width, height, tracking, face, shade):
    points = []
    for index, symbol in enumerate(text):
        start = left + index * (width + tracking)
        glyph = GLYPHS[symbol]
        for y in range(height):
            line = glyph[y * 7 // height]
            for x in range(width):
                if line[x * 5 // width] == '#':
                    points.append((start + x, top + y))
    if any(rows[y][x] or rows[y + 1][x + 1] for x, y in points):
        raise ValueError('Redone lettering would overlap original splash artwork')
    for x, y in points:
        rows[y + 1][x + 1] = shade
    for x, y in points:
        rows[y][x] = face


def paint_bitmap(original):
    rows = decode_rows(original)
    # Center the two words as a group on the original logo's 198px centerline.
    # Both sit on the same baseline, with the smaller byline offset by a 12px gap.
    letter(rows, 'REDONE', 105, 212, 15, 17, 3, 11, 3)
    letter(rows, 'By Retch', 222, 216, 7, 13, 2, 15, 7)
    stream = encode_rows(rows)
    body = bytearray(original[:104])
    pack_into('<I', body, 20, len(stream))
    body.extend(stream)
    if len(body) > len(original) or decode_rows(body) != rows:
        raise ValueError('Redone splash failed its in-place bitmap round trip')
    return body.ljust(len(original), b'\0')


def splash_resources(data):
    ne = unpack_from('<I', data, 0x3C)[0]
    if data[:2] != b'MZ' or data[ne:ne + 2] != b'NE':
        raise ValueError('Expected a Windows NE executable')
    table_start = ne + _word(data, ne + 0x24)
    table_end = ne + _word(data, ne + 0x26)
    types, _ = _read_resources(data, table_start, table_end)
    return [types[0x8002][1][identity] for identity in (0x800A, 0x800B)]


def brand(data):
    result = bytearray(data)
    resource = splash_resources(data)[0]
    # Match the framed DIB payload, allowing different NE alignment padding.
    size = 104 + unpack_from('<I', resource.body, 20)[0]
    if sha256(resource.body[:size]).hexdigest() != ORIGINAL_SPLASH:
        raise ValueError(f'Unknown original title bitmap resource {resource.identity:#06x}')
    result[resource.offset:resource.offset + len(resource.body)] = paint_bitmap(resource.body)
    return bytes(result)
