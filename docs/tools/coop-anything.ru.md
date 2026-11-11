# Co-op Anything MCP (`coop-anything`)

English version: [coop-anything.md](coop-anything.md)

- Источник: `D:\Projects\Co-op Anything\coop-anything\tools\mcp\coop_mcp.py` (файл хаба
  `coop-anything`; читает тот репозиторий, в котором лежит, поэтому `git pull` держит его актуальным).
- Что это: MCP-сервер **только на чтение**, дающий агенту общие знания хаба (каталог co-op-проектов,
  playbook, агентские навыки, разборы игр, README инструментов проверки синхронизации) плюс три
  локальных анализатора (определение движка, личность exe, проверка записи каталога).
- О сервере (проверено вживую 2026-11-08): `name: coop-anything`, `version: 0.1.0`,
  `protocolVersion: 2025-06-18`, транспорт **stdio / JSON-RPC 2.0** (без SDK). Корень знаний — корень
  репозитория (`parents[2]` от скрипта); пути вне репозитория отклоняются.
- Нужно: **Python 3.9+** и **PyYAML** (`pip install pyyaml`).

## Запуск / регистрация

- Конфиг хаба `coop-anything\.mcp.json` и конфиг **pi** `C:\Users\<user>\.pi\agent\mcp.json`
  регистрируют его одинаково:

  ```json
  "coop-anything": {
    "command": "python",
    "args": ["D:/Projects/Co-op Anything/coop-anything/tools/mcp/coop_mcp.py"]
  }
  ```

- Ручная проверка (без записи): подать в `python tools/mcp/coop_mcp.py` пару JSON-RPC `initialize` +
  `tools/list`; сервер отвечает девятью инструментами ниже.

## Девять инструментов

| Инструмент | Обязательное | Что возвращает | Нужен PyYAML |
|---|---|---|---|
| `search_directory` | — (`query,status,qa,engine,limit`) | поиск по каталогу co-op-модов/форков/портов/свободных ниш по игре, проекту, движку, ключевому слову; каждая запись говорит, что реально синхронизируется, статус, уровень QA | **да** |
| `detect_engine` | `game_dir` | обойти папку установленной игры **только на чтение**, определить движок по сигнатурам файлов, с доказательствами, подсказками по хукам, предупреждениями об анти-чите, co-op-проектами на том же движке | нет |
| `game_identity` | `exe_path` | SHA-256, размер, архитектура, сведения PE, версия exe, плюс Steam app id / build id если в библиотеке Steam | нет |
| `list_docs` | — | список страниц playbook, разборов игр, навыков и инструментов проверки синхронизации | нет |
| `read_playbook` | `page` | прочитать страницу playbook (triage, research, reverse-engineering, tools, how-coop-mods-work, networking, automated-qa, …) или `AGENTS` | нет |
 `get_skill` | `name` | прочитать `.agents/skills/<name>/SKILL.md` | нет |
| `get_game` | `slug` | прочитать `games/<slug>/README.md` | нет |
| `get_test_tool` | `name` | прочитать `tools/<name>/README.md` (chaos, flight, fuzz, ownership, fakeworld, gameslot, gamepool, scenarios, bots, animcheck, bridge, inspect, hotreload, mutants, buildlock) | нет |
| `validate_entry` | `entry_yaml` | проверить запись каталога (YAML) по схеме перед вкладом | **да** |

## Состояние на этом ПК (проверено 2026-11-08)

- `pi mcp list`: `coop-anything: connected, 9 tools (codemode, global)`. Режим подачи — **`codemode`**,
  поэтому инструментов **нет** в прямом наборе функций схемы — это норма, не сбой. Доступ через
  инструмент `codemode`: `await ALL_TOOLS`, `await searchTools("…")`,
  `await describeNamespace("mcp__coop_anything")` или прямой вызов
  `await tools.mcp__coop_anything__list_docs({})`. Префикс имени заменяет `-` на `_`
  (`mcp__coop_anything__…`, а не `mcp__coop-anything__…`).
- **PyYAML отсутствовал** и ломал `search_directory` / `validate_entry`. **Исправлено 2026-11-08**:
  `pyyaml 6.0.3` установлен в `C:\Users\<user>\AppData\Local\Programs\Python\Python311\Lib\site-packages`
  (тот интерпретатор `python`, который запускает MCP). Оба возвращают результат — `search_directory`
  → записи, `validate_entry` → `valid: true` (проверено через шлюз codemode).
## Правила использования (из хаба)

Хаб читать и **не править из этого проекта**. Правку хаба делать в его собственном репозитории по
`CONTRIBUTING.md`. Сервер по замыслу только на чтение; `validate_entry` лишь проверяет YAML, не пишет.
