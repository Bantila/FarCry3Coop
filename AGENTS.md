# Project rules for the coding agent / Правила проекта для кодинг-агента

Canonical instruction file. The agent harness (Pi) auto-loads `AGENTS.md` from the working

directory and from every parent directory, and reads candidates in this order:

`AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, `CLAUDE.MD`. So this file is read

by the agent automatically in every session; `CLAUDE.md` in this repo is only a pointer to it.

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

**EN:** Work only inside the paths listed in "Workspace on this PC" below. NEVER read, write or

download anything on drive C: — no exceptions. NEVER download into `%TEMP%`. Never modify a game

install (`H:\Uplay\Far Cry 3\` is read-only); work on the copy `H:\FarCryCoop\TestFC3\`. Scratch

files go to ignored locations only (`local/scratch/`, `Temp/`, `*.scratch*`). If a step needs

drive C:, stop and ask the owner. Scratch notes, scratch scripts and scratch summaries are written in English only (Russian is reserved for the shipped bilingual files `NOTES.md`/`NOTES.ru.md` and commit messages) — mixed-language scratch text costs review time. One deviation is unavoidable and already accepted by the owner:

the agent harness writes its own temp files and delegate output under

`C:\Users\<user>\AppData\Roaming\pi-desktop\` — flagged, not fixed, see docs/workspace.md.

**RU:** Работать только в путях из раздела «Рабочая папка на этом ПК» ниже. НИКОГДА ничего не

читать, не писать и не скачивать на диск C: — без исключений. НИКОГДА не качать в `%TEMP%`.

Игровую установку не изменять (`H:\Uplay\Far Cry 3\` — только чтение); работать с копией

`H:\FarCryCoop\TestFC3\`. Черновые файлы — только в папках вне git (`local/scratch/`, `Temp/`,
`*.scratch*`). Если шаг требует диска C:, остановиться и спросить владельца. Черновые заметки, черновые скрипты и черновые выжимки — только на английском (русский только для поставляемых двуязычных файлов `NOTES.md`/`NOTES.ru.md` и сообщений коммита) — смешанный язык в черновниках тратит время на просмотр Одно отклонение

неустранимо и принято владельцем: агентская программа пишет свои временные файлы и выводы

делегатов в `C:\Users\<user>\AppData\Roaming\pi-desktop\` — отмечено, не исправлено, см.
docs/workspace.md.

## Commits / Коммиты

**EN:** Commit messages follow Conventional Commits (https://www.conventionalcommits.org/en/v1.0.0/)

and are written in English only: `<type>(<optional scope>): <description>`, e.g.

`docs(far-cry-6): add research notes`. Types: feat, fix, docs, chore, refactor, test, build, ci, perf, style, revert.

**RU:** Сообщения коммитов пишутся по Conventional Commits и только на английском:

`<тип>(<область, необязательно>): <описание>`, например `docs(far-cry-6): add research notes`.

## Tools / Инструменты

**EN:** Reverse engineering uses REA (https://github.com/morluto/rea) as an MCP server, version 6.8.0,
installed on this PC (npm global `rea-agents`) and registered for the **pi** agent in
`C:\Users\<user>\.pi\agent\mcp.json`: see [docs/tools/rea.md](docs/tools/rea.md). The `coop-anything` and `supermemory` MCP servers are registered in the same file: see [docs/tools/coop-anything.md](docs/tools/coop-anything.md) and [docs/tools/supermemory.md](docs/tools/supermemory.md). Ghidra 12.1.4
(`C:\tools\ghidra_12.1.4_PUBLIC`) and Temurin JDK 21.0.13+9 (`C:\tools\jdk-21.0.13+9`) are present;
Claude Code is not installed here. The Python scripts in `scripts/` stay the fallback for read-only probes.
`rea doctor --client pi --provider ghidra` reports healthy (verified 2026-11-03).

**RU:** Для реверс-инжиниринга используется REA (https://github.com/morluto/rea) как MCP-сервер,
версия 6.8.0: установлен на этом ПК (глобальный npm пакет `rea-agents`) и прописан для агента **pi** в
`C:\Users\<user>\.pi\agent\mcp.json`: см. [docs/tools/rea.ru.md](docs/tools/rea.ru.md). Серверы MCP `coop-anything` и `supermemory` зарегистрированы в том же файле: см. [docs/tools/coop-anything.ru.md](docs/tools/coop-anything.ru.md) и [docs/tools/supermemory.ru.md](docs/tools/supermemory.ru.md).

На этом ПК есть Ghidra 12.1.4 (`C:\tools\ghidra_12.1.4_PUBLIC`) и Temurin JDK 21.0.13+9
(`C:\tools\jdk-21.0.13+9`); Claude Code отсутствует. Скрипты из `scripts/` остаются запасным
средством для зондов только на чтение. `rea doctor --client pi --provider ghidra` сообщает, что всё
в порядке (проверено 2026-11-03).

## Hub tools and documents / Инструменты и документы хаба

**EN:** `D:\Projects\Co-op Anything\coop-anything\` is a **source of tools and documents for this
project**, not only the issue tracker. Look there before writing a new tool or writing a claim about
the game:

- `playbook/` (33 guides): methodology `methods.md`, `research.md`, `triage.md`, `lessons.md`;
  architecture `how-coop-mods-work.md`, `engine-families.md`, `effect-capture-story-sync.md`;
  reverse engineering `reverse-engineering.md`, `decomp-and-recomp.md`, `patching-a-closed-mod-exe.md`;
  networking `networking.md`, `networking-steam-spacewar.md`, `in-game-bridge.md`; testing
  `multi-instance-testing.md`, `automated-qa.md`, `network-chaos-testing.md`, `fuzzing-coop-sync.md`,
  `desync-hunting.md`, `actor-ownership.md`, `animation-sync-checks.md`, `fake-world-testing.md`,
  `bots-and-playbooks.md`, `hot-reloading-your-mod.md`, `fast-iteration.md`; plus
  `shipping-to-players.md`, `split-screen.md`, `console-emulators.md`, `switch.md`, `mcp.md`,
  `tools.md`.
- `tools/` (game-agnostic sync test tools): `chaos`, `flight`, `fuzz`, `ownership`, `fakeworld`,
  `gameslot`, `gamepool`, `scenarios`, `bots`, `bridge`, `inspect`, `hotreload`, `mutants`,
  `buildlock`, `animcheck`, plus the hub's own `build_directory.py` and `mcp/`. Each tool runs its own
  tests with `python -I tools/<name>/run_tests.py` and prints `ALL OK`; `python -I tools/test_all.py`
  runs them all. `tools/README.md` says what each tool checks.
- `.agents/skills/` and `.claude/skills/` (13 skills): `coop-triage`, `coop-research`,
  `coop-reverse-engineer`, `coop-build-from-zero`, `coop-networking`, `coop-sync-testing`, `coop-qa`,
  `coop-revive`, `coop-decomp-port`, `coop-console-emulator`, `coop-switch`, `coop-contribute`,
  `triage-contributions`. Read the `SKILL.md` that matches the task.
- `games/far-cry-3/README.md` — the published Far Cry 3 entry (game identity, 1.05 and 1.06 SHA-256
  hashes, the known co-op attempts, QA level); `games/far-cry/` and `games/far-cry-2/` are the siblings
  that already have co-op. Also `data/directory.yaml` + `data/SCHEMA.md`, `DIRECTORY.md`,
  `templates/game.md`, `research/reference-repos.md`.
- The MCP server `coop_anything` (`search_directory`, `detect_engine`, `game_identity`, `list_docs`,
  `read_playbook`, `get_skill`, `get_game`, `get_test_tool`, `validate_entry`) queries the hub
  read-only.

Read the hub, do not edit it from this project: a hub change goes into the hub's own repo following its
`CONTRIBUTING.md`. The hub's own `AGENTS.md` rules apply here as well: ask before installing or
downloading anything, never touch the owner's game install or saves, verify before claiming, record the
game identity before following someone else's notes, and never put private paths or names in a pull
request.

**RU:** `D:\Projects\Co-op Anything\coop-anything\` — это **источник инструментов и документов для
этого проекта**, а не только трекер задач. Обращаться к нему раньше, чем писать новый инструмент или
формулировать утверждение об игре:

- `playbook/` (33 руководства): методология (`methods.md`, `research.md`, `triage.md`, `lessons.md`);
  устройство (`how-coop-mods-work.md`, `engine-families.md`, `effect-capture-story-sync.md`);
  реверс-инжиниринг (`reverse-engineering.md`, `decomp-and-recomp.md`, `patching-a-closed-mod-exe.md`);
  сеть (`networking.md`, `networking-steam-spacewar.md`, `in-game-bridge.md`); тестирование
  (`multi-instance-testing.md`, `automated-qa.md`, `network-chaos-testing.md`, `fuzzing-coop-sync.md`,
  `desync-hunting.md`, `actor-ownership.md`, `animation-sync-checks.md`, `fake-world-testing.md`,
  `bots-and-playbooks.md`, `hot-reloading-your-mod.md`, `fast-iteration.md`); плюс
  `shipping-to-players.md`, `split-screen.md`, `console-emulators.md`, `switch.md`, `mcp.md`,
  `tools.md`.
- `tools/` (универсальные инструменты проверки синхронизации): `chaos`, `flight`, `fuzz`, `ownership`,
  `fakeworld`, `gameslot`, `gamepool`, `scenarios`, `bots`, `bridge`, `inspect`, `hotreload`,
  `mutants`, `buildlock`, `animcheck`, плюс собственные инструменты хаба `build_directory.py` и
  `mcp/`. Тесты каждого: `python -I tools/<name>/run_tests.py` (успех — строка `ALL OK`);
  `python -I tools/test_all.py` запускает их все. `tools/README.md` описывает, что проверяет каждый
  инструмент.
- `.agents/skills/` и `.claude/skills/` (13 навыков): `coop-triage`, `coop-research`,
  `coop-reverse-engineer`, `coop-build-from-zero`, `coop-networking`, `coop-sync-testing`, `coop-qa`,
  `coop-revive`, `coop-decomp-port`, `coop-console-emulator`, `coop-switch`, `coop-contribute`,
  `triage-contributions`. Если задача подходит под навык, прочитать его `SKILL.md`.
- `games/far-cry-3/README.md` — опубликованная запись Far Cry 3 (личность игры, SHA-256 хеши версий
  1.05 и 1.06, известные попытки co-op, уровень проверки качества); `games/far-cry/` и
  `games/far-cry-2/` — соседи, у которых co-op уже есть. Ещё `data/directory.yaml` + `data/SCHEMA.md`,
  `DIRECTORY.md`, `templates/game.md`, `research/reference-repos.md`.
- MCP-сервер `coop_anything` (`search_directory`, `detect_engine`, `game_identity`, `list_docs`,
  `read_playbook`, `get_skill`, `get_game`, `get_test_tool`, `validate_entry`) обращается к хабу только
  на чтение.

Хаб читать, а не править из этого проекта: правку хаба делать в его собственном репозитории по правилам
его `CONTRIBUTING.md`. Правила из `AGENTS.md` самого хаба действуют и здесь: спросить перед установкой
или скачиванием, не трогать папку установленной игры и сохранения владельца, проверить прежде чем
утверждать, записать личность игры прежде чем следовать чужим заметкам, и не помещать личные пути или
имена в pull request.

## Communication / Общение

**EN:** Chat with the owner in Russian.

**RU:** С владельцем общаться по-русски.

## Session mechanics / Механика сессии

**EN:** Tool calls: one tool block per turn, one tool name per block, arguments under ~4 KB. Never

paste a long script into a tool call: write it to a file and run `python -I scripts/<name>.py`.

Read files by line ranges, not whole.

Concretely: `Read(offset=42, limit=30, path="<file>")`; to jump to a region, `grep -n <pattern> <file>`
first, then read from that line number.

Model requests: launch ONE model-facing request at a time (sub-agent, web search, source check) and

wait for its result before starting the next one — model requests are processed sequentially.

Owner rules are never rewritten by the agent silently: report the gap and let the owner decide.

**NEVER invent a tool, command or program name.** Call only the tools this session actually declares; if a capability is not declared, say so and use a declared alternative — a guessed tool name burns the turn and produces nothing.

**NEVER write tool-call markup as message text.** A `tool_call`/`parameter` block typed into the reply (instead of a real tool call) is a lost turn. One real tool call per tool used.

Shell surface on this session: the plain shell tool is not available (`Shell not available: unavailable in this session`). Shell commands run through `ctx_execute` with `language: "shell"`, and that shell is **PowerShell, not bash** — `cd a && b`, `$(…)`-substitutions and bash-isms fail with `InvalidEndOfLine`. Chain with `;`, quote Windows paths, or prefer `language: "javascript"` / `"python"`.

`ctx_execute` / `ctx_execute_file` `timeout` is taken as **milliseconds** here (`timeout: 60` → 60 ms → the run dies before the shell even starts). Omit it, or pass a large value (`120000`).

**RU:** Вызовы инструментов: один блок на ход, один инструмент в блоке, аргументы не больше

~4 КБ. Длинные probe-скрипты писать в файл и запускать короткой командой

(`python -I scripts/<имя>.py`), не вставлять код в вызов; читать файлы частями по номерам

строк, не целиком. Пример записи: `Read(offset=42, limit=30, path="<файл>")`; чтобы найти область,
сначала `grep -n <шаблон> <файл>`, потом читать от найденного номера строки.

Запросы к модели: запускать ОДИН запрос к модели за раз (суб-агент, веб-поиск, проверка

источников) и ждать его результат перед следующим — запросы к модели обрабатываются

последовательно. Правила владельца не переписывать молча: сообщать о расхождении и решать

владельцу.

**НИКОГДА не выдумывать имена инструментов, команд и программ.** Вызывать только те инструменты,
которые реально объявлены в сессии; если нужной возможности нет — сообщить и использовать объявленную
альтернативу. Выдуманное имя сжигает ход и даёт пустой результат.

**НИКОГДА не печатать разметку вызова инструмента как текст сообщения.** Блок вида `tool_call` /
`parameter`, набранный в ответе вместо настоящего вызова, — потерянный ход. Один настоящий вызов на
один использованный инструмент.

Оболочка в этой сессии: обычный shell-инструмент недоступен (`Shell not available: unavailable in
this session`). Команды выполнять через `ctx_execute` с `language: "shell"`, и этот shell —
**PowerShell, а не bash**: `cd a && b`, подстановки `$(…)` и прочие bash-измы падают с
`InvalidEndOfLine`. Цеплять через `;`, кавычить виндовые пути, либо использовать
`language: "javascript"` / `"python"`.

Параметр `timeout` у `ctx_execute` / `ctx_execute_file` здесь понимается как **миллисекунды**
(`timeout: 60` → 60 мс → процесс умирает до запуска оболочки). Либо не указывать его, либо давать
большое значение (`120000`).

MCP tool calls in this session may fail silently: the tool result comes back as a rendered
`<tool_call>…<tool_call>` block — the same markup the rule above forbids printing.
Status 2026-11-08: both namespaces verified live — `mcp__rea__*` (`rea doctor --client pi --provider
ghidra` healthy; a real `current_document` round-trip returned structured JSON) and
`mcp__supermemory__*` (a real `memory` save landed in FarCry3Coop, id 3WTpQLTSaHNZujpZT6RQAi),
so neither is assumed broken any more — but the failure mode was seen in earlier sessions, so both
stay under watch: if a call returns the echoed markup, do not retry it (it burns a turn and produces
nothing), report it to the owner, and use the declared alternative — for reverse engineering the
read-only Python probes in `scripts/` (capstone + raw FC3.dll), for project memory the repo's own
documents (`NOTES.md`, `PLAN.md`, `docs/`).

**Clarification 2026-11-08 (mechanism, not a failure):** all three MCP servers are registered with
`exposure=codemode`, so their tools are intentionally **not** in the direct function schema — reach
them through the `codemode` tool (`ALL_TOOLS`, `searchTools(query)`, `describeNamespace(name)`, or
`tools.mcp__<server>__<tool>({...})`; the prefix uses `_`, e.g. `mcp__coop_anything__list_docs`).
`pi mcp list` shows coop-anything, supermemory and rea all connected. Do not read their absence from
the schema as "MCP is broken". Details in `docs/tools/coop-anything.md`, `docs/tools/supermemory.md`,
`docs/tools/rea.md`.

**RU:** Вызовы MCP-инструментов в этой сессии могут молча падать: вместо результата приходит
отрендеренный блок `<tool_call>…<tool_call>` — та самая разметка, которую правило выше
запрещает печатать. Статус на 2026-11-08: оба пространства имён проверены живым вызовом —
`mcp__rea__*` (`rea doctor --client pi --provider ghidra` здоров; настоящий round-trip
`current_document` вернул структурированный JSON) и `mcp__supermemory__*` (настоящий save
через `memory` сохранился в FarCry3Coop, id 3WTpQLTSaHNZujpZT6RQAi), поэтому ни одно из них
больше не считается сломанным — но режим сбоя наблюдался в прошлых сессиях, за обоими следим:
если вызов вернёт эхо-разметку, повторно его не звать (он сжигает ход и ничего не даёт),
сообщить владельцу и использовать объявленную альтернативу — для реверс-инжиниринга черновые
Python-зонды из `scripts/` (capstone и сырой FC3.dll), для проектной памяти документы самого
репозитория (`NOTES.md`, `PLAN.md`, `docs/`).

**Уточнение 2026-11-08 (механизм, а не сбой):** все три MCP-сервера зарегистрированы с
`exposure=codemode`, поэтому их инструменты намеренно **не** в прямом наборе функций схемы — доступ
через инструмент `codemode` (`ALL_TOOLS`, `searchTools(query)`, `describeNamespace(name)` или
`tools.mcp__<server>__<tool>({...})`; префикс через `_`, напр. `mcp__coop_anything__list_docs`).
`pi mcp list` показывает, что coop-anything, supermemory и rea подключены. Не считать их отсутствие в
схеме признаком «MCP сломан». Подробности в `docs/tools/coop-anything.md`, `docs/tools/supermemory.md`,
`docs/tools/rea.md`.

## Repo layout / Раскладка репозитория

- `NOTES.md` / `NOTES.ru.md` — findings log. The owner's granular Phase 1 sections stay first and

  are the authoritative Phase 1 record; agent-session sections are appended after them with a

  provenance heading. Do not rewrite the owner's Phase 1 text without telling the owner.

- `PLAN.md` / `PLAN.ru.md` — campaign-co-op plan. The owner's version is authoritative; the agent's

  plan lives in the hub clone (`D:\Projects\Co-op Anything\FarCryCoop\games\far-cry-3\PLAN.md`)

  until the owner merges it.

- `scripts/` — analysis scripts, tracked, indexed in `scripts/README.md` + `scripts/README.ru.md`.

  `tools/` — external binaries only (Ghidra, packer), ignored. Caches (`*_dis_cache.json`) ignored.

- `local/` — private state, never committed: `local/scratch/` (one-off drafts, Russian text fragments,
  commit-message files) and `local/archive/` (82 carried-over evidence files + `MANIFEST.md`, copied

  from the hub clone `FarCryCoop/Temp`, `FarCryCoop/local/scratch` and the scratch folder

  `H:\FarCryCoop`). The archive is a read-only record: do not edit it, read `local/archive/MANIFEST.md`

  to find an artifact.

- Remotes: `upstream` = https://github.com/Bantila/FarCry3Coop, `origin` = the agent fork

  https://github.com/peperonid/FarCry3Coop, `hub` = https://github.com/peperonid/FarCryCoop.

- Branch `backup` is the owner's own pre-append snapshot of `main`. Never delete, never sync, never

  merge into it.

- Stage explicit paths only: `git add -A` aborts on this machine with `error: invalid path 'NUL'`

  (undeletable file `D:\Projects\Co-op Anything\nul`). Commit message via `git commit -F

  .git/COMMIT_MSG.txt`. Commit text is English; Russian text lives only in `.ru.md` files.

## Workspace on this PC / Рабочая папка на этом ПК

| Path | Role |
|---|---|
| `D:\Projects\Co-op Anything\FarCry3Coop-bantila\` | This repo (agent fork of Bantila/FarCry3Coop) |
| `D:\Projects\Co-op Anything\FarCryCoop\` | Multi-game hub clone (per-game notes under `games/<slug>/`) |
| `D:\Projects\Co-op Anything\coop-anything\` | Upstream hub repo (issue tracker, playbook, tools, skills) |
| `H:\Uplay\Far Cry 3\` | Real Uplay 1.06 install — read-only (golden rule 2) |
| `H:\FarCryCoop\TestFC3\` | Working copy of the 1.06 build: disassembly probes, menu runs, test mods |
| `H:\FarCryCoop\` | Scratch working folder (not a git repo): `TOOLS.md`, screenshots, UI-automation helpers, `tools\fc3_stub_probe.py` |
| `D:\Projects\Co-op Anything\FarCryCoop\tools\`, `...\games\far-cry-3\tools\` | Superseded copies of the FC3 analysis scripts; this repo's `scripts\` is the canonical set |
| `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp\` | Agent harness temp (unavoidable, see golden rule 2) |
Every `E:\FarCryCoop\...` and `E:\SteamLibrary\...` path in this repo is the original layout of

the owner's previous PC (October 2026, drive `E:`). On this PC drive `E:` is a game drive and has no

`FarCryCoop` folder. Docs and script headers were retargeted to this table on 2026-11-02; the

historical record of what was found stays unchanged.

## Mandatory use of Supermemory (MCP) / Работа с Supermemory (MCP) обязательна

**EN:** Project memory lives in the **supermemory MCP** (container tag: `FarCry3Coop`). It is a
**supplementary** layer over `docs/` and the other `*.md` documents (docs remain the source of truth —
keep docs and memory in sync).

- **Before a task:** run `recall` (query about the feature/module in scope, `containerTag: FarCry3Coop`)
  to restore context fast: stack, architecture, mechanics, DB schema, conventions, known problems,
  current version.
- **During / at the end:** when project state changes (new feature/version, mechanics change, DB
  schema, commands, dependencies, deploy, new problem or debt) **save** the current facts with the
  `memory` tool (action `save`, `containerTag: FarCry3Coop`). Do not pile up micro-entries — update
  the themed records (overview/stack · architecture · mechanics · commands · DB schema ·
  conventions · problems/debt · current state).
- If a record is outdated (version, server or mechanics changed) — **overwrite** it (`memory` action
  `replace` with the record id), do not add a new one next to the stale one.

Goal: any agent, following `AGENTS.md → supermemory (recall) → docs`, instantly understands the state
of the project without re-reading all the docs.

**RU:**

## ⚠️ Обязательное использование Supermemory (MCP)
Проектная память живёт в **supermemory MCP** (тег/контейнер проекта: `FarCry3Coop`).
Это **дополняющий** слой поверх `docs/` и других документов `*.md` (доки остаются источником истины —
держать их и память в sync).

- **Начало работы:** перед стартом задачи делать **`recall`** по supermemory (запрос по тематике
  фичи/модуля, `containerTag: FarCry3Coop`) — чтобы восстановить контекст: стек, архитектуру,
  механики, схему БД, конвенции, известные проблемы, текущую версию.
- **По ходу / по завершении:** при изменении состояния проекта (новая фича/версия, смена
  механики, схемы БД, команд, зависимостей, деплой, новая проблема/долг) **сохранять**
  актуальные сведения в supermemory (**`save`**, `containerTag: FarCry3Coop`). Не плодить
  мелочь — обновлять тематические записи (обзор/стек · архитектура · механики · команды ·
  схема БД · PRNG/кубики · конвенции · проблемы/долг · текущее состояние).
- Если в памяти устарело (изменилась версия, сервер, механика) — **перезаписать** запись, а не
  добавлять рядом старое.

Цель: любой агент по `AGENTS.md → supermemory (recall) → docs` мгновенно понимает
состояние проекта, даже без полного перечитывания доков.

## Read first in every session / Что читать в начале сессии

**EN:** `NOTES.md` (findings log, including the TODO list at the end), `PLAN.md`, `scripts/README.md`,
`AGENTS.md`. Do not re-derive a finding that is already written in `NOTES.md`. When the task is
about testing, networking, sync tools, or packaging, also read the hub's `playbook/` and its
`tools/README.md`.

**RU:** `NOTES.md` (журнал находок, список TODO в конце), `PLAN.md`, `scripts/README.md`,
`AGENTS.md`. Не заново выводить то, что уже записано в `NOTES.md`. Если задача про тестирование,
сеть, инструменты синхронизации или сборку — читать и хабовский `playbook/` с `tools/README.md`.

## Tooling gotchas on this machine / Особенности инструментов на этом ПК

**EN:**

- `ctx_*` tools run under PowerShell: `&&` and `||` are parser errors, `>` writes UTF-16,
  `2>/dev/null` creates `D:\dev\null`. Multi-command work goes through bash.

- The edit tool corrupts Cyrillic text. Write Russian text with a bash heredoc plus a Python splice.

- Console output on this machine is cp1251: print Cyrillic with
  `sys.stdout.buffer.write(...encode('utf-8'))`.
- Run Python inside game folders as `python -I`: the game folder ships `python3.dll`, which
  otherwise breaks `python.exe`.
- `gh api --jq` does not accept expressions containing `(`; pass JSON through `python -c`, and
  decode PowerShell dumps as UTF-16.
- In a bash heredoc a backslash inside Python string literals gets mangled: build it with
  `chr(92)`.
- MCP tools can fail silently: the tool result comes back as a literal `<tool_call>…</…>` text
  block instead of a real result. That is a FAILED call, not a success — do not treat the echoed
  markup as the tool having done anything, and do not retry it in a loop. Status 2026-11-08: both
  `mcp__rea__*` (`rea doctor` healthy + a real tool round-trip) and `mcp__supermemory__*` (a real
  `memory` save landed) verified working — treated as working but under watch. On a call that
  returns echoed markup, fall back to the read-only Python probes in `scripts/` + `local/scratch/`
  (capstone over the raw FC3.dll) and to `NOTES.md`/`docs/`, and report the failure to the owner.

