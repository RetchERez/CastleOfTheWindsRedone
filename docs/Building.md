# Build Castle of the Winds Redone

Building requires Python 3.10 or later, Capstone for Python, and NASM on your `PATH`. The installer in a release ZIP only needs Python.

Extract the clean 16-bit v1.1A archive into a local folder with all four files.

```text
CASTLE1.EXE
CASTLE1.HLP
CASTLE2.EXE
CASTLE2.HLP
```

From the repository root, run the following. Pick a new build destination.

```sh
python -m pip install capstone
python tools/redone/build_mods.py private-inputs dist
```

This creates the three installer folders under `dist`. Zip each folder's contents to make a patch distribution. The build checks the original executable hashes. The installer checks all four input files and writes a new output directory.

To include direct upgrades from the previous releases, pass both `--previous-loot` and `--previous-combined` with folders containing their two verified EXEs. Omit both arguments for a build from the original game and current standalone mods.

To run the relocation tests with your original files on Linux:

```sh
COTW_VANILLA=private-inputs python -m unittest discover -s tools/redone -v
```

In PowerShell, set `$env:COTW_VANILLA = 'private-inputs'` before running the same unittest command. Original binaries, runtime files, and saves stay outside version control.

## Build the Windows setup files

Use 64-bit Python for Windows with Tcl/Tk installed and build the three patch folders above first. Then run the following from the repository root.

```powershell
py -3 -m pip install pyinstaller==6.22.3
py -3 tools/redone/package_windows.py dist dist/windows
```

The resulting three EXEs bundle the setup runtime, the corresponding patch data, and runtime license notices. The original game files stay in your own source folder.

## Build the More Monsters preview

Put copies of both installed All-in-One v1.1 EXEs in `stable-all-in-one`. Keep the original EXEs and help files in `private-inputs`. Build the preview packages with the same Python, Capstone and NASM setup.

```sh
python tools/redone/more_monsters/build_packages.py private-inputs stable-all-in-one preview-dist
```

This builds the standalone More Monsters package and the All-in-One preview package. On 64-bit Windows, pass `preview-dist` to `package_windows.py` to bundle their Windows installers.
