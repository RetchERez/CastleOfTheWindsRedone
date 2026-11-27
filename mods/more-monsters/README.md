# More Monsters v1.0

Adds 25 enemy types in Part I and 40 in Part II of **Castle of the Winds I & II: Redone**. Each has original 32×32 art for the game's color and monochrome modes.

Early encounters include giant insects, kobolds, and goblins. Later floors add undead, trolls, wyverns, and elementals. Every species has its own floor range, and its health, damage, speed, and experience are based on a creature from the original games. Some enemies poison, shoot, or regenerate. Casters get three ranged attacks, and the Dark Sorcerer can briefly slow the player.

New enemies rotate into the original spawn pool. The original engine still decides when and where to place an enemy. The patch caps new enemies per floor, prevents duplicate active spawns of each new species, and protects scripted encounters. Some enemies carry native copper.

On 64-bit Windows, open **Windows Setup** and select the original Win16 v1.1A ZIP or extracted folder. Setup upgrades More Monsters v0.1 and accepts All-in-One v1.1 or v1.2 Preview to produce the three-mod edition. Choose a new destination and run the installed games in a Win16 runtime.

If you are using the standalone installers for all three mods, install More Monsters last and select the folder containing both DiabloLoot and Black Background. [Standalone install order](../../README.md#install-all-three-without-all-in-one)

For the portable patch ZIP, extract it and run the following from that folder.

```sh
python3 apply_redone.py castl11a.zip Redone-More-Monsters
```

Use `py -3` on Windows. Copy backed-up saves separately. Continue saves that contain new enemies in a build with More Monsters installed.
