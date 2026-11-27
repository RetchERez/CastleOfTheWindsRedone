# Redone v1.0 refresh verification

The refresh adds the optional Enhanced Interface themes and revised town roof and sign art. Both games target the registered Win16 v1.1A originals. All-in-One uses Classic by default. The standalone Enhanced Interface setup uses Warm Stone by default.

## Headless checks

| Area | Evidence |
| --- | --- |
| Fresh install and theme switching | Exercised the frozen Windows Setup packages with the original ZIP. Installed both chapters, switched through Warm Stone, Dark Slate and Classic, verified the resulting executable digests, and verified that Classic restored the baseline bytes without changing the copied saves |
| Standalone install order | Installed Diablo Loot, More Monsters, More Equipment, Graphics Overhaul and Enhanced Interface in order. Both executables and Help files matched the direct All-in-One installation with Warm Stone byte for byte |
| Existing saves | Loaded old saves in both chapters with all three themes in Windows 3.1 on private DOSBox displays. Saved and reloaded. Inspected map, position, XP, HP, mana and inventory |
| Inventory and nested containers | Opened carried inventory, nested packs and bags, and the item-naming dialog. Checked selection, the focused name field, the window menu and dismissal in both chapters with all three themes |
| Shop interface | Opened the armor shop in each chapter with all three themes. Dragged a stock item into the carried inventory, reviewed and canceled a quote, then exercised confirmation. Checked purchases and the insufficient-funds response where encountered. Saved and inspected the resulting inventory |
| Other interface screens | Captured character, spellbook, options, story review, Save As and reload in both chapters with all three themes. Repeated inventory opening and closing on the themed builds |
| Modern Windows compatibility | Loaded old saves with WineVDM on a private Windows desktop and captured each chapter’s inventory at 640 × 480 in all three themes |
| Graphics and resource preservation | Checked the revised town art in both chapters. Automated tests verified that interface patching preserved game resources and left Classic byte-identical |

These checks use representative saves and interface paths. They do not certify every merchant, transient control state, hardware palette or full campaign. Native system-owned window elements retain their original behavior.

## Executable CRC32

| Build | Part I | Part II |
| --- | --- | --- |
| Registered original | `F1381DB2` | `2226834D` |
| Graphics Overhaul | `AB410951` | `D02DEEBD` |
| All-in-One with Classic | `FC6959FC` | `D645BC23` |
| All-in-One with Warm Stone | `552C1724` | `B329728F` |
| All-in-One with Dark Slate | `DE3CC76C` | `E9D7B684` |
| Standalone Warm Stone on registered v1.1A | `0F51F729` | `123ABDBB` |
| Standalone Dark Slate on registered v1.1A | `1D08A48E` | `ACA08BD9` |

The portable manifests include the SHA-256 digests for the supported inputs and outputs. The release includes `SHA256SUMS.txt` for the downloaded archives and installers.
