# Рабочая папка

English version: [workspace.md](workspace.md)

Каноническая схема проекта — дерево с прежнего ПК владельца, `E:\FarCryCoop\`. Золотое правило 2 в
[AGENTS.ru.md](../AGENTS.ru.md) перечисляет пути, которые на этом ПК легально использовать (её раздел
«Рабочая папка на этом ПК»); `E:\FarCryCoop` в нём не назван. Это дерево и его загрузчик
`E:\FarCryCoop\env.ps1` на данном ПК отсутствуют; фактические пути этого ПК — в разделе «Пути на этом
ПК» ниже.

История прежнего ПК (октябрь 2026, диск E:) — раскладка папок, оставлена как запись того, где жили
инструменты и репозитории:

| Папка | Содержимое |
|---|---|
| `Downloads\<имя>\` | Исходные архивы, у каждого своя папка, SHA-256 проверен |
| `Tools\` | Распакованные портативные инструменты |
| `Data\` | Настройки и кэши инструментов (настройки/кэш Ghidra, кэш npm, глобальный префикс npm) |
| `Temp\` | Временные файлы (сюда указывают `TEMP`/`TMP`) |
| `FarCryCoop\`, `FarCry<N>Coop\` | Репозитории, по одной папке на игру |

## Пути на этом ПК (проверено 2026-11-03)

| Что | Путь |
|---|---|
| Репозитории (эта игровая копия, многоигровой хаб, конвейер coop-anything) | `D:\Projects\Co-op Anything\` |
| Тестовая копия игры (1.06) | `H:\FarCryCoop\TestFC3\` |
| Установка только для чтения (Ubisoft Connect) | `H:\Uplay\Far Cry 3\` |
| Черновики и личные данные | `<репозиторий>\local\`, `<репозиторий>\local\scratch\` (вне git) |
| Временные файлы агентской программы | `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp` |
| Связка REA / Ghidra / JDK | `C:\tools\`, `C:\Program Files\nodejs\`, глобальный префикс npm `%USERPROFILE%\AppData\Roaming\npm` (см. ниже и `docs/tools/rea.ru.md`) |

Все пути `E:\FarCryCoop\` в этом документе и в NOTES.ru.md — историческая запись с прежнего ПК
владельца (октябрь 2026). Диск `E:` на этом ПК существует как игровой диск, но папки `FarCryCoop` на
нём нет и нет `env.ps1`. Живые пути — в таблице выше.

## Установленные инструменты на этом ПК (проверено 2026-11-03)

| Инструмент | Версия | Путь | Источник |
|---|---|---|---|
| REA (`rea-agents`) | 6.8.0 (`rea --version`) | `%USERPROFILE%\AppData\Roaming\npm\node_modules\rea-agents` | глобальная установка npm; зарегистрирован для pi командой `rea setup --client pi --yes` |
| Ghidra | 12.1.4 | `C:\tools\ghidra_12.1.4_PUBLIC` | https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build |
| Eclipse Adoptium Temurin JDK | 21.0.13+9 (`JAVA_RUNTIME_VERSION 21.0.13+9-LTS`) | `C:\tools\jdk-21.0.13+9` | Temurin 21 (Adoptium) |
| Node.js | v22.23.4 | `C:\Program Files\nodejs\node.exe` | системная установка (удовлетворяет «Node 22.23.4+» от REA); npm 10.9.9 |

Архив Ghidra на этом ПК: `C:\tools\ghidra_12.1.4_PUBLIC_20260921.zip`, 569 649 598 байт,
SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` — тот же контрольный хэш,
что записан для загрузки октября 2026, то есть архив совпадает с уже документированным.
`Ghidra\application.properties` здесь читается как `application.version=12.1.4`,
`application.java.min=21`. SHA-256 установщиков Temurin и Node на этом ПК не перепроверялся (нового
хэша нет).

Переменные окружения пользователя (`HKCU\Environment`): `GHIDRA_INSTALL_DIR=C:\tools\ghidra_12.1.4_PUBLIC`,
`JAVA_HOME=C:\tools\jdk-21.0.13+9`. Машинного уровня `JAVA_HOME` нет. Загрузчика `env.ps1` на этом ПК
нет; нужные две переменные несёт блок `env` самой регистрации REA (см. `docs/tools/rea.ru.md`).

Файл Ghidra `support\launch.properties` на этом ПК **не** изменён: нет `JAVA_HOME_OVERRIDE`,
`application.settingsdir`, `application.cachedir`, `application.tempdir` и `java.io.tmpdir` ссылок в
`E:\FarCryCoop` (перенаправлять некуда, этой папки нет).

`rea doctor --client pi` / `--provider ghidra` (2026-11-03): `healthy: true`, у ghidra
`configured: true` / `available: true`, `providerVersion 12.1.4`, java принята как
`"21.0.13; 64-bit; JDK"`. REA признаёт только Ghidra 12.1.x, поэтому `C:\tools\ghidra_12.2_PUBLIC`
(`application.version=12.2`, `application.java.min=25`, 879 МБ) на этом ПК не используется и ждёт
решения владельца об удалении.

## История прежнего ПК (октябрь 2026, диск E:) — установки, записанные 2026-10-18

| Инструмент | Версия | Источник | SHA-256 (архив) |
|---|---|---|---|
| Node.js | v24.22.0 LTS (zip win-x64) | https://nodejs.org/dist/v24.22.0/ | `f9683a19877e12a9b167305c8db71040d812876359de21f0d2e97c3f321f80c3` |
| Eclipse Temurin JDK | 21.0.12.1+1 (zip x64) | https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1 | `f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e` |
| Ghidra | 12.1.4 (`ghidra_12.1.4_PUBLIC_20260921.zip`) | https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build | `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db` |

Контрольные суммы взяты из `SHASUMS256.txt` на nodejs.org, API Adoptium и релиза Ghidra на GitHub;
все три загрузки совпали. Оболочку там загружали командой `. E:\FarCryCoop\env.ps1`.

Там же у Ghidra был изменён `support\launch.properties` (оригинал сохранён как `launch.properties.orig`):
`JAVA_HOME_OVERRIDE`, `application.settingsdir`, `application.cachedir`, `application.tempdir`,
`java.io.tmpdir` указывали в `E:\FarCryCoop`. Проверка: `analyzeHeadless.bat` вывел справку и создал
папки настроек/кэша в `E:\FarCryCoop\Data`.

Историческая запись (2026-10-18): эти установки инструментов и проверка Ghidra записаны на прежнем ПК
владельца, где был диск `E:`. Node v24.22.0 (портативный) и Temurin 21.0.12.1+1 лежали в
`E:\FarCryCoop\Tools`; на этом ПК они не установлены — живая связка в таблице выше.

## Известные пределы правила «не трогать C:»

- Windows, PowerShell и системный `git.exe` (`C:\Program Files\Git`) находятся на C:. Они используются
  как установлены; наши инструменты туда ничего нового не пишут. Claude Code на этом ПК не установлен
  (`where claude` не находит; нет `%USERPROFILE%\.claude`, нет `%USERPROFILE%\.claude.json`).
- Регистрация REA пишет в `C:\Users\<user>\.pi\agent\mcp.json` на C: (сделано 2026-11-03 командой
  `rea setup --client pi --yes`; REA оставил рядом резервные копии `mcp.json.rea.backup` и
  `mcp.json.rea.backup.fbd170df1fed8f45e9e0d4080d072c68a433d38797d2ba5294b89069866f8b2e.recovery`, а
  навык — в `C:\Users\<user>\.agents\skills\`). Прежний путь `claude mcp add --scope local` писал в
  `%USERPROFILE%\.claude.json`; это запись с прежнего ПК, здесь она не применяется.
  Обе записи — отклонения от золотого правила 2, помечены. На прежнем ПК владелец явно разрешил единственную
  запись `.claude.json` (см. `docs/tools/rea.ru.md`); на этом ПК REA записал только регистрацию и свои
  резервные копии в `C:\Users\<user>\.pi\agent\` плюс навык в `C:\Users\<user>\.agents\skills\`.
- Файл правил агента — `AGENTS.md` и `AGENTS.ru.md`; `CLAUDE.md` оставлен только как заглушка на них,
  потому что часть окружения читает именно это имя. Прежний текст сохранён как `CLAUDE.md.keep`.
- Агентская программа пишет свои временные файлы в `C:\Users\<user>\AppData\Roaming\pi-desktop\tmp` (вывод субагентов, песочные скрипты).
  Это нельзя перенастроить нашими настройками, и это противоречит золотому правилу 2 — помечено,
  не исправлено (решение владельца, вопрос открыт).
