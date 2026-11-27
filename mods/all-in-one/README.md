# All-in-One v1.1

Installs the complete Castle of the Winds Redone collection in both chapters of the original Win16 v1.1A game.

| Included mod | Version |
| --- | --- |
| DiabloLoot | 1.2 |
| Black Background | 1.0 |

DiabloLoot adds randomized enemy drops and shop gear, stat rolls, rarity accents, and first-equip rarity reveal for cursed gear. Black Background makes unexplored tiles black. The collection includes both features in each game executable.

On 64-bit Windows, open the **Windows Setup** asset, select your game files, and choose **Install**. The setup includes its own runtime. For the portable ZIP, extract it and use the following command.

```powershell
py -3 apply_redone.py castl11a.zip Redone-All-in-One
```

Use `python3` on Linux. The release accepts original files, Black Background v1.0, DiabloLoot v1.1 or v1.2, and All-in-One v1.0. Choose a new output folder. Run the matching chapter's EXE in a Win16 runtime, and copy saves separately. Legendary icon accents show as orange in true-color mode.
