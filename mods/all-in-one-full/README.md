# All-in-One v1.0

Installs all four released mods for both chapters of **Castle of the Winds I & II: Redone**.

- **Diablo Loot v1.0** adds randomized gear to enemy drops and shops, with blue Enchanted, yellow Rare, and orange Legendary markings. Cursed gear uses the original curse behavior, with rarity hidden until first equipped
- **More Monsters v1.0** adds 25 enemy types in Part I and 40 in Part II using the original spawn pools, each with original 32×32 sprites
- **More Equipment v1.0** adds 16 weapons and 12 other equipment types to each game
- **Graphics Overhaul v1.0** adds the black dungeon background, terrain details, and refinements to monster art, item icons, and toolbar icons. Inventory, menu, and dialog background colors stay vanilla

On 64-bit Windows, open **Windows Setup** from the [Redone v1.0 release](https://github.com/RetchERez/CastleOfTheWindsRedone/releases/tag/redone-v1.0). Select the original Win16 v1.1A ZIP or extracted game folder. Choose a new destination and click **Install**. Run the installed games in a Win16 runtime.

For the portable patch ZIP, extract it and run the following from that folder.

```sh
python3 apply_redone.py castl11a.zip Redone-All-in-One
```

Use `py -3` on Windows. Copy backed-up saves separately. Continue saves that contain new enemies in a build with More Monsters installed.
