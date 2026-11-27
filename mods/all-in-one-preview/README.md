# All-in-One v1.2 Preview

Installs **DiabloLoot v1.2**, **Black Background v1.0**, and **More Monsters v0.1 Preview** for both chapters of Castle of the Winds I & II: Redone.

More Monsters adds the Giant Centipede and Giant Beetle to ordinary early dungeon encounters. Both have new native-style sprites. See the More Monsters release for the floor, combat and loot details.

On 64-bit Windows, open **Windows Setup**. Select the original Win16 v1.1A game ZIP or extracted folder, your All-in-One v1.1 installed folder, or your standalone More Monsters v0.1 installed folder. Choose a new destination and click **Install**. Use a Win16 runtime to play.

For the portable patch ZIP, extract it and use the following command.

```sh
python3 apply_redone.py castl11a.zip Redone-All-in-One-Preview
```

Use `py -3` on Windows. Back up and copy saves separately. Continue saves that contain the new monsters in a build with More Monsters installed.
