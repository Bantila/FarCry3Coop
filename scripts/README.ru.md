# scripts/

Инструменты анализа **только для чтения** сборок Far Cry 3 1.05 (`H:/FarCryCoop/105/game-105`)
и 1.06 (`H:/FarCryCoop/TestFC3`), установщика Ubisoft Connect (`H:/Uplay`) и розничной 1.06
(`H:/Uplay/Far Cry 3`). Почти все скрипты читают PE-файлы; байты могут менять только
`patch_dll.py` и `fc3_trampoline.py`, причём `fc3_trampoline.py install --apply` на этой машине
ни разу не запускался. Запускать нужно через `python -I` (изолированный режим: в каталоге игры
лежит `python3.dll`, который иначе ломает `python.exe`).

## Общий помощник

| Скрипт | Что делает |
|---|---|
| `fc3_addrmap.py` | карта RVA → файловое смещение для одной сборки (`PE`, `va2off()`, поиск строк и ссылок на данные). Нужен скриптам `fc3_func_dump.py`, `fc3_gate_probe.py`, `fc3_iat_find.py`, `fc3_iat_scan.py`, `fc3_reexec_probe.py`, `fc3_reg_keys.py`. |

## Основы PE

`fc3_pe_info.py` (заголовок, секции, экспорты, импорты), `fc3_imports.py` (директория импорта),
`fc3_dump.py` (hex/ASCII-дамп диапазона VA и поиск прологов функций), `fc3_vinfo_probe.py` и
`fc3_version_probe.py` (версия файла и sha256 текущей установки), `fc3_rsrc_probe.py`
(ресурсная директория `farcry3_d3d11.exe`).

## Строки и таблица импортов

`fc3_strings.py` (строки лагнера и перезапуска, их читатели), `fc3_strgrep.py` (поиск строк в
.rdata/.data), `fc3_args_scan.py` (поиск маркеров по каталогу или всей установке),
`fc3_args_context.py` (читаемый контекст вокруг найденных маркеров), `fc3_iat_scan.py`,
`fc3_iat_map.py`, `fc3_iat_find.py` (слот таблицы импорта ↔ импортируемое имя ↔ места вызова),
`fc3_iat_reverse.py` (адрес трюка ↔ импортируемое имя).

## Разбор командной строки и пути запуска

`fc3_cmdline_cluster.py` (кластер разбора ключа по VA строки-ключа), `fc3_switchtable.py`
(таблица переходов за разбором аргументов запуска), `fc3_quicklaunch_map.py`, `fc3_switch_context.py` (находит все места, которые кладут в стек
строку-ключ и вызывают разбор: сырой скан `68 <VA строки> ... e8 <rel32>` плюс проход по
el beginnings функций, который сообщает, куда попадает тело — `--mode prologue|raw|both`),
`fc3_reloc_xref.py` (перекрёстные ссылки адреса данных; поправка: disp32 в `.text` содержит VA как есть,
поэтому обход `.reloc` даёт только места патча загрузчика), `fc3_param_records.py` (перечисление
записей дескриптора сессии: `push <VA имени>; push <код типа>; call <создатель>` -> имя, код типа,
место вызова; аргументы-создатели передаются позиционно, не флагом), `fc3_func_dump.py`
(тело функции: встроенные строки и ссылки на данные), `fc3_callers.py` (обратные поиски
вызывающих), `fc3_dataslot.py` (на какой слот данных указывает абсолютная ссылка),
`fc3_reexec_probe.py` (перезапуск-бутстрап 1.06), `fc3_drm_probe.py` (бутстрап DRM/UPC),
`fc3_gate_probe.py` (проверка gates и mutex-ов), `fc3_reg_keys.py` (кто читает
`HKCU/Software/Ubisoft/Far Cry 3`), `fc3_dis.py` (разбирающий дизассемлер capstone с
аннотациями: вызывающие, импортируемые имена, ссылки на строки — главный инструмент всех
наблюдений по 1.06),
`fc3_mode_cascade.py` (разбирает каскад флагов запуска в одном PE: какие имена режимов сопоставляются,
какие проверки `cmp`/`test` встречаются, какие globals с id режима читаются и что лежит в каждом, и в
какую локальную ячейку пишется выбранный id. Запуск: `python -I scripts/fc3_mode_cascade.py <pe>
<стартовый VA> [--end <VA> | --limit N] [--no-strings] [--json]`; голое имя модуля разрешается через
`H:/FarCryCoop/TestFC3/bin/`. Проверено на `FC3.dll` `0x11a8c440 .. 0x11a8c5f0` и на `FC3_d3d11.dll`
`0x11aa08d0 .. 0x11aa0980`; см. NOTES.md, «каскад флагов запуска»).

## Запуск (реально что-то запускают)

`fc3_launch_probe.py` (запуск тестовой копии 1.06 с аргументами quick-launch и сбор логов),
`fc3_upc_probe.py` (просим Ubisoft Connect запустить нашу тестовую копию и записываем точную
командную строку), `fc3_test_startargs.py` (проверяет, передаёт ли хаб реестровое значение
`ExecutableName` в командную строку запущенного процесса игры), `launch_105.ps1`,
`build_testgame.ps1`, `build_patch.ps1`, `reunpack.ps1`, `switch_variant.ps1`, `thread_eips.ps1`.

## Сравнение и данные (работа владельца Phase 1)

`bindiff.py`, `contentcompare.py`, `dupcheck.py`, `fat.py`, `fatcompare.py`, `manifest_diff.py`,
`edit_playlist.py`, `names.py`, `names_ext.py`, `find.py`, `findpats.py`, `patchctx.py`,
`reg_fields.py`, `peinfo.py`, `patch_dll.py` (правит байты **копии** FC3.dll / FC3_d3d11.dll),
`fc3_trampoline.py` (14-байтовый jmp-трамполин; `install --apply` здесь не запускался — решение
за владельцем),
`fc3_accessor_thunks.py` (переписывает thunk-ы вида `mov eax, imm32` + `jmp <helper-aksesora>` одного
PE, группирует их в непрерывные прогоны и печатает шаг базовой глобальной ячейки каждого контейнера;
проверка парности цепочки accessor-ов из NOTES.md. Запуск: `python -I
scripts/fc3_accessor_thunks.py <pe> [--helper 0x10004b70] [--min-count 3] [--range START:END]
[--show-va <VA>] [--json]`; проверено: 3228 thunk-ов в 523 прогонах в обоих модулях 1.06).

## Трассировка в рантайме (Frida)
`fc3_h3_trace.js` — трассировка и два рычага H3 для переключения кооперативного режима (PLAN.md, «Статус точек внедрения после сессии 7»). Присоединяется к живому **офлайн**-процессу FC3 и журналирует (только чтение) диспетчер режима по `0x113405a0` (поле менеджера режима `[this+0x4c]`), установщик id кооператива `0x11279910` и его два статических вызывателя `0x1127a0f0` / `0x11279fc0` с трейсами вызовов, и читает живой контейнер `CFCXPlaylistService` `[service+0x8c0]` через `dumpService()`. RPC `switchCoop(dryRun)` (H3a) пишет `[modeManager+0x4c]=0x43521e6f` и вызывает `modeManager->vtable[+0x5c](&id)`; `populate(dryRun)` (H3b) вызывает `FUN_1127a0f0(service)` для построения co-op-записи. Всегда сначала `dryRun=true` — слепой вызов виртуального метода движка может уронить игру. Адреса — для 1.06 (база `FC3.dll` `0x10000000`); перед применением перенести в 1.05 через `fc3_addrmap.py`. Присоединяться только к **офлайн**-экземпляру (`-offline`) — никогда к онлайн / Ubisoft Connect (античит + страж `OpenMutexA("FarCry3Instance")`). Запуск одной командой: `scripts\fc3_h3_run.bat` (цепляется к запущенному `farcry3.exe` / `farcry3_d3d11.exe`, грузит этот скрипт, сохраняет всю сессию в `H:\FarCryCoop\scratch\h3_live.log` и даёт цикл команд `dump`/`modes`/`mode`/`switch`/`pop`). Или вручную: процесс игры называется `farcry3` (не `FC3`), поэтому `frida -n farcry3 -l scripts/fc3_h3_trace.js` и в REPL `rpc.exports.dumpService()` / `lastMode()` / `switchCoop(true)` / `populate(true)`. `fc3_h3_run.py` — драйвер, который вызывает `.bat`; передайте `--pid`, чтобы пропустить автопоиск. Упорядоченная процедура для владельца — в `docs/h3-live-test.md` (+ `.ru.md`).

## Офлайн-проект Ghidra (headless)
Сессия 7 построила офлайн-проект Ghidra для `FC3.dll` 1.06, чтобы выгружать псевдокод для любого RVA **без запуска игры**. `.gpr` лежит в черновике (`H:\FarCryCoop\scratch\ghidra\proj\FC3_106`, ~647 МБ, анализ `-default`, ~2 ч один раз) — не коммитится. Для выгрузки новых функций переиспользуйте сохранённый анализ (загружается ~3 мин, без повторного анализа) скриптом-постскриптом headless:
`analyzeHeadless <каталогПроекта> FC3_106 -process "FC3.dll" -noanalysis -scriptPath <папка> -postScript <имя>.java`.
`ghidra/DecompileH3.java` — рабочий пример (выгружает диспетчер режима `FUN_11340560`, init сервиса `FUN_1127a0f0`, инсталлер `FUN_11279910`, геттер синглтона `FUN_103d1640` и переключатель режима `vtable +0x5c`); `ghidra/run_decomp_h3.bat` показывает вызов (пути указывают на черновой проект — правьте их). `ghidra/DisasmSwitch.java` (+ `run_disasm.bat`) — вариант линейного дизассемблирования, применённый для подтверждения ABI переключателя по дизассемблеру. `ghidra/DumpCallers.java` (+ `run_dump_callers.bat`) перечисляет кросс-рефы диспетчера (доказано, что он вызывается только виртуально), `ghidra/DumpVtable.java` (+ `run_dump_vtable.bat`) обходит таблицу виртуалов функции, а `ghidra/DecompileModeSwitch.java` (+ `run_decomp_modeswitch.bat`) декомпилирует живой виртуал-переключатель режима `vtable+0x5c` (`FUN_1030f8a0`, установщик id) и слоты обвязки на входе диспетчера. `ghidra/FindModeConsumers.java` перечисляет все функции, загружающие константу id режима (и ссылки на таблицы виртуалов менеджера), а `ghidra/DecompileConsumers.java` декомпилирует обработчик смены режима в co-op `FUN_10fa1990`, его конструктор и функцию-загрузчик. `ghidra/TraceDescriptor.java` находит ссылки на `FUN_10fa1990` (это слот `+0x0C` vtable менеджера) и декомпилирует использование `param_3`; `ghidra/TraceRegistry.java` перечисляет READ/WRITE-ссылки на глобальный синглтон-список режимов `DAT_128048c0` (и `DAT_12804acc`/`DAT_12804b3c`); `ghidra/DecompRegistry.java` декомпилирует его конструктор `FUN_10048230` и уничтожение `FUN_11756e00`. В рантайме команда `modes` (`fc3_h3_run.py`, RPC `dumpModes`) читает живой список `DAT_128048c0` и печатает каждую зарегистрированную запись режима (`id@+0x20`, `name@+0xC`), чтобы офлайн проверить, есть ли уже запись CO-OP (`0x43521e6f`). Универсальный офлайн-запуск — `ghidra/run_headless.py <Script.java> <лог>` (переиспользует проанализированный проект `FC3_106`, без повторного анализа). Требует Ghidra 12.1.4 (`C:\tools\ghidra_12.1.4_PUBLIC`) и Temurin JDK 21.

## ## Кооп-мир / патчинг (офлайн)

- `h7a_coopmap_patch.py` — офлайн-патч селектора кооп-карты для `FC3.dll` версии 1.05. Перезаписывает
  строку стартового кооп-мира `mpdlc1_aegir` -> `fc3_main` по смещению файла `0x15345D0` (12 байт,
  минимально по байтам), чтобы кооп-сессия грузила одиночную кампанию вместо штатного кооп-острова;
  та же единственная правка, что и у мода OpenWorld220 (подтверждено по тому же смещению).
  Подкоманды `status` / `apply` / `restore`; `apply` сначала пишет резервную копию рядом `FC3.dll.bak_h7a`,
  `restore` откатывает. Целится только в `H:\FarCryCoop\TestFC3_105`. md5 ванильной 1.05 `5ff04533…` ->
  пропатченного `e4516487…`. Другая кооп-строка `mpdlc1_idun` (в `0x15A2568`) не тронута.

Кэши и игнорируемые файлы

`*_dis_cache.json` (кэш дизассемлирования), `__pycache__/`, `../Temp/` (черновики агента) и
`../local/` в git не попадают.

## Зонды LAN / неткода (Сессия 23)

- `fc3_lan_probe.py` — зонд только на чтение: находит в `FC3.dll` опорные строки LAN-матчмейкинга /
  хостинга (`storm::echo::lan::*`, `LanHostBroadcastPort`, ключи `-dedicated`/`-client`, …) и код,
  который на них ссылается; печатает RVA (`VA - imageBase`). `python -I scripts/fc3_lan_probe.py
  [strings|xrefs] [extra substr ...]`. Не пишет.

## Прокси лодера orbit-API (Сессия 27)

Наблюдаемая надстройка orbit-API в процессе живёт в `../src/uplay_proxy` (исходники в git; собранный
`uplay_r1_loader.dll` в gitignore). Эти скрипты им управляют:

- `gen_uplay_proxy.py` — генерирует `src/uplay_proxy/uplay_proxy.cpp` + `.def`: 58 cdecl-экспортов
  `UPLAY_*` как thunk-пробрасыватели стека с логом (читает `local/scratch/loader_exports.json`).
- `build_uplay_proxy.py` — собирает 32-битный прокси без причуд `.bat` (берёт окружение MSVC x86 из
  `vcvars32` через `cmd /c`).
- `build_proxytest.py` — собирает `src/uplay_proxy/proxytest.c`, стенд проверки прозрачности проброса.
- `probe_orbit_gates.py` — только на чтение: дизассемблирует прологи экспортов-гейтов orbit-API в
  настоящем лодере, чтобы подтвердить соглашение `int(void)` cdecl перед их подделкой (Сессия 28).
- `probe_memberlist_imports.py` — только на чтение: печатает, какие `UPLAY_*` импортирует
  `FC3_d3d11.dll` (и RVA их IAT-слотов), чтобы затем найти xref-потребителей пати/сессий (Сессия 28c).
- `probe_rv_party.py` — только на чтение: дизассемблирует хуки Rv party/session-контроллера
  (`FUN_11273650`, `FUN_11218480`, …) из 1.06 `FC3.dll` для проектирования детура ростера на 2-4 (Сессия 28d).
- `probe_rv_detour.py` — только на чтение: xref-вызывающих и выровненный дизасм контроллера
  роста/входа (`FUN_11218480`, `FUN_11273650`, геттер `0x10070590`) (Сессия 28e).
- `probe_rv_live.py` — только на чтение: для РАБОТАЮЩЕГО модуля (`FC3_d3d11.dll` копии, md5 46bcc097) и живого
  RVA из Frida разрешает ImageBase + RVA->файловый сдвиг, находит IAT `gethostbyname` и дизасмит окно, чтобы
  подтвердить совмещение bootstrap RendezVous и что файл не упакован (Сессия 28q). ВНИМАНИЕ: RVA из
  `probe_rv_party.py` / `probe_rv_detour.py` получены из DX9-установки `FC3.dll` (md5 5742de2a), а НЕ из
  работающего модуля — не переиспользовать.

`ghidra/decompile_session_callers_106.py` — Jython-скрипт Ghidra (открыть проанализированный `FC3_106`,
декомпилировать сборщики параметров create/join Rv `GameSession` и вызывающих). Хранится как задуманный
зонд офлайн-входа в сессию; в Ghidra 12.1.4 привязка `currentProgram` через PyGhidra не сработала, поэтому
прогон надо делать Java-скриптом с `-noanalysis` (см. заметки сессий 23/24).

## Перенесённые пути

Скопированные с ПК владельца (октябрь 2026) скрипты содержали пути старой раскладки: `DLL_106 = E:\SteamLibrary\steamapps\common\Far Cry 3\bin\FC3.dll`, `DLL_105 = E:\FarCryCoop\Downloads\fc3-1.05\bin\FC3.dll`. Диска `E:` на этом ПК нет. Такие скрипты сохранены как запись и НЕ перенацеливаются молча: перенацелить скрипт, который пишет в папку игры (patch / build / unpack), — решение владельца. На этом ПК установка только для чтения — `H:\Uplay\Far Cry 3\`, тестовая копия 1.06 — `H:\FarCryCoop\TestFC3\`; скрипты только для анализа здесь уже читают проверенные пути.


## Живой Frida-трейс (`scripts/frida/`)

- `fc3_coop_trace.py` + `fc3_coop_trace.js` - attach Frida к запущенному `farcry3_d3d11.exe` (через Ubisoft Connect)
  и трассировать подключение кооп-сервиса. Ядро = хуки winsock (`gethostbyname`/`getaddrinfo`/`connect`/`sendto`/
  `recvfrom`/`bind`) -> показать host:port кооп-сервиса и сбой DNS/connect; плюс best-effort хуки на смещения гейта
  FC3.dll. Запускать дойдя до главного меню, затем идти в кооп. Вывод: `local/scratch/frida_coop_<ts>.log`.
  Для разведки направления (B) rendez-vous (NOTES 28k-28n).
- `fc3_coop_force.py` + `fc3_coop_force.js` - живой go/no-go-зонд направления (B) в памяти (без записи на диск). Логирует режим сети движка (`FUN_1092d256` поле +0xe: 0=LAN/1=Online/2=Offline) и вход в онлайн-кооп (`FUN_1044123b`); при `FORCE=true` форсит гейт RendezVous (`FUN_11245090`/`FUN_112492a0`/`FUN_11279ba0`) в успех, чтобы увидеть, где он упирается (ожидаемо: UbiAuthentication). Смещения под `FC3_d3d11.dll` копии md5 46bcc097. Вывод: `local/scratch/frida_force_<ts>.log` (NOTES 28r).
