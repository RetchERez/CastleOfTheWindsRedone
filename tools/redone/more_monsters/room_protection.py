"""Capture and persist bounds of native scripted rooms without changing CWG layout."""

from dataclasses import dataclass
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Layout:
    section: int
    static_records: int
    count: int
    room_field: int
    begin: int
    outcome: int
    failure: int
    original_outcome: bytes


LAYOUTS = {
    1: Layout(11, 0x63, 22, 0x3d8a, 0x225b, 0x22ab, 0x22fc, bytes.fromhex('0bc0744d')),
    2: Layout(8, 0x9b, 28, 0x3d9a, 0x24dd, 0x252d, 0x257e, bytes.fromhex('0bc0744d')),
}
ORIGINAL_BEGIN = bytes.fromhex('b82400f72e96008bd8')


def script_flags(executable, part):
    layout = LAYOUTS[part]
    body = executable.segments[layout.section].data
    flags = []
    for level in range(layout.count):
        kind, _, pointer = struct.unpack_from('<HHH', body, layout.static_records + 0x24*level)
        flags.append(int(kind == 2 and pointer != 0 and struct.unpack_from('<H', body, pointer)[0] != 0))
    return tuple(flags)


def selector_source(executable, part):
    """Append after the selector's code and call room_protected with the floor in BX."""
    layout = LAYOUTS[part]
    source = (HERE / 'room_selector.asm').read_text(encoding='ascii')
    flags = ','.join(map(str, script_flags(executable, part)))
    return f'\n%define ROOM_FIELD {layout.room_field}\n{source}\nscripted_floors: db {flags}\n'


def capture_code(executable, part, assemble):
    """Return (native map segment, relocated content) suitable for relocate_segment."""
    layout = LAYOUTS[part]
    segment = executable.segments[layout.section]
    origin = segment.allocation
    constants = {'ROOM_FIELD': layout.room_field, 'ROOM_BEGIN': layout.begin,
                 'ROOM_OUTCOME': layout.outcome, 'ROOM_FAILURE': layout.failure}
    payload = assemble(HERE / 'room_capture.asm', origin, constants)
    body = bytearray(segment.data.ljust(origin, b'\x00'))
    destinations = struct.unpack_from('<HH', payload)
    for offset, expected, destination in (
            (layout.begin, ORIGINAL_BEGIN, destinations[0]),
            (layout.outcome, layout.original_outcome, destinations[1])):
        size = len(expected)
        if body[offset:offset + size] != expected:
            raise ValueError(f'Unexpected native scripted-room bytes at {offset:#x}')
        if any(offset <= fixup < offset + size for fixup in segment.relocations):
            raise ValueError('Scripted-room redirect would overwrite a native relocation')
        jump = b'\xe9' + struct.pack('<H', (destination-offset-3) & 0xffff)
        body[offset:offset + size] = jump + b'\x90' * (size-3)
    body.extend(payload)
    return layout.section, bytes(body)
