# Redone v1.1 verification

This release updates Windows Setup and the installation instructions. Select the original registered Win16 v1.1A `castl11a.zip` as downloaded, or an extracted folder with both game executables and Help files. The original files are supplied separately. [Original game archive at Boxedwine](https://www.boxedwine.org/app/castleofthewindows/)

On 64-bit Windows, all six v1.1 setup executables ran with their windows withdrawn and without Python on PATH. From the original ZIP, each produced both game files and both Help files byte for byte with its corresponding v1.0 setup output. The source ZIP retained its original SHA-256. The six portable archives retain their original patch and manifest bytes. Both BPS downloads retain their original apply and restore patch bytes.

- Verified the source checklist and next-step message in the actual Windows Setup flow
- Verified the extracted original folder and each compatible Redone output folder in the five-mod install order
- Compared the five-mod chain with the direct Classic All-in-One setup byte for byte
- Compared Warm Stone and Dark Slate All-in-One output with v1.0 and verified in-place restoration to Classic
- Verified error messages and destination protection with a malformed ZIP, a missing Help file, an altered game executable, and an existing destination

Game behavior is covered by the [original v1.0 checks](Redone-v1.0.md) and the [v1.0 refresh checks](Redone-v1.0-refresh.md). This installer release reused their game patches and did not rerun the campaigns.
