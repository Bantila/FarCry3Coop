# FC3 co-op probe (English) / Зонд co-op для Far Cry 3

> Русский: [README.ru.md](README.ru.md)

> **Status / Статус:** early research probe (Phase 2, hook H1). Not a working co-op mod.

## What this is

The first **injection probe** for the Far Cry 3 co-op project. It is a 32-bit `dinput8.dll`
proxy: the engine (`FC3.dll` / `FC3_d3d11.dll`) imports `dinput8.dll`, so a `dinput8.dll`
placed next to the game loads first. Our proxy:

1. forwards all six `dinput8` exports to the real system `dinput8.dll` (so the game still
   launches), and
2. runs a background thread that writes the co-op session id `0x43521E6F` into the two engine
   globals that Phase 1 proved hold the active session id.

This is hook **H1** from the plan — *the cheapest first experiment*: force the co-op id at
runtime and observe whether the game enters a co-op (host) state. It only writes two global
dwords, so it cannot brick a save, but it is an untested experiment: the engine may overwrite
the value during its own init, or the two globals alone may be insufficient to reach a playable
co-op state. That is exactly what it is meant to find out.

## Layout

```
mod/fc3coop_probe/
  fc3coop_probe.c   source: DllMain, 6 forwarders, poke thread (see header comment for design)
  dinput8.def       exports the 6 names by ordinal 1..6 (the set that keeps the game loading)
  build.bat         MSVC x86 build -> build/dinput8.dll
  verify_build.py   checks the built DLL: x86 + the 6 exports on ordinals 1..6
  build/            (git-ignored) compiled dinput8.dll lands here
```

Sources are tracked; binaries (`build/`) and logs are git-ignored.

## ASLR — why the code uses base + RVA

`FC3.dll` is ASLR-enabled (`DllCharacteristics=0x0140`, relocations present, preferred base
`0x10000000`). Every VA in `NOTES.md` is a *preferred-base* VA only. The probe reads the live
module base at runtime (`GetModuleHandleW`) and adds the RVA (`VA − 0x10000000`):

| Meaning | Preferred-base VA | RVA used by the probe |
|---|---|---|
| co-op id global 1 | `0x12891ca0` | `+0x2891CA0` |
| co-op id global 2 | `0x12891ca8` | `+0x2891CA8` |
| co-op id value | — | `0x43521E6F` |

## Build

```
cd mod/fc3coop_probe
cmd //c build.bat        # needs the VS x86 tools (vcvars32.bat)
python -I verify_build.py
```

Produces `build/dinput8.dll` (x86, static CRT `/MT`). `verify_build.py` must print
`EXPORTS CHECK : PASS` with the six names on ordinals 1..6 and `machine 0x14C`.

Verified build (2026-11-07): `build/dinput8.dll`, 115,200 bytes, `machine=0x014C`,
`DllCharacteristics=0x0140`, exports `DirectInput8Create@1, DllCanUnloadNow@2,
DllGetClassObject@3, DllRegisterServer@4, DllUnregisterServer@5, GetdfDIJoystick@6`.

## Install & run (the owner does this — never automated here)

1. Copy `build/dinput8.dll` into the **working copy** game bin dir
   (`H:\FarCryCoop\TestFC3\bin\`). Never into the real install (`H:\Uplay\Far Cry 3\` is
   read-only by project rule).
2. Launch the game normally and load into a single-player game.
3. Open `bin\fc3coop_probe.log`. It now logs enough to answer H1 from a *single* run:
   - `FC3 coop probe: engine base = 0xXXXXXXXX (from FC3.dll)` — the probe loaded and found the engine.
   - `pre-poke default: [g1]=0xAAAAAAAA [g2]=0xBBBBBBBB` — the value the engine held *before* we
     touched it (the single-player default). This tells us what a normal game stores there.
   - `poke n/5: ... readback [g1]=0x... [g2]=0x...` — after each forced write, the value we read
     back. If read-back equals `0x43521E6F` the poke stuck; if it shows the default again, the
     engine overwrote us (H1 alone is not enough).
   - `OVERWRITE: readback ...` / `heartbeat poke #N ...` — periodic proof of whether the value holds.
4. Observe whether the game reports/enters a co-op (host) state or changes behaviour.

If the game fails to start, delete `dinput8.dll` from the bin dir to restore it.

## Safety

- Does not touch the real game install or saves.
- Writes only two global dwords in the engine's data section, guarded by `VirtualQuery` +
  `VirtualProtect` + SEH, so a wrong pointer can never crash the game.
- Forwarding is transparent; removing the DLL fully restores the game.
