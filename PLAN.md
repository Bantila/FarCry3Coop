# Far Cry 3 — campaign co-op for 4 players: plan

Russian version: [PLAN.ru.md](PLAN.ru.md)

Status: plan, approved by the owner 2026-10-22. Branch `game/far-cry-3`.

## Goal

Four players pass the whole single-player story of Far Cry 3 together, with cutscenes, side
activities (outposts, towers, hunting, Path of the Hunter, Wanted Dead, trials, races) and
collectibles (relics, letters, memory cards). Friends join through a **Steam invite**.

The game has no campaign co-op: only a separate 6-mission co-op campaign in multiplayer.
Prior art: "Open World Co-op" by scubrah (https://www.nexusmods.com/farcry3/mods/220, alpha,
no story missions).

## Architecture

Same shape as the Far Cry (2004) mod: **the host is the authority**. The host runs the real
single-player game (story, AI, mission scripts, save). Joined players run their own copy of the
game and get the host's world replicated.

Two candidate transports; the Phase 2 spike picks one:

- **A. The engine's own network layer:** run the single-player island inside a co-op network
  session. Most sync for free. Risk: single-player systems (missions, shops, skills) may not be
  network-aware. First learn how scubrah's mod starts the island in co-op.
- **B. Own netcode in the ASI:** every player runs single-player; the ASI sends the host's state
  over its own UDP; other players appear as puppet characters; the joined players' AI and mission
  scripts are switched off and driven by host events. More work, full control. Fallback if A
  breaks on story maps.

Parts in both cases:

- `FarCry3Coop.asi` loaded by Ultimate ASI Loader; hooks in `FC3.dll` / `FC3_d3d11.dll` by
  address, found with REA/Ghidra. Pattern: the Far Cry (2004) `FarCryCoopNet.asi`.
- Script layer: changed mission scripts in our own archive; original files are not replaced.
- **Steam invite:** the game has no `steam_api.dll` (Steam only starts it, Ubisoft Connect runs
  it), so the Far Cry (2004) Steam bridge (Spacewar, AppID 480) is reused: "Join" in the Steam
  friends list, connection relayed through localhost. Direct IP stays as a fallback.
- Launcher and lobby: the Far Cry (2004) launcher (Rust + Tauri) gets a game profile, not a fork.

## Phases

0. **Game identity.** Done 2026-10-22, see [NOTES.md](NOTES.md).
1. **Research (read-only).** Unpack the data with Gibbed.Dunia into `E:\FarCryCoop\Work\fc3`.
   Find mission scripts, the cutscene system, the save format, collectible and progress tables.
   Study scubrah's mod. Open the game DLL in REA: network layer, player spawn, entity replication,
   player cap.
2. **Spike, choose A or B.** Two game windows on one PC (host left, joined player right): both walk
   the island, see each other, shoot the same enemy.
3. **Free roam, 2 players.** Movement, weapons, damage, AI reacts to any player, vehicles, death
   and respawn near the host, outposts captured for everyone.
4. **Story missions.** Start, objectives, failure and completion from the host to all; move
   everyone to the mission start; mission triggers fire for any player; interiors and linear
   levels (Hoyt's ship, dream sequences) load for all.
5. **Cutscenes.** The host triggers, every player plays the same cutscene locally; players are
   frozen and hidden during it; skip by the host. Scripted takedowns and QTE: the host plays,
   others watch.
6. **Side activities.** Towers, outposts, hunts, Path of the Hunter, Wanted Dead, supply drops,
   trials, races; world state comes from the host.
7. **Collectibles and progress.** Owner decision 2026-10-22: campaign progress and statistics are
   shared. Story, side activities, towers, outposts and collectibles count for **every player in
   the lobby**, wherever they stand; the item disappears for all. Personal per player: weapons,
   skills, crafting, money, loot and other personal data.
8. **4 players.** Raise caps, bandwidth and priority limits, test with 4 windows / 4 PCs.
9. **Release.** Launcher profile, Steam invite, install guide (EN + RU), beta checklist.

## Main risks

- Story scripts expect one Jason: forced animations, takedowns, vehicle seats, chases. Plan: the
  host is Jason in scripted parts; others are moved or watch for a short time.
- The save may be tied to the Ubisoft account: joined players may need state sync instead of a
  copied save.
- If the engine's network play needs Ubisoft servers for matchmaking, transport A needs direct
  join (as in Far Cry 2004) or the project falls back to B.

## Checks

Each phase ends with a check in game on one PC, two windows, written into NOTES. Phase 2: see and
shoot each other. Phase 4: the first three story missions together. Phase 5: the Vaas intro
cutscene on all players. Phase 7: a relic taken by a joined player counts and disappears for the
host. Phase 8: 4 windows, one full mission. Phase 9: join through a Steam invite.
