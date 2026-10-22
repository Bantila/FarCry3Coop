# Far Cry 3 — co-op notes

Russian version: [NOTES.ru.md](NOTES.ru.md)

Status: active (owner decision 2026-10-22). Plan: [PLAN.md](PLAN.md).

## Game identity (AGENTS.md rule 5)

Observed 2026-10-22 on the owner's PC:

- Store: Steam, app 220240, `E:\SteamLibrary\steamapps\common\Far Cry 3`; runs through Ubisoft Connect (`bin\upc_r1_loader.dll`), no `steam_api.dll`
- Steam build id: 13146413
- SHA-256 `bin\farcry3.exe`: `fd3929f19ff825912f73bd0158604823c46ab9c124d18d57b0fab05a51cda9bb`
- SHA-256 `bin\farcry3_d3d11.exe`: `5437b2e37a54f8a3b28c342f2b2670ca907fd60bc74905b0b7527f69bafc965e`
- SHA-256 `bin\FC3.dll`: `71d58a7a4503c5c67dcd6f4b9445b5e7ac34c12043987f4c7285e13f2ed51c9b`
- SHA-256 `bin\FC3_d3d11.dll`: `e541594e11ac6091dc7d3702f2cd90504280b82cf15ec10b4eb148aae27f0809`
- Engine: Dunia
- Install checked for third-party DLLs: `bin` holds only the game's own files
- `data_win32\patch.dat/.fat` held the owner's auto-skip-cutscenes mod. With the owner's permission it was renamed to `patch.dat.skipcutscenes` / `patch.fat.skipcutscenes`, and the vanilla pair (kept as `.vanilla`) was put back. SHA-256 vanilla `patch.dat`: `b76a3ae5092bec46e4d000dfebb0dc1fac9d7990d217421528447d59a7661833`, `patch.fat`: `39dc4178723bfd4e2f9f512d42401790b80a3f4ea305d4ab38889f546780b39f`
- Also present: `bin\FC3Editor.exe` (official map editor), `data_win32\worlds\fc3_main`, `data_win32\worlds\multicommon`

## Known so far

- Official co-op: separate 6-mission campaign, up to 4 players online https://co-optimus.com/article/8473/far-cry-3-follow-up-questions-plus-new-co-op-campaign-trailer-and-images.html . Mod: Open World Co-op (scubrah), no story missions, alpha https://www.nexusmods.com/farcry3/mods/220 (coop-anything directory).
