# Castle of the Winds Redone

Modular patches for both chapters of the original 16-bit *Castle of the Winds* v1.1A, by **RetchERezzed**.

| Download | What it changes |
| --- | --- |
| [All-in-One v1.0](https://github.com/RetchERez/CastleOfTheWindsRedone/releases/tag/all-in-one-v1.0) | Installs both current mods in one step. |
| [DiabloLoot v1.1](https://github.com/RetchERez/CastleOfTheWindsRedone/releases/tag/diabloloot-v1.1) | Adds randomized gear to enemy drops and shop stock, with stat rolls and color-coded rarity. |
| [Black Background v1.0](https://github.com/RetchERez/CastleOfTheWindsRedone/releases/tag/black-background-v1.0) | Makes unexplored map cells black while keeping explored tiles and the interface in their original colors. |

## Install

1. Get the original Win16 v1.1A `castl11a.zip` with both games and their help files. [Boxedwine archive](https://www.boxedwine.org/app/castleofthewindows/)
2. Extract the patch ZIP you chose. In that folder, run the patch installer with Python 3. Use a new destination folder.

   ```powershell
   py -3 apply_redone.py castl11a.zip Castle-Redone
   ```

   On Linux, use `python3` in place of `py -3`. You can also give the installer the path to an extracted game folder.

3. Run `CASTLE1.EXE` for *A Question of Vengeance* or `CASTLE2.EXE` for *Lifthransir's Bane* in a Win16 runtime. Verification used Windows 3.1 under DOSBox. The downloads contain patches and an installer. Supply the original game and runtime separately.

Both standalone patches can be stacked in either order. Give the second installer the output folder from the first and choose a new destination. All-in-One also accepts the output from either standalone mod. Copy your saves separately into the matching chapter's new folder.

## In-game previews

| DiabloLoot | Black Background |
| --- | --- |
| ![Inventory showing rarity colors and equipped cursed gear](docs/verification/DiabloLoot.png) | ![Dungeon with black unexplored cells and original floor, walls, and interface](docs/verification/Black-Background.png) |

## Verification

- [DiabloLoot test results](docs/verification/DiabloLoot.txt) cover kills, drops, pickup, reload, curses, and shop stocking and restocking in each chapter.
- [Black Background test results](docs/verification/Black%20Background.txt) compare the original and patched screens in both chapters.

See the [build instructions](docs/Building.md) to produce the patches from your own original files.
