# Solo offline co-op live test (patch_solo_offline_coop_vanilla-262) / Живой тест соло-офлайн-коопа

Bilingual pair: this file is English, `solo-coop-test.ru.md` is Russian. Update both together.

This is the on-machine procedure to launch the 1.05 working copy through Ubisoft Connect and enter a solo co-op session with the `patch_solo_offline_coop_vanilla-262` (nexus 262) loader set. Everything is on the working copy only (`H:\FarCryCoop\TestFC3_105`); the real install is reached only through an NTFS junction and is never modified. All scripts live in `H:\FarCryCoop\scratch\`.

## State right now
- `TestFC3_105` = mod 1.05: `bin\FC3.dll` (5ff045331557), `bin\FC3_d3d11.dll` (46bcc0975905), `bin\uplay_r1_loader.dll` (dacd14c07775), `bin\ubiorbitapi_r2_loader.dll` (ba6015e566c9), `bin\uplay_r14.dll` (6c75cb01cef6), `data_win32\patch.dat` (212,002,032 B, md5 157f2d7682a5), `data_win32\patch.fat` (850412635760).
- Pre-mod 1.06 backup: `TestFC3_105\_backup_106_before_solo262\` (FC3 5742de2aaa76, FC3_d3d11 916c6d4b876d, patch.dat 5a788dd5f7be, patch.fat c829e677c352).
- NTFS junction `H:\Uplay\Far Cry 3` -> `H:\FarCryCoop\TestFC3_105` (created by `use_copy_junction.bat`; real dir kept as `Far Cry 3.OFFICIAL`).
- NOT yet done: `uplay_r14.dll` into the launcher dir (needs Administrator).

## Step 1 — put uplay_r14.dll where the launcher sees it (Administrator)
Run `install_uplay_r14_launcher.bat` as Administrator. It copies `uplay_r14.dll` (6c75cb01cef6) to `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\` (additive — the dir has no such file; rollback is just deleting that file).

## Step 2 — launch through Ubisoft Connect
1. Fully quit Ubisoft Connect (tray icon -> Quit), then start it again so it re-reads the game files.
2. Press **Play** on Far Cry 3 (the junction makes upc launch the 1.05 copy).
3. When the main menu appears, the loader chain is: `farcry3.exe` -> `bin\uplay_r1_loader.dll` -> `uplay_r14.dll` (the fake Uplay/orbit platform).

## Step 3 — verify the emulator actually loaded (optional, read-only)
With the game in the menu, from a normal console:
```
python -I H:\FarCryCoop\scratch\fc3_probe_modules.py
```
It lists the running `farcry3.exe` modules and reports whether `uplay_r14.dll` and `uplay_r1_loader.dll` are loaded. If `uplay_r14.dll` is absent, the shim is not being reached — send `H:\FarCryCoop\scratch\fc3_mods.txt` and `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\logs\launcher_log.txt` (tail) back to the agent.

## Step 4 — enter the solo co-op session
In the main menu: **PLAY -> CO-OP -> Private Session -> Play Alone -> Start**. The mod counts down ~10 s and loads the co-op world offline. Success = you are controllable in the co-op spawn. Record which chapter/area loads.

## Rollback
- Undo just the mod: run `uninstall_solo262.bat` as Administrator (removes the C: `uplay_r14.dll` + the 3 bin dependency DLLs, restores 1.06 `FC3.dll`/`FC3_d3d11.dll`/`patch.dat`/`patch.fat` from `_backup_106_before_solo262\`).
- Undo the junction: run `undo_junction.bat` as Administrator (removes the junction, restores `H:\Uplay\Far Cry 3` real folder).
