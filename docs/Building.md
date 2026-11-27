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

To run the relocation tests with your original files on Linux:

```sh
COTW_VANILLA=private-inputs python -m unittest discover -s tools/redone -v
```

In PowerShell, set `$env:COTW_VANILLA = 'private-inputs'` before running the same unittest command. Original binaries, runtime files, and saves stay outside version control.
