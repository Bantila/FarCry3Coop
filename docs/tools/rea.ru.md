# REA (Reverse Engineer Anything)

English version: [rea.md](rea.md)

- Репозиторий: https://github.com/morluto/rea (MIT). Пакет npm: `rea-agents`.
- Что это: MCP-сервер + CLI, дающий агенту инструменты реверс-инжиниринга (нативные бинарники через
  Ghidra / IDA / Hopper, JavaScript/Electron, .NET, сайты). Анализ выполняется локально.
- Проверенная версия: 6.8.0 (`rea --version` -> 6.8.0, `package.json` -> 6.8.0, проверено 2026-11-03 на
  этом ПК). Первая запись была 6.7.0 (`server.json`, `package.json`, коммит `a25eb5fb`, 2026-10-18) на
  прежнем ПК.

## Установлено и зарегистрировано на этом ПК (проверено 2026-11-03)

REA 6.8.0 установлен глобально через npm и зарегистрирован для агента **pi**. Ghidra 12.1.4 и JDK 21
присутствуют; Claude Code на этом ПК не установлен.

| Компонент | Состояние на этом ПК |
|---|---|
| REA | 6.8.0 (`rea --version`), глобальный пакет npm `rea-agents` в `%USERPROFILE%\AppData\Roaming\npm\node_modules\rea-agents` (запускающий скрипт `scripts\rea.mjs`) |
| Навык REA | `reverse-engineer-anything` v49 в `%USERPROFILE%\.agents\skills\reverse-engineer-anything` (cli_commands 175, mcp_tools 229, mcp_prompts 6) |
| Ghidra | 12.1.4 в `C:\tools\ghidra_12.1.4_PUBLIC` (`application.version=12.1.4`, `application.java.min=21`) |
| JDK | Eclipse Adoptium Temurin 21.0.13+9 (`JAVA_RUNTIME_VERSION 21.0.13+9-LTS`) в `C:\tools\jdk-21.0.13+9` |
| Node.js | v22.23.4 в `C:\Program Files\nodejs\node.exe` (системная установка, удовлетворяет «Node 22.23.4+» от REA), npm 10.9.9 |

Регистрация выполнена командой `rea setup --client pi --yes`. Запись `rea` в
`%USERPROFILE%\.pi\agent\mcp.json` — stdio:

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

REA создал рядом свои резервные копии: `mcp.json.rea.backup` и
`mcp.json.rea.backup.fbd170df1fed8f45e9e0d4080d072c68a433d38797d2ba5294b89069866f8b2e.recovery`.
Записи `coop-anything` и `supermemory` не тронуты.

Переменные пользователя (`HKCU\Environment`): `GHIDRA_INSTALL_DIR=C:\tools\ghidra_12.1.4_PUBLIC`,
`JAVA_HOME=C:\tools\jdk-21.0.13+9`. Машинного уровня `JAVA_HOME` нет.

`rea doctor --client pi` / `--provider ghidra` (2026-11-03): `healthy: true`, `environment_healthy: true`,
у ghidra `configured: true`, `available: true`, `providerVersion 12.1.4`; 9 проверок ghidra в порядке,
включая java `"21.0.13; 64-bit; JDK; accepted a 64-bit full JDK 21 or newer"` и native_decompiler
`win_x86_64` / `decompile.exe` / `pe x86_64`. ida, jadx и kuna показывают `missing_analysis_engine`
(своими руками: `REA_IDA_MCP_CONFIG`, `REA_JADX_MCP_JAR`, `REA_KUNA_COMMAND`) — здесь они не нужны.

Яма (проверено на этом ПК): проверки ghidra-провайдера в `rea doctor` читают окружение процесса CLI.
Изменения в `HKCU` или через `setx` не видны уже запущенным процессам, поэтому после изменения этих
переменных нужно перезапустить и оболочку, и самого агента (MCP-сервер `rea` в pi). `rea setup` также
сам записывает найденное окружение провайдера в регистрацию клиента.

Политика версий (`rea-agents/dist/ghidra/GhidraReleasePolicy.js`): `SUPPORTED_GHIDRA_VERSION` = `"12.1.4"`,
признаётся только линия релизов 12.1.x, `SUPPORTED_GHIDRA_JAVA_MAJOR` = 21, и JDK должен попадать в
диапазон `application.java.min`/`max` самой установки Ghidra. Поэтому Ghidra 12.2
(`application.version=12.2`, `application.java.min=25`) отвергается: `C:\tools\ghidra_12.2_PUBLIC`
(879 МБ) на этом ПК не используется, ждёт решения владельца об удалении.

Крутик старта (оставлен из прежней работы с FC3): `REA_GHIDRA_STARTUP_TIMEOUT_MS=3600000` — первый
проход по `FC3.dll` (40 МБ) занимает около 10 минут, штатный лимит 330 с не выдерживает. На этом ПК
`FC3.dll` через REA ещё не анализировался.

## Требования (по документации REA)

Из `docs/windows-ghidra-p0.md` (поддержка Windows **экспериментальная**, только чтение):

- Windows 10+ x64, копия игры на локальном диске NTFS;
- Node.js 22.x (>=22.23.4), 24.x (>=24.22.1) или 26.12.1+;
- Ghidra 12.1.x, установленная вами (проверено на 12.1.4) — REA её никогда не ставит;
- 64-битный полный JDK 21+ в пределах версий Java, указанных в Ghidra.

Все четыре выполнены на этом ПК (2026-11-03): Windows x64, Node v22.23.4, `C:\tools\ghidra_12.1.4_PUBLIC`,
`C:\tools\jdk-21.0.13+9`. Для анализа используется копия игры `H:\FarCryCoop\TestFC3\`.

## Почему REA НЕ прописан в `.mcp.json` этого репозитория

Документация REA (`docs/installation.md`, раздел «One project») советует не использовать
`--scope project`, который пишет `.mcp.json` в репозиторий, откуда его можно закоммитить или скопировать.
На этом ПК запись лежит в пользовательской конфигурации агента `C:\Users\<user>\.pi\agent\mcp.json`
(см. раздел выше); локальная область Claude Code здесь недоступна, так как Claude Code отсутствует
(`where claude` не находит, нет `%USERPROFILE%\.claude`, нет `%USERPROFILE%\.claude.json`). Анализ в любом
случае только на чтение.

## История прежнего ПК (октябрь 2026, диск E:)

Весь этот раздел — запись с прежнего ПК владельца, где инструментальная связка лежала под
`E:\FarCryCoop` (Ghidra 12.1.4, Temurin 21.0.12.1+1, портативный Node v24.22.0), а REA был версии 6.7.0.
Этой папки здесь нет: `E:` — игровой диск без папки `FarCryCoop`. Живые пути этого ПК — в
`AGENTS.ru.md` и `docs/workspace.ru.md`.

Команды установки там же (PowerShell, из папки проекта, путь через Claude Code):

```powershell
Remove-Item Env:CLAUDE_CONFIG_DIR -ErrorAction SilentlyContinue
claude mcp add --scope local rea -- cmd.exe /d /c npx -y rea-agents@6.7.0 mcp
$env:GHIDRA_INSTALL_DIR = "C:\tools\ghidra_12.1.4_PUBLIC"   # ваш путь
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21"              # ваш путь
npx -y rea-agents@6.7.0 doctor --json
claude mcp list
```

Локальная область хранила запись в `%USERPROFILE%\.claude.json` только для той папки и не ставила навык
REA. Удаление — `claude mcp remove --scope local rea` из той же папки.
Альтернатива: `npx rea-agents setup` регистрирует REA для всех проектов (user scope) и ставит навык.

### Зарегистрировано там 2026-10-18

Владелец разрешил одну запись в `C:\Users\<user>\.claude.json` (локальная область, только та папка).
Все пути инструментов вели в `E:\FarCryCoop`:

```powershell
$R='E:\FarCryCoop'
claude mcp add --scope local rea -e "GHIDRA_INSTALL_DIR=$R\Tools\ghidra_12.1.4_PUBLIC" -e "JAVA_HOME=$R\Tools\jdk-21.0.12.1+1" `
  -e "TEMP=$R\Temp" -e "TMP=$R\Temp" -e "npm_config_cache=$R\Data\npm-cache" `
  -e "XDG_CONFIG_HOME=$R\Data\xdg-config" -e "XDG_CACHE_HOME=$R\Data\xdg-cache" `
  -- cmd.exe /d /c "$R\Tools\node-v24.22.0-win-x64\npx.cmd" -y rea-agents@6.7.0 mcp
```

Имя сервера должно идти до опций `-e` (`-e` принимает несколько значений). `claude mcp get rea`
показывал `Connected`; инструменты появлялись в новой сессии Claude Code. `rea doctor` там: Ghidra 12.1.4
и JDK 21 в порядке; Hopper, IDA, jadx, Kuna не установлены (не нужны).

### Перенесено там в пользовательскую область 2026-10-22

Решение владельца: по репозиторию на игру, поэтому REA был зарегистрирован для всех папок. Локальная
запись удалена (`claude mcp remove rea -s local`), та же команда выполнена с `--scope user` вместо
`--scope local`. Тот же файл `C:\Users\<user>\.claude.json`, теперь его общий раздел; все пути
по-прежнему вели в `E:\FarCryCoop`. `claude mcp get rea` из `E:\FarCryCoop\FarCry3Coop`:
`Scope: User config`, `Connected`. Удаление — `claude mcp remove rea -s user`.

## Правила, которые нас касаются

- Золотое правило 2 из AGENTS.md (рабочая папка): анализируем только **копию** папки игры, не установку.
- `DISCLAIMER.md` REA: проект не поддерживает «circumventing DRM, license checks, anti-cheat systems or
  other technical protection measures» (обход DRM, проверок лицензии, античитов и других мер защиты) и
  «developing game cheats or tampering with online services» (создание читов и вмешательство в
  онлайн-сервисы). Та же граница, что и правило 10 («Stay fair») в хабовом `AGENTS.md`
  (`D:\Projects\Co-op Anything\coop-anything\AGENTS.md`).
- Windows Ghidra P0 работает только на чтение: REA не меняет байты исполняемых файлов.

## Неизвестно / догадка

- Догадка, не проверено: `FC_m64d3d12.dll` защищена Denuvo и VMProtect, поэтому статический анализ
  в Ghidra может показать мало полезного кода. Неизвестно, пока не попробуем на копии игры
  (`H:\FarCryCoop\TestFC3\`).

## Состояние на этом ПК (перепроверено 2026-11-08)

- `rea doctor --client pi --provider ghidra` -> `healthy: true`, `environment_healthy: true`; node
  `24.22.2` (шим `rea` на PATH; запись pi закрепляет `C:\Program Files\nodejs\node.exe`, указанный в
  таблице выше как v22.23.4), Ghidra 12.1.4 в `C:\tools\ghidra_12.1.4_PUBLIC`, `analyzeHeadless.bat` на
  месте, win32/x64.
- `pi mcp list`: `rea: connected, 229 tools (codemode, global)`. Доступ через `codemode`
  (`await searchTools("ghidra …")`, `await describeNamespace("mcp__rea")` или
  `await tools.mcp__rea__<tool>({…})`). Оговорка из AGENTS.md про «не выставлены / откат на скрипты»
  **снята**: инструменты доступны через шлюз codemode; черновые Python-зонды из `scripts\` остаются
  удобным запасным вариантом.
