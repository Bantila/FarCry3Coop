# context-mode

Russian version: [context-mode.ru.md](context-mode.ru.md)

- What it is: context-mode is a context-window saver for coding agents (sandboxed code execution, FTS5
  search, session continuity). On this PC it is the **pi** in-process extension that provides the `ctx_*`
  tools (`ctx_execute`, `ctx_search`, `ctx_index`, `ctx_doctor`, `ctx_upgrade`, …) and the
  context-management tools (`compress`, `decompress`, `search_context`, `acp_status`).
- Version: 2.1.1 (build sha `2652fe2`) — the latest release, verified 2026-11-05 on this PC.
- Source: https://github.com/mksglu/context-mode (npm package `context-mode`).

## Installed on this PC (verified 2026-11-05)

| Component | State on this PC |
|---|---|
| context-mode | 2.1.1 (`2652fe2`), npm dependency of `pi-extensions` at `%USERPROFILE%\.pi\agent\npm\node_modules\context-mode` |
| pi install mode | `in-process` (adapter `pi`, hook channel `pi/index.js`); not a git-checkout install |
| pi host config | `%USERPROFILE%\.pi\agent\settings.json`, `packages: ["npm:context-mode", "npm:billion-context", "npm:@keenable/pi-search"]` |
| Context-mode data | `%USERPROFILE%\.context-mode\` (`plugins/`, `projects/`, `reports/`, `hook-errors.log`) |
| `context-mode` CLI | **not on PATH** — run via `node %USERPROFILE%\.pi\agent\npm\node_modules\context-mode\cli.mjs …` |
| Latest upstream release | v2.1.1 (published 2026-11-05); only git branch is `main` (no `release` branch); tags `v*` up to v2.1.1 |

`ctx_doctor` (2026-11-05): D1–D11 mostly PASS. Two failures are explained below (D3, D7).

## Status: TRACKING an upstream bug — do NOT run `context-mode setup --agents pi`

**Do not run `context-mode setup --agents pi` (and `ctx_upgrade` is already broken) until upstream fixes the
`release` ref.** Running the setup now would break context-mode on the next pi start.

### Root cause

context-mode 2.1.1 still targets a `release` git ref that upstream removed. The repo now ships only the
`main` branch plus `v*` version tags — there is no `release` branch and no `release` tag.

Verified 2026-11-05:
- `git ls-remote --heads https://github.com/mksglu/context-mode.git` → only `refs/heads/main`.
- `gh api repos/mksglu/context-mode/branches` → `["main"]`.
- `gh api repos/mksglu/context-mode/releases/latest` → tag `v2.1.1`, published 2026-11-05 (== installed).

### Symptom 1 — `ctx_upgrade` fails

`ctx_upgrade` (self-upgrade) runs `fetchRelease`, which does:

```
git clone --depth 1 --branch release https://github.com/mksglu/context-mode.git <fetchdir>
```

It fails with:

```
fatal: Remote branch release not found in upstream origin.
```

Code (context-mode 2.1.1, `server.mjs`): `RELEASE_REPO_URL = "https://github.com/mksglu/context-mode.git"`
(L28408), `RELEASE_BRANCH = "release"` (L28409), `GIT_CLONE_ARGS = ["clone", "--depth", "1", "--branch"]`
(L28589), used in `fetchRelease` (L55597). Because we are already on the latest release (2.1.1) there is
nothing newer to install anyway — but the clone fails first.

### Symptom 2 — D3 host-config "FAIL" is cosmetic, and the "fix" is dangerous

`ctx_doctor` reports **D3 FAIL: wrong entry in `%USERPROFILE%\.pi\agent\settings.json`**. This is a
versioning mismatch, not a functional break: the doctor wants the *modern* git spec in `packages`, but we use
the working *v1* npm spec.

The modern spec in the code is `PI_GIT_PACKAGE = "git:github.com/mksglu/context-mode@release"` (L28707); the
v1 spec is `V1_PI_PACKAGE = "npm:context-mode"` (L28731); key is `PI_PACKAGES_KEY = "packages"` (L28767).
`context-mode setup --agents pi` / `ctx_upgrade`'s `regenerateHostConfig` would replace `npm:context-mode`
with `git:github.com/mksglu/context-mode@release` (keeping `npm:billion-context` and
`npm:@keenable/pi-search`).

Why that would break the next pi start:
- `@release` in the git spec is a git ref (branch/tag) that no longer exists.
- pi loads a git package by cloning and resetting to that ref; on failure it falls back to a cached copy.
- There is **no** git-package cache for context-mode here (`%USERPROFILE%\.pi\agent\tmp\extensions\` is
  empty; the working copy is the npm install at `%USERPROFILE%\.pi\agent\npm\node_modules\context-mode`).
- Result: pi tries to clone `…@release` → ref not found → no cache → **context-mode not loaded → all
  `ctx_*` tools gone.**

### What to do

- **Keep `npm:context-mode`** (v1 entry) — it works; do not switch to the git spec now.
- **Do not run `context-mode setup --agents pi`** until upstream either restores the `release` branch or
  changes `PI_GIT_PACKAGE` to a valid ref (e.g. `@main` or a tag).
- Watch the next context-mode release (≥ 2.1.2) for the fix, then re-run the setup.

### Unrelated open item

- **D7 FAIL** (`pi:ctx.cwd does not match the host's actual cwd`) is a separate session-setup issue — fix by
  restarting pi in the correct working directory. Not related to the `release` bug.

## Reporting

- Upstream tracker: https://github.com/mksglu/context-mode/issues
- Agent issue rules: https://github.com/mksglu/context-mode/blob/main/.github/AGENT_ISSUE.md
