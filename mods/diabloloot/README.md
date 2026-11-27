# DiabloLoot v1.1

For Part One and Part Two of the original Win16 *Castle of the Winds* v1.1A.

- Enemies can drop randomized weapons and body armor alongside their original rewards. Shops share the same rarity and stat-roll rules when generating new stock.
- Enchanted uses blue, Rare uses yellow, and Legendary uses orange. Indexed display modes can show Legendary as a red-and-yellow pattern. A true-color display shows the orange accents.
- Native Identify can reveal a curse before the item is worn. DiabloLoot reveals its rarity on successful equip. The item then keeps that reveal through save, reload, and Remove Curse.
- Cursed gear retains the original effects and equipment lock. Remove Curse lets you take it off. The item's underlying penalties can remain.

Extract the patch ZIP and run this command in its folder. Use `python3` on Linux.

```powershell
py -3 apply_redone.py castl11a.zip Redone-DiabloLoot
```

You can also pass your extracted original files or an install of Black Background v1.0. Choose a new output folder. Open the matching chapter's EXE in a Win16 runtime, and copy saves separately.
