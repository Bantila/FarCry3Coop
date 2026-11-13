# context-mode

Английская версия: [context-mode.md](context-mode.md)

- Что это: context-mode — сберегатель контекстного окна для кодинг-агентов (песочное исполнение кода,
  поиск FTS5, непрерывность сессии). На этом ПК это **in-process** расширение **pi**, которое предоставляет
  инструменты `ctx_*` (`ctx_execute`, `ctx_search`, `ctx_index`, `ctx_doctor`, `ctx_upgrade`, …) и инструменты
  управления контекстом (`compress`, `decompress`, `search_context`, `acp_status`).
- Версия: 2.1.1 (sha сборки `2652fe2`) — самый свежий релиз, проверено 2026-11-05 на этом ПК.
- Источник: https://github.com/mksglu/context-mode (npm-пакет `context-mode`).

## Установлено на этом ПК (проверено 2026-11-05)

| Компонент | Состояние на этом ПК |
|---|---|
| context-mode | 2.1.1 (`2652fe2`), npm-зависимость `pi-extensions` в `%USERPROFILE%\.pi\agent\npm\node_modules\context-mode` |
| Режим установки pi | `in-process` (адаптер `pi`, канал хука `pi/index.js`); не git-выгрузка |
| Конфиг хоста pi | `%USERPROFILE%\.pi\agent\settings.json`, `packages: ["npm:context-mode", "npm:billion-context", "npm:@keenable/pi-search"]` |
| Данные context-mode | `%USERPROFILE%\.context-mode\` (`plugins/`, `projects/`, `reports/`, `hook-errors.log`) |
| CLI `context-mode` | **нет в PATH** — запускать через `node %USERPROFILE%\.pi\agent\npm\node_modules\context-mode\cli.mjs …` |
| Самый свежий релиз upstream | v2.1.1 (опубликован 2026-11-05); единственная git-ветка `main` (ветки `release` нет); теги `v*` до v2.1.1 |

`ctx_doctor` (2026-11-05): D1–D11 в основном PASS. Два сбоя разобраны ниже (D3, D7).

## Статус: отслеживаем баг в upstream — НЕ запускать `context-mode setup --agents pi`

**Не запускать `context-mode setup --agents pi` (и `ctx_upgrade` уже сломан), пока upstream не исправит
git-ref `release`.** Запуск setup сейчас сломает context-mode при следующем старте pi.

### Корневая причина

context-mode 2.1.1 по-прежнему ссылается на git-ref `release`, который upstream удалил. В репозитории теперь
только ветка `main` плюс теги версий `v*` — ни ветки `release`, ни тега `release` нет.

Проверено 2026-11-05:
- `git ls-remote --heads https://github.com/mksglu/context-mode.git` → только `refs/heads/main`.
- `gh api repos/mksglu/context-mode/branches` → `["main"]`.
- `gh api repos/mksglu/context-mode/releases/latest` → тег `v2.1.1`, опубликован 2026-11-05 (== установленная).

### Симптом 1 — `ctx_upgrade` падает

`ctx_upgrade` (самообновление) запускает `fetchRelease`, который делает:

```
git clone --depth 1 --branch release https://github.com/mksglu/context-mode.git <fetchdir>
```

Он падает с ошибкой:

```
fatal: Remote branch release not found in upstream origin.
```

Код (context-mode 2.1.1, `server.mjs`): `RELEASE_REPO_URL = "https://github.com/mksglu/context-mode.git"`
(L28408), `RELEASE_BRANCH = "release"` (L28409), `GIT_CLONE_ARGS = ["clone", "--depth", "1", "--branch"]`
(L28589), используется в `fetchRelease` (L55597). Поскольку у нас уже самый свежий релиз (2.1.1), обновлять
всё равно нечего — но клон падает первым.

### Симптом 2 — D3 «FAIL» в хост-конфиге: косметический, а «исправление» опасно

`ctx_doctor` сообщает **D3 FAIL: wrong entry in `%USERPROFILE%\.pi\agent\settings.json`**. Это расхождение
версионирования, а не функциональный сбой: doctor ожидает *современную* git-спецификацию в `packages`, а мы
используем рабочую *v1* npm-спецификацию.

Современная спецификация в коде: `PI_GIT_PACKAGE = "git:github.com/mksglu/context-mode@release"` (L28707);
v1-спецификация: `V1_PI_PACKAGE = "npm:context-mode"` (L28731); ключ: `PI_PACKAGES_KEY = "packages"` (L28767).
`context-mode setup --agents pi` / `regenerateHostConfig` из `ctx_upgrade` заменили бы `npm:context-mode`
на `git:github.com/mksglu/context-mode@release` (сохранив `npm:billion-context` и `npm:@keenable/pi-search`).

Почему это сломает следующий старт pi:
- `@release` в git-спецификации — это git-ref (ветка/тег), которого больше нет.
- pi грузит git-пакет клонированием и сбросом на этот ref; при неудаче — с кэшированной копии.
- Кэша git-пакета для context-mode здесь **нет** (`%USERPROFILE%\.pi\agent\tmp\extensions\` пуст; рабочая
  копия — npm-установка в `%USERPROFILE%\.pi\agent\npm\node_modules\context-mode`).
- Итог: pi попытается клонировать `…@release` → ref не найден → нет кэша → **context-mode не загружен → все
  инструменты `ctx_*` исчезают.**

### Что делать

- **Оставить `npm:context-mode`** (v1-запись) — она работает; пока не переключаться на git-спецификацию.
- **Не запускать `context-mode setup --agents pi`**, пока upstream либо не восстановит ветку `release`, либо
  не поменяет `PI_GIT_PACKAGE` на валидный ref (например, `@main` или тег).
- Следить за следующим релизом context-mode (≥ 2.1.2) в поисках фикса, затем повторно запустить setup.

### Отдельный открытый пункт

- **D7 FAIL** (`pi:ctx.cwd does not match the host's actual cwd`) — отдельная проблема настройки сессии;
  лечится перезапуском pi в правильной рабочей директории. К багу `release` не относится.

## Отчёт

- Трекер upstream: https://github.com/mksglu/context-mode/issues
- Правила issue для агентов: https://github.com/mksglu/context-mode/blob/main/.github/AGENT_ISSUE.md
