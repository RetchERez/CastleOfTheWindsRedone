"""Canonical design roster and per-title spawn policy."""
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Creature:
    logical_id: int
    name: str
    anchor: str
    xp: int
    hp_pct: int
    damage_pct: int
    speed_pct: int
    role: str
    loot: str
    part1: list[int]
    part2: list[int]

    @property
    def slug(self):
        return self.name.lower().replace(' ', '-')

    @property
    def portrait(self):
        return 0x1EF + self.logical_id if self.logical_id < 3 else 0x400 + self.logical_id - 3

    @property
    def behavior(self):
        risky = self.logical_id in (1, 4, 6, 7, 12, 16, 27, 28, 30, 31, 32)
        caster = self.logical_id in (7, 27)
        heals = self.logical_id in (20, 21, 33, 34, 35)
        return int(risky) | (int(caster) << 1) | (int(heals) << 2)

    @property
    def copper_chance(self):
        # This gate precedes the game's own 3-in-4 native copper roll.
        return {'A': 96, 'H': 128, 'U': 64, 'C': 32, 'M': 96, 'D': 64}[self.loot]

    def floors(self, part):
        return self.part1 if part == 1 else self.part2

    def weight(self, part, floor):
        floors = self.floors(part)
        if floor not in floors:
            return 0
        if self.role == 'Caster':
            base = 40
        elif self.behavior & 1 or self.role == 'Elemental melee':
            base = 60
        elif self.role in ('Armored', 'Regenerator'):
            base = 75
        else:
            base = 100
        if part == 2 and floor == 23 and self.logical_id in (34, 38):
            return base // 4
        if (floor - 1 in floors) != (floor + 1 in floors):
            return base // 2
        return base


ROSTER = [Creature(**entry)
          for entry in json.loads(Path(__file__).with_name('roster.json').read_text(encoding='utf-8'))]


def for_title(part):
    return [creature for creature in ROSTER if creature.floors(part)]
