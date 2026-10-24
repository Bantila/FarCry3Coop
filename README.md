# FarCry3Coop — co-op for Far Cry 3

Russian version: [README.ru.md](README.ru.md)

Part of the FarCryCoop project: co-op mods for the Far Cry series, one repository per game.
Other games: https://github.com/Bantila/FarCryCoop#other-games-of-the-series

Status: research. Notes and findings: [NOTES.md](NOTES.md).
Plan: 4 players through the whole story, with cutscenes, side activities and collectibles, join through a Steam invite: [PLAN.md](PLAN.md).

## Testing / helping

The repository holds no game files and no files from other mods: you need your own copy of Far Cry 3
(Steam). Research and test tools are in [scripts/](scripts/) (Python 3 and Windows PowerShell). They
still use the owner's folder layout (`E:\FarCryCoop\...`, Steam library on `E:`); edit the paths at
the top of a script for your PC.

- `build_testgame.ps1 -Version 1.05|1.06` — test copy of the game outside the Steam folder (1.05 `bin` comes from Steam depot 220241, manifest `7362101836779063707`, via DepotDownloader).
- `patch_dll.py <copy of FC3.dll / FC3_d3d11.dll>` — current DLL patches (`--selftest` checks them); refuses to touch the Steam install.
- `build_patch.ps1`, `switch_variant.ps1` — patch archive and switching a test copy between vanilla and mod.
- `launch_105.ps1 -Role host|client` — host and client on one PC with the developers' quick-launch switches.
- `thread_eips.ps1 -ProcessId <pid>` — where the game's busiest threads are running.

Current state and open problems: the last sections of [NOTES.md](NOTES.md).
