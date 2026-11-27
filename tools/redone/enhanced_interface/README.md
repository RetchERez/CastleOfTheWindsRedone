# Enhanced Interface development

By RetchERezzed

Warm Stone and Dark Slate change the game's own windows and drawing calls. Classic returns the selected game build byte for byte. The standalone installer defaults to Warm Stone. All-in-One includes the themes and starts on Classic, with Warm Stone and Dark Slate available in Setup.

`theme.py` checks exact supported game hashes and the native import relocation chains. It appends local drawing callbacks without changing dungeon drawing, native art, game data, or the save format. The paper doll keeps its native vector commands. Dark Slate supplies readable pen colors during playback. Indexed displays use solid fallback colors. Menus, title bars, scrollbars, common dialogs, and Windows Help continue to use the operating system's native controls.

Build the patch catalogue with `build_package.py` using local copies of the registered executables and supported Redone editions. It requires Python, Capstone, and NASM. The generated `.dlpatch` files contain reproducible forward transforms and a SHA-256 manifest. `package_windows.py` packages the catalogue and the native Windows installer. The installer uses its local Classic backups to switch themes or restore the previous executable. Backups belong in the player's installation and must stay out of archives and releases.

## Candidate verification

- The frozen standalone and All-in-One Windows installers accepted the registered v1.1A ZIP and installed both chapters headlessly
- Switching through Warm Stone, Dark Slate, and Classic restored the baseline bytes and preserved the copied saves in both installs
- Both installed chapters loaded old saves in all three themes. Native Save As retained the map, position, experience, HP, mana, and carried inventory. The native reload route reopened the written file
- Inventory and paper-doll colors were rendered on modern Windows using WineVDM and in Windows 3.1 using DOSBox. The DOSBox runs also exercised the town, character screen, spell dialog, options, story list and native Save As dialog
- The Classic game binaries match their respective unthemed builds. The original releases keep their original engine and UI assets

Full runtime coverage of every window and interaction remains a release requirement. Verify shop transactions, nested container interactions, all transient windows and visual states before certifying the build as final.
