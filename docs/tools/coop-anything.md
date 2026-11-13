# Co-op Anything MCP (`coop-anything`)

Russian version: [coop-anything.ru.md](coop-anything.ru.md)

- Source: `D:\Projects\Co-op Anything\coop-anything\tools\mcp\coop_mcp.py` (part of the hub repo
  `coop-anything`; it reads the repo it lives in, so `git pull` keeps it current).
- What it is: a **read-only** MCP server that gives an agent the hub's shared knowledge (the
  directory of co-op projects, the playbook, the agent skills, the game write-ups, the sync-test
  tool READMEs) plus three local analysis helpers (engine detection, exe identity, entry validation).
- Server info (verified live 2026-11-08): `name: coop-anything`, `version: 0.1.0`,
  `protocolVersion: 2025-06-18`, transport **stdio / JSON-RPC 2.0** (no SDK). It resolves its
  knowledge root to the repo root (`parents[2]` of the script) and refuses any path outside it.
- Needs: **Python 3.9+** and **PyYAML** (`pip install pyyaml`).

## Launch / registration

- Hub project config `coop-anything\.mcp.json` and the **pi** config
  `C:\Users\<user>\.pi\agent\mcp.json` both register it the same way:

  ```json
  "coop-anything": {
    "command": "python",
    "args": ["D:/Projects/Co-op Anything/coop-anything/tools/mcp/coop_mcp.py"]
  }
  ```

- Manual smoke test (no writes): pipe an `initialize` + `tools/list` JSON-RPC pair into
  `python tools/mcp/coop_mcp.py`; it answers with the 9 tools below.

## The 9 tools

| Tool | Required | What it returns | Needs PyYAML |
|---|---|---|---|
| `search_directory` | — (`query,status,qa,engine,limit`) | search the directory of co-op mods/forks/ports/open gaps by game, project, engine, keyword; each entry says what it really syncs, status, QA level | **yes** |
| `detect_engine` | `game_dir` | scan a game install folder **read-only**, identify the engine from file signatures, with evidence, suggested hooking tools, anti-cheat warnings, co-op projects on the same engine | no |
| `game_identity` | `exe_path` | SHA-256, size, architecture, PE details, version resource of an exe, plus Steam app id / build id when in a Steam library | no |
| `list_docs` | — | list playbook pages, game write-ups, agent skills, sync-test tools | no |
| `read_playbook` | `page` | read one playbook page (triage, research, reverse-engineering, tools, how-coop-mods-work, networking, automated-qa, …) or `AGENTS` | no |
| `get_skill` | `name` | read `.agents/skills/<name>/SKILL.md` | no |
| `get_game` | `slug` | read `games/<slug>/README.md` | no |
| `get_test_tool` | `name` | read `tools/<name>/README.md` (chaos, flight, fuzz, ownership, fakeworld, gameslot, gamepool, scenarios, bots, animcheck, bridge, inspect, hotreload, mutants, buildlock) | no |
| `validate_entry` | `entry_yaml` | validate a directory entry (YAML) against the schema before contributing | **yes** |

## Health on this PC (verified 2026-11-08)

- `pi mcp list`: `coop-anything: connected, 9 tools (codemode, global)`. The exposure is **`codemode`**,
  so the tools are **not** in the direct function schema — that is expected, not a failure. Reach them
  through the `codemode` tool: `await ALL_TOOLS`, `await searchTools("…")`,
  `await describeNamespace("mcp__coop_anything")`, or call directly
  `await tools.mcp__coop_anything__list_docs({})`. The tool-name prefix replaces `-` with `_`
  (`mcp__coop_anything__…`, not `mcp__coop-anything__…`).
- **PyYAML was missing** and broke `search_directory` / `validate_entry`. **Fixed 2026-11-08**:
  `pyyaml 6.0.3` installed into `C:\Users\<user>\AppData\Local\Programs\Python\Python311\Lib\site-packages`
  (the interpreter named `python` that the MCP launches). Both now return results — `search_directory`
  → entries, `validate_entry` → `valid: true` (verified through the codemode gateway).
## Rules of use (from the hub)

Read the hub, **do not edit it from this project**. A hub change goes into the hub's own repo following
its `CONTRIBUTING.md`. The server is read-only by design; `validate_entry` only checks YAML, it does
not write.
