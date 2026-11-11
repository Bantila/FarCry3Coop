# Supermemory MCP (`supermemory`)

Russian version: [supermemory.ru.md](supermemory.ru.md)

- Source: `D:\supermemory-mcp-local\index.ts`, run by Bun. Client id `supermemory-mcp-local`,
  `version 1.0.0`.
- What it is: project memory. AGENTS.md makes its use **mandatory** (recall before a task, save when
  project state changes). It is a **supplementary** layer over `docs/` and the `*.md` documents — docs
  stay the source of truth; keep memory and docs in sync.
- Project container tag: **`FarCry3Coop`**.

## Registration (pi)

`C:\Users\<user>\.pi\agent\mcp.json` (the API key is stored here as an env value — it is a secret,
never copy it into a doc, commit, or PR):

```json
"supermemory": {
  "command": "C:\\Users\\<user>\\.bun\\bin\\bun.exe",
  "args": ["run", "D:\\supermemory-mcp-local\\index.ts"],
  "env": { "SUPERMEMORY_API_KEY": "<the key>" }
}
```

## The 4 tools (verified live 2026-11-08)

| Tool | Purpose |
|---|---|
| `memory` | save / overwrite / forget a memory (`action: save|replace|...`, `containerTag: FarCry3Coop`) |
| `recall` | search the memory for this container (`query`, `containerTag: FarCry3Coop`) |
| `listProjects` | list available projects (containers) |
| `whoAmI` | current logged-in user (in this install it answers with a stub note `Using local fixed MCP server`, so it does **not** prove cloud connectivity — `recall` does) |

## Health on this PC (verified 2026-11-08)

- `pi mcp list`: `supermemory: connected, 4 tools (codemode, global)`. Reach it through the `codemode`
  tool, e.g. `await tools.mcp__supermemory__recall({query, containerTag:"FarCry3Coop"})` or
  `await tools.mcp__supermemory__memory({action:"save", …, containerTag:"FarCry3Coop"})`. Pass only the
  tool's own fields: `recall` takes `query`/`containerTag` (an extra `limit` fails validation).
- A **`recall`** for `FarCry3Coop` returns real, current entries, so `memory`/`recall` are live against
  the supermemory backend. `whoAmI` answers with a stub note `Using local fixed MCP server`, so it does
  **not** prove connectivity — `recall` does.
## Rules of use (from AGENTS.md)

- Recall (`FarCry3Coop`) before starting a task; save on every state change (new feature/version,
  mechanics, schema, commands, dependencies, deploy, new problem/debt).
- Do not pile up micro-entries — update the themed records (overview/stack · architecture · mechanics
  · commands · DB schema · conventions · problems/debt · current state).
- If a record is stale, overwrite it (`memory`, `action: replace`, with the record id) — do not add a
  new one beside it.
