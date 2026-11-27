# Redone v1.1 verification

This release updates Windows Setup, adds Redone lettering to the native title screen in both chapters, and clarifies installation. Select the original registered Win16 v1.1A `castl11a.zip` as downloaded, or an extracted folder with both game executables and Help files. The original files are supplied separately. [Original game archive at Boxedwine](https://www.boxedwine.org/app/castleofthewindows/)

On 64-bit Windows, all six v1.1 setup executables ran with their windows withdrawn and without Python on PATH. The Windows and portable installers reproduced the same game and Help files. Comparisons with v1.0 found changes only in the title-logo bitmap resource in each chapter. The source ZIP retained its original SHA-256. Both BPS downloads passed apply and restore round trips.

- Verified the source checklist and next-step message in the actual Windows Setup flow
- Verified the extracted original folder and each compatible Redone output folder in the five-mod install order
- Compared the five-mod chain with the direct Classic All-in-One setup byte for byte
- Compared Warm Stone and Dark Slate All-in-One output with v1.0 and verified in-place restoration to Classic
- Verified new `.bak` theme backups and restoration from legacy `.bin` backups, then upgraded the restored v1.0 install to v1.1
- Verified error messages and destination protection with a malformed ZIP, a missing Help file, an altered game executable, and an existing destination
- Captured the actual title screens in Windows 3.1 on a private DOSBox display. [Part I](screenshots/Redone-Title-Part-I.png) · [Part II](screenshots/Redone-Title-Part-II.png)

Game behavior is covered by the [original v1.0 checks](Redone-v1.0.md) and the [v1.0 refresh checks](Redone-v1.0-refresh.md). The title changes preserve the original game code and artwork outside the blank band below the blue logo. The v1.1 checks did not rerun the campaigns.
