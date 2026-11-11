# Far Cry 3 — campaign co-op for 4 players: plan

Russian version: [PLAN.ru.md](PLAN.ru.md)

Status: plan, approved by the owner 2026-10-22. Branch `game/far-cry-3`.

## Goal

Four players pass the whole single-player story of Far Cry 3 together, with cutscenes, side
activities (outposts, towers, hunting, Path of the Hunter, Wanted Dead, trials, races) and
collectibles (relics, letters, memory cards). Friends join through a **Steam invite**.

**Game versions (owner decision 2026-10-24):** both are supported: **1.05** (Steam depot 220241,
manifest `7362101836779063707`, DLL build 2018-05-02, the last version with multiplayer, the one
scubrah's mod is built on) and **1.06** (current Steam / Ubisoft Connect, build 2022-10-03; hard to
downgrade to 1.05). Each version has its own addresses; a shared address map is built by the script
`scripts\fc3_addrmap.py`. Ubisoft servers for FC3 are shut down, so joining goes only
through our own transport.

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
- Injection for the first experiments does **not** need the ASI loader: the H1 probe is a
  self-contained `dinput8.dll` proxy (`mod/fc3coop_probe/`, built 2026-11-07) that needs no
  external loader. The ASI + Ultimate ASI Loader path stays the eventual shipping form.
  **Caveat (2026-11-08, NOTES session 5):** the probe's poke of `0x12891ca0/0x12891ca8` is now known
  to be a *diagnostic only* — those are `static const` lookup keys, not the live mode state; the real
  co-op switch is the mode-manager field `[this+0x4c]` and the live playlist container
  `[service+0x8c0]` (`CFCXPlaylistService`, instance global `0x12863890`), which need a runtime trace.
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

---

## Critical path v2 (agent, updated 2026-11-09)

Agent addendum per the owner's standing instruction to keep PLAN current; the numbered plan above
is unchanged. Authoritative evidence: `NOTES.md`.

**What the read-only reverse engineering established (no code shipped):**

1. The offline co-op host is the game's own Uplay / RendezVous session path. The solo-262
   `FC3.dll` is byte-identical to stock; it unlocks offline co-op with loader shims
   (`uplay_r1_loader.dll`, `ubiorbitapi_r2_loader.dll`, `upc_r1_loader.dll`) plus a data patch.
2. Offline co-op is already selectable on 1.05 and 1.06. No session-gate or version blocker is left.
3. Loading the island as a co-op map is a DATA problem (patch.dat world-asset expansion plus the
   mod's small one-shot content-spawn hooks), not a hosting hook. The mod's `FC3.dll` code is a
   content spawner (`FUN_108c4b09`) plus count bumps; it does not create a host session.
4. The one hard problem left for 2-4 players OFFLINE is the native HOST path: FC3's party
   controller (≈ `0x10620400`-`0x10623500`) drives `UPLAY_PARTY_*` (`SetGameSession` declares the
   host, `GetFullMemberList` enumerates peers, `IsPartyLeader` gates the host, `SetGuest` marks
   remotes). The data plane is the RendezVous stack inside `uplay_r14.dll`.

**New critical path (offline-host prototype), pending the owner's go for writing code:**

- A. Map offline, in Ghidra FC3_106, the exact Rv / party call flow a second peer must satisfy.
- B. Prototype a shim that reports a synthesized second party member
  (`UPLAY_PARTY_GetFullMemberList` thunk `0x10CFD84C`, `UPLAY_PARTY_IsPartyLeader` thunk `0x10CFD85E`)
  so the engine believes it hosts a two-player session.
- C. Only if the RendezVous data plane will carry a second OFFLINE instance with no Ubisoft relay,
  run two game windows (host + joined) on one loopback / LAN.

Until B/C, stay read-only: the engine's co-op session transport is online-only by the mod author's
own report (LAN = no), so offline multiplayer needs the host path, not more online joining.

## Critical path v3 — concrete hook points (agent, 2026-11-09, read-only)

Deeper pass over the party controller (FC3_106). The three `FUN_1056ec80 / 1056f3d0 / 103642f0`
that first looked like the logic are only lazy-singleton getters; the real co-op join/host logic is
below. Authoritative record: `NOTES.md` + supermemory (ids `nvjxCfpQn79eavDMBirw1P`, `chzyBsC2o83CHAcLdYT3Uu`).

Key objects (FC3.dll 1.06, Ghidra addresses):
- Master live session object = `*(DAT_12805180 + 4)`. `+0x118/+0x11c` identity args; `+0x120` = the
  host/principal id. The local player id comes from `FUN_1006f990()`; host check is
  `FUN_1006f990() == *(session + 0x120)`.
- Co-op join / reject gate = `FUN_11218480` (virtual). It trusts the current member list built by
  `FUN_11273650(provider, &list)`, where the provider is returned by `FUN_103660e0()`; it compares
  counts against the **config variable `MaxPartySize` at config-block offset `0xa88`**
  (registered `FUN_10065cd0("MaxPartySize",0xa88,0,3)` in `FUN_112250c0`), then emits the
  "Rejecting partyId … max allowed size / team size difference > 2" verdicts.
- Party netcode ctor = `FUN_11275750` (vtable `PTR_FUN_11faba78`) — ships the `CParty*NetMessage`.

**Path 1 (offline host: let the in-game party layer, not the Rv GameSession, decide membership).**
Minimal set of levers, all reversible, to be validated on solo-262 (1.05) first:
1. Raise config `MaxPartySize` (cfg offset `0xa88`) from 1 to the target (2/4).
2. Hook the member-list builder `FUN_11273650` (or its provider `FUN_103660e0`) so the host's
   session reports the desired number of members.
3. Relax/skip the reject branches in `FUN_11218480` so a locally-synthesized member is not refused.
4. Make `*(session+0x120)` equal the local principal so the host/leader gate passes.

**Open question that decides if Path 1 can give >1 real human:** a second game *instance* still has
to find and join a live session; that join goes through the RendezVous `GameSession`
(`CJoinGameSessionParam` `FUN_10207af0`). Synthesizing the host's member list lets one window behave
as a full 2-player session (good for solo, AI-like slots, testing), but two separate windows need
either the Rv GameSession to carry a real second participant (Rv relay/NAT — normally online) or a
second path that bypasses Rv join entirely. **Next read-only step:** decompile `FUN_11273650`,
`FUN_103660e0`, and the `CJoinGameSessionParam` path `FUN_10207af0` to see exactly which list the
joiner validates against, and whether a loopback/UDP Rv join is even reachable offline. No game code
is written until the owner approves step B.

Step-B concrete offsets (from `final2.txt`, session 22): provider member array = count `provider+0x38`,
array base `provider+0x3c`, entry size 0x20, member id at entry `+0x14`; provider gate = party type `>2`
AND party id `== DAT_1285fe3c`; host test `FUN_1006f990() == *(session+0x120)`. Single-instance
multi-slot is reachable with these; true 2-human offline still needs the Rv join (`FUN_10207af0`).

Transport verdict (session 22, decisive): the engine's co-op transport (`uplay_r14.dll` / RendezVous) is
service-bound only — zero LAN/loopback/listen/socket/p2p primitives, single `connectToNamedPipe` path,
`SessionFactory` asserts `!IsStandalone()`. So offline **2 real humans via the engine's transport is not
achievable**. Reachable offline: single-instance multi-slot (`local/scratch/multislot_design.md`). True
2-4 humans requires external netcode (transport B: reimplement the Rv GameSession + `CParty*NetMessage`
handshake in a custom layer) — a re-hosting project, decide scope with the owner.

## 7. Transport B architecture — 2-4 human campaign co-op (session 23, REVISED the feasibility)

**Key finding that reopens the path:** FC3.dll imports the **full Winsock API directly** (ws2_32 +
wsock32, 43 funcs: socket/bind/connect/listen/accept/send/recv/sendto/recvfrom/WSASendTo/WSARecvFrom/
select/getaddrinfo/inet_addr/...). So the co-op **gameplay DATA runs over FC3's own raw sockets**
(expected UDP). Only **session establishment / roster** is service-bound (`uplay_r14.dll`,
`connectToNamedPipe`). Classic split: matchmaking over the service, gameplay P2P over the game's UDP.

Therefore offline 2-4 humans is NOT a full netcode rehost. It reduces to **Transport B = a
session-establishment shim**: make each instance believe it is in the same session with peers at
given LAN addresses, then let the game's own socket netcode carry the actual co-op sync. This is a
MUCH smaller surface than reimplementing Rv/Orbit messaging.

Staged (each stage is a gate; do not proceed if a gate fails):
- TB1 — Map the game socket (in progress, delegate del_mw9o18i4_l0dn): socket type (UDP?), the
  send/recv pump, the bind port, and above all **where the peer endpoint (IP+port) comes from**
  (member struct? getaddrinfo of an Rv hostname string? a config/launch IP? LAN broadcast?), and
  whether the wire is **encrypted/authenticated** with a service-minted key. The whole plan hinges on
  these two answers.
- TB2 — If the endpoint is data we can supply and the wire is not service-keyed: a shim (detour the
  Orbit CGameSessionAPI vtable + the peer-address source) that reports a 2/4-member roster whose
  addresses point at the real LAN peers; raise MaxPartySize (cfg 0xa88). Verify two offline instances
  see each other and one joins.
- TB3 — Drive a co-op campaign mission across the two instances; measure what needs a connected peer
  vs. a listed member; fix desyncs with the hub sync tools (chaos/ownership/animcheck).
- TB4 — Robustness: NAT is out of scope (LAN/loopback first); add reconnect, host migration only if
  the engine already has a path for it.

Blockers that would downgrade this: TB1 shows the game socket is keyed by a service-minted secret,
or the peer endpoint is opaque service data we cannot synthesize. Both would push us back toward a
deeper Orbit/Rv protocol reimplementation. Decide after TB1.


## PLAN revision 2026-11-10 (session 23): offline 2-4 is a session-establishment shim, not a netcode re-host

Downgrades the Session 22 "offline 2-human infeasible via engine transport" verdict. That verdict only
looked at `uplay_r14.dll` (Orbit front-end). The engine's own `storm::echo` netcode has a **LAN + loopback
matchmaking layer** and FC3 has a **first-class command-line session launch**. Full detail in
`NOTES.md` / `NOTES.ru.md` "Session 23". Memory `cLjJUL76bobvfWw9AWxBPF`.

Confirmed offline-relevant primitives (FC3_106, RVA = VA - 0x10000000; map to 1.05 by string later):
- LAN/loopback discovery: `storm::echo::lan::BroadcastLanDiscovery2`, `storm::echo::lan::DiscoverSession`.
- LAN config vars (registered in `FUN_111f6650`): `LanMatchmakingDiscoveryOnLoopbackEnable` ("discover
  sessions on the local machine only"), `LanMatchmakingReuseAddress`, `LanHostBroadcastPort`,
  `LanClientBroadcastPort`.
- CLI launch (`InitDuniaEngine` @ 0x117a5750): `-coop` (0x11fb81fc), `-online` (0x11fb8234), `-ranked`,
  `-sessionuid` (0x11fb81e4), `-dedicated` (0x11f0e7dc) + `dedicatedConfig`, `-client` requiring
  `-login` + `-ip` ("Missing -login or -ip for -client."), `-offline` (0x11f37244) which skips the online
  frontend world + online-only session localization.
- Winsock fully imported (43 funcs): `WSASocketA` 0x10abeb9b, `WSASendTo` 0x10abed37, `WSARecvFrom`
  0x10abef04 = FC3's own UDP data plane. Orbit named-pipe is only matchmaking/rendezvous/auth.
- Rv GameSession param **singletons** (verified): `CJoinGameSessionParam` getter `FUN_10207af0`,
  `CCreateGameSessionParam` getter `FUN_10208000`, `CDeleteGameSessionParam` getter `FUN_10207b90`. Their
  caller/builder bodies are NOT yet decompiled, so the concrete host/join hook points are still TBD (a
  Java/REA pass over FC3_106 + FC3s105 will pin them; the earlier draft's `FUN_1188ca20` was erroneous).

Revised path (replaces TB1-TB4 severity):
- S1 — Live loopback probe: with the working solo262/1.05 mod (already boots a co-op-ruleset session
  offline), set `LanMatchmakingDiscoveryOnLoopbackEnable=1` + `LanMatchmakingReuseAddress=1` +
  `LanHostBroadcastPort`/`LanClientBroadcastPort`, and see whether a second instance discovers/joins the
  first offline. Cheap, decisive, no code yet.
- S2 — If discovery works but join is gated: the concrete detour surfaces are now the GameSession result
  handler tables `joinResultHandlerTable @ 0x11f56dac` / `createResultHandlerTable @ 0x11f57c14` (verified,
  PLAN Session-24), NOT the singleton getters. The join handshake is a LAN storm::echo event flow
  (`DiscoverSession` → `RequestJoinSessionRefId` → `RequestTicket` → host `ReceiveTicketRequest` →
  `AcceptTicketRequest` → `DistributeTicket`) over **PRUDP** (`prudp:/`, pump `FUN_10ac3340` → send
  `FUN_10abec30` / recv `FUN_10abedb0`).
- S3 — Drive a co-op campaign mission across two instances; fix desyncs with hub sync tools.

Blockers (updated by Session-24 evidence):
1. RESOLVED toward feasible: `SessionTicket` is **host-issued** on the LAN event channel
   (`DistributeTicket`/`ReceiveTicketRequest`), no Orbit/service symbol in the path → not Ubisoft-gated.
   Remaining: confirm by reading those two handler bodies (one pass).
2. REFRAMED: payload is **not bulk-encrypted** (no AES/SHA/MD5/Blowfish sigs; PRUDP = XOR+Adler CRC). The
   work is to **be inside/be adjacent to PRUDP** (replicate its connect handshake), not to defeat a cipher.


## Transport phase 2 — over-the-internet relay (HXCoop / Steam Spacewar AppID 480) — agent, 2026-11-11

Scope: let 2-4 friends play together over the internet with **no port forwarding / no NAT config**. This is
*phase 2 only* and is **not** the current critical path. Phase 1 (offline + LAN, via the engine's own
`storm::echo` LAN/loopback) is unaffected by, and independent of, this.

**Prerequisite (hard blocker first).** The relay bridges an already-running session's UDP; it does not create
a session. It only becomes usable once phase 1 has FC3 opening a real co-op session with a 2-4 roster over
loopback/LAN (the session-glue work, Sessions 27-28). Until then there is nothing to relay. So the transport
decision is: **phase 1 transport = native `storm::echo` LAN/loopback; this relay is layered on top for
phase 2.** The Spacewar relay is NOT a way around the session/party blocker - it sits one layer below it.

**Pattern (hub `playbook/networking-steam-spacewar.md`, "A relay instead of engine code" / HXCoop):**

- **Host machine:** one local UDP socket per remote player, `connect()`ed to the game's port on `127.0.0.1`
  (the `storm::echo` data ports 9000-9003 / `LanHostBroadcastPort` 9004 in `defaultnetworkconfig.xml`).
  A friend's Steam messages are written out of that player's socket, and whatever the game answers on it goes
  back to that player. The game sees every friend as a separate `127.0.0.1` client.
- **Client machine:** the helper binds a free `127.0.0.1` port, the game's `storm::echo` client connects to it,
  and the helper forwards everything to the host's SteamID.
- **Transport:** `ISteamNetworkingMessages` under **AppID 480 (Spacewar)** - a standalone helper exe next to the
  game loads `steam_api.dll` (FC3 is 32-bit, so `Windows-x86/steam_api.dll`) with `steam_appid.txt` = `480`.
  FC3 itself is never made a Steam game and ships unmodified. Send game packets **unreliable with NoNagle**
  (`storm::echo`/PRUDP has its own reliability); keep-alive and goodbye on channel 1 as reliable messages.
- **Authorization gate:** only lobby members get through - before forwarding a new peer's traffic into the local
  game port, check their SteamID against the lobby (`GetNumLobbyMembers` / `GetLobbyMemberByIndex`).
- **One-PC testing:** use the hub's mock `steam_api.dll` (~400 lines, `steamlink/mock`) so two helper instances
  + two game instances can be exercised without two real Steam accounts.

**Known trade-offs (accepted for a friend-shared mod):** both players show as "playing Spacewar"; AppID-480
lobbies are visible worldwide unless filtered by lobby data; cannot ship through the Steam store this way.

**Effort / order:** a standalone helper exe (~300 lines C) + the mock; fully independent of FC3's code once
phase-1 loopback co-op works on one PC. Sequence: (1) prove 2-4 humans on one PC via `storm::echo` loopback
(`LanMatchmakingDiscoveryOnLoopbackEnable=1`), (2) put the helper pair between them and test through the mock,
(3) two real Steam accounts over Spacewar.
