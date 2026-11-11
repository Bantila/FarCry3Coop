# scripts/

Read-only analysis tooling for Far Cry 3 builds 1.05 (`H:\FarCryCoop\105\game-105`) and
1.06 (`H:\FarCryCoop\TestFC3`), plus the Ubisoft Connect install at
`H:\Uplay` and the retail install `H:\Uplay\Far Cry 3`. Every script here is meant to
**read** PE files and, in two cases, to **run** the game; `patch_dll.py` and
`fc3_trampoline.py` are the only ones that can write bytes, and `fc3_trampoline.py
install --apply` has never been run on this machine. Run them with `python -I`
(isolated mode: no user site-packages, no stray `python*.dll` on PATH - required because
the game directory contains `python3.dll`, which otherwise breaks `python.exe`).

## Shared helper

| Script | What it does |
|---|---|
| `fc3_addrmap.py` | RVA -> file-offset map for one build (`PE` class, `va2off()`, string/dref lookup). Used by `fc3_func_dump.py`, `fc3_gate_probe.py`, `fc3_iat_find.py`, `fc3_iat_scan.py`, `fc3_reexec_probe.py`, `fc3_reg_keys.py`. |

## PE basics

`fc3_pe_info.py` (header/sections/exports/imports), `fc3_imports.py` (import directory),
`fc3_dump.py` (hex/ASCII dump of a VA range + prologue detection), `fc3_vinfo_probe.py`
and `fc3_version_probe.py` (file version + sha256 of the current install),
`fc3_rsrc_probe.py` (resource directory of `farcry3_d3d11.exe`).

## Strings and IAT

`fc3_strings.py` (launcher/re-exec strings + readers), `fc3_strgrep.py` (grep .rdata/.data
strings), `fc3_args_scan.py` (marker scan in a directory or whole install),
`fc3_args_context.py` (readable context around marker hits), `fc3_iat_scan.py`,
`fc3_iat_map.py`, `fc3_iat_find.py` (IAT slot <-> imported name <-> call sites),
`fc3_iat_reverse.py` (thunk address -> imported name).

## Command-line / launch analysis

`fc3_cmdline_cluster.py` (switch-parsing cluster from a switch-string VA),
`fc3_switchtable.py` (jump table behind the launch switch), `fc3_quicklaunch_map.py`,
`fc3_switch_context.py` (find every site that pushes a switch string and calls the parser:
raw `68 <switch VA> ... e8 <rel32>` scan plus a function-prologue walk that reports where the
function body lands - `--mode prologue|raw|both`), `fc3_reloc_xref.py` (cross references of an absolute
data VA - premise corrected 2026-11-03: disp32 fields in `.text` hold the default image-base VA
verbatim, so the tool scans the ModRM disp32 forms and verifies each hit by backward decoding, while
relocation patch sites are reported separately - `--mode code|reloc|both`),
`fc3_param_records.py` (enumerate session-descriptor records: `push <name VA>; push <type code>;
call <creator>` -> name, type code, call site. Creator VAs are POSITIONAL arguments (not `--creator`);
`--window 64` is the look-back distance and `--ident-only` drops cross-function false positives. Use the
corrected registrar families: `FC3_d3d11.dll` `0x11acaba0`/`0x11acac50`/`0x11acad00`/`0x11acb320`/
`0x11acaf10`, `FC3.dll` `0x11ab6750`/`0x11ab6800`/`0x11ab68b0`/`0x11ab6ac0`/`0x11ab6b70`/`0x11ab6e20`/
`0x11ab6ed0`, and the exec-record creators `0x1003b4b0` (FC3.dll) / `0x10638fb0` (FC3_d3d11.dll) -
see NOTES.md "Session-descriptor record tables"),
`fc3_func_dump.py` (function body: embedded strings + data references),
`fc3_callers.py` (reverse callers of a function), `fc3_dataslot.py` (which data slot a
absolute data reference points at), `fc3_reexec_probe.py` (1.06 re-exec bootstrap),
`fc3_drm_probe.py` (DRM/UPC bootstrap), `fc3_gate_probe.py` (gate/lock check),
`fc3_reg_keys.py` (which code reads `HKCU\Software\Ubisoft\Far Cry 3`),
`fc3_dis.py` (annotating capstone disassembler: callers, imported names, string
references - the main RE tool of the 1.06 findings),
`fc3_mode_cascade.py` (disassemble a launch-mode cascade in one PE: the mode-name strings it matches,
the `cmp`/`test` gates, the mode-id globals it reads together with the value stored in each global,
and the local slot the chosen id is written to. Usage `python -I scripts/fc3_mode_cascade.py <pe>
<start VA> [--end <VA> | --limit N] [--no-strings] [--json]`; a bare module name resolves against
`H:/FarCryCoop/TestFC3/bin/`. Verified on FC3.dll `0x11a8c440 .. 0x11a8c5f0` and FC3_d3d11.dll
`0x11aa08d0 .. 0x11aa0980`; see NOTES.md "the mode-flag cascade").

## Launch helpers (run things)

`fc3_launch_probe.py` (launch the 1.06 test copy with quick-launch arguments and capture
logs), `fc3_upc_probe.py` (ask Ubisoft Connect to launch our test copy and record the
exact command line), `fc3_test_startargs.py` (check whether the hub forwards the
`ExecutableName` registry value), `launch_105.ps1`, `build_testgame.ps1`,
`build_patch.ps1`, `reunpack.ps1`, `switch_variant.ps1`, `thread_eips.ps1`.

## Diffing / data tools (from the owner's Phase 1 work)

`bindiff.py`, `contentcompare.py`, `dupcheck.py`, `fat.py`, `fatcompare.py`,
`manifest_diff.py`, `edit_playlist.py`, `names.py`, `names_ext.py`, `find.py`,
`findpats.py`, `patchctx.py`, `reg_fields.py`, `peinfo.py`, `patch_dll.py` (byte patches
of a **copy** of FC3.dll / FC3_d3d11.dll), `fc3_trampoline.py` (14-byte jmp stub writer;
`install --apply` never run here - owner decision pending),
`fc3_accessor_thunks.py` (census the `mov eax, imm32` + `jmp <accessor helper>` thunks of one PE,
group them into contiguous runs and report the stride of each container base global; the parity check
behind the accessor chain in NOTES.md. Usage `python -I scripts/fc3_accessor_thunks.py <pe>
[--helper 0x10004b70] [--min-count 3] [--range START:END] [--show-va <VA>] [--json]`; verified: 3228
thunks in 523 runs in both 1.06 modules).

## Runtime tracing (Frida)
`fc3_h3_trace.js` — runtime trace + the two H3 levers for the co-op mode switch (PLAN.md, "Hook status
after session 7"). Attaches to a live **offline** FC3 process and logs (read-only) the mode dispatch at
`0x113405a0` (mode-manager field `[this+0x4c]`), the co-op-id installer `0x11279910` and its two static
callers `0x1127a0f0` / `0x11279fc0` with backtraces, and reads the live `CFCXPlaylistService` container
`[service+0x8c0]` through `dumpService()`. The RPC `switchCoop(dryRun)` (H3a) writes
`[modeManager+0x4c]=0x43521e6f` and calls `modeManager->vtable[+0x5c](&id)`; `populate(dryRun)` (H3b)
calls `FUN_1127a0f0(service)` to build the co-op entry. Always run `dryRun=true` first — calling an engine
virtual blind can crash the game. Addresses are 1.06 (`FC3.dll` base `0x10000000`); map to 1.05 with
`fc3_addrmap.py` before use. Attach to an `-offline` instance only — never an online / Ubisoft Connect
session (anti-cheat + the `OpenMutexA("FarCry3Instance")` guard). Run it one-command with
`scripts\fc3_h3_run.bat` (attaches to the running `farcry3.exe` / `farcry3_d3d11.exe`, loads this script,
mirrors the whole session to `H:\FarCryCoop\scratch\h3_live.log`, and gives a `dump`/`modes`/`mode`/`switch`/`pop`
command loop). Or attach by hand: the game process is `farcry3` (not `FC3`), so
`frida -n farcry3 -l scripts/fc3_h3_trace.js` and use `rpc.exports.dumpService()` / `lastMode()` /
`switchCoop(true)` / `populate(true)` in the REPL. `fc3_h3_run.py` is the driver the `.bat` calls; pass
`--pid` to skip auto-detect. The owner's ordered procedure is in `docs/h3-live-test.md` (+ `.ru.md`).

## Ghidra offline project (headless)
Session 7 built an offline Ghidra project of the 1.06 `FC3.dll` so pseudocode can be exported for any RVA
**without running the game**. The `.gpr` lives in scratch (`H:\FarCryCoop\scratch\ghidra\proj\FC3_106`,
~647 MB, `-default` analysis, ~2 h once) — not committed. To re-export more functions, reuse the saved
analysis (loads in ~3 min, no re-analysis) with a headless postScript:
`analyzeHeadless <projDir> FC3_106 -process "FC3.dll" -noanalysis -scriptPath <dir> -postScript <name>.java`.
`ghidra/DecompileH3.java` is the worked example (exports the mode dispatcher `FUN_11340560`, the service
init `FUN_1127a0f0`, the installer `FUN_11279910`, the singleton getter `FUN_103d1640` and the mode
switch vtable `+0x5c`); `ghidra/run_decomp_h3.bat` shows the invocation (paths point at the scratch
project — edit them). `ghidra/DisasmSwitch.java` (+ `run_disasm.bat`) is the linear-disasm variant used to
disasm-confirm the switch ABI. `ghidra/DumpCallers.java` (+ `run_dump_callers.bat`) lists xrefs to the
dispatcher (proved it is invoked only virtually), `ghidra/DumpVtable.java` (+ `run_dump_vtable.bat`) walks a
function's vtable, and `ghidra/DecompileModeSwitch.java` (+ `run_decomp_modeswitch.bat`) decompiles the live
mode-switch virtual `vtable+0x5c` (`FUN_1030f8a0`, an id-setter) and the dispatcher's entry-bookkeeping slots.
`ghidra/FindModeConsumers.java` lists every function that loads a mode-id constant (and xrefs to the manager
vtables), and `ghidra/DecompileConsumers.java` decompiles the co-op mode-change handler `FUN_10fa1990` plus
its constructor and loader sibling. `ghidra/TraceDescriptor.java` finds xrefs to `FUN_10fa1990` (it is the
manager vtable slot `+0x0C`) and decompiles its `param_3` usage; `ghidra/TraceRegistry.java` lists the
READ/WRITE xrefs of the global mode-list singleton `DAT_128048c0` (and `DAT_12804acc`/`DAT_12804b3c`);
`ghidra/DecompRegistry.java` decompiles its constructor `FUN_10048230` and teardown `FUN_11756e00`.
At runtime `fc3_h3_run.py`'s `modes` command (`dumpModes` RPC) reads the live `DAT_128048c0` list and
prints every registered mode entry (`id@+0x20`, `name@+0xC`), to check offline whether a CO-OP
(`0x43521e6f`) entry already exists. The generic offline runner is `ghidra/run_headless.py <Script.java> <log>`
(reuses the analyzed `FC3_106` project, no re-analysis).
Requires Ghidra 12.1.4 (`C:\tools\ghidra_12.1.4_PUBLIC`) + Temurin JDK 21.

## Co-op world / patching (offline)

- `h7a_coopmap_patch.py` — offline co-op map selector patch for the 1.05 `FC3.dll`. Rewrites the
  co-op startup world string `mpdlc1_aegir` -> `fc3_main` at file offset `0x15345D0` (12 bytes,
  byte-minimal) so a co-op session loads the single-player campaign world instead of the stock co-op
  island; the same single change as the community mod OpenWorld220 (verified at the same offset).
  Subcommands `status` / `apply` / `restore`; `apply` first writes an in-place backup `FC3.dll.bak_h7a`
  and `restore` reverts. Targets only `H:\FarCryCoop\TestFC3_105`. Vanilla 1.05 md5 `5ff04533…` ->
  patched `e4516487…`. The other co-op string `mpdlc1_idun` (at `0x15A2568`) is left untouched.

## LAN / netcode probes (Session 23)

- `fc3_lan_probe.py` — read-only probe: locate LAN-matchmaking / hosting anchor strings in `FC3.dll`
  (`storm::echo::lan::*`, `LanHostBroadcastPort`, `-dedicated`/`-client` switches, …) and the code that
  references them; prints RVAs (`VA - imageBase`). `python -I scripts/fc3_lan_probe.py [strings|xrefs]
  [extra substr ...]`. No writes.

## Orbit-API loader proxy (Session 27)

The in-process orbit-API observation shim lives in `../src/uplay_proxy` (source tracked; the built
`uplay_r1_loader.dll` is gitignored). These scripts drive it:

- `gen_uplay_proxy.py` — generate `src/uplay_proxy/uplay_proxy.cpp` + `.def`: the 58 `UPLAY_*` cdecl
  exports as stack-forwarding logging thunks (reads `local/scratch/loader_exports.json`).
- `build_uplay_proxy.py` — build the 32-bit proxy without shell `.bat` quirks (pulls the MSVC x86 env
  from `vcvars32` via `cmd /c`).
- `build_proxytest.py` — build `src/uplay_proxy/proxytest.c`, the forwarding-transparency test harness.
- `probe_orbit_gates.py` — read-only: disassemble the prologues of the orbit-API gate exports in the real
  loader to confirm the `int(void)` cdecl convention before faking them (Session 28).
- `probe_memberlist_imports.py` — read-only: dump which `UPLAY_*` `FC3_d3d11.dll` imports (and their IAT slot
  RVAs), to xref the party/session consumers (Session 28c).
- `probe_rv_party.py` — read-only: disassemble the Rv party/session controller hooks (`FUN_11273650`,
  `FUN_11218480`, …) from the 1.06 `FC3.dll` to design the 2-4 roster detour (Session 28d).
- `probe_rv_detour.py` — read-only: caller xref + aligned disasm of the roster/join controller (`FUN_11218480`,
  `FUN_11273650`, member getter `0x10070590`) on the 1.06 `FC3.dll` (Session 28e).
- `probe_rv_live.py` — read-only: for the RUNNING module (`FC3_d3d11.dll` copy, md5 46bcc097) and a live Frida
  RVA, resolve ImageBase + RVA->file-offset, locate the `gethostbyname` IAT and disasm the window to confirm the
  RendezVous bootstrap is aligned and the file is unpacked (Session 28q). WARNING: `probe_rv_party.py` /
  `probe_rv_detour.py` RVAs came from the DX9 install `FC3.dll` (md5 5742de2a), NOT the running module - do not reuse.

`ghidra/decompile_session_callers_106.py` is a Jython Ghidra script (open analyzed `FC3_106`, decompile
the Rv `GameSession` create/join param builders + callers). Kept as the intended offline-join hook-point
probe; under Ghidra 12.1.4 the PyGhidra `currentProgram` binding failed, so the pass must be run as a
Java `-noanalysis` script instead (see Session 23/24 notes).

## Caches and ignored files

`*_dis_cache.json` (disassembly cache), `__pycache__/`, `../Temp/` (agent scratch) and
`../local/` are gitignored.

## Carried-over paths

The scripts copied from the owner's PC (October 2026) hardcoded the old layout: `DLL_106 = E:\SteamLibrary\steamapps\common\Far Cry 3\bin\FC3.dll`,
`DLL_105 = E:\FarCryCoop\Downloads\fc3-1.05\bin\FC3.dll`. Drive `E:` does not exist on this PC. These scripts are
kept as evidence and are NOT retargeted silently: re-pointing a script that writes into the game
install (patch / build / unpack) is an owner decision. On this PC the read-only install is
`H:\Uplay\Far Cry 3\`, the 1.06 test copy is `H:\FarCryCoop\TestFC3\`; analysis-only scripts here
already read those verified paths.


## Live Frida tracing (`scripts/frida/`)

- `fc3_coop_trace.py` + `fc3_coop_trace.js` - attach Frida to the running `farcry3_d3d11.exe` (launched via
  Ubisoft Connect) and trace the co-op service connection. Core = winsock hooks (`gethostbyname`/`getaddrinfo`/
  `connect`/`sendto`/`recvfrom`/`bind`) to reveal the co-op service host:port and the DNS/connect failure; plus
  best-effort hooks on the FC3.dll gate offsets. Run after reaching the main menu, then navigate to co-op. Output:
  `local/scratch/frida_coop_<ts>.log`. Used for the direction (B) rendez-vous recon (NOTES 28k-28n).
- `fc3_coop_force.py` + `fc3_coop_force.js` - direction (B) in-memory go/no-go probe (no disk writes). Logs the
  net-engine connection mode (`FUN_1092d256` field +0xe: 0=LAN/1=Online/2=Offline) and the online-coop entry
  (`FUN_1044123b`), and with `FORCE=true` forces the RendezVous gate (`FUN_11245090`/`FUN_112492a0`/`FUN_11279ba0`)
  to success to see where it dead-ends (expected: UbiAuthentication). Offsets target the running `FC3_d3d11.dll`
  copy md5 46bcc097. Output: `local/scratch/frida_force_<ts>.log` (NOTES 28r).
