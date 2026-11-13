# Workspace

Russian version: [workspace.ru.md](workspace.ru.md)

Canonical layout of this project is the tree from the owner's previous PC, `E:\FarCryCoop\`. Golden rule 2 in
[AGENTS.md](../AGENTS.md) lists the paths that are legal to work in on this PC (its "Workspace on this PC"
table); it does not name `E:\FarCryCoop`. That old layout and its loader `E:\FarCryCoop\env.ps1` do not exist
on this PC; the paths in use here are in "Paths on this PC" below.

History of the previous PC (October 2026, drive E:) — folder layout, kept as the record of where the
tools and repos lived:

| Folder | Contents |
|---|---|
| `Downloads\<name>\` | Original archives, one folder each, SHA-256 checked |
| `Tools\` | Unpacked portable tools |
| `Data\` | Tool settings and caches (Ghidra settings/cache, npm cache, npm global prefix) |
| `Temp\` | Temporary files (`TEMP`/`TMP` point here) |
| `FarCryCoop\`, `FarCry<N>Coop\` | Repositories, one folder per game |

## Paths on this PC (verified 2026-11-03)

| What | Path |
|---|---|
| Repos (this game repo, the multi-game hub, the coop-anything hub) | `D:\Projects\Co-op Anything\` |
| Test copy of the game (1.06) | `H:\FarCryCoop\TestFC3\` |
| Read-only install (Ubisoft Connect) | `H:\Uplay\Far Cry 3\` |
| Scratch and private state | `<repo>\local\`, `<repo>\local\scratch\` (gitignored) |
| Agent harness temp | `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp` |
| REA / Ghidra / JDK toolchain | `C:\tools\`, `C:\Program Files\nodejs\`, npm global prefix `%USERPROFILE%\AppData\Roaming\npm` (see below and `docs/tools/rea.md`) |

Every `E:\FarCryCoop\` path kept in this document and in NOTES.md is a historical record from the
owner's previous PC (October 2026). Drive `E:` does exist on this PC as a game drive, but it has no
`FarCryCoop` folder and no `env.ps1`. Use the table above for live paths.

## Installed tools on this PC (verified 2026-11-03)

| Tool | Version | Path | Source |
|---|---|---|---|
| REA (`rea-agents`) | 6.8.0 (`rea --version`) | `%USERPROFILE%\AppData\Roaming\npm\node_modules\rea-agents` | npm global install; registered for pi by `rea setup --client pi --yes` |
| Ghidra | 12.1.4 | `C:\tools\ghidra_12.1.4_PUBLIC` | https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build |
| Eclipse Adoptium Temurin JDK | 21.0.13+9 (`JAVA_RUNTIME_VERSION 21.0.13+9-LTS`) | `C:\tools\jdk-21.0.13+9` | Temurin 21 (Adoptium) |
| Node.js | v22.23.4 | `C:\Program Files\nodejs\node.exe` | system install (satisfies REA "Node 22.23.4+"); npm 10.9.9 |

Ghidra archive on this PC: `C:\tools\ghidra_12.1.4_PUBLIC_20260921.zip`, 569,649,598 bytes,
SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` — same hash that is recorded
for the October 2026 download, so the archive matches the one already documented.
`Ghidra\application.properties` here reads `application.version=12.1.4`, `application.java.min=21`.
No SHA-256 was re-checked on this PC for the Temurin and Node installers (no new hash recorded).

User environment (`HKCU\Environment`): `GHIDRA_INSTALL_DIR=C:\tools\ghidra_12.1.4_PUBLIC`,
`JAVA_HOME=C:\tools\jdk-21.0.13+9`. No machine-level `JAVA_HOME`. There is no `env.ps1` loader on this
PC; REA's own registration carries those two variables in its `env` block (see `docs/tools/rea.md`).

Ghidra `support\launch.properties` on this PC was **not** modified: no `JAVA_HOME_OVERRIDE`,
`application.settingsdir`, `application.cachedir`, `application.tempdir` or `java.io.tmpdir` redirects
(there is no `E:\FarCryCoop` to redirect into).

`rea doctor --client pi` / `--provider ghidra` (2026-11-03): `healthy: true`, ghidra
`configured: true` / `available: true`, `providerVersion 12.1.4`, java accepted as
`"21.0.13; 64-bit; JDK"`. REA accepts Ghidra 12.1.x only, so `C:\tools\ghidra_12.2_PUBLIC`
(`application.version=12.2`, `application.java.min=25`, 879 MB) is unused on this PC and awaits the
owner's delete decision.

## History of the previous PC (October 2026, drive E:) — installs recorded on 2026-10-18

| Tool | Version | Source | SHA-256 (archive) |
|---|---|---|---|
| Node.js | v24.22.0 LTS (win-x64 zip) | https://nodejs.org/dist/v24.22.0/ | `f9683a19877e12a9b167305c8db71040d812876359de21f0d2e97c3f321f80c3` |
| Eclipse Temurin JDK | 21.0.12.1+1 (x64 zip) | https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1 | `f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e` |
| Ghidra | 12.1.4 (`ghidra_12.1.4_PUBLIC_20260921.zip`) | https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build | `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` |

Checksums came from nodejs.org `SHASUMS256.txt`, the Adoptium API and the Ghidra GitHub release;
all three downloads matched. The shell there was loaded with `. E:\FarCryCoop\env.ps1`.

There Ghidra `support\launch.properties` was changed (original kept as `launch.properties.orig`):
`JAVA_HOME_OVERRIDE`, `application.settingsdir`, `application.cachedir`, `application.tempdir`,
`java.io.tmpdir` pointed into `E:\FarCryCoop`. Check run: `analyzeHeadless.bat` printed its usage and
created its settings/cache folders under `E:\FarCryCoop\Data`.

Historical evidence (2026-10-18): those tool installs and the Ghidra check were recorded on the owner's
previous PC with drive `E:`. Node v24.22.0 (portable) and Temurin 21.0.12.1+1 lived under
`E:\FarCryCoop\Tools`; on this PC they are not installed — the live toolchain is the table above.

## Known limits of "never touch C:"

- Windows, PowerShell and the system `git.exe` (`C:\Program Files\Git`) live on C:. They are used as
  installed; nothing new is written there by our tools. Claude Code is not installed on this PC
  (`where claude` fails; no `%USERPROFILE%\.claude`, no `%USERPROFILE%\.claude.json`).
- REA's registration writes to `C:\Users\<user>\.pi\agent\mcp.json` on C: (done on 2026-11-03 by
  `rea setup --client pi --yes`; REA left the backups `mcp.json.rea.backup` and
  `mcp.json.rea.backup.fbd170df1fed8f45e9e0d4080d072c68a433d38797d2ba5294b89069866f8b2e.recovery`, and
  its skill under `C:\Users\<user>\.agents\skills\`). The old route `claude mcp add --scope local`
  wrote to `%USERPROFILE%\.claude.json`; that is the previous PC's record, not applicable here.
  Both writes are deviations from golden rule 2 — flagged. On the previous PC the owner explicitly
  approved the single `.claude.json` write (see `docs/tools/rea.md`); on this PC REA wrote only the
  registration and its backups under `C:\Users\<user>\.pi\agent\` plus the skill under
  `C:\Users\<user>\.agents\skills\`.
- The agent instruction file is `AGENTS.md` (with `AGENTS.ru.md`); `CLAUDE.md` is kept only as a shim that
  points to it, because some harnesses read that file name. The previous version is preserved as
  `CLAUDE.md.keep`.
- The agent harness writes its own temp work to `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp` (delegate outputs, sandbox scripts).
  That is not redirectable through our settings and contradicts golden rule 2 — flagged, not fixed
  (owner decision, still open).
