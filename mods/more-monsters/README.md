# More Monsters v0.1 Preview

For both chapters of **Castle of the Winds I & II: Redone**. This preview introduces two regular enemies with original 32×32 pixel art.

| Enemy | Profile | Where it can appear |
| --- | --- | --- |
| Giant Centipede | 5–10 HP, 4 XP, a modest speed boost and weaker bite and poison than a Viper | Part I Mine 2–4 and Fortress 2–3. Part II Castle 1–2 |
| Giant Beetle | 12–17 HP, 6 XP, stronger defense, a slower turn rate and a weaker bite than the Giant Red Ant | Part I Mine 2–4 and Fortress 2–4. Part II Castle 1–3 |

They rotate into the original ordinary encounters. Regular generation and the original respawn paths choose their positions. The existing spawn limits and scripted encounters remain in place. The ordinary pool allows at most one living member of each new species at a time. Some carry a native copper drop.

On 64-bit Windows, open **Windows Setup** and select the original Win16 v1.1A ZIP or extracted folder. You can also select the output folder from **All-in-One v1.1** to use all three patches. Pick a new destination. To play, use a Win16 runtime.

For the portable patch ZIP, extract it and run the following from that folder.

```sh
python3 apply_redone.py castl11a.zip Redone-More-Monsters
```

Use `py -3` on Windows. Back up your original saves and copy them separately. Continue saves that contain the new monsters in a build with More Monsters installed.
