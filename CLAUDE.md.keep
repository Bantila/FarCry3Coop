# Project rules for Claude / Правила проекта для Claude

## Golden rule / Золотое правило

**EN:** ALWAYS write documentation and every other human-readable project text (README, notes,
guides, comments in docs, issue/PR descriptions) in BOTH Russian and English. No exceptions.
Use a pair of files `NAME.md` (English) + `NAME.ru.md` (Russian), or both languages in one file
for short texts. When one language version changes, update the other in the same commit.

**RU:** ВСЕГДА пиши документацию и любые другие тексты проекта для людей (README, заметки,
руководства, комментарии в документах, описания issue/PR) на ДВУХ языках: русском и английском.
Без исключений. Используй пару файлов `NAME.md` (английский) + `NAME.ru.md` (русский) или оба
языка в одном файле для коротких текстов. Если меняется одна языковая версия, обнови другую в
том же коммите.

## Golden rule 2: workspace / Золотое правило 2: рабочая папка

**EN:** Work ONLY inside `E:\FarCryCoop`. NEVER read, write or download anything on drive C: —
no exceptions. NEVER download into `%TEMP%`. Before running any tool, load `. E:\FarCryCoop\env.ps1`
(it points TEMP/TMP, npm cache, JAVA_HOME, Ghidra to `E:\FarCryCoop`). Layout:
`Downloads\<name>\` — verified archives (one folder each); `Tools\` — unpacked tools;
`Data\` — tool settings and caches; `Temp\` — temporary files. The game install
folder (path in NOTES.md) is read-only (AGENTS.md rule 2); work on copies in
`E:\FarCryCoop\Work`. If a step would need drive C:, stop and ask the owner.

**RU:** Работать ТОЛЬКО внутри `E:\FarCryCoop`. НИКОГДА ничего не читать, не писать и не скачивать
на диск C: — без исключений. НИКОГДА не качать в `%TEMP%`. Перед запуском любых инструментов
загружать `. E:\FarCryCoop\env.ps1` (он направляет TEMP/TMP, кэш npm, JAVA_HOME, Ghidra в
`E:\FarCryCoop`). Структура: `Downloads\<имя>\` — проверенные архивы (у каждого своя папка);
`Tools\` — распакованные инструменты; `Data\` — настройки и кэши инструментов; `Temp\` — временные
файлы. Папка установки игры (путь в NOTES.ru.md) — только чтение (правило 2 AGENTS.md);
работать с копиями в `E:\FarCryCoop\Work`. Если шаг требует диска C:, остановиться и спросить владельца.

## Commits / Коммиты

**EN:** Commit messages follow Conventional Commits (https://www.conventionalcommits.org/en/v1.0.0/)
and are written in English only: `<type>(<optional scope>): <description>`, e.g.
`docs(far-cry-6): add research notes`. Types: feat, fix, docs, chore, refactor, test, build, ci, perf, style, revert.

**RU:** Сообщения коммитов пишутся по Conventional Commits и только на английском:
`<тип>(<область, необязательно>): <описание>`, например `docs(far-cry-6): add research notes`.

## Tools / Инструменты

**EN:** Reverse engineering uses REA (https://github.com/morluto/rea) as an MCP server, registered
locally on the owner's PC: see [docs/tools/rea.md](docs/tools/rea.md).

**RU:** Для реверс-инжиниринга используется REA (https://github.com/morluto/rea) как MCP-сервер,
подключённый локально на ПК владельца: см. [docs/tools/rea.ru.md](docs/tools/rea.ru.md).

## Communication / Общение

**EN:** Chat with the owner in Russian.

**RU:** С владельцем общаться по-русски.

## Repo layout (session 2026-11-02, agent session)

- `NOTES.md` / `NOTES.ru.md` - findings log. Bilingual rule: every documentation pair has an English file and a `.ru.md` mirror (README.md, PLAN.md, NOTES.md, docs/**, scripts/README.md); English is the primary record, the Russian file mirrors it.
- `NOTES.md` section order: the owner's granular Phase 1 sections stay first and are the
  authoritative Phase 1 record; agent-session sections are appended after them with a
  provenance heading. Do not rewrite the owner's Phase 1 text without telling the owner.
- `PLAN.md` / `PLAN.ru.md` — campaign-co-op plan. The owner's version is authoritative;
  the agent's plan lives in the hub repo (`FarCryCoop/games/far-cry-3/PLAN.md`) until the
  owner merges it.
- `scripts/` — analysis scripts, **tracked** (disassembler, xref maps, patchers, build
  helpers). `tools/` — external binaries only (Ghidra, packer), **ignored**. Caches
  (`*_dis_cache.json`) are ignored.
- `local/` — private state (registry backups, scratch scripts), ignored. Scratch files use
  `*.scratch*`, `.scratch*`, `scratch_*`, `local/scratch/`.
- `Temp/` — agent-harness scratch (delegate output, probe scripts), ignored.
- Commits: stage explicit paths only (`git add -A` aborts on this machine with
  `error: invalid path 'NUL'` because of an undeletable `nul` file at the workspace root);
  commit message via `git commit -F .git/COMMIT_MSG.txt`. Commit text is English; keep
  Russian only inside the `.ru.md` files.

## Known environment gaps (owner decision needed, not resolved by the agent)

- Golden rule 2 says everything local lives under `E:\FarCryCoop` with `env.ps1` loaded per
  command. `E:\FarCryCoop` does not exist on this machine and `env.ps1` is not present; the
  repos live under `D:\Projects/Co-op Anything/`, the test copy at `H:\FarCryCoop/TestFC3`.
- The agent harness writes its own temp work to `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp`
  (delegate outputs, sandbox scripts). This contradicts golden rule 2 and is outside the
  agent's control. Flagged, not fixed.
- Carried-over scripts contain stale hardcoded paths (`E:\SteamLibrary\…`,
  `E:\FarCryCoop\Downloads\…`). Fixing them is an owner decision; the agent lists them in
  `NOTES.md` instead of editing silently.
