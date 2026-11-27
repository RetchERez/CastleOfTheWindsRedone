# Black Background v1.0

Makes unexplored map cells black in both chapters of the original Win16 *Castle of the Winds* v1.1A. Explored terrain, creatures, and the interface keep their original colors.

On 64-bit Windows, open the **Windows Setup** asset, select your game files, and choose **Install**. The setup includes its own runtime. For the portable ZIP, extract it and use the following command.

```powershell
py -3 apply_redone.py castl11a.zip Redone-Black-Background
```

Use `python3` on Linux. The current release assets accept original files or DiabloLoot v1.1 or v1.2. Choose a new output folder. Open the matching chapter's EXE in a Win16 runtime, and copy saves separately.
