# Supermemory MCP (`supermemory`)

English version: [supermemory.md](supermemory.md)

- Источник: `D:\supermemory-mcp-local\index.ts`, запускается Bun. Идентификатор клиента
  `supermemory-mcp-local`, `version 1.0.0`.
- Что это: проектная память. AGENTS.md делает её использование **обязательным** (recall перед задачей,
  save при изменении состояния). Это **дополняющий** слой поверх `docs/` и других `*.md` — доки остаются
  источником истины; держать память и доки в sync.
- Тег контейнера проекта: **`FarCry3Coop`**.

## Регистрация (pi)

`C:\Users\<user>\.pi\agent\mcp.json` (API-ключ лежит здесь в env — это секрет, никогда не переносить его
в документ, коммит или PR):

```json
"supermemory": {
  "command": "C:\\Users\\<user>\\.bun\\bin\\bun.exe",
  "args": ["run", "D:\\supermemory-mcp-local\\index.ts"],
  "env": { "SUPERMEMORY_API_KEY": "<ключ>" }
}
```

## Четыре инструмента (проверено вживую 2026-11-08)

| Инструмент | Назначение |
|---|---|
| `memory` | сохранить / перезаписать / забыть память (`action: save|replace|...`, `containerTag: FarCry3Coop`) |
| `recall` | поиск по памяти контейнера (`query`, `containerTag: FarCry3Coop`) |
| `listProjects` | список доступных проектов (контейнеров) |
| `whoAmI` | текущий пользователь (в этой установке отвечает заглушкой `Using local fixed MCP server`, то есть **не** доказывает связь с облаком — это доказывает `recall`) |

## Состояние на этом ПК (проверено 2026-11-08)

- `pi mcp list`: `supermemory: connected, 4 tools (codemode, global)`. Доступ через инструмент
  `codemode`, напр. `await tools.mcp__supermemory__recall({query, containerTag:"FarCry3Coop"})` или
  `await tools.mcp__supermemory__memory({action:"save", …, containerTag:"FarCry3Coop"})`. Передавать
  только собственные поля инструмента: `recall` принимает `query`/`containerTag` (лишнее `limit` падает
  на валидации).
- **`recall`** по `FarCry3Coop` возвращает настоящие актуальные записи, то есть `memory`/`recall` живы
  и связаны с бэкендом supermemory. `whoAmI` отвечает заглушкой `Using local fixed MCP server`, поэтому
  связь с облаком проверяет именно `recall`, а не `whoAmI`.
## Правила использования (из AGENTS.md)

- Делать recall (`FarCry3Coop`) перед началом задачи; сохранять при каждом изменении состояния (новая
  фича/версия, механика, схема, команды, зависимости, деплой, новая проблема/долг).
- Не плодить мелочь — обновлять тематические записи (обзор/стек · архитектура · механики · команды ·
  схема БД · конвенции · проблемы/долг · текущее состояние).
- Если запись устарела — перезаписать (`memory`, `action: replace`, с id записи), а не добавлять рядом.
