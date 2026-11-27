"""Write Win16 New Executable code segments without changing resources."""

import struct


def _word(buffer, offset):
    return struct.unpack_from('<H', buffer, offset)[0]


def relocate_segment(executable, number, contents, selectors, imports=None):
    """Append a replacement code segment and re-point its original table entry.

    Selector offsets refer to new far pointers in the appended code. An
    isolated selector fixup has a 0xffff chain tail in the on-disk bytes.
    """
    if executable[:2] != b'MZ':
        raise ValueError('Expected a DOS executable header')
    ne = struct.unpack_from('<I', executable, 0x3C)[0]
    if executable[ne:ne + 2] != b'NE':
        raise ValueError('Expected a Windows NE executable')
    count = _word(executable, ne + 0x1C)
    if not 1 <= number <= count:
        raise ValueError(f'Invalid segment number {number}')

    entry = ne + _word(executable, ne + 0x22) + 8 * (number - 1)
    sector, disk_size, flags, allocated = struct.unpack_from('<HHHH', executable, entry)
    if not sector or flags & 0x0009:
        raise ValueError('Expected an ordinary file-backed code segment')
    shift = _word(executable, ne + 0x32)
    old_start = sector << shift
    old_size = disk_size or 0x10000
    new_size = len(contents)
    if not old_size <= new_size <= 0x10000:
        raise ValueError('Replacement must retain the original segment and fit in 64 KiB')

    fixup_records = bytearray()
    if flags & 0x0100:
        records = old_start + old_size
        current_count = _word(executable, records)
        first = records + 2
        fixup_records.extend(executable[first:first + 8 * current_count])
        if len(fixup_records) != 8 * current_count:
            raise ValueError('Truncated original fixup table')
    for offset, target in sorted(selectors.items()):
        if not old_size <= offset <= new_size - 2 or not 1 <= target <= count:
            raise ValueError(f'Invalid new selector fixup {offset:#x} -> {target}')
        if contents[offset:offset + 2] != b'\xff\xff':
            raise ValueError(f'Selector fixup {offset:#x} must end its chain')
        fixup_records.extend(struct.pack('<BBHHH', 2, 0, offset, target, 0))
    module_count = _word(executable, ne + 0x1E)
    for offset, (module, ordinal) in sorted((imports or {}).items()):
        if not old_size <= offset <= new_size - 4 or not 1 <= module <= module_count or not 1 <= ordinal <= 0xFFFF:
            raise ValueError(f'Invalid new import fixup {offset:#x} -> {module}.{ordinal}')
        if contents[offset:offset + 4] != b'\xff\xff\0\0':
            raise ValueError(f'Import fixup {offset:#x} must use a single far-pointer chain entry')
        fixup_records.extend(struct.pack('<BBHHH', 3, 1, offset, module, ordinal))
    if fixup_records:
        flags |= 0x0100

    alignment = 1 << shift
    pad = (-len(executable)) % alignment
    new_sector = (len(executable) + pad) >> shift
    if new_sector > 0xFFFF:
        raise ValueError('Appended segment would overflow the NE file sector field')
    new_allocated = max(allocated or 0x10000, new_size)

    result = bytearray(executable)
    struct.pack_into('<HHHH', result, entry, new_sector, new_size & 0xFFFF, flags, new_allocated & 0xFFFF)
    result.extend(b'\0' * pad)
    result.extend(contents)
    if flags & 0x0100:
        result.extend(struct.pack('<H', len(fixup_records) // 8))
        result.extend(fixup_records)
    return bytes(result)
