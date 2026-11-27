# Redone v1.0 verification

The release targets the registered Windows v1.1A executables. The main functional checks ran in Windows 3.1 on a private DOSBox display. Matched clean and patched checks also ran in Boxedwine WASM with Wine 1.7.55 and a headless Chromium process.

## What was exercised

- Installed each Windows Setup in a withdrawn test window and checked both game and Help files against the expected payload
- Installed all four standalone mods in order and matched the direct All-in-One game and Help files byte for byte
- Verified the Black Background migration to Graphics Overhaul and rejected an executable with a modified byte
- Downloaded the public All-in-One Windows Setup and installed both games from the registered v1.1A ZIP. Opened a pre-mod save for each chapter, saved to a new file, and reloaded it. The original ZIP and saves retained their hashes. Both round trips preserved the player's equipment, inventory, XP, HP, mana, map and position
- Compared the inventory, File menu, and Save As interface surfaces against the original game in both chapters. The sampled pixels matched in all four standalone downloads and All-in-One. Graphics Overhaul supplies the black dungeon background
- Applied and restored both Graphics Overhaul and More Equipment BPS patches and checked the resulting binaries against the expected originals and outputs
- Used native town shops, purchased and equipped gear, climbed stairs, fought enemies, picked up dropped gear, saved, and reloaded in both games
- Replayed 240 matched bonus-reward cases across both games with the Buckler compatibility hook, including 49 Buckler substitutions and native curse reveal checks
- Compared map, movement, save and reload with clean controls in the second runtime. The sampled original floor pixels and cursor artwork matched the controls
- Defeated the native Hrungnir and Surtur actors in controlled late-game encounters. The native drop and pickup paths yielded the Amulet of Kings and the Helm of Storms
- Equipped the recovered Amulet in Part I and activated it twice in town. The second activation opened the native Part I ending
- Loaded the saved Helm of Storms after the Part II fight and triggered the native throne ending. The game recorded the character as a winner
- Imported the completed Part I `.CWG` in Part II using **File → Load**. The native intro led to the Part II town with the character’s Glaive and Potion Belt intact
- Saved and reloaded the imported character in Part II. Level, XP, HP, mana, and all 46 carried item records matched. The first reload placed the character at a different tile in the same town

The test plan used real game saves and controlled endgame checkpoints. The endgame runs used aided characters and position warps in disposable saves. The native bosses, rewards, and ending interactions ran in the game itself. Fresh start-to-finish balance and economy remain unverified.

## Executable CRC32

| Build from clean v1.1A | Part I | Part II |
| --- | --- | --- |
| Registered original | `F1381DB2` | `2226834D` |
| All-in-One v1.0 | `2A640B8F` | `782A3C6A` |
| Diablo Loot v1.0 | `15CF6F85` | `032E3E0A` |
| More Monsters v1.0 | `AF44A699` | `1FB65F67` |
| More Equipment v1.0 | `3FB1B7A6` | `FF5D198F` |
| Graphics Overhaul v1.0 | `9350827B` | `9D92C959` |

The portable manifests include SHA-256 checks for the supported inputs and outputs. `SHA256SUMS.txt` on the release covers every downloadable package.
