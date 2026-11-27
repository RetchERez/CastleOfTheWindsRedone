"""Inspect the clean Win16 Castle executables without launching them."""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import struct

from capstone import CS_ARCH_X86, CS_MODE_16, Cs
from capstone.x86 import X86_OP_IMM


def word(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def prefixed_string(data, offset):
    return data[offset + 1:offset + 1 + data[offset]].decode('ascii', errors='replace')


@dataclass(frozen=True)
class Segment:
    index: int
    file_offset: int
    flags: int
    allocation: int
    data: bytes
    relocations: dict

    @property
    def code(self):
        return self.flags & 1 == 0


class Executable:
    def __init__(self, path):
        self.data = data = Path(path).read_bytes()
        header = struct.unpack_from('<I', data, 0x3C)[0]
        if data[:2] != b'MZ' or data[header:header + 2] != b'NE':
            raise ValueError('Expected an MZ/NE executable')
        self.ne = ne = data[header:header + 0x40]
        self.dgroup = word(ne, 0x0E)
        self.resource_table = header + word(ne, 0x24)
        self.segments = {}
        modules = header + word(ne, 0x28)
        names = header + word(ne, 0x2A)
        self.imports = [None] + [prefixed_string(data, names + word(data, modules + i * 2))
                                 for i in range(word(ne, 0x1E))]
        segment_table = header + word(ne, 0x22)
        for index in range(1, word(ne, 0x1C) + 1):
            sector, length, flags, allocation = struct.unpack_from('<HHHH', data, segment_table + 8 * (index - 1))
            start = sector << word(ne, 0x32)
            length = (length or 65536) if sector else 0
            body = data[start:start + length]
            relocations = {}
            if flags & 0x0100:
                first = start + length
                for i in range(word(data, first)):
                    source_type, relocation_type, source, dest1, dest2 = struct.unpack_from('<BBHHH', data, first + 2 + 8 * i)
                    kind = relocation_type & 3
                    if kind == 0:
                        target = (dest1 & 0xFF, dest2)
                    elif kind == 1:
                        target = (self.imports[dest1], dest2)
                    elif kind == 2:
                        target = (self.imports[dest1], prefixed_string(data, names + dest2))
                    else:
                        target = ('OS', dest1)
                    seen = set()
                    while source != 0xFFFF:
                        if source in seen or source + 2 > len(body):
                            raise ValueError(f'Invalid relocation chain in segment {index}: {source:04x}')
                        seen.add(source)
                        relocations[source] = (source_type, target)
                        if relocation_type & 4:
                            break
                        source = word(body, source)
            self.segments[index] = Segment(index, start, flags, allocation or 65536, body, relocations)

    def instructions(self, segment, start=0, end=None):
        body = self.segments[segment].data
        md = Cs(CS_ARCH_X86, CS_MODE_16)
        md.detail = True
        md.skipdata = True
        yield from md.disasm(body[start:end], start)

    def reference(self, segment, instruction):
        offset = instruction.address
        return [(address, fixup) for address in range(offset + 1, offset + instruction.size)
                if (fixup := self.segments[segment].relocations.get(address)) is not None]

    def calls(self):
        for s in self.segments.values():
            if not s.code:
                continue
            for pos, item in sorted(s.relocations.items()):
                if pos and s.data[pos - 1] == 0x9A and item[0] == 3:
                    yield s.index, pos - 1, item[1]
                elif pos >= 3 and s.data[pos - 3] == 0x9A and item[0] == 2:
                    yield s.index, pos - 3, (item[1][0], word(s.data, pos - 2))

    def resources(self):
        p = self.resource_table
        alignment = word(self.data, p)
        p += 2
        while (kind := word(self.data, p)):
            count = word(self.data, p + 2)
            p += 8
            for _ in range(count):
                offset, length, flags, identity = struct.unpack_from('<HHHH', self.data, p)
                start = offset << alignment
                yield kind, identity, self.data[start:start + (length << alignment)]
                p += 12

    def resource_strings(self):
        for kind, block, data in self.resources():
            if kind != 0x8006 or not block & 0x8000:
                continue
            base = ((block & 0x7FFF) - 1) * 16
            position = 0
            for i in range(16):
                length = data[position]
                if length:
                    yield base + i, data[position + 1:position + 1 + length].decode('cp1252', errors='replace')
                position += length + 1


def fmt(target):
    segment, offset = target
    if isinstance(segment, int):
        return f'{segment}:{offset:04x}'
    return f'{segment}.{offset}'


def anchors(exe, pattern):
    hits = defaultdict(list)
    dgroup = exe.segments[exe.dgroup]
    for match in re.finditer(rb'[ -~]{4,}', dgroup.data):
        if re.search(pattern, match.group().decode('ascii'), flags=re.I):
            hits[match.start()].append(match.group().decode('ascii'))
    references = defaultdict(list)
    for seg in exe.segments.values():
        if not seg.code:
            continue
        for instruction in exe.instructions(seg.index):
            if not instruction.id or instruction.mnemonic not in {'mov', 'push', 'lea'}:
                continue
            for op in instruction.operands:
                if op.type == X86_OP_IMM and (op.imm & 0xFFFF) in hits:
                    references[op.imm & 0xFFFF].append((seg.index, instruction.address))
    for pos, strings in sorted(hits.items()):
        print(f'{dgroup.index}:{pos:04x} {strings[0]!r}', ', '.join(map(fmt, references[pos])))


def resource_anchors(exe, pattern):
    hits = {i: value for i, value in exe.resource_strings() if re.search(pattern, value, flags=re.I)}
    references = defaultdict(list)
    for seg in exe.segments.values():
        if not seg.code:
            continue
        for i in exe.instructions(seg.index):
            if i.mnemonic not in {'push', 'mov'}:
                continue
            for op in i.operands:
                if op.type == X86_OP_IMM and (op.imm & 0xFFFF) in hits:
                    references[op.imm & 0xFFFF].append((seg.index, i.address))
    for key, value in sorted(hits.items()):
        print(f'{key:5} (0x{key:04x}): {value!r}', ', '.join(map(fmt, references[key])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe', type=Path)
    command = parser.add_subparsers(dest='mode', required=True)
    command.add_parser('inventory')
    anchor = command.add_parser('anchors')
    anchor.add_argument('pattern')
    strings = command.add_parser('resources')
    strings.add_argument('pattern')
    disasm = command.add_parser('asm')
    disasm.add_argument('segment', type=int)
    disasm.add_argument('start', type=lambda s: int(s, 16))
    disasm.add_argument('end', type=lambda s: int(s, 16))
    callers = command.add_parser('callers')
    callers.add_argument('segment', type=int)
    callers.add_argument('offset', type=lambda s: int(s, 16))
    args = parser.parse_args()
    exe = Executable(args.exe)
    if args.mode == 'inventory':
        print(f'NE: {len(exe.segments)} total segments; DGROUP {exe.dgroup}; imports {exe.imports[1:]}')
        for s in exe.segments.values():
            kind = 'code' if s.code else 'data'
            print(f'{s.index:2}  {kind}  file {s.file_offset:06x}  size {len(s.data):5}  alloc {s.allocation:5}  fixups {len(s.relocations):4}')
    elif args.mode == 'anchors':
        anchors(exe, args.pattern)
    elif args.mode == 'resources':
        resource_anchors(exe, args.pattern)
    elif args.mode == 'asm':
        for ins in exe.instructions(args.segment, args.start, args.end):
            refs = ', '.join(fmt(item[1]) for _, item in exe.reference(args.segment, ins))
            print(f'{ins.address:04x}  {ins.bytes.hex():14} {ins.mnemonic:8} {ins.op_str:33} {refs}')
    elif args.mode == 'callers':
        for segment, offset, target in exe.calls():
            if target == (args.segment, args.offset):
                print(fmt((segment, offset)))


if __name__ == '__main__':
    main()
