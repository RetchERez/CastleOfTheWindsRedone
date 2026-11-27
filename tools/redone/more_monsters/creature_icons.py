from dataclasses import replace
from pathlib import Path
from struct import pack_into

from color_resources import RT_GROUP_ICON, RT_ICON, _word, repack_resources

ART = Path(__file__).resolve().parent / 'art'
CREATURE_ART = (('giant-centipede', 0x1F0), ('giant-beetle', 0x1F1))


def add_creature_icons(executable, part):
    def insert(types):
        groups = types[RT_GROUP_ICON][1]
        images = types[RT_ICON][1]
        source_group = groups[0x8139]
        if _word(source_group.body, 4) != 2:
            raise ValueError('Unexpected stock monster icon group')
        for index, (name, group_number) in enumerate(CREATURE_ART):
            new_group = 0x8000 | group_number
            if new_group in groups:
                raise ValueError('Monster icon group is already assigned')
            descriptor = bytearray(source_group.body)
            for variant, (mode, pointer, size) in enumerate((('mono', 18, 304), ('color', 32, 744))):
                image_number = 0x500 + index * 2 + variant
                new_image = 0x8000 | image_number
                if new_image in images:
                    raise ValueError('Monster image is already assigned')
                native = images[0x8000 | _word(descriptor, pointer)]
                drawing = (ART / f'{name}.{mode}.dib').read_bytes()
                if len(drawing) != size or drawing[:40] != native.body[:40]:
                    raise ValueError(f'Unexpected {mode} format in {name}')
                images[new_image] = replace(native, offset=-1, identity=new_image, body=drawing)
                pack_into('<H', descriptor, pointer, image_number)
            groups[new_group] = replace(source_group, offset=-1, identity=new_group, body=bytes(descriptor))
    return repack_resources(executable, part, 3 * len(CREATURE_ART), insert)
