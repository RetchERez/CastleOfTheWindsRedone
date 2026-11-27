# DiabloLoot v1.2

For Part One and Part Two of the original Win16 *Castle of the Winds* v1.1A.

- Enemies can drop randomized weapons and body armor alongside their original rewards. Shops share the same rarity and stat-roll rules when generating new stock.
- Enchanted uses blue, Rare uses yellow, and Legendary uses orange. Wider corners and a lower accent keep the colors visible near long item names. Indexed modes show Legendary as a red-and-yellow pattern. A true-color mode shows the orange accents.
- Native Identify can reveal a curse before the item is worn. DiabloLoot reveals its rarity on successful equip. The item then keeps that reveal through save, reload, and Remove Curse.
- Cursed gear retains the original effects and equipment lock. Remove Curse lets you take it off. The item's underlying penalties can remain.

On 64-bit Windows, open the **Windows Setup** asset, select your game files, and choose **Install**. The setup includes its own runtime. For the portable ZIP, extract it and use the following command.

```powershell
py -3 apply_redone.py castl11a.zip Redone-DiabloLoot
```

Use `python3` on Linux. The release accepts original files, Black Background v1.0, DiabloLoot v1.1, or All-in-One v1.0. Choose a new output folder. Open the matching chapter's EXE in a Win16 runtime, and copy saves separately.
