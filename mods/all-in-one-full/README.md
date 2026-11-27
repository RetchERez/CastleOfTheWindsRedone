# All-in-One v1.0

Installs all three patches for both chapters of **Castle of the Winds I & II: Redone**.

- **DiabloLoot v1.2** adds randomized gear to enemy drops and shops, with blue Enchanted, yellow Rare, and orange Legendary markings. Cursed gear uses the original curse behavior, with rarity hidden until first equipped
- **Black Background v1.0** makes the unexplored part of the playable map black while retaining the terrain and interface colors
- **More Monsters v1.0** adds 25 enemy types in Part I and 40 in Part II using the original spawn pools, each with original 32×32 sprites

On 64-bit Windows, open **Windows Setup**. Select the original Win16 v1.1A ZIP or extracted folder, or an installation of DiabloLoot v1.2, Black Background v1.0, All-in-One v1.1, All-in-One v1.2 Preview, or More Monsters v0.1 or v1.0. Choose a new destination and click **Install**. Run the installed games in a Win16 runtime.

For the portable patch ZIP, extract it and run the following from that folder.

```sh
python3 apply_redone.py castl11a.zip Redone-All-in-One
```

Use `py -3` on Windows. Copy backed-up saves separately. Continue saves that contain new enemies in a build with More Monsters installed.
