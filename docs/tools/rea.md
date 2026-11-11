# REA (Reverse Engineer Anything)

Russian version: [rea.ru.md](rea.ru.md)

- Repository: https://github.com/morluto/rea (MIT). npm package: `rea-agents`.
- What it is: one MCP server + CLI that gives an agent reverse-engineering tools (native binaries via
  Ghidra / IDA / Hopper, JavaScript/Electron, .NET, websites). Analysis runs locally.
- Version checked: 6.8.0 (`rea --version` -> 6.8.0, `package.json` -> 6.8.0, verified 2026-11-03 on this
  PC). The first record was 6.7.0 (`server.json`, `package.json`, commit `a25eb5fb`, 2026-10-18) on the
  previous PC.

## Registered on this PC (verified 2026-11-03)

REA 6.8.0 is installed globally via npm and registered for the **pi** agent. Ghidra 12.1.4 and a JDK 21
are present; Claude Code is not installed here.

| Component | State on this PC |
|---|---|
| REA | 6.8.0 (`rea --version`), npm global package `rea-agents` at `%USERPROFILE%\AppData\Roaming\npm\node_modules\rea-agents` (entry script `scripts\rea.mjs`) |
| REA skill | `reverse-engineer-anything` v49 at `%USERPROFILE%\.agents\skills\reverse-engineer-anything` (cli_commands 175, mcp_tools 229, mcp_prompts 6) |
| Ghidra | 12.1.4 at `C:\tools\ghidra_12.1.4_PUBLIC` (`application.version=12.1.4`, `application.java.min=21`) |
| JDK | Eclipse Adoptium Temurin 21.0.13+9 (`JAVA_RUNTIME_VERSION 21.0.13+9-LTS`) at `C:\tools\jdk-21.0.13+9` |
| Node.js | v22.23.4 at `C:\Program Files\nodejs\node.exe` (system install, satisfies REA "Node 22.23.4+"), npm 10.9.9 |

Registration was made by `rea setup --client pi --yes`. The `rea` entry in
`%USERPROFILE%\.pi\agent\mcp.json` is stdio:

```json
"rea": {
  "type": "stdio",
  "command": "C:\\Program Files\\nodejs\\node.exe",
  "args": ["C:\\Users\\USER\\AppData\\Roaming\\npm\\node_modules\\rea-agents\\scripts\\rea.mjs", "mcp"],
  "env": {
    "GHIDRA_INSTALL_DIR": "C:\\tools\\ghidra_12.1.4_PUBLIC",
    "JAVA_HOME": "C:\\tools\\jdk-21.0.13+9"
  }
}
```

REA wrote its own backups next to that file: `mcp.json.rea.backup` and
`mcp.json.rea.backup.fbd170df1fed8f45e9e0d4080d072c68a433d38797d2ba5294b89069866f8b2e.recovery`.
The `coop-anything` and `supermemory` entries were untouched.

User environment (`HKCU\Environment`): `GHIDRA_INSTALL_DIR=C:\tools\ghidra_12.1.4_PUBLIC`,
`JAVA_HOME=C:\tools\jdk-21.0.13+9`. There is no machine-level `JAVA_HOME`.

`rea doctor --client pi` / `--provider ghidra` (2026-11-03): `healthy: true`, `environment_healthy: true`,
ghidra `configured: true`, `available: true`, `providerVersion 12.1.4`; 9 ghidra checks ok, including
java `"21.0.13; 64-bit; JDK; accepted a 64-bit full JDK 21 or newer"` and native_decompiler
`win_x86_64` / `decompile.exe` / `pe x86_64`. ida, jadx and kuna come back as `missing_analysis_engine`
(BYO: `REA_IDA_MCP_CONFIG`, `REA_JADX_MCP_JAR`, `REA_KUNA_COMMAND`) and are not needed here.

Pitfall (verified here): the ghidra provider checks in `rea doctor` read the environment of the CLI
process. Changes in `HKCU` or `setx` are invisible to processes already running, so after changing those
variables both the shell and the running agent (the pi MCP `rea` server) must be restarted.
`rea setup` also writes the detected provider env into the client registration.

Version policy (`rea-agents/dist/ghidra/GhidraReleasePolicy.js`): `SUPPORTED_GHIDRA_VERSION` is
`"12.1.4"`, the accepted release line is 12.1.x only, `SUPPORTED_GHIDRA_JAVA_MAJOR` is 21, and the JDK
must fall inside the Ghidra installation's own `application.java.min`/`max`. That is why Ghidra 12.2
(`application.version=12.2`, `application.java.min=25`) is rejected: `C:\tools\ghidra_12.2_PUBLIC`
(879 MB) is left unused on this PC, awaiting the owner's delete decision.

Startup timeout knob (kept from the earlier FC3 work): `REA_GHIDRA_STARTUP_TIMEOUT_MS=3600000` — the
first pass over `FC3.dll` (40 MB) takes about 10 minutes and the default 330 s start limit fails.
`FC3.dll` has not been analysed with REA on this PC yet.

## Requirements (per REA docs)

From `docs/windows-ghidra-p0.md` (Windows support is **experimental**, read-only):

- Windows 10+ x64, game copy on a local NTFS drive;
- Node.js 22.x (>=22.23.4), 24.x (>=24.22.1) or 26.12.1+;
- Ghidra 12.1.x installed by you (verified with 12.1.4) — REA never installs it;
- 64-bit full JDK 21+ inside Ghidra's declared Java range.

All four are satisfied on this PC (2026-11-03): Windows x64, Node v22.23.4, `C:\tools\ghidra_12.1.4_PUBLIC`,
`C:\tools\jdk-21.0.13+9`. The game copy used for analysis is `H:\FarCryCoop\TestFC3\`.

## Why REA is not registered in this repository's `.mcp.json`

REA's own docs (`docs/installation.md`, "One project") say: avoid `--scope project`, which writes
`.mcp.json` into the repository where it can be committed or copied. On this PC the entry lives in the
agent's user-level config `C:\Users\<user>\.pi\agent\mcp.json` (see the section above); Claude Code's
local scope is not an option here because Claude Code is absent (`where claude` fails, no
`%USERPROFILE%\.claude`, no `%USERPROFILE%\.claude.json`). Analysis is read-only either way.

## History of the previous PC (October 2026, drive E:)

Everything in this section is the record of the owner's previous PC, where the toolchain lived under
`E:\FarCryCoop` (Ghidra 12.1.4, Temurin 21.0.12.1+1, portable Node v24.22.0) and REA was version 6.7.0.
That folder does not exist here: `E:` is a game drive without a `FarCryCoop` folder. Live paths for this
PC are in `AGENTS.md` and `docs/workspace.md`.

Setup steps as they were written there (PowerShell, from the project folder, Claude Code route):

```powershell
Remove-Item Env:CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
claude mcp add --scope local rea -- cmd.exe /d /c npx -y rea-agents@6.7.0 mcp
$env:GHIDRA_INSTALL_DIR = "C:\tools\ghidra_12.1.4_PUBLIC"   # your path
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21"              # your path
npx -y rea-agents@6.7.0 doctor --json
claude mcp list
```

Local scope stored the entry in `%USERPROFILE%\.claude.json` for that folder only and did not install
REA's skill. Remove was `claude mcp remove --scope local rea` from the same folder.
Alternative: `npx rea-agents setup` registers REA for every project (user scope) and installs the skill.

### Registered there on 2026-10-18

Owner approved the one write to `C:\Users\<user>\.claude.json` (local scope, that folder only). All tool
paths pointed to `E:\FarCryCoop`:

```powershell
$R='E:\FarCryCoop'
claude mcp add --scope local rea -e "GHIDRA_INSTALL_DIR=$R\Tools\ghidra_12.1.4_PUBLIC" -e "JAVA_HOME=$R\Tools\jdk-21.0.12.1+1" `
  -e "TEMP=$R\Temp" -e "TMP=$R\Temp" -e "npm_config_cache=$R\Data\npm-cache" `
  -e "XDG_CONFIG_HOME=$R\Data\xdg-config" -e "XDG_CACHE_HOME=$R\Data\xdg-cache" `
  -- cmd.exe /d /c "$R\Tools\node-v24.22.0-win-x64\npx.cmd" -y rea-agents@6.7.0 mcp
```

The server name must come before the `-e` options (`-e` takes several values). `claude mcp get rea`
showed `Connected`; the tools appeared in a new Claude Code session. `rea doctor` there: Ghidra 12.1.4
and JDK 21 healthy; Hopper, IDA, jadx, Kuna not installed (not needed).

### Moved to user scope there on 2026-10-22

Owner decision: one repository per game, so REA was registered for every folder. The local entry was
removed (`claude mcp remove rea -s local`) and the same command was run with `--scope user` instead of
`--scope local`. Same file `C:\Users\<user>\.claude.json`, now its user section; all paths still
pointed to `E:\FarCryCoop`. `claude mcp get rea` from `E:\FarCryCoop\FarCry3Coop`: `Scope: User config`,
`Connected`. Remove would be `claude mcp remove rea -s user`.

## Rules that apply to us

- AGENTS.md golden rule 2 (workspace): analyse only a **copy** of the game folder, never the install.
- REA's `DISCLAIMER.md` says the project does not support "circumventing DRM, license checks,
  anti-cheat systems or other technical protection measures" or "developing game cheats or tampering
  with online services". Same boundary as rule 10 ("Stay fair") in the hub `AGENTS.md`
  (`D:\Projects\Co-op Anything\coop-anything\AGENTS.md`).
- Windows Ghidra P0 is read-only: REA does not change executable bytes.

## Unknown / guess

- Guess, not verified: `FC_m64d3d12.dll` is protected by Denuvo and VMProtect, so static Ghidra
  analysis may show little useful code. Unknown until tried on the game copy.

## Health on this PC (re-checked 2026-11-08)

- `rea doctor --client pi --provider ghidra` -> `healthy: true`, `environment_healthy: true`; node
  `24.22.2` (the `rea` PATH shim; the pi entry pins `C:\Program Files\nodejs\node.exe`, listed in the
  table above as v22.23.4), Ghidra 12.1.4 at `C:\tools\ghidra_12.1.4_PUBLIC`, `analyzeHeadless.bat`
  present, win32/x64.
- `pi mcp list`: `rea: connected, 229 tools (codemode, global)`. Reach through `codemode`
  (`await searchTools("ghidra …")`, `await describeNamespace("mcp__rea")`, or
  `await tools.mcp__rea__<tool>({…})`). The AGENTS.md caution that these tools are "not exposed / fall
  back to scripts" is **resolved**: they are reachable via the codemode gateway; keep the raw Python
  probes in `scripts\` only as a convenience fallback.
