# Far Cry 3 — заметки по кооперативу

English version: [NOTES.md](NOTES.md)

Статус: в работе (решение владельца 2026-10-22). План: [PLAN.ru.md](PLAN.ru.md).

## Данные игры (правило 5 AGENTS.md)

Проверено 2026-10-22 на ПК владельца:

- Магазин: Steam, app 220240, `E:\SteamLibrary\steamapps\common\Far Cry 3`; работает через Ubisoft Connect (`bin\upc_r1_loader.dll`), `steam_api.dll` нет
- Номер сборки Steam: 13146413
- SHA-256 `bin\farcry3.exe`: `fd3929f19ff825912f73bd0158604823c46ab9c124d18d57b0fab05a51cda9bb`
- SHA-256 `bin\farcry3_d3d11.exe`: `5437b2e37a54f8a3b28c342f2b2670ca907fd60bc74905b0b7527f69bafc965e`
- SHA-256 `bin\FC3.dll`: `71d58a7a4503c5c67dcd6f4b9445b5e7ac34c12043987f4c7285e13f2ed51c9b`
- SHA-256 `bin\FC3_d3d11.dll`: `e541594e11ac6091dc7d3702f2cd90504280b82cf15ec10b4eb148aae27f0809`
- Движок: Dunia
- Установка проверена на сторонние DLL: в `bin` только файлы игры
- В `data_win32\patch.dat/.fat` был мод владельца на автопропуск катсцен. С разрешения владельца он переименован в `patch.dat.skipcutscenes` / `patch.fat.skipcutscenes`, оригинальная пара (лежала как `.vanilla`) возвращена. SHA-256 оригинального `patch.dat`: `b76a3ae5092bec46e4d000dfebb0dc1fac9d7990d217421528447d59a7661833`, `patch.fat`: `39dc4178723bfd4e2f9f512d42401790b80a3f4ea305d4ab38889f546780b39f`
- Есть также: `bin\FC3Editor.exe` (официальный редактор карт), `data_win32\worlds\fc3_main`, `data_win32\worlds\multicommon`

## Что известно

- [x] Найти реестр игровых режимов и routine заполнения: ЗАКРЫТО 2026-11-06 — контейнер `[0x128048c0]`
  заполняется из `engine\gamemodes\GameModesConfig.xml` (строка `0x11f16940` в `FC3.dll`; загрузчик
  `0x117568a0`, вызываемый из `0x117569f0`, который затем запрашивает `GameModeProperties` `0x11f16968`
  через `mov edx,[eax+0x58]` / `call edx` на `0x117569ba..0x117569c5`); заполнение выполняет
  `0x11709af0 .. 0x11709ca0`: количество потомков `[ecx]+0x4c` (`0x11709b03`), потомок по индексу
  `[eax]+0x50` (`0x11709b1c`), проверка имени `push 0x11f10d78 'GameMode'` + vtable `[edx+0x14]`
  (`0x11709b35..0x11709b3d`), выделение записи `mov edx,0x10; lea ecx,[edx+0x30]; call 0x1177f7c0`
  (`0x11709b5c..0x11709b64`), инициализация записи: vtable `mov dword ptr [eax], 0x11f224b4`
  (`0x11709b86`), `mov dword ptr [eax+0x20], 0xffffffff` (`0x11709ba1`, идентификатор режима, который
  ищет `cmp dword ptr [ebx+0x20], esi` на `0x1181cf13`), `movss [eax+0x28], xmm0` из `[0x11ef3764]`,
  `mov word ptr [eax+0x34], 0x100` (`0x11709bb6`), `mov byte ptr [eax+0x36], 1` (`0x11709bbc`), затем
  `call 0x11969740` (`0x11709bcc`). Остается открытым: какой атрибут XML пишет идентификатор в
  `[eax+0x20]`.
- [x] Проверить, есть ли ко-оп как игровой режим в поставляемых данных 1.06: ЗАКРЫТО 2026-11-06 — да.
  `H:\FarCryCoop\TestFC3\data_win32\worlds\downloadcontent\mp_dlc1\toc.rml` (1989 байт) содержит
  `GameModes Desc FCXCoop`, и обе карты DLC помечены `gamemodemask 128`: `mpdlc1_aegir` (`id 3001`,
  `presenceId 690271114`) и `mpdlc1_idun` (`id 3002`, `presenceId 3534781404`); там же регистрируется
  `ClassService CharacterAppearancesCoopULC` с `yuriy_ulc_2`, `leonard_ulc_2`, `tisha_ulc_2`,
  `callum_ulc2`. `FCXCoop` встречается и внутри пакетов: `multicommon/multicommon.dat` — 1 совпадение
  (`_FCXCoop.207146615258375806` на смещении 407859421), плюс `MZoneEntity_Coop_Island.2070649460439908519`
  (350109489) и `MZoneEntity_Coop_ToRockets.2077132487061948236` (350279600) среди 331 совпадений `Coop`;
  `downloadcontent/mp_dlc1/mp_dlc1.dat` — 5 совпадений (`DynLoad/ … Mode/FCXCoop)` на смещениях 68659542,
  69112499, 120652426, 121131557 и `_FCXCoop.2077257745930653048` на 160905944); `fc3_main/fc3_main.dat`
  (3496061837 байт) — 1 совпадение на смещении 2379019038 в той же форме `DynLoad/ … Mode/FCXCoop)` плюс
  331 совпадений `Coop`, в том числе категории DOMINO `<Display Category="Coop|Group" …` (1304419581,
  1304592795) и функции DOMINO `Coop/Group/AddTo…` (400798582), `Coop/Entity/Is…` (1030651053),
  `Coop/AllP…` (1088269141, 1312711018). Отрицательный результат: `grep -a -c -i gamemodesconfig` по всем
  `data_win32/*.dat` и `*.fat` дал 0 совпадений, то есть сам XML в этом экземпляре в открытом виде не
  хранится.
- [x] Подтвердить, что классы ко-оп обращаются кодом, а не только присутствуют строками: ЗАКРЫТО
  2026-11-06 — `CFCXCoopService` `0x11fc3d3c` передается через `push` на `0x103ca3aa`, `0x11020fe9`,
  `0x11021004`; `CFCXCoopGateService` `0x11fc5384` на `0x103d141a`, `0x11833c19`, `0x11833c34`;
  `CFCXCompetitiveCoop` `0x11ff136c` на `0x10466e1a`, `0x11047bd1`, `0x11047bec`;
  `CFCXCompetitiveCoopNetFunc…` `0x11ff1334` на `0x10466c80`, `0x10467704`; `CoopBarks` `0x11fd9c1c` на
  `0x11120455`; `SupportedGameModes` `0x11fa84bc` на `0x10351eb7` и на
  `0x10351ebe mov dword ptr [esi + 4], 0x11fa84bc`. Имена служб и консольных команд регистрируются парой
  `push <имя>` + `call 0x10a00be0`, а сканирование всего `.text` насчитывает 1817 таких вызовов и 842
  различных имен (`local/scratch/console_cmds.txt`). Следствие для патчинга: идентификаторы режимов живут
  только в `FC3.dll`, а `FC3.exe` — заглушка на 213 КБ, поэтому патч запуска ко-оп нужен в `FC3.dll`, а не
  в `FC3.exe`.
- Штатный кооп: отдельная кампания из 6 миссий, до 4 игроков онлайн https://co-optimus.com/article/8473/far-cry-3-follow-up-questions-plus-new-co-op-campaign-trailer-and-images.html . Мод: Open World Co-op (scubrah), без сюжетных миссий, альфа https://www.nexusmods.com/farcry3/mods/220 (каталог coop-anything).

## Фаза 1: распаковка данных игры (2026-10-24)

- Инструмент: Gibbed.Dunia (https://github.com/Gibbed/Gibbed.Dunia, commit a43405c), собран из исходников портативным .NET SDK 8.0.426 (`Tools\dotnet-sdk-8.0.426`). Клон: `Downloads\gibbed-dunia\src`, результат сборки `bin_fc3\Gibbed.FarCry3.Unpack.exe`.
- В репозитории Gibbed нет распаковщика Far Cry 3, но `BigFileV2_64` уже знает FAT версии 9 (Windows, версия сжатия 3). Локальный патч [docs/gibbed-dunia-fc3.patch](docs/gibbed-dunia-fc3.patch) добавляет: проект `Gibbed.FarCry3.Unpack`, конфиг `configs/Far Cry 3`, соответствие схем сжатия FAT v9 (0 без сжатия, 1 LZO1x, 2 Zlib) и ограничение вывода LZO для определения типа по первым 64 байтам.
- Результат в `Work\fc3`: `patch.fat` даёт 427 файлов (388 Lua, 11 bin, 6 xbg, 5 hkx, 2 seq); `common.fat` даёт 3099 файлов (1984 xbt, 184 feu, 89 xml, 58 fcb). Списков имён для FC3 нет, поэтому файлы названы хешами.
- Скрипты миссий — обычный текст Lua, созданный инструментом «Domino» (`-- {\v/} Domino auto-generated LUA script file`, в заголовке исходный документ, например `domino/library/sp/lib_mission.domino.xml`).
- Дальше: распаковать `worlds\fc3_main` и остальные архивы, сгруппировать скрипты Domino по исходному документу, найти таблицы миссий и коллекционных предметов.

### Результаты фазы 1: `fc3_main` (2026-10-24)

- `worlds\fc3_main\fc3_main.fat` распаковывается в `Work\fc3\fc3_main`: 2,7 ГБ; 17944 xbt, 5247 xbg, 3628 bin, 3397 hkx, 2229 lua, 1069 fcb, 818 seq. Поля заголовка FAT по смещениям 0x0C/0x10 (здесь 117303 и 50) относятся к таблицам локалей после основной таблицы; одна основная таблица (64354 записи) покрывает весь `.dat` (максимальное смещение + размер = размер файла). Локальный патч пропускает таблицы локалей. Архивы локалей и `multicommon` пока не распакованы.
- Индекс скриптов (файл скрипта → исходный документ Domino): `Work\fc3\script-index.tsv`, 2363 строки. Группы: основные миссии 1175 скриптов (`fc3_mainmissions/<id>`, около 80 идентификаторов: `jas_*` Джейсон, `hoy_*` Хойт, `doc_*` Док, `bam_*`, `cit_*`, `den_*`, `hur_*`, `sam_*`, `wil_*`, `bng_*`, `game_chapter02..10`, `game_credits`), побочные задания 155 (`fc3_poisquests`), столкновения 103, социальные испытания 82, раздатчики заданий 82, хаб и цепочки заданий 81, DLC ulc 74, аванпосты 33 (`fc3_outpost/<клетка карты>`), сохранение состояния 21 (`fc3_persistency`), занятия 14 (покер, метание ножей, гонки, тир, магазин), главные скрипты 91 (`fc3_master`: аванпосты, радиовышки, сохранение состояния, телепорт, нарративные сцены, закрытые зоны, побочные задания).
- Lua-файлы — только графы Domino: они создают и соединяют «боксы» (`Domino/System/AI/`, `Player/`, `Narrative/`, `UI/` и т. д.). Код боксов не на Lua, он собственный в `FC3.dll`. Поэтому логику миссий и прогресса можно менять в двух местах: в графах (наш архив) и в родных боксах (перехваты ASI).
- В игре уже есть кооперативные боксы: `Domino/System/Coop/` (AllPlayers: GodMode, UnlimitedAmmo, TeleportPlayer; Group: AddToGroup, GetFromGroup, GroupUseSTP; Misc: GetEntityByName, EndGame) и библиотека `domino/library/coop/helpers`. Их используют 6 штатных кооперативных миссий из `multicommon`, а не одиночная кампания.
- Для выбора варианта (A: сетевой слой движка, B: свой сетевой код в ASI): в графах одиночной кампании нет учёта нескольких игроков, поэтому решение требует разбора родной части (`FC3.dll`) в REA/Ghidra и мода scubrah. REA при старте сессии не подключился (CONNECT_TIMEOUT).

### Результаты фазы 1: `multicommon` и кооперативные боксы (2026-10-24)

- `worlds\multicommon\multicommon.fat` распаковывается в `Work\fc3\multicommon` (2128 Lua-скриптов; их документы добавлены в `script-index.tsv`). Там 6 штатных кооперативных миссий в виде документов Domino `domino/user/coop/coop_{vidar,huginn,skadi,freyja,sleipnir,fenrir}` (около 1650 скриптов), режим гонки `coop_cce_race` и общие библиотеки `domino/library/coop/{mission,pawns,vehicle,mapsetup,ui,helpers}`.
- Кооперативные боксы рассчитаны на небольшие миссии с целями, а не на сюжет: `PlayerCount` / `PlayerCountTest` (3178 использований), `AllPlayers/*` (GodMode, TeleportPlayer, ProximityTrigger, ManageInventoryAllPlayers), `SetCoopCheckPoint`, `Group*`, `StrayPlayerZone`, `CoopGate`, `ForceOutPlayerFromVehicle`. Полезная мысль: движок уже считает игроков, телепортирует всех и хранит общую кооперативную контрольную точку.
- Графы одиночной кампании получают игрока через один бокс: `Domino/System/Player/GetLocalPlayer` (1484 использования в `fc3_main`, 291 в `patch`, всего 10 в `multicommon`). Остальные боксы игрока (`ManageInventory_v4` 197, `SetHudMode` 136, `PostFx` 637, `ForceInVehicle`, `SwitchPawnPlayer`) принимают этого игрока на вход. Кандидат на перехват для варианта B: родной код `GetLocalPlayer` и поиск игрока по слоту `GetPlayerFromSlot`; для варианта A: как `PlayerCountTest` читает список игроков.
- Дальше: найти эти боксы в `FC3.dll` (REA/Ghidra, строки `GetLocalPlayer`, `PlayerCount`), затем попробовать запустить открытый мир внутри кооперативной сессии. (Сделано ниже: боксы оказались Lua, а не родным кодом.)

### Результаты фазы 1: `FC3.dll` и боксы Domino (2026-10-24)

- **Исправление:** код боксов — Lua. Граф подключает боксы через `cbox:RegisterBox("Domino/System/Player/GetLocalPlayer.lua")`; каждый бокс — Lua-файл в тех же архивах с заголовком-описанием (`-- DOMINO REFLECTION BOX START`, `<Display>`, `<ControlIn>`, `<DataOut>`). Прежнее утверждение «код боксов родной в `FC3.dll`» было неверным. Родными являются только Lua-глобалы, которые вызывают боксы (например `GetLocalPlayerId()`).
- **Имена файлов — хеши имён боксов.** Хеш имени = CRC-64/ISO (отражённый, полином 0xD800000000000000, начальное значение 0, без финального xor, таблица = `Gibbed.Dunia.FileFormats.Hashing.CRC64`) от **пути в нижнем регистре с обратными косыми чертами**. Проверка: `domino\system\player\getlocalplayer.lua` даёт `9716CA537E634631`; такой файл есть в `fc3_main\__UNKNOWN\unknown\` и в `multicommon\__UNKNOWN\unknown\` (782 байта, одинаковый, MD5 `5E8EFF68D5AF85A2E7F849D233170134`). Ещё: `domino\system\getscriptentity.lua` даёт `235DF3F86557C6FA`. Файлы без расширения в `unknown\` — это боксы.
- **Списки имён всё-таки есть:** манифесты ресурсов `__UNKNOWN\misc\*.root.xml` (например `fc3_main\__UNKNOWN\misc\7215F999AEACCD55.root.xml`, `multicommon\__UNKNOWN\misc\7FFFAC13D814F0C8.root.xml`) перечисляют `<CDominoBoxResource ID="Domino/...lua">`, текстуры, материалы и другое. Хеширование этих ID даёт имена всех файлов. Пока не сделано.
- **Бокс `GetLocalPlayer` тривиален:** `function GetLocalPlayer:In() self.LocalPlayer = GetLocalPlayerId(); Out(self) end`. Значит, графы одиночной кампании получают локального игрока через Lua-глобал `GetLocalPlayerId`, а файл-замена бокса в нашем архиве может изменить это для 1484 мест вызова в `fc3_main`.
- **`FC3.dll` (x86, Ghidra 12.1.4, через REA):** у строки `GetLocalPlayerId` по адресу `0x11fbdcc4` две ссылки. (1) `0x111ce912` в `FUN_111cdb00` — таблица регистрации **консольных команд** (`GetLocalPlayerId` -> `FUN_111cb980`, она только форматирует строку, то есть это не Lua-функция; в той же таблице `TeleportToCurrentObjective`, `SetHealth`, `HitMe`, `GetCurrentPrimaryBuddy`, `SetNoWeaponMode`, `ActivateChallenge`, `CompleteChallenge`). (2) `0x11b1b5c4` в `FUN_11b1b4e0` (4442 байта) — вероятно, регистрация **Lua-глобала**. Строка `Game:GetLocalPlayerId(%%)` по адресу `0x11fba634` упоминается из `0x111ef365` (очень большая функция). Пока не декомпилированы.
- В `FC3.dll` строками не найдены: `PlayerCount`/`GetPlayerFromSlot` (есть только `m_playerCount: %i` по `0x11fafae8` и `MultiCaptureBarPlayerCount` по `0x12026c84`) и `Domino/System/Player`. Имён боксов в DLL нет; `PlayerCount` — Lua-бокс в `multicommon`.
- REA и `FC3.dll` (40 МБ): первый анализ занимает около 10 минут; лимит старта по умолчанию 330 с не хватает. В записи `rea` уровня пользователя теперь `REA_GHIDRA_STARTUP_TIMEOUT_MS=3600000`. Рабочая копия: `Work\fc3\bin\FC3.dll` (SHA-256 равен оригиналу). Лишняя запись `rea` уровня проекта (`npx -y`) вызывала CONNECT_TIMEOUT и удалена.
- Дальше: декомпилировать `FUN_11b1b4e0` и найти родную функцию за Lua-глобалом `GetLocalPlayerId`; прочитать файлы боксов `PlayerCount` и `Coop/AllPlayers/*`; захешировать ID из манифестов и назвать все файлы; затем выбрать вариант A или B. (Сделано ниже.)

### Результаты фазы 1: имена файлов и родные кооперативные примитивы (2026-10-24)

- **Имена файлов.** Все 22 манифеста `*.root.xml` содержат 65217 уникальных ID ресурсов; хеширование (правило выше) называет 45045 из 162363 файлов с хешем (3555 — Lua; остальное — .mab, .xbt, .xbg, .spk, .bin, .dpax и т. д.). Список: `Work\fc3\names.tsv` (`hash`, `name`, `archives`). Текстовые файлы (.lua, .xml) с настоящими путями: `Work\fc3\named\<архив>\...` (4104 файла). В манифестах нет, найдены хешированием известного пути: Lua-библиотеки в `common` (например `Domino/System/Coop/LuaLibraries/LuaLibCoop.lua` = `common\__UNKNOWN\unknown\D2329431C5AD239C`, `Domino/System/LuaLibraries/LuaLibStateless.lua` = `6FD38B2074BAB4CB`).
- **В одиночной сборке у движка уже есть 4 слота игроков.** Бокс `Domino/System/Player/GetPlayerFromSlot` лежит в `fc3_main` и побайтно совпадает с боксом из `multicommon`. `LuaLibCoop:GetNrOfPlayers()` вызывает родную `GetNumberOfPlayers()` и превращает 0 или 1 в 2; `SetNrOfPlayersOverride` принимает 2..4. Боксы `GetPlayers` регистрируют `OnSpawnPlayer_0..3` через `CScriptCallbackSystem_GetInstance():RegisterGenericCallback`. `AllPlayers/TeleportPlayer` вызывает родную `CoopTeleportPlayer(игрок, цель)`.
- **Идентификаторы сущностей в Lua — десятичные строки** (`sprintf("%llu")` от 64-битного числа); неверный идентификатор даёт `GetInvalidEntityId()`.
- **Родные Lua-функции в `FC3.dll`** (таблица регистрации около `0x11b1d252`..`0x11b1df2e`; колбэк, который кладётся в стек прямо перед `mov edi, <строка имени>`, относится к этому имени; имена с `0x1206ad0c`: `SpawnCoopAI`, `GetSlotForPlayer`, `GetPlayerInSlot`, `CoopGetCharacterName`, `GetNumberOfPlayers`, `CoopDoGetPawnState`):
  - `GetLocalPlayerId()` = `FUN_1065ef50` -> `FUN_10c79cb0`: читает поставщика локального игрока `DAT_1280437c` (по смещению +8 объект, у которого слот vtable +0x10 возвращает указатель на 64-битный id), `-1` если его нет.
  - `GetPlayerInSlot(slot)` = `FUN_10680ef0` -> `FUN_10c73340(out, slot)`: глобальный указатель сессии `DAT_12804acc`; если байт `+0x6c` установлен, объект сессии `S = FUN_1039e1f0(*(DAT_12804acc+0x68))`; таблица слотов = `S+0xb8` (массив 32-битных дескрипторов, `-1` = пусто), размер в `S+0xbc`; дескриптор разворачивает `FUN_10260770` в объект игрока `P`, id сущности = `**(P+0xcc)`. Если слот 0 пуст, берётся `FUN_11305eb0()` (вероятно, локальный игрок одиночной игры). Остальные пустые слоты дают `-1`.
  - `GetNumberOfPlayers()` = `FUN_10681070`: `*(S+0x54)`, или 0 без сессии.
  - `CoopGetCharacterName(entity)` = `FUN_10680f90`; `GetSlotForPlayer` — соседний с `FUN_10680ef0` (не проверена); у `CoopTeleportPlayer` ссылка регистрации `0x11b1d252` (колбэк пока не разобран).
- **Вывод для выбора A/B.** Одиночная игра уже работает с объектом сессии, у которого есть таблица на 4 слота игроков. Если положить второй `P` (пешку-«куклу») в слот 1, то `GetPlayerInSlot(1)`, `GetNumberOfPlayers()` и все кооперативные боксы его увидят. Открытые вопросы: кто создаёт `S` и заполняет слоты в одиночной сборке, равно ли там `S+0x54` единице, как создать удалённую пешку (`SpawnCoopAI`, `OnSpawnPlayer`).
- Проверка правила пар: `GetNumberOfPlayers` -> `FUN_10681070` (без аргумента, возвращает число) и `GetPlayerInSlot` -> `FUN_10680ef0` (слот в строку id) совпадают с Lua-боксами; `FUN_10680f90` (сущность в строку) совпадает с `CoopGetCharacterName`.
- Дальше: декомпилировать `FUN_11305eb0`, `FUN_10260770`, `FUN_1039e1f0` (кто создаёт объект сессии и таблицу слотов); найти код `SpawnCoopAI` и `OnSpawnPlayer_%u` (`0x11fc1c64`); проверить `CoopTeleportPlayer`; затем небольшой тест: ASI, который пишет поддельный дескриптор в слот 1, и чтение `GetNumberOfPlayers` из Lua. (Частично сделано ниже.)

### Результаты фазы 1: сервис игроков — сетевой объект (2026-10-24)

- `S` — компонент **`CFCXPlayerService`**. `FUN_1039e1f0(контейнер)` перебирает массив компонентов (`контейнер+8`, количество `контейнер+0xc`) и возвращает тот, чей тип (слот vtable +4) совпадает со статическим типом из `FUN_1039e0d0` (`&DAT_12860b80`, имя `CFCXPlayerService`); последний индекс кэшируется в `DAT_1217a7d4`. Контейнер — `*(DAT_12804acc+0x68)`; на `DAT_12804acc` 4529 ссылок (центральный объект игры/сервисов).
- Класс **реплицируется по сети**: статический инициализатор по `0x11b6ff80` регистрирует `NetObject.FCXPlayerService` (дескриптор `0x12838424`) и сетевые сообщения `PlayerService_HidePlayerMessage` / `PlayerService_ShowPlayerMessage` (`0x1283842c`, `0x12838434`). Другие строки: `IPlayerService`, `CPlayerService`, `NetDiscoveryGroup.PlayerService`. Код сетевой регистрации: `FUN_11839b60`, `FUN_10468480`.
- Запасной вариант для слота 0, `FUN_11305eb0`, использует того же поставщика локального игрока, что и `GetLocalPlayerId` (`DAT_1280437c`), иначе статический неверный id. Значит, в одиночной игре слот 0 — локальный игрок даже при пустой таблице слотов.
- **Open World Co-op от scubrah (вторичные источники; страницы Nexus без входа отвечают HTTP 403):** онлайн-кооператив на карте одиночной игры с ИИ врагов, транспортом, аванпостами и всей картой, максимум игроков поднят до 8, сюжетных миссий нет, загрузка около 2 ГБ, альфа (2020-07-10). Источники: https://www.dsogaming.com/news/there-is-now-a-co-op-mod-for-far-cry-3-that-you-can-download/ , https://vgtimes.com/games/far-cry-3/files/24390-co-op-mode.html . По размеру похоже на перепакованный архив мира (остров как кооперативная карта), то есть собственная кооперативная сетевая сессия движка, запущенная на острове.
- **Рабочий вывод (пока не решение):** транспорт **A**, вероятно, жизнеспособен: кооперативная сессия движка уже работает на острове (scubrah), а сервис игроков, слоты и кооперативный Lua API есть в той же DLL. Не хватает сюжета: графы Domino одиночной игры используют `GetLocalPlayer` и ничего не знают о других игроках. Риск из PLAN.ru.md остаётся: как сегодня находить кооперативные сессии и подключаться к ним (может требоваться подбор игроков Ubisoft).
- Дальше: владелец скачивает мод 220 с Nexus (нужен вход) в `Downloads\fc3-open-world-coop\`, чтобы распаковать его архивы и сравнить с оригиналом; найти, как кооперативная сессия выбирает мир (строки `multicommon`, `fc3_main`, список кооперативных карт); найти путь подключения (прямой IP или LAN против сервисов Ubisoft). (Путь подключения: см. ниже.)

### Результаты фазы 1: сетевой транспорт и путь подключения (2026-10-24)

- **Сетевая библиотека: Ubisoft Storm** (`storm::echo::session`, `storm::echo::player`, `storm::echo::lan`, `storm::punch`). У сессий есть миграция хоста, билеты, запросы на вход, маршрутизация пиров через хост и обход NAT (`punchclient`, `punchtraversal`, `Storm NAT Client`).
- **Онлайн-сервисы: Ubisoft RendezVous** (`CGameMatchmakingProvider_RdV`, `CRendezVousInitPunchOperation`, `onlineconfigservice.ubi.com`, `/OnlineConfigService.svc/GetOnlineConfig?onlineConfigID=`). Меню игры использует этот путь. Работает ли он сегодня, неизвестно; быстрая проверка в игре — открыть кооперативное меню и создать закрытый матч.
- **LAN в движке есть:** `storm::echo::lan::inEvent::DiscoverSession`, `BroadcastLanDiscovery2`, `lan::outEvent::DiscoveredSession`, `lan::inFunc::GenerateSessionId`; настройки Storm `LanMatchmakingReuseAddress` («SO_REUSEADDR, чтобы несколько приложений хостили сессии на одной машине»), `LanMatchmakingDiscoveryOnLoopbackEnable` («искать сессии только на этой машине»), `LanMaxUploadInbps` / `LanInitialUploadInbps` / `LanMinUploadInbps`, а также `DisableRouting`, `ForceRouting`, `SessionJoinTimeoutInMs` и другие таймауты (строки около `0x11fb6f00`). В меню настроек есть «LAN Match Making Port» (`OPTIONS_NETWORK_LANMATCHMAKINGPORT`), но режима игры по LAN в английских строках интерфейса не найдено. Как игра переключается на LAN, пока не найдено.
- **Конфиги движка:** движок читает пары `engine\settings\Default<X>Config.xml` и `engine\settings\Override<X>Config.xml` для X = Engine, Network, EngineServices, Threading, Render, Sound, Game, Realtree (+ `ProfileSpecific*GameConfig.xml`, `*engineconfig_legacy.xml`). Файлы по умолчанию есть в `common` (по хешу): `DefaultNetworkConfig.xml` = `common\__UNKNOWN\misc\02E1D1848EC84585.Profile.xml`, `DefaultEngineConfig.xml` = `4C5BBCC4AC9D8E00`, `DefaultGameConfig.xml` = `50C61851314582D5`, `DefaultEngineServicesConfig.xml` = `5FDA7AF3F9DB5B99`. **Файлов `Override*` в игре нет**, поэтому наш архив может добавить `OverrideNetworkConfig.xml`, не заменяя файл игры.
- `DefaultNetworkConfig.xml`: `EnableNatTraversal=1`, `SecureSocketEnabled=1`, `MainSocketEncrypted=1`, `MaximumPeerCount=25`, `MigrationEnabled=1`, `OnlineEnginePort=9000`, `OnlineServicePort=9001`, `FileTransferHostPort=9002`, `FileTransferClientPort=9003`, `LanHostBroadcastPort=9004`, `LanClientBroadcastPort=9005`, `ScanFreePorts=1` с 9000 на 1000 портов; фильтры сетевого журнала (в том числе `session`, `lanmanager`) и **профили эмуляции сети** `moderate` / `high` (потеря, задержка, перестановка пакетов), включаются через `EmulatorEnabled` + `EmulatorProfile`. Полезно для проверки задержек на одном ПК.
- **Параметры подключения:** `FUN_11342740` регистрирует поля структуры параметров сессионной операции: `SearchIdAddress` (+0x8), `SearchSessionId` (+0x10), `JoinSessionId` (+0x18), `SessionRefId` (+0x20), `DeleteSessionId` (+0x28), `PlaylistId` (+0x34), `SessionType` (+0x38), `NetEngineType` (+0x3c), `AccountType` (+0x40), `SearchRetries` (+0x44), `SearchSlots` (+0x48). Рядом строки: `JoinGame`, `JoinService`, `MatchMakingEnabled`, `fullNetworkInitialization`, `isInEditor`, `execLines`, `mapIdLow` / `mapIdHigh`, `saveGameFilename`. Состояния сетевого движка: `ENetEngineState_Initialized_Offline` / `_Online`. Операции: `CFCXCreateSessionOperation`, `CFCXJoinSessionOperation`, `CFCXNetEngineStartupOperation`, `CSessionNetEnginePlayerAddOperation`.
- Найден флаг командной строки: `-enablenetobjectstats`.
- **Что это значит для плана.** У транспорта A два возможных пути подключения: (1) LAN-обнаружение Storm, выведенное в интернет так же, как в моде Far Cry (2004) (ретранслятор через localhost плюс приглашение Steam); (2) онлайн-путь Ubisoft, если его сервисы ещё работают. Оба нужно проверить в игре. Неизвестно, что включает LAN (значение `NetEngineType`, опция конфига или ветка кода).
- Дальше (статика): найти код, который читает `NetEngineType` (смещение +0x3c), и создателя LAN-менеджера (`lan::inEvent::SetDiscoveryHandler`); (в игре, ПК владельца): проверить, доходит ли штатное кооперативное меню до сервисов Ubisoft.
- **Обновление 2026-10-24 (владелец):** онлайн-сервисы Ubisoft для Far Cry 3 отключены. Путь через RendezVous отпадает; транспорт A должен идти через LAN Storm (выведенный в интернет нашим ретранслятором), иначе откат на B. Ссылки на `LanMatchmaking*` и типы событий `lan` по `0x1070de..` — только таблицы регистрации типов; код, запускающий LAN-обнаружение, пока не найден.

### Инструменты: упаковщик архивов и исправление распаковщика (2026-10-24)

- **Список архивов, которые грузит движок** (`0x120701c4`): `patch.dat`, `patch_%lang%.dat`, `patch_sound_%lang%.dat`, `common.dat`, `sound.dat`, `sound_%lang%.dat`, `ige.dat`, `igepatch.dat`, `shadersobj.dat`, `worlds/fc3_main/fc3_main{,_%lang%,_vistas}.dat`, `worlds/multicommon/multicommon{,_%lang%,_vistas}.dat`; ещё строки `_2.dat`, `subfat_%s.fat`, `mergedBigFileName` (смысл неизвестен). Значит, мод поставляет пересобранный `patch.dat/fat` = штатное содержимое patch плюс наши файлы (так же был устроен мод владельца на пропуск роликов).
- **Устройство FAT v9 (проверено на штатных `patch.fat` и `common.fat`):** заголовок 24 байта `FAT2`, версия 9, флаги `0x301` (платформа 1 = Windows, версия сжатия 3), `u0C = u10 = 0`, число записей; записи по 20 байт, отсортированы по хешу; затем 8 нулевых байт. У несжатых записей схема 0, `UncompressedSize = 0`, размер в `CompressedSize`. Смещения данных в штатных файлах не выровнены.
- **Упаковщик:** новый проект `Gibbed.FarCry3.Pack` (`bin_fc3\Gibbed.FarCry3.Pack.exe output.fat input_dir`, файлы без сжатия). Изменения в Gibbed: `BigFileV2.Serialize` реализован только для v9; `Pack` принимает версию и версию сжатия по умолчанию (9, 3 для FC3); файлы из `__UNKNOWN` теперь сохраняют 16-значный хеш (старый код обрезал до 8 цифр, что годится только для 32-битных хешей). LZO-сжатие в исходном проекте по-прежнему не реализовано (не нужно).
- **Ошибка распаковщика, исправлена:** распаковщик читал несжатые записи по `UncompressedSize`, а в FC3 там 0, поэтому каждый несжатый файл записывался **пустым** в `__UNKNOWN\null\`. Затронуто в результатах фазы 1: `patch` 4 файла (два видео `.bik` по 136 МБ и 63 МБ, два материала), `common` 429, `multicommon` 17108, `fc3_main` 11799 файлов и 16 файлов в `named\`. Исправлено в `EntryDecompression.cs` и в определении типа в `Unpack.cs`; все четыре архива распакованы заново с исправлением: `patch` 427, `common` 3099, `multicommon` 122255, `fc3_main` 64354 файла, пустых файлов нет; `names.tsv` и `named\` пересобраны (45045 имён, 0 пустых текстовых файлов). Вспомогательные скрипты (хеширование имён, разбор FAT, перераспаковка): `scripts\`.
- **Круговая проверка:** штатный `patch.fat` распакован, упакован снова и снова распакован: 427 из 427 файлов совпали (MD5).
- Для сборки нужен локальный кэш NuGet (про мод scubrah и версию 1.05 см. ниже): `$env:NUGET_PACKAGES='E:\FarCryCoop\Data\nuget'`, `dotnet build ... --source E:\FarCryCoop\Data\nuget` (`env.ps1` его не задаёт). Файл патча: [docs/gibbed-dunia-fc3.patch](docs/gibbed-dunia-fc3.patch).

### Open World Co-op от scubrah, patch 1.5 (2026-10-24)

- Владелец скачал в `Downloads\fc3-open-world-coop\` (Nexus, мод 220). Readme: ставить поверх игры; «создать закрытую кооперативную сессию в главном меню и сменить главу на ROOK ISLANDS / fc3_main»; одиночная игра и штатные кооперативные карты при установленном моде не работают. Закрытая сессия идёт через онлайн-сервисы Ubisoft, а они отключены (владелец, 2026-10-24), поэтому в исходном виде мод не запустится.
- **Его DLL — другая сборка движка:** `FC3.dll` 29994856 байт, время PE 2018-05-02, PDB `E:\Work\FC3_Chinese\sub-pc\bin\FC3.pdb` (у нас: 2022-10-03, `F:\Projects\FC3\bin\FC3.pdb`, 40720424 байта). Вариант `No_Minimap` отличается 6 байтами данных (`A`/`H`/`R` -> `X` по смещениям файла `0x159c8b4`..`0x15cfbf6`). Остальные правки DLL мода точно найти можно только сравнением с чистой DLL той же сборки.
- **Версии:** нынешняя сборка Steam (1.06, 2022) без мультиплеера; 1.05 — последняя версия с ним (гайды сообщества). Манифест депо 220241 для 1.05 по гайду Steam: `7362101836779063707` (ещё не проверен). Мод Nexus 262 «Solo Offline Coop Game Mode» (на базе 1.05) запускает кооперативный режим офлайн и служит образцом запуска сессии без серверов.
- **Архивы:** `patch.fat` мода — 3316 записей (оригинал 427): 2864 мировых сектора `.fcb` (`WorldSector` / `MissionLayer` / `Entity`), 404 Lua (основные миссии 150, `fc3_master` 91, DLC 66, `lib_*`), конфиги. `fc3_main_vistas` мода — 129894 записи, 3 ГБ (оригинал 13261, 150 МБ); около 100000 совпадают по хешу с `multicommon` и 25000 с `fc3_main`, 14309 новых. Распаковано в `Work\fc3\mod\`; штатный vistas в `Work\fc3\fc3_main_vistas\`. Полное сравнение содержимого: `Work\fc3\mod\compare.tsv` (скрипт `scripts\contentcompare.py`).
- **Конфиги мода:** `DefaultNetworkConfig.xml` включает эмулятор сети с новым профилем `upstream32k`, где `upload_bandwidth bits_per_sec="0"` (без потерь и задержек), ставит `ObjectTrafficStatsEnabled=1` и удваивает лимиты отдачи до 20480000. Два `Profile.xml` движка увеличивают кольца стриминга (`RingData="15,16,10,20,1"`, `RingLod="10,12"`) и лимиты физики. Автор пользовался FCBConverter (ArmanIII) для `.fcb` <-> XML.
- **План:** скачать чистые `bin` и `patch` версии 1.05 через DepotDownloader 3.4.0 (`Tools\depotdownloader-3.4.0`, SHA-256 архива `41C9E9F0DF54B3AD02E67A11726756E5C73283BD7C2E1B04ACFA5AE4C2ED3767`, размер сверен с релизом GitHub; exe без подписи) в `Downloads\fc3-1.05\`, список файлов `scripts\fc3-105-filelist.txt`; запускает владелец со своим входом в Steam. Затем сравнить чистую DLL 1.05 с DLL мода и получить точные правки мода.

### Чистая 1.05 и точные правки DLL мода (2026-10-24)

- Владелец скачал DepotDownloader-ом (вход `-qr`) в `Downloads\fc3-1.05\`: `bin\` и `data_win32\patch*`, `igepatch*`. `FC3.dll` 1.05: 29994856 байт, SHA-256 `98e34155266de3627202e520bff92b2be17a21ee3f89d9a6213915b83e9e1166`, время PE 2018-05-02, GUID PDB `b0ba4c20...` = та же сборка, что DLL мода. Значит, манифест `7362101836779063707` — это 1.05 и основа мода scubrah. В `bin` версии 1.05 ещё есть `uplay_r1_loader.dll` и `ubiorbitapi_r2_loader.dll`.
- **Решение владельца:** поддерживать и 1.05, и 1.06 (PLAN.ru.md).
- **Правки DLL от scubrah = 90 байт в 45 местах**, одинаковые в `FC3.dll` и `FC3_d3d11.dll` (скрипт `scripts\patchctx.py`; адреса для `FC3.dll` 1.05):
  - `.rdata` `0x11535dd0`: строка `mpdlc1_aegir` -> `fc3_main`. Имя карты мультиплеерного DLC заменено на мир одиночной игры — так остров появляется как глава кооператива.
  - границы мира для сетевого квантования: блок по `0x11535bb0` и отдельные float: +/-1536 -> +/-5120, +/-1029 -> +/-5120, 1535.99/2047.99/1279.99 -> 5119.99, 127.99/255.99 -> 511.99/512, 129 -> 512, 153600 -> 512000, 12900 -> 51200, 1.536e6 -> 5.12e6. Кооперативные карты примерно 3 км в ширину, остров около 10 км.
  - код: три помощника сериализации `push 8` -> `push 9` (`0x1027b5da`, `0x1027b5fb`), `push 6` -> `push 7` (`0x1027b627`, `0x1027b648`), `push 7` -> `push 8` (`0x10592f7a`, `0x10592f9b`): по одному биту больше в парах (запись и чтение), под больший диапазон координат.
  - имена, переименованные, чтобы выключить функции (`F`/`C` -> `X`): свойства смены FOV камеры (`fBlendOutFOVTime` и другие), `CRadioTowerPanelComponent`, `CoopNameplatesUI` / `CFCXCoopNameplatesUI` (readme: «Removed NPC tag icon»). Вариант `No_Minimap` добавляет ещё 6 таких байт.
- **Переносимость на 1.06:** якоря данных в DLL 1.06 есть (`mpdlc1_aegir` по смещению файла `0x1f893b4`, блок границ по `0x207b8e0`, `CoopNameplatesUI`, `fBlendOutFOVTime`), но три шаблона кода сериализации побайтно не совпадают; нужно сопоставление функций.
- **Архивы мода по содержимому** (`Work\fc3\mod\compare.tsv`, сравнение с данными 1.06): `fc3_main_vistas`: 115585 файлов побайтно совпадают со штатными (`multicommon`, `fc3_main`, vistas) плюс 14309 новых; `patch`: 396 совпадают, 64 изменены, 2856 новых (2827 мировых секторов `.fcb`). Являются ли новые файлы штатными под новыми именами — проверяется (`dupcheck.py`).
- **Скрипт карты адресов** `scripts\fc3_addrmap.py` (без Ghidra, секунды): находит строки-якоря, ссылки из кода, зарегистрированный колбэк и глобалы, которые колбэк читает. Понимает оба вида регистрации: 1.06 `push 0; push CB; call; mov edi, имя` (колбэк перед именем) и 1.05 `push имя; push esi; push edi; call; push ebx; push CB; push edi; call` (колбэк после имени). Самопроверка по вручную подтверждённым значениям 1.06 (`--selftest`): проходит. Результат: `Work\fc3\addrmap-105.tsv`, `addrmap-106.tsv`.
- Колбэки 1.05, **подтверждённые декомпиляцией** (снимок REA `E:\FarCryCoop\Data\rea-snapshots\fc3-105-FC3.dll.snapshot`): `GetPlayerInSlot` `0x10bad843` (целый слот -> 64-битный id), `GetNumberOfPlayers` `0x10baba48` (без аргумента -> число, через `FUN_10bca625`), `CoopGetCharacterName` `0x10badb62` (аргумент `EntityId`), `CoopDoGetPawnState` `0x10bad8b5` (целый аргумент -> число); из скрипта, ещё не декомпилированы: `GetLocalPlayerId` `0x10bb3f60`, `GetSlotForPlayer` `0x10bad7cb`, `CoopTeleportPlayer` `0x10bac7d0`, `SpawnCoopAI` `0x10bae756`, `GetInvalidEntityId` `0x10bb7709`. В обеих сборках одинаковая раскладка: колбэк кладётся в стек прямо перед именем (прежнее правило «колбэк после имени» для 1.05 было неверным и убрано из скрипта; `--selftest` теперь проверяет обе сборки).

### Мод Nexus 262 «Solo Offline Coop Game Mode» (2026-10-24)

- Владелец скачал в `Downloads\fc3-solo-offline-coop\`: `FC3.dll`, `FC3_d3d11.dll`, `patch.dat/fat` (дата 2022-07-20), сделан на 1.05.
- **DLL: всего две правки**, обе заменяют `call 0x108c4b09` пятью NOP (в `FC3.dll` 1.05 по `0x108c4c6b` и `0x108c5c36`; в `FC3_d3d11.dll` смещения файла `0xa1e1e2`, `0xa1f1ad`). Контекст: `74 07 8b ce e8 ..` и `80 7d ff 00 74 07 8b cb e8 ..` (вызов только при установленном флаге). Гипотеза: проверка, которая выводит из сессии при отсутствии онлайн-сервисов. Подтвердить декомпиляцией (анализ 1.05 в REA идёт).
- **patch: штатный patch 1.05 (427 файлов, без изменений) + 4 файла:** переопределения из `common` `9B788D77FCFA35BB.fcb` (игровая база, 1040772 -> 2617955 байт; новых строк всего 12, значит в основном числовые и структурные изменения) и `E88B7431DC8E7DBF.feu` (интерфейс главного меню в контейнере Ubisoft `UEF`, +3 КБ); `36A67CE0D3C22326.xml` (раскладка управления, тот же файл есть у scubrah); один Lua `coop_vidar_defend` «AllInRoom» с закомментированным роликом закрытия двери.
- Дальше: декомпилировать `0x108c4b09` и два места вызова в 1.05; распаковать меню `UEF` (JPEXS или свой разборщик), чтобы увидеть изменение меню; перевести `.fcb` через FCBConverter, чтобы увидеть изменение базы.
- **FCBConverter** (Jakub Marecek, ник ArmanIII; исходники https://github.com/JakubMarecek/FCBConverter, сборка 20230711-1830 с https://downloads.fcmodding.com/files/FCBConverter.zip, хеш автор не публикует; SHA-256 архива `803B04CC9DA0D40BF2CB390C1D1C0EB26D6AFFDAD1E6D4E0360EED8E63B3BDCE`) в `Tools\fcbconverter-20230711\FCBConverter\`. Поддерживает FC3 (FAT v9). Нужен .NET 7; работает на нашем переносимом .NET 8 с `DOTNET_ROOT=E:\FarCryCoop\Tools\dotnet-sdk-8.0.426` и `DOTNET_ROLL_FORWARD=Major` (без установки на C:). Запуск: `FCBConverter.exe -source=<file.fcb>` пишет `<file>.converted.xml`. В комплекте `FCBConverterFileNames.list` (4189677 имён файлов) и `FCBConverterStrings.list` (483419 строк), по ним можно назвать больше наших хешей.
- **Изменение базы в моде 262** (`9B788D77FCFA35BB.fcb`, переведено в `Work\fc3-105\fcb\`): всего два поля в плейлисте **«Local Coop»** (`id` 0xFFFFFFFC, `sessionType` 3, `maxPlayersInRound` 2): `minPlayersInRound` 2 -> 1 и `matchCountdownInSecs` 0 -> 10. Бинарник больше только из-за способа записи конвертером. Плейлисты в штатной базе: `sessionType` 2 = User (12), Beta Test (14), Map Archive (14), Private Coop (4); `sessionType` 3 = Local Coop (2). Значит, мод 262 запускает штатный тип сессии «Local Coop» (вероятно, консольный split-screen) с одним игроком, без серверов. Это офлайн, а не сетевая игра, но видно, что кооперативный мир стартует без сервисов Ubisoft.
- **Что за новые файлы мода scubrah** (`dupcheck.py`: из 17165 «новых» только 6 — штатные файлы под другим именем): 2827 новых `.fcb` в `patch` — мировые секторы с собственными сущностями автора `CoopAI_EncounterPawn_<случайное>` (кооперативные ИИ-противники, с точками укрытия) и `CoopVehicle_<случайное>` (транспорт с вариантами разрушения); случайные суффиксы значат, что их сгенерировал инструмент. То есть остров заселён кооперативными спавнерами ИИ и машинами вместо скриптов одиночной игры. 14309 новых файлов vistas начинаются с `04 4B 50 53` (вероятно, звуковые пакеты `.spk`). Образцы: `Work\fc3\mod\sample\`.
- **Больше имён файлов:** `scripts\names_ext.py` хеширует 4189677 путей из `FCBConverterFileNames.list`: +84934 имени (из 192788 файлов с хешем в штатных архивах и архивах мода, без имени осталось 62809). Результат `Work\fc3\names_ext.tsv` (столбец `source` = manifest или fcbconverter); ещё 1395 Lua/XML скопированы в `named\`. Ключевые имена: `9B788D77FCFA35BB` = `generated\nomadobjecttemplates.fcb` (шаблоны объектов, включая плейлисты), `E88B7431DC8E7DBF` = `ui\multiplayer\menu\multimain.feu` (главное меню мультиплеера, его меняет мод 262), `8BDCD85D74264EB2` = `engine\settings\pc\defaultengineconfig.xml`, `36A67CE0D3C22326` = `actionmaps\inputactionmapcommon.xml`; секторы scubrah — `worlds\fc3_main\levels\<клетка>\generated\worldsectors\worldsector_<n>.data.fcb` (2834 файла, в штатных архивах их нет).
- **Правки DLL мода 262 выключают «сессия завершена: мало игроков» (декомпилировано, 1.05):** `FUN_108c4b09` сбрасывает `[this+0x180]`, создаёт окно-сообщение на 0xE4 байта (vtable `0x1156d990`) с текстом из таблицы id строк по `0x115ac030` = {167676, 167677, 167678} = `*_END_OF_GAME_INSUFFICIENT_PLAYERS` («The game session ended prematurely because of an insufficient number of players.») и заголовком 160927 («Alert»; его enum — `MP_LinkApp_Passport_Locked_Alert`, но строка просто используется как общий заголовок), затем отправляет событие типа `DAT_118644bc` (завершение сессии). Вызовы в 1.05: `FUN_108c4c48` по `0x108c4c6b` (`if (тип события == DAT_118644bc && [this+0x180]) ...`) и `0x108c5c36` (после цикла по игрокам, если флаг остался 0). Это ровно те два вызова, которые мод 262 заменяет NOP. **Исправление:** раньше здесь было написано, что это проверка Uplay Passport — по имени enum заголовка; это было неверно, проверкой лицензии это не является.
- **Та же функция в 1.06:** таблица id строк по `0x11ffac34`, ссылка из `0x10ff276f`, начало функции `0x10ff2750`; три вызова: `0x10fddbc8` и `0x10ff3be4` (`cmp eax,[0x1283a184]; jne; cmp byte [reg+0x180],0; je; push reg; call`, проверка типа события) и `0x10ff2adc` (`cmp byte [esp+0x13],0; je; push edi; call`, после цикла по игрокам). Подтверждено декомпиляцией 1.06: `FUN_10ff2750(param)` сбрасывает `[param+0x180]`, берёт текст из `0x11ffac34`, заголовок `0x2749F`, отправляет событие типа `DAT_1283a184`; объект передаётся через стек (отсюда `push reg` в местах вызова). Снимки REA: `E:\FarCryCoop\Data\rea-snapshots\fc3-105-FC3.dll.snapshot` (38 КБ) и `fc3-106-FC3.dll.snapshot` (11 КБ); они маленькие, поэтому, вероятно, хранят только доказательства и пометки, а не базу Ghidra; избавляет ли открытие с ними от повторного анализа, пока не проверено.
- **Решение владельца 2026-10-24: завершение «сессия окончена: мало игроков» в нашем моде выключается** (как в моде 262), чтобы сессия шла и с одним игроком. Владелец одобрил это, когда считалось, что это проверка Passport; после декомпиляции оказалось, что это правило числа игроков, а не проверка лицензии. Собственная защита игры (запуск через Ubisoft Connect с лицензией на аккаунте) не трогается; каждому игроку нужна своя копия.

### Прототип v0: одиночная кооп-сессия без серверов, собранная нашими инструментами (2026-10-24)

- **Тестовые копии** (`scripts\build_testgame.ps1 -Version 1.05|1.06`): `E:\FarCryCoop\Work\game-105` и `game-106`. `bin\` — настоящая копия (1.05 из `Downloads\fc3-1.05`, 1.06 из установки); в `data_win32\` 94 жёсткие ссылки на архивы установки (тот же диск, места не занимают) и настоящие копии `patch*` / `igepatch*`. Файл-ссылку нельзя менять на месте, только заменять новым файлом. `Support\` не копируется. Установка проверена после: хеши `FC3.dll` и `patch.fat` не изменились. Штатный `patch.fat` одинаков в 1.05 и 1.06.
- **Патчер DLL** `scripts\patch_dll.py`: находит функцию «мало игроков» по её таблице id строк и заменяет каждый её вызов NOP; работает на всех четырёх DLL; отказывается работать с путями внутри установки Steam; `--selftest`: пропатченные `FC3.dll` и `FC3_d3d11.dll` 1.05 побайтно равны файлам мода 262, повторный запуск ничего не меняет. Применён к тестовым копиям: 1.05 `FC3.dll` функция `0x108c4b09` (вызовы `0x108c4c6b`, `0x108c5c36`), `FC3_d3d11.dll` `0x10a1ec80` (`0x10a1ede2`, `0x10a1fdad`); 1.06 `FC3.dll` `0x10ff2750` (`0x10fddbc8`, `0x10ff2adc`, `0x10ff3be4`), `FC3_d3d11.dll` `0x10ff7f90` (`0x10fe33f8`, `0x10ff831c`, `0x10ff9424`).
- **Правка базы** `scripts\edit_playlist.py` по XML FCBConverter для `generated\nomadobjecttemplates.fcb`: плейлист «Local Coop» `minPlayersInRound=1`, `matchCountdownInSecs=10`; обратно через FCBConverter: побайтно совпадает с файлом мода 262 (SHA-256 `9A3C6D8D...`).
- **Архив patch** `scripts\build_patch.ps1` -> `Work\mod-build\patch.dat/fat`: штатный patch (427 файлов) + наш `generated\nomadobjecttemplates.fcb` + **только для теста, чужой** `ui\multiplayer\menu\multimain.feu` из мода 262 (не наш, в релиз не идёт; заменить своей правкой меню). Проверка распаковкой: 429 файлов. Установлен в обе тестовые копии.
- Дальше: владелец запускает `Work\game-105\bin\farcry3.exe` (потом 1.06) и пробует меню мультиплеера -> Local Coop одним игроком. Ожидается: кооперативная карта (пока без острова) грузится в одиночку без окончания «insufficient number of players». Тестовая копия 1.05 использует архивы данных 1.06 (из 1.05 только `bin` и `patch`); если не загрузится — скачать депо 1.05 целиком.

### Тесты прототипа v0 на ПК владельца (2026-10-24)

- **1.06** (`Work\game-106`, наш мод): запускается; кнопка «Мультиплеер» сразу показывает «The online multiplayer service is not available anymore.» Откуда: `FUN_11751440` (получение строки по id, 1.06) возвращает зашитый текст UTF-16 (английский по `0x11f17378`, переводы рядом, выбор в `FUN_11750980`), когда id строки = `0x23894` = 145556 = `X360_EU_NETWORK_XLSP_DOWN` («The Far Cry 3 service is not available. Please try again later.»). То есть 1.06 по-прежнему пытается подключиться к онлайн-сервису Ubisoft при входе в мультиплеер; Ubisoft поменяла только текст. Чтобы попасть в кооп-сессию в 1.06, этот путь онлайн-входа нужно обойти в коде.
- **Запуск 1.05:** `farcry3.exe` (DX9) в полноэкранном режиме даёт чёрный экран (при `UseD3D11` 1 и 0 в профиле); `farcry3_d3d11.exe` работает в полноэкранном; `farcry3.exe` работает в окне (`Fullscreen="0"`). Профиль `C:\Users\<user>\Documents\My Games\Far Cry 3\GamerProfile.xml` общий для 1.05 и 1.06. С разрешения владельца для тестов изменён: `UseD3D11="0"`, `Fullscreen="0"`; копия оригинала: `E:\FarCryCoop\Work\fc3-profile\GamerProfile.xml.bak` (вернуть после тестов). Логов игра туда не пишет.
- **Данные 1.05:** манифест депо 1.05 (`Downloads\fc3-1.05-manifest\`, 326 файлов, 2018-05-21) совпадает с установкой 1.06, кроме `bin\` и двух лишних файлов 1.05 `worlds\multicommon\multicommon_japanese.dat/fat` (скачаны, теперь в `game-105`; `build_testgame.ps1` их копирует). 8 отличий `sound_*.dat` — ложное срабатывание (пустые файлы; манифест пишет для них нулевой SHA-1).
- **1.05 с модом:** чистая 1.05 показывает только «online co-op»; с нашим patch (и с точным patch мода 262) в меню Coop появляется **«Offline coop»**, но его запуск **вылетает**: нарушение доступа в одной и той же функции в обеих сборках: `FC3.dll` `FUN_10622c58`+0x27 (`0x10622c7f`, DX9) и `FC3_d3d11.dll` `0x1077e1bd`+0x27 (`0x1077e1e4`). Код обходит массив: `mov esi, <результат вызова>; cmp [esi], 0; jbe ...; mov eax, [esi+4]; mov eax, [eax+ebx*4]` -> число элементов > 0, а указатель на данные битый. Причина не в наших инструментах (точный patch мода 262 падает так же), не в японском архиве и не в рендере. Декомпилирую `FUN_10622c58` (анализ 1.05 в REA идёт).
- **Вылет Offline coop: причина и исправление (2026-10-25).** `FUN_10622c58` (1.05) обходит список, который возвращает `FUN_10622144`, а та вызывает `UPLAY_PARTY_GetFullMemberList(this+0xc0)`; нынешний Ubisoft Connect больше не обслуживает API групп Uplay, вызов падает с ошибкой (`UPLAY_GetLastError`), в списке остаётся мусор (число > 0, битый указатель) и цикл падает. Прямых вызовов `FUN_10622c58` нет (вызывается через таблицу). Исправление в `patch_dll.py`: `jbe`, который пропускает пустой список, становится `jmp` (один байт, `76 3C` -> `EB 3C`), ищется по шаблону `call; mov esi,eax; xor ebx,ebx; cmp [esi],ebx; jbe +3c; mov eax,[esi+4]; mov eax,[eax+ebx*4]`: 1.05 `FC3.dll` `0x10622c7a`, `FC3_d3d11.dll` `0x1077e1df`; в 1.06 шаблона нет (новый API UPC). Самопроверка: наши DLL 1.05 = DLL мода 262 + ровно этот байт.
- **Прототип v0 работает на 1.05 (тест владельца, 2026-10-25):** `Work\game-105` с нашим архивом patch и пропатченными DLL: меню Coop -> «Offline coop» -> кооперативная карта загружается с одним игроком, без вылета и без «insufficient number of players». Тестовый профиль на C: всё ещё в оконном DX9 (копия в `Work\fc3-profile\`).

### Сессионный слой PC 1.05: LAN-провайдера нет (2026-10-25)

- Флаги аккаунта (`FUN_110d39c8`): `Offline` 1, `LAN` 2, `Live` 4, `Gator` 0x20, `Rendezvous` 0x40. Поля операции входа (`FUN_104c0f03`): `login` (+4), `password` (+8), `onlineKey` (+0xc), `guestlogin` (+0x10), `primaryAccount` (+0x14), `accountFlags` (+0x18), `controllerIndex` (+0x1c), `silentLogin` (+0x1d), `isPrimaryIndex` (+0x1e), `platformSpecificId` (+0x20).
- В сетевом конфиге (`FUN_1024dbef`, профиль `NetworkProfile` / `engine\settings\*NetworkConfig.xml`) есть список `Accounts` из `Account` (`CAccountConfig`, смещение 0x6c) и строка `SessionProvider` (0x64). Тест с разрешения владельца: в `GamerProfile.xml` добавлено `<Accounts><Account login="Host" accountFlags="2" .../></Accounts>` (копия `Work\fc3-profile\GamerProfile.xml.before-lan`): игра запускается, меню не меняется.
- Причина: все игровые онлайн-провайдеры в PC-сборке есть только в вариантах `_RdV` (Ubisoft RendezVous), `_UplayPC` или `_Win`: `CSessionLoginOperationProvider_RdV`, `CGameMatchmakingProvider_RdV`, `CGameInviteProvider_RdV`, `CGameFriendProvider_RdV` / `_UPlayPC`, `CGamePartyProvider_UplayPC`, `CGameFrontendServiceProvider_RdV` / `_Win` и другие. LAN-провайдера нет; `storm::echo::lan` в Storm есть ниже, но игровой слой PC его не использует.
- Другое найденное: ключ командной строки `-offline` (`FUN_10680f27` выбирает режим сообщений; `FUN_10922ac6`, отладочное главное меню с «COOP Story» / «Adversarial» / «UPlay» / «!What Sebra did before this ;)!», скрывает онлайн-пункты), `-splitscreen`, `-splitscreen4`, `CFCXSplitScreenService`, `CGRQueryIsLocalCoopGame`, `OfflinePlaylist`.
- **Вывод:** без сервисов Ubisoft сетевая кооп-сессия на PC требует одного из: (A1) свои замены провайдеров `_RdV` входа / подбора / приглашений в ASI (отвечать локально и создавать или подключаться к сессии Storm по адресу); (A2) локальный эмулятор сервиса RendezVous (перенаправить хосты сервиса на него); (B) свой сетевой код поверх работающей локальной сессии «Offline coop». Решить дальше.

### Быстрый запуск разработчиков: прямой хост / клиент без подбора игроков (2026-10-25)

- `FUN_10652061` (1.05, один вызов `0x10652215`) проверяет командную строку: `-host` -> `FUN_106518ba`, `-client` -> `FUN_10651d10`, `-wait`, `-quickmatch`.
- **Хост** (`FUN_106518ba`): нужен `-login <имя>`; читает `-host <значение>` (карта), `-bfname`, `-dedicated`, `-sessionuid <u64>`, режим `-deathmatch` / `-coop` / `-domination` / `-headquarters` / `-firestorm` / `-dash`, `-class`, `-spawn`, `-spawnpos x,y,z`, `-spawnangle`, `-netemulator <профиль>`, `-ranked`. Тип сессии = **3 без `-online`** (тот же локальный тип, что у плейлиста «Local Coop»), 2 с `-online`.
- **Клиент** (`FUN_10651d10`): нужны `-login <имя>` и `-ip <адрес>` («Missing -login or -ip for -client.»); `-online` дополнительно требует `-password`; для `localhost` своя ветка; те же режимы, `-sessionuid`, `-class`, `-ranked`.
- Другие найденные ключи: `-xpos -ypos -xres -yres` (окно), `-numclients`, `-offline`, `-quickstartup`, `-skipintro`, `-world`, `-exec`, `-execline`, `-login2..4`, `-password2..4`, `-splitscreen`, `-splitscreen4`, `-netemulator`, `-cmdport`, `-logFile`, `-steam_mode`, `-fromuplay`.
- Имена кооперативных карт: `coop_vidar`, `coop_skadi`, `coop_freyja`, `coop_huginn`, `coop_sleipnir`, `coop_fenrir`; ещё `fc3_main`, `mpdlc1_aegir`, `mpdlc1_idun`.
- Доступные сессионные операции: `CSessionCreateOperation`, `CSessionSearchIPOperation`, `CSessionJoinOperation`, `CSessionStartNetOperation`, `CFCXCreateSessionOperation`, `CFCXJoinSessionOperation` и другие. Провайдер входа `CSessionLoginOperationProvider_RdV` (геттер типа `0x110cdef8`, vtable около `0x11696d98`, методы `0x110cd961`, `0x110cd71d`, `0x110ccb46`, `0x110cc8ac`) — машина состояний заданий RendezVous.
- Скрипт теста: `scripts\launch_105.ps1 -Role host|client [-Map coop_vidar] [-Ip 127.0.0.1] [-Dx9]` (два оконных экземпляра рядом; по умолчанию DX11 `farcry3_d3d11.exe`).

### Тест быстрого запуска: хост + клиент на одном ПК (2026-10-25)

- **Проверка второго запуска.** Вторая копия останавливается с «You already have a Far Cry 3 session (game or editor) active or left open after an irregular shutdown» (`ERROR_INSTANCE_MUTEX`). Код при запуске: `push 0x1f0001; call [OpenMutexA]; test eax,eax; jnz <ошибка>`. `patch_dll.py` заменяет `jnz` на 6 NOP: 1.05 `FC3.dll` `0x100041bb`, `FC3_d3d11.dll` `0x10004092`. Теперь две копии работают рядом.
- **Сетевой адрес.** Хост открывает UDP 9000 на первом адаптере, здесь это адаптер VirtualBox `192.168.56.1`, а не `127.0.0.1`; клиент открывает 9001. Клиент запускался с `-ip 192.168.56.1`.
- **Результат:** хост загружает `coop_vidar` (мир виден за меню); клиент, похоже, подключается и показывает тот же экран. Затем у обоих пустая тёмная панель без текста и кнопок; картинка не обновляется (следы курсора), ввод не работает. После нажатия кнопки «ОК» на хосте то же самое. Одинаково в DX9 и DX11, с оверлеем RivaTuner (RTSS) и без него.
- **Это не зависание:** оба процесса отвечают Windows; главный поток занимает одно ядро и выполняет разный код игры и вызовы драйвера (`scripts\thread_eips.ps1` снимает EIP потоков и ищет в стеке адреса `FC3*.dll`).
- **Подозрения / дальше:** (1) чужой тестовый `multimain.feu` из мода 262 в нашем `patch.dat` ломает интерфейс сетевого меню: повторить тест с пропатченной DLL и штатным `patch.dat`; (2) экран лобби (выбор персонажа / готовность), который ждёт ответа от отключённых онлайн-сервисов; (3) проанализировать `FC3_d3d11.dll` в REA и разобрать адреса из стека главного потока (например `0x10338ad4`, `0x102f1b1d`, `0x103e07db`, `0x1040aaa3`, `0x10327bbd`).


---

## Дозаписанные сессионные заметки, 2026-11-02 (агентская сессия на этой машине)

Эти разделы написаны в агентской сессии. Материал Phase 1 здесь не повторяется:
первоисточником по Phase 1 остаются разделы владельца выше («Фаза 1: … и т.д.).
Новые находки переносятся и в английскую, и в русскую версию — правило двуязычия
записано ниже в AGENTS.md.
### Ghidra-адреса из 1.05 `FC3.dll` (заметки Phase 1; против 1.06 не перепроверены)

Это имена, которые Ghidra присвоил функциям 1.05-исполняника. Это единственное место, где
записаны хендлеры загрузчика и точки входа сервисов игроков, поэтому они сохранены даже тогда,
когда файла 1.05 на машине нет. Все адреса — в `FC3.dll` (1.05).

| Элемент | 1.05 адрес | Роль |
| --- | --- | --- |
| хендлер `-host` | `FUN_106518ba` | запуск host-сессии из командной строки |
| хендлер `-client` | `FUN_10651d10` | запуск client-сессии из командной строки |
| хендлер `-offline` | `FUN_10680f27` | включает отладочное меню (пункт COOP Story) |
| строка `GetLocalPlayerId` | `0x11fbdcc4` (xref `0x111ce912`) | имя net-поля сервиса игроков |
| `GetNumberOfPlayers` | `FUN_10681070` | количество игроков |
| `GetPlayerInSlot` | `FUN_10680ef0` | слот → id игрока |
| `CoopGetCharacterName` | `FUN_10680f90` | имя игрока |
| xref `CoopTeleportPlayer` | `0x11b1d252` | место вызова телепорта |
| поиск компонента | `FUN_1039e1f0` (тип из `FUN_1039e0d0`) | получить net-компонент по типу |
| фолбэк слота 0 | `FUN_11305eb0` (провайдер `DAT_1280437c`) | путь одиночной игры |
| создание объекта сессии | `FUN_10260770` | ещё не декомпилирован; аналог в 1.06 open |
| `SpawnCoopAI` / `OnSpawnPlayer_%u` | строка `0x11fc1c64` (в 1.06 пара: `0x11fbda7c` push `0x111cdf76`, `0x1206ad0c` push `0x11b1da06`) | запрос спавна ко-опа |
| net-регистрация | `FUN_11839b60` / `FUN_10468480` | регистрация компонента и поля |
| «Not enough players» | место вызова `0x108c4b09`, внутри функций `0x108c4c6b` и `0x108c5c36` | цель 5-NOP патча мода 262 |
| центральный объект игры | `DAT_12804acc` (4 529 ссылок, `+0x68` контейнер компонентов) | объект, через который идёт любой поиск компонента |

Локальные измерения 1.06 (см. раздел про командную строку в англиском файле): функция загрузчика
`0x11aa2fe0`, экстрактор значений `0x11a1b940` (места вызова `-host` `0x11aa12a6`, `-client`
`0x11aa1362`, `-load` `0x11aa2b31`, `-wait` `0x11aa2680`), перезапись командной строки
`0x11aa39d0`..`0x11aa3b60` с хелпом добавления `0x100041b0` и хардкодными фрагментами
`' -world=fc3_main'` `0x11fdbdb1`, `' -spawnpos=333.63,964.5,124.465'` `0x11fdbdc4`,
`' -spawnangle=0.0,0.0,0.0'` `0x11fdbde4`, `' -spawnpos=-857.626,2317.1,119.752'` `0x11fdbe0c`,
`' -spawnangle=0.0,0.0,-20.0'` `0x11fdbe30`; блоки строк флагов в `FC3_d3d11.dll` `0x11fdbc*` и
в `FC3.dll` `0x11fb7*` (`0x11fb7d90`..`0x11fb7e27` — набор читов и графики).
## Открытые вопросы

- [ ] Какая версия установлена у владельца? 1.05 или 1.06?
- [ ] Где путь к установке? (сохранить в local/)
- [ ] У друзей тоже есть FC3, или одна копия + ко-оп?
- [ ] Сколько всего игроков (2? 3? 4?)?
- [ ] Все друзья имеют Windows-ПК с Steam?

## Запуск и командная строка в Uplay-сборке 1.06 (2026-11-01)

Проверено на машине владельца: `H:/Uplay/Far Cry 3` = Uplay-сборка **1.06**
(FC3_d3d11.dll 40869416 байт на диске, PE compile time 2022-05-04, версия файла 1.06.0.90512,
product 1089053420; MD5 FC3_d3d11 `916c6d4b876d8be5f0ad68f50719a838`, FC3
`5742de2aaa76935d46947bf89e2e2eb7`, farcry3_d3d11.exe `47d4c992b0e82b7d52cc48e8d1bd9119`).
Сборки 1.05 на дисках нет нигде (%USERPROFILE%/Downloads, Desktop, D:/, E:/, H:/).

- **exe — DRM-загрузчик.** `bin/farcry3_d3d11.exe` (60992 байта) стартует и заново запускает exe
  **из канонической установки**, путь к которой берётся из реестра
  (`HKLM\SOFTWARE\WOW6432Node\Ubisoft\Far Cry 3`: `InstallDir=H:/Uplay/Far Cry 3`,
  `ExecutableName=bin/FC3Updater.exe`, SKU=WW, Version=1.05, Language=Russian).
  Дополнительные аргументы стираются перед запуском:
  только `-language=Russian` доходит до игры.

- Следствие для тестовой копии: запуск `H:/FarCryCoop/TestFC3/bin/farcry3_d3d11.exe` с
  `-host fc3_main -login h1 -coop` порождает дочерний процесс из `H:\Uplay\Far Cry 3\bin` только с
  `-language=Russian`. Быстрый запуск из своей копии невозможен.
- Строки быстрого запуска в 1.06 `FC3_d3d11.dll` (замер 2026-11-02; блок `.rdata` `0x11fdbc*`, зеркало
  в `FC3.dll` `0x11fb7d*`): `-exec` `0x11fb7d78`, `-execline` `0x11fb7d6c`, `-quickstartup` `0x11fb7d80`,
  `-perfhud` `0x11fb7d4c`, `-logFile` `0x11fb7d58`, `-bfname` `0x11fb7d64`; блок сетевых параметров
  `0x11fdc02c`..`0x11fdc27c` (`FC3.dll` зеркало `0x11fad15c`..`0x11fad308`): `-login` `0x11fdc040`,
  `-sessionuid` `0x11fdc0b4`, `-coop` `0x11fdc0cc`, `-online` `0x11fdc104`, `-ip` `0x11fdc124`,
  "Invalid parameters for -host, missing (-login)" `0x11fdc084`, "Missing -login or -ip for -client."
  `0x11fdc128`, `-netemulator` `0x11fdc10c`.
- **ОТКАЗ (2026-11-02):** старая таблица `0x1fb6f6c`-`0x1fb74f6` (`-host` @0x1fb73cb, `-client` @0x1fb7472,
  `-offline` @0x1f36444, `-dedicated` @0x1f0d9dc, "Missing -login or -ip" @0x1fb7458) оказалась ложной — эти
  адреса это концы строк в `\0`-наполнении. В `FC3.dll` 1.06 таких строк нет вовсе (`-offline`, `-dedicated`,
  `-dedicator`, `-hostmaster`, `-mapname`, `-stageName`, `-profile`, `-demo`), как и строк отладочного меню 1.05
  ("Not enough players", "Local Coop", "Coop Story"). Урок: поиск `\0<строка>\0` возвращает индекс ведущего
  `\0` — сдвигать +1.
- **Разобрано (2026-11-05, заново проверено скриптом `scripts/fc3_mode_cascade.py`):** каскад flags
  режима. Каскад — цепочка `push <строка>` / `push esi` / `call edi` (`strstr`), `add esp,8`,
  `test eax,eax`, `je <следующий flag>`; совпадение читает **статический id режима** из global-адреса
  и пишет его в `[ebp+8]`.
- **Тело каскада (`FC3.dll`): `0x11a8c440`** (`push ebp` / `mov ebp,esp` / `sub esp,0x2c` / `push ebx`
  / `mov ebx,[ebp+0x14]` / `mov esi,[ebp+0xc]` / `push edi` / `mov edi,[0x11bcb5c0]` =
  `MSVCR100.dll:strstr`). Ранее записанный диапазон `0x11a8c533` .. `0x11a8c567` — фрагмент этого тела.
- **Порядок flags и места сравнения (`FC3.dll`, `0x11a8c440` .. `0x11a8c5b1`):** `-login` `0x11a8c455`,
  `-ip` `0x11a8c464`, `Missing -login or -ip for -client.` `0x11a8c476`, `-online` `0x11a8c49d`,
  `-password` `0x11a8c4ac`, `Trying to launch an online client, but missing password (-password)`
  `0x11a8c4be`, `-ip` `0x11a8c4f0`, `-bfname` `0x11a8c4fe`, `-sessionuid` `0x11a8c50c`,
  `-deathmatch` `0x11a8c51a` (читает `[0x1216aedc]`), `-coop` `0x11a8c533` (читает `[0x1216aee4]`),
  `-domination` `0x11a8c54d` (`[0x1216aeec]`), `-headquarters` `0x11a8c567` (`[0x1216aef4]`),
  `-firestorm` `0x11a8c57d` (`[0x1216aefc]`), `-dash` `0x11a8c597` (`[0x1216af04]`), запасной variant
  `[0x1216af0c]` на `0x11a8c5b1`.
- **Значения id (`FC3.dll` `0x1216aed0` .. `0x1216af10`, блок побайтово идентичен
  `FC3_d3d11.dll` `0x1218ffd0` .. `0x12190010`):** `0x9ba82025` первый entry (`0x1216aed0` и
  `0x1216aed4`), `-deathmatch 0x8b40f692`, `-coop 0x43521e6f`, `-domination 0xab4fc8e2`,
  `-headquarters 0x9991daec`, `-firestorm 0xf66ffb87`, `-dash 0x2100ced7`, запасной `0x6c2b3868`;
  после каждого id идёт пара `0xffffffff`, и ещё один id `0xd2fd0a6b` стоит прямо перед блоком
  (`0x1216aecc` / `0x1218ffcc`). Две поправки к прежней записи: `-deathmatch` читает `0x1216aedc`
  (не `0x1216aed4`), и id, помеченный как "unknown" (`0xf66ffb87`) — это **`-firestorm`**.
- **Каскад читает эти id, а не пишет их:** значения — статические инициализаторы `.data`, присутствующие
  в обоих модулях 1.06, значит `-coop` в 1.06 это живой id режима, а не удалённая строка. `-online`
  выбирается отдельно: `[ebp-0xc]` равняется `3` на `0x11a8c5bf` по умолчанию и `2` на `0x11a8c5cf` при
  совпадении `-online` (сходится с выводом модели хоста: «тип сессии = 3 без `-online`»).
- **Потребитель id каскада (`FC3.dll` `0x11a8c5d6` .. `0x11a8c5f0`):** `mov ecx,[ebp+8]` →
  `mov edx,[ebx]` → `mov eax,[edx+0x14]` → **`mov [ebx+0xa4],ecx`** (id режима попадает в поле объекта
  `+0xa4`) → `mov ecx,ebx` / `call eax`, затем `mov eax,[edx+0x18]`, `mov ecx,ebx`, `call eax`.
  `FC3_d3d11.dll` даёт тот же каскад (`-domination` `0x11aa08ed`, `-headquarters` `0x11aa0907`,
  `-firestorm` `0x11aa091d`, `-dash` `0x11aa0937`, `-online` `0x11aa0959`) с диспатчем по слоту `+0x14`
  на `0x11aa0976`.
- **Что функция каскада делает после записи id (`FC3.dll` `0x11a8c5f0` .. `0x11a8c6b9`, вывод
  `local/scratch/cascade_tail.txt`):** она вызывает `0x119696d0` (`0x11a8c5f7`) и `0x11a8bdc0`
  (`0x11a8c601`), выполняет ref-count блок из `[ebx+0x9c] + 0x4c` и `[ebp+0x14]` (`cmp` на `0x11a8c612`,
  `lock xadd [edx], 1` на `0x11a8c62d`, `lock xadd [edx], -1` на `0x11a8c645`, `call 0x100945e0` на
  `0x11a8c64f`), ставит флаг `[ecx+0xd] = 1` (`0x11a8c668`), читает строковый global `-sessionuid`
  `0x11fb81e4` (`0x11a8c696`) и затем пишет поля записи запуска: `[ebx+0x64] = 0xfffffffd`
  (`0x11a8c69c`), `[ebx+0x40] = eax` (`0x11a8c6a3`), `[ebx+0x44] = edx` (`0x11a8c6a6`) и
  `[ebx+0x74] = 6` (`0x11a8c6b2`). Id режима уходит через объект с vtable-диспатчем; отсюда ни одна
  запись в реестр не регистрируется.
- **Обход `+0xa4` по всему `.text` (`FC3.dll`, скрипт `local/scratch/probe5.py`, вывод
  `local/scratch/a4sites.txt` 93637 байт):** 832 функций работают со слотом `[reg+0xa4]` (835
  обращений), и ровно одна заодно трогает global с id режима — `0x1181c440`; она оказалась UI-кодом
  (следующий пункт). Значит `+0xa4` не является уникальным признаком режима запуска, и потребителя
  надо искать через vtable-диспатч.
- **Тупик: `FC3.dll 0x1181c440` — это FlowGraph UI-обработчик `customMapEvaluation`.** Его `+0xa4` —
  слоты стека (`mov [esp+0xa4],4` на `0x1181d09e`, `mov [esp+0xa4],0x190` на `0x1181d101`); тело грузит
  своё имя `mov esi, 0x1201b27c` (`0x1181c45b`, UTF-16 строка сразу после fourcc `CFCX` на `0x1201b276`);
  `scripts/fc3_callers.py` даёт `0 E8 callers` плюс один абсолютный data-ref на `0x1201b444`, который
  лежит в таблице обработчиков `0x1201b404` .. `0x1201b458` с соседями `OnMapPublish` `0x1201b380`,
  `OnEnterMyMapsOK` `0x1201b39c`, `OnEnterMapArchiveOK` `0x1201b3bc`, `ExitMyMaps` `0x1201b3e4`,
  `updateCustomMapEvaluation` `0x1201b478`, `multiCustomMapEvaluationReportContent` `0x1201b4b0`,
  `multiCustomMapEvaluationFavoriteContent` `0x1201b500`, `multiCustomMapEvaluationLikeContent`
  `0x1201b550`, `customMapEvaluationTagsRequest` `0x1201b598`.
- **Похожий на реестр цикл сравнения внутри этого обработчика (`0x1181ceef` .. `0x1181cf30`), листинг `local/scratch/registry_scan_loop.txt`; оставлен,
  потому что это ровно тот шаблон, который показал бы настоящий реестр сессий:** `mov edi,[edx+0xc4]`
  (`0x1181cef5`), `mov ecx,[0x128048c0]` (`0x1181ceef`), `mov eax,[ecx+8]` (`0x1181cefb`),
  `mov edx,[ecx+4]` (`0x1181cefe`), `lea edx,[edx+eax*4]` (`0x1181cf01`), `mov eax,[ecx+4]` (`0x1181cf04`), `cmp eax,edx` (`0x1181cf07`), `je 0x1181cf21` (`0x1181cf09`), затем скан `mov ebx,[eax]`
  (`0x1181cf11`) → `cmp dword ptr [ebx+0x20], esi` (`0x1181cf13`) → `add eax,4` (`0x1181cf18`) →
  `cmp eax,edx` (`0x1181cf1b`) → `jne 0x1181cf11` (`0x1181cf1d`) при промахе, `je 0x1181cf1f` (`0x1181cf16`) при совпадении; `xor ebx,ebx` (`0x1181cf1f`) достигается и из прыжка совпадения, и из исчерпанного цикла, а `0x1181cf21` (`mov edx,[ecx+8]`, `mov ecx,[ecx+4]`, `lea edx,[ecx+edx*4]`) начинает второй проход по тому же контейнеру; `esi = [0x1216aeec]`
  (`-domination 0xab4fc8e2`, прочитано на `0x1181cf0b`), `edi = [0x1216af0c]` (запасной `0x6c2b3868`,
  прочитано на `0x1181ce50`). Новый контейнер: **`[0x128048c0]`**, `+4` = количество, `+8` = база
  индекса со множителем ×4, элементы — указатели, в поле `+0x20` которых лежит id; это другой
  контейнер, не `execLines` (`[0x12829424]`). Открыто: что такое `[0x128048c0]` и сравнивается ли
  значение `+0xa4` из каскада с полем `+0x20` такого элемента.
- **Найдены потребители launch-mode id** (скан whole-`.text` по инструкциям, читающим mode-id global,
  дамп `local/scratch/modeid_sites.txt`: в `FC3.dll` их читают только 3 функции): `0x1111e390`
  (`cmp eax,[0x1216aee4]` в `0x1111e4e3`), `0x1111e860` (`cmp eax,[0x1216aee4]` в `0x1111e91e`),
  `0x1181c440` (запасной id в `0x1181ce50`, `-domination` в `0x1181cf0b`). В `0x1111e390` id лежит в
  `mov eax,[edi+0x10]` (`0x1111e399`), контейнер берётся из `mov ecx,[ebx+0x154]` (`0x1111e3bc`),
  поиск id→record делает `call 0x10260770` (`0x1111e3c7`: `cmp byte ptr [ecx+0x5c],0` `0x10260773`,
  `cmp dword ptr [ecx+0x54],0` `0x1026077b`, `mov eax,[ecx+0x50]` `0x10260781`, `call 0x1025fee0`
  `0x1026078a`, `cmp dword ptr [eax+4],2` `0x1026079a`, `cmp ecx,[edi+0xc]` `0x102607a3`, возвращает
  record или 0), а поле record `+0xcc` (`0x1111e3d8 mov eax,[eax+0xcc]`) даёт контейнер этой записи.
- **Сама проверка coop идёт через второй синглтон (`FC3.dll 0x1111e4ce .. 0x1111e517`)**:
  `mov edx,[0x12804acc]` (`0x1111e4ce`) → `mov eax,[edx+0x68]` (`0x1111e4d4`) → `mov eax,[eax+0x30]`
  (`0x1111e4db`) → `or eax,0xffffffff` при пустом аксессоре (`0x1111e4e0`) → `cmp eax,[0x1216aee4]`
  (`0x1111e4e3`) → `mov ecx,[ebx+0x154]` (`0x1111e4ef`) → `mov eax,[ecx]` → `mov eax,[eax+0x68]` →
  `call eax` с `[esp+0x18]` (`0x1111e4fe`) → `mov eax,[edx+0x24]` (`0x1111e508`) → `call eax`
  (`0x1111e50b`) → `test al,al` → `cmp byte ptr [esp+0xb],al` → `cmp dword ptr [0x12835c94],0`
  (`0x1111e517`). Новые глобалы: **`[0x12804acc]`** (аксессор `+0x68`, vtable слоты `+0x30` и `+0x24`)
  и **`[0x12835c94]`**.
- **Тот же тест кооп-режима встречается второй раз внутри `0x1111e860` (`FC3.dll 0x1111e860 .. 0x1111ecb0`,
  разбор `local/scratch/r1_out.txt`)**: `mov eax,[0x12804acc]` (`0x1111e902`) → `mov eax,[eax+0x68]`
  (`0x1111e907`) → `mov eax,[eax+0x30]` (`0x1111e916`) / `or eax,0xffffffff` (`0x1111e91b`) →
  `cmp eax,[0x1216aee4]` (`0x1111e91e`) → `sete al` (`0x1111e924`) → `mov byte ptr [esp+0x13],al`
  (`0x1111e927`) → `test al,al` → `jne 0x1111e98e` (`0x1111e92d`); в отрицательной ветке
  `cmp dword ptr [ecx+0xc],0` (`0x1111e932`), `cmp dword ptr [0x12835c94],0` (`0x1111e938`),
  `call 0x10003cd0` (`0x1111e94a`), `call 0x10002aa0` (`0x1111e961`), `call 0x10425d20` (`0x1111e96e`,
  `cmp eax,ebx` → `je 0x1111e98e`), `mov ecx,[0x12805434]` (`0x1111e97f`), `call 0x11363ab0`
  (`0x1111e985`). Общая форма обеих функций: `mov ebx,[ebp+8]` + `add ebx,0x108` (`0x1111e8ad`) либо
  `mov ecx,[ebx+0x154]` (`0x1111e3bc`, `0x1111e437`) как искомый контейнер, `call 0x10425d20`
  (`0x1111e8b8`, `0x1111e96e`) с проверкой конца контейнера `cmp eax,ebx`, чтение поля записи
  `mov eax,[eax+0x20]` (`0x1111e8c5` — тот же `+0x20`, что и у записей `[0x128048c0]`),
  `mov ecx,[0x12805434]` (`0x1111e8c8`), `call 0x11363b10` (`0x1111e8de`),
  `cmp dword ptr [ebp+0x14],2` (`0x1111e98e`) и `cmp dword ptr [ebp+0x14],1` (`0x1111ea44`) как
  переключатель режима, `call 0x104245c0` (`0x1111e9a5`), и итоговая проверка `mov ecx,[0x12805180]`
  (`0x1111ea72`) → `mov eax,[ecx+4]` (`0x1111ea78`) → `mov edx,[eax+0x11c]` (`0x1111ea7b`) →
  `mov ecx,[eax+0x118]` (`0x1111ea81`) → `push edx; push ecx; push eax` → `call 0x102000d0`
  (`0x1111ea8a`) → `test al,al` → `je 0x1111eb48` (`0x1111ea91`). Открыто: чем являются
  `[0x12805180]`, `[0x12805434]`, `0x102000d0`, `0x10425d20` и кто вызывает `0x1111e390`/`0x1111e860`.
- **Владелец контейнера `[0x128048c0]` (`local/scratch/container_sites.txt`, 13 функций)**: создаёт его
  `0x10048230`, публикует дважды (`0x10048289`, `0x10048297 mov dword ptr [0x128048c0], eax`); читают
  `0x10f0c770` `0x10f0c7ca`, `0x10f0ea50` `0x10f0ec39`, `0x10f0ed30` `0x10f0ef19`, `0x113224c0`
  `0x11322514`, `0x113235d0` `0x113236a9`, `0x11340560` `0x113408f8` + `0x11340bdb`, `0x11709440`
  `0x11709450`, `0x1181c440`, `0x118227d0` `0x11822875`, `0x119288b0` `0x11928dee`, `0x11997720`
  `0x11997723` (чтение — первая инструкция функции, похоже на getter). Анатомия создателя: проверки
  `cmp byte ptr [0x128042fc], bl` (`0x1004823a`) и `cmp byte ptr [0x12162beb], bl` (`0x10048247`),
  `call 0x11789a00` (`0x10048242`), аллокация 0x20 `mov edx,0x10` / `lea ecx,[edx+0x10]` /
  `call 0x1177f7c0` (`0x1004824f`, `0x10048254`, `0x10048257`), vtable `mov dword ptr [eax], 0x11f224c4`
  (`0x10048271`), поля `+4 +8 +0xc +0x10 +0x14 +0x18` обнулены.
- **Vtable контейнера `0x11f224c4` выбирает слоты по флагам `+0x10`**: слот 1 `0x100a5df0`
  (`test byte ptr [ecx+0x10],1` `0x100a5df3`, `mov esi,[ecx+0x14]`, `add esi,[ebp+8]`,
  `cmp dword ptr [ecx+8],-1`, `lea eax,[ecx+4]`, `mov eax,[edx+0x20]` → `call eax` в `0x100a5e14`),
  слот 2 `0x100a5e30` (бит 2), слот 3 `0x100a5e70` (бит 4); слот 0 `0x100a5b10` после `call 0x117097d0`
  ограничивает `esi` интервалами `[0x121bbff8]` (`0x100a5b25`) и `[0x121a7fdc]` (`0x100a5b2d`).

- **Эти id встречаются в трёх других таблицах `FC3.dll`** (следующие кандидаты на реестр
  дескриптора сессии): `0x1216aa2c` .. `0x1216aa44` (`-deathmatch 0x1216aa2c`, запасной `0x1216aa30`,
  `-firestorm 0x1216aa34`, `-domination 0x1216aa38`, `-headquarters 0x1216aa3c`, `-coop 0x1216aa40`,
  `-dash 0x1216aa44`); `0x12173ff0` .. `0x1217400c` (`-domination 0x12173ff0`, `-coop 0x12173ff4`,
  `-deathmatch 0x12173ff8`, `-headquarters 0x12174000`, `-firestorm 0x12174008`, `-dash 0x1217400c`,
  запасной `0x12173ffc`); пара `-coop`/`-dash` на `0x1216a00c` / `0x1216a010`; `0x9ba82025` повторяется
  через `0x12163450` .. `0x121636e8`; `0xd2fd0a6b` ещё и на `0x1216cab0`. Открытым остаётся, что
  выбирает каждая таблица и кто их обходит.
- **Вторая цепочка сравнения имён режима (`FC3.dll`, `0x11a8c944` .. `0x11a8c9c1`)** (начало фукции —
  `0x11a8c8b0`, см. запись в конце файла) (`-deathmatch`
  `0x11a8c944`, `-coop` `0x11a8c95d`, `-domination` `0x11a8c977`, `-headquarters` `0x11a8c991`,
  `-firestorm` `0x11a8c9a7`, `-dash` `0x11a8c9c1`); у `-online` есть ещё ссылки на `0x11a8b8d3`,
  `0x11a8b91f`, `0x11a8cd09`. Открытым остаётся, что выбирает эта цепочка.
- **Счёт patch-сайтов reloc-режима для global-ов id режима и контейнера (`scripts/fc3_reloc_xref.py
  --mode reloc`, 772159 записей на модуль).** Global id режима `-coop` в `FC3.dll` `0x1216aee4` имеет
  **30** сайтов, значение в которых на него указывает, и `FC3_d3d11.dll` `0x1218ffe4` — ровно те же
  **30**; у строки имени режима **2** сайта в каждом модуле (`FC3.dll` `0x11fb81fc` -> `0x11a8c534`,
  `0x11a8c95d`; `FC3_d3d11.dll` `0x11fdc0cc` -> `0x11aa08d4`, `0x11aa0cfd`). У базового global-а
  accessor-ов `0x1282f6cc` в `FC3.dll` **4** сайта HIGHLOW (`0x1199cdcb`, `0x1199cddd`, `0x1199cf76`,
  `0x11bb33f1`), а у global-а контейнера `0x12829424` — **0**: до него доходят только через `disp32`,
  который загрузчик не патчит, поэтому 17 502 записей выше получены поиском по байтовому шаблону, а не
  из `.reloc`. Полные списки сайтов лежат в `local/scratch/xref_sites_fc3.txt` и
  `local/scratch/xref_sites_d3d11.txt`.
- Урок (2026-11-05): id режимов не являются `hash(имя)`. Пересчёт `-deathmatch`, `-coop`, `-domination`,
  `-headquarters`, `-firestorm`, `-dash` и имени режима по умолчанию алгоритмами FNV-1a, FNV-1, djb2,
  sdbm, ELF и CRC32 (на уже проверенном наборе из 26 имён) дал **0** совпадений в обоих модулях, то есть
  это константы игровой таблицы, а не значения, выведенные из имён флагов.
- Урок (2026-11-05): `scripts/fc3_reloc_xref.py` в режиме `code` не видит форму `push imm32`. Для двух
  мест `push <адрес строки режима>` внутри тела каскада режим `code` выдал `verified instructions: 0` и
  `rejected (no instruction ends at the field): 2`, а `--mode reloc` нашёл оба места: для аргументов
  `push imm32` надёжен только reloc-режим.
- Открытым остаётся, доходит ли co-op id до реестра дескриптора сессии.
 Global-адрес `-coop` передаётся аргументом в `FC3_d3d11.dll` на `0x10fed7f1` /
  `0x10fed817` (`call 0x103878e0`, `call 0x10656d90`); остальные места, где он хранится:
  `0x10fed7f2`, `0x10fed818`, `0x10fed876`, `0x10fed8c7`, `0x10fed8f5`, `0x10fed933`, `0x10fee3e6`,
  `0x11123d95`, `0x111241d0`, `0x111a38b1`, `0x111a5335`, `0x111a62d6`, `0x11a6e78f`, `0x11a6e81e`,
  `0x11aa08e4`, `0x11aa0a5e`, `0x11aa0d0d`, `0x11aa0e60`. Адрес строки `-coop` в `FC3.dll`
  (`0x11fb81fc`) встречается только на `0x11a8c534` и `0x11a8c95d`.
  Урок: id не являются `hash(имя_режима)` по FNV-1a/FNV-1/djb2/sdbm/ELF/CRC32 (проверено 26
  имён с вариантами регистра и суффиксов — 0 совпадений), то есть это игровая таблица id.
  Урок: `fc3_reloc_xref.py` в режиме `code` не подтверждает форму `push imm32` (`verified
  instructions: 0, rejected (no instruction ends at the field): 2`), а reloc-режим эти места
  находит — для аргументов `push imm32` надёжен только reloc-режим.
- Переименование `bin/upc_r1_loader.dll` загрузчик не развязывает: игра тихо выходит примерно за
  25 с (без окна, без события WER) — загрузчик Ubisoft Connect является обязательной зависимостью
  старта.
- Писать в `HKLM` текущему пользователю недоступно (без повышения прав), поэтому реестр нельзя
  перенаправить на приватную копию. Оригинальные значения сохранены в `local/registry-fc3-backup.reg`.
- Что в 1.06 работает: патч мютекса единственного экземпляра (`jnz` в `0x100041bb` /
  `0x10004092` -> NOPы) позволяет запустить две копии рядом; патч падения по списку Uplay-party —
  только для 1.05 (в 1.06 образец не встречается, там новый UPC API).
- Меню мультиплеера в 1.06 мертво: показывается жёстко зашитый loc id `0x23894` = 145556 = X360_EU_NETWORK_XLSP_DOWN (см. `D:/Projects/Co-op Anything/FarCry3Coop-bantila/NOTES.md`, строка 152).
  Поэтому быстрый запуск должен обходить меню, а не проходить через него. В верхней ветке (Bantila) обход уже применён.
- Автоматизация меню: меню не принимает синтетические `mouse_event`-клики;
  нажатия клавиш, посланные через `SendInput`, доходят до меню
  (проверено: `local/menu.py press down|enter`).

**Вывод:** быстрый запуск ко-опа на этой сборке невозможен без (а) DRM-free exe версии 1.05 или
(б) патченного загрузчика-заглушки, который мог бы запускать нашу копию с аргументами быстрого
запуска. Нужно решение владельца.

## Размещение скриптов и артефактов

Скрипты анализа лежат в `scripts/` и попадают в git — по конвенции Bantila: `scripts/`
отслеживается, а `/tools/` игнорируется (там внешние бинарники вроде Ghidra или паковщика).
Скрипты этой сессии закоммичены: `fc3_dis.py`, `fc3_callers.py`, `fc3_addrmap.py`,
`fc3_iat_reverse.py`, `fc3_strgrep.py`, `fc3_reloc_xref.py`, `fc3_trampoline.py`,
`fc3_upc_probe.py`, `fc3_launch_probe.py`, `fc3_execlines_probe.py`. Кэши разборки
(`fc3_dis_cache.json`), черновики агента (`Temp/`) и приватное состояние (`local/`,
`local/scratch/`) игнорируются. Карточки черновиков в `.gitignore`: `*.scratch*`,
`.scratch*`, `scratch_*`, `local/scratch/`.

Каноническая схема владельца: всё под `E:\FarCryCoop\` — `Downloads\`, `Tools\`, `Data\`, `Temp\`,
`Work\` (см. `docs/workspace.md`). Диска `E:` на этом ПК нет, поэтому все записи про `E:\FarCryCoop\`
в этом файле — историческая запись с ПК владельца (октябрь 2026), а не рабочий путь здесь.
Рабочие пути этого ПК (проверено 2026-11-02, канон — `AGENTS.md` + `docs/LOCAL.md` в конвейере
FarCryCoop): репозитории в `D:\Projects\Co-op Anything\`, тестовая копия 1.06 в
`H:\FarCryCoop\TestFC3\`, установка только для чтения (Ubisoft Connect) в `H:\Uplay\Far Cry 3\`.
Перенесённые из bantila скрипты изначально содержали устаревшие константы
`DLL_106 = E:\SteamLibrary\steamapps\common\Far Cry 3\bin\FC3.dll` и
`DLL_105 = E:\FarCryCoop\Downloads\fc3-1.05\bin\FC3.dll`; в местных `scripts\` они перенацелены на
проверенные пути выше. Агентская программа пишет временные файлы в
`C:\Users\<user>\AppData\Roaming\pi-desktop\tmp` (выводы делегатов, скрипты песочницы) — это
противоречит золотому правилу 2 (не трогать C:): отмечено, не исправлено. Противоречие внутри
правил владельца решает владелец, а не агент.

В корне рабочей папки лежит неудаляемый файл `nul`, из-за него `git add -A` падает
(`error: invalid path 'NUL'`) — коммитить только с явными путями.

## execLines и запуск batch-файлов (проверено 2026-11-02, 1.06)

- Поле `execLines` регистрируется как параметр сессионной операции, а не как точка исполнения: в `FC3.dll`
  `push 0x11f90af0; push 8` (`0x113429ca`, защита `cmp byte ptr [0x12805494], 0`, вызов `0x1030f2b0`, кэш
  `[0x1282f900]`/`[0x1282f8fc]`); близнец в `FC3_d3d11.dll` — `push 0x11fb4a80; push 8; call 0x103173f0`
  (`0x1134824a`), соседи `execFilenames` `0x11fb4ad8`, `map`, `mapIdLow/High`, `mapIdType`, `bfname`. У строки
  `execLines` в обеих 1.06-библиотех ровно одна код-ссылка: отследить, кто её читает, через
  `PE.code_refs()` нельзя — тот метод видит только `push imm32`/`mov r32, imm32` и слеп к vftable и
  поле-ссылкам.
- Контейнер ExecLines — глобальный синглтон `0x12829424` (`FC3_d3d11.dll`); конструируется в
  `0x11788440`..`0x11788476`: `test byte ptr [0x128ac410], al; push 0; mov ecx, 0x128ac3f4; call 0x106c4b40`,
  затем `push 0x11bb98c0; call 0x1070085d` и `mov dword ptr [0x12829424], 0x128ac3f4; ret`. Сырой поиск по
  `.text` даёт 17 502 обращений и ровно два constructor-подобных записи (`c7 05` в `0x1178846e` и `0x118e82fd`)
  — то есть это один объект, а не реестр всех batch-файлов. VA в образе little-endian (`0x12829424` → байты
  `24 94 82 12`).
- Консольная команда `exec`: имя `exec` `0x11fdd478`, сигнатура `Game:Exec(%%)` `0x11fdd468`, справка
  `Runs a console command "batchfile". Usage: "exec <batchfile>"` `0x11fdd428` (ссылки `0x111f5c0a`,
  `0x111f5c1a`); блок регистрации `0x111f5b80`..`0x111f5cbc`, его функция начинается с `0x111f4eab`; сам вызов
  регистрации `0x111f5c7b`: `push ebx; push 1; push edx; push <sig>; push eax; push ecx; call 0x1163d910` —
  указатель обработчика лежит в `ebx`, поэтому `code_refs()` его не находит. Близнецы в `FC3.dll`: справка
  `0x11fb9558`, `Usage: runbatch <batchfile>` `0x11fba5bd` (близнец `0x11fde48d`), ссылки `0x111f032a`,
  `0x111f033a`.
- Класс batch-файловой операции движка `CFCXRunBatchFileOperation` (`FC3_d3d11.dll` `0x12032844`, ссылка
  `0x104e5fe9`; `FC3.dll` `0x1200e72c`, ссылка `0x104df159`) регистрируется из инициализационной функции
  `0x104e5f42` (защита `cmp byte ptr [0x1288b074], 0`; идиом `call 0x103a9180` → `push <имя>` →
  `call 0x10038870`), рядом регистрируются `CFCXClearMessageBoxManager` `0x12032808` и
  `CFCXPrepareUnloadWorldOperation` `0x12032824`. У `0x104e5f42` и у `0x111f5a00` ноль E8-вызовов: блоки
  регистрации выполняются CRT-инициализатором (`.initterm`), поэтому «0 вызовов» не означает «мёртвый код».
- Вызов создания сессии в ветке `-quickmatch`/`-host` (`FC3.dll`, `0x11a8d0c5`..`0x11a8d0e2`):
  `lea edx,[ebp+8]; push edx; lea edi,[ebp-0xb4]; call 0x11341dc0` → `mov ecx,[eax]` (vftable) →
  `mov eax,[ecx]` → `mov eax,[eax+0x74]` → `lea edx,[ebp+0x10]; push edx; lea esi,[ebx+0x18]; call eax` →
  `mov edi,eax; call 0x10005570`; путь отказа — `lea ecx,[ebp-0xb4]; call 0x11343640` (`0x11a8d0f6`),
  освобождающий поля `[obj+0x98]`/`[obj+0x9c]`. Вывод: слот vftable `0x74` принимает ровно один аргумент —
  180-байтную (0x
B4) структура параметров сессии по адресу `[ebp+0x10]`. Геттер интерфейса сессии `0x11341dc0` имеет
31 E8-вызовов в `FC3.dll` (`0x10ce93c9`, `0x10edd676`, `0x11163252`, `0x111fa8de`…) — это общий
аксессор, поэтому ко-оп маршрут нужно опознавать по раскладке 180-байтной структуры, а не по уникальности
вызывающих.
- Урок (2026-11-02): блоки регистрации, которые запускаются только CRT-инициализатором, не видны поиску
  вызывающих, а указатели обработчиков, переданные в регистрах, не видны `code_refs()`. Единственная
  зацепка для потребителя `-exec` — 180-байтная структура параметров сессии в `FC3.dll 0x10a8d0db` и поле
  сессионного объекта `[obj+0x98]`; их и нужно зондировать следующим шагом.

- **Тупик статического анализа для исполнителя `execLines` (2026-11-02, `FC3_d3d11.dll` 1.06):**
  ленивый thunk с начала `0x118e82d0` — это Meyers-синглтон-доступ контейнера: `test byte ptr
  [0x128ac410], 1` / `or dword ptr [0x128ac410], 1` / `push 0; mov ecx, 0x128ac3f4; call 0x106c4b40` /
  `push 0x11bb98c0; call 0x1070085d` / `mov al, 1; mov dword ptr [0x12829424], 0x128ac3f4; ret`, а
  `0x11bb98c0` — thunk уничтожителя, зарегистрированный в atexit (`mov ecx, 0x128ac3f4; jmp 0x106c4b70`),
  сосед `0x11bb98d0` для следующего глобального объекта. Имена полей сессионной операции
  регистрируются при первом обращении (`0x11348230` с защитой `byte [0x1282a60c], 0` → `call 0x11347c60`
  с защитой `byte [0x1282a607], 0` → `push <имя>; push <размер>` → `call 0x103173f0`, далее пары
  `[0x12852d54]`/`[0x12852d58]` и `[0x12852dcc]`/`[0x12852dd0]`, `sar ecx, 2` = число элементов), а
  реестр трогают только 10-байтные accessor-thunkи в `0x11bc8a80`..`0x11bc8ad0` вида
  `b8 <слот> ; e9 <jmp 0x10004d70>`. Вывод: статически исполнителя не изолировать — идиом
  `mov ecx,[0x12829424]; call 0x106c99b0; mov eax,<строка>; call 0x11788480` в библиотеке 8 311
  экземпляров (это общий контейнерный вызов), а у кандидата в исполнители `0x118e8310` вообще 0 E8
  ссылок. Следующая зацепка — динамическая: запуск тестовой копии с `-exec`/`-execline` либо
  декомпиляция thunkей в Ghidra (`scripts/fc3_ghidra_dis.py`).

## Зацепки 1.06: флаг `-coop`, пароль бунта и блок полей сессии (2026-11-02, сеанс 22:xx)

- **Второй разбор аргументов в `FC3_d3d11.dll` полностью разобран (2026-11-05, `scripts/fc3_mode_cascade.py`):**
  цепочка `0x11aa0cfc .. 0x11aa0d7a` сравнивает тот же набор флагов и пишет id режима в локальную ячейку
  `[ebp+0xc]` (главный разбор пишет в `[ebp+8]`): `-coop` → `0x11aa0d0b mov ecx, [0x1218ffe4]`
  (`0x43521e6f`) → `0x11aa0d11 mov [ebp+0xc], ecx`; `-domination` → `[0x1218ffec]` = `0xab4fc8e2`, запись
  `0x11aa0d2b`; `-headquarters` → `[0x1218fff4]` = `0x9991daec` (чтение `0x11aa0d3f`); `-firestorm` →
  `0x11aa0d55 mov ecx, [0x1218fffc]` = `0xf66ffb87` → `0x11aa0d5b`; `-dash` → `0x11aa0d6f mov edx,
  [0x12190004]` = `0x2100ced7` → `0x11aa0d75`; резерв `[0x1219000c]` = `0x6c2b3868`. Зеркало в `FC3.dll`
  подтверждено только по строкам (`-coop` `0x11a8c95d`, `-domination` `0x11a8c977`, `-headquarters`
  `0x11a8c991`, `-firestorm` `0x11a8c9c1`): интервал `0x11a8c944 .. 0x11a8c9c1` — это часть функции с началом в **`0x11a8c8b0`** (RESOLVED 2026-11-06); см. запись «Вторая цепочка launch-режимов, вход RESOLVED» в конце файла.
- **Флаг `-coop` и разбор запуска.`FC3_d3d11.dll`** строка `-coop` лежит в `0x11fdc0cc` — в том же
  связном блоке переключателей, что `-perfhud` `0x11fdbc1c`, `-logFile` `0x11fdbc28`, `-bfname`
  `0x11fdbc34`, `-execline` `0x11fdbc3c`, `-exec` `0x11fdbc48`, `-quickstartup` `0x11fdbc50`,
  `-debugFramerateCameras` `0x11fdbcf8`. Флаг разбирают две функции: главный разбор аргументов входа
  `0x11aa0670` (`-coop` в `0x11aa08d3` и `0x11aa0cfc`, `-bfname` в `0x11aa089e` и `0x11aa0cb9`) и второй
  блок разбора `0x11aa1b90` (там же `-netemulator` `0x11fdc10c` в `0x11aa10cc`/`0x11aa10db`, `-ranked`
  `0x11fdc11c` в `0x11aa0bda`/`0x11aa1198`, `-spawn` `0x11fdbe90`, `-spawnpos` `0x11fdbe98`,
  `-spawnangle` `0x11fdbea4`, `-class` `0x11fdbe88`). Отдельный парсер консольных строк — `0x11aa2fe0`
  (`-bfname` `0x11aa302a`, `-execline` `0x11aa3054`/`0x11aa3070`/`0x11aa30ce`, `-exec`
  `0x11aa3144`/`0x11aa3167`/`0x11aa3244`/`0x11aa3250`, `-quickstartup` `0x11aa326a`, дальше консольные
  строки `gfx_NoLaunchCountdown 1` `0x11fdbc60`, `gfx_NoPostRoundCountdown 1` `0x11fdbc78`,
  `gfx_NoPreRoundTimeOut 1` `0x11fdbc94`, `multi_DisableInitialSpawnDelay 1` `0x11fdbcac`,
  `hack_loadOutIsWaitingForMissionBlocks 0` `0x11fdbcd0`). Три вызова в `0x11aa2fe0`: `0x117b565d`,
  `0x117b7003`, `0x11997f41` плюс слот таблицы `0x11f31b10`. У `-splitscreen` `0x11f31d75`,
  `-splitscreen4` `0x11f31d85` и `-numclients` `0x11fb1e18` нет ссылок с немедленным операндом — их
  читают через смещения строковой таблицы, поэтому поиск `push imm32` / `mov reg, imm32` их не находит.
- **Обработчик `-password` и буфер пароля бунта:** функция `0x117b5580` (`push ebp; mov ebp,esp;
  sub esp,8; mov eax,[ebp+8]`) собирает строку из `[eax]` или `[eax+0xc]` (при пустом значении
  `0x117b5597 mov eax,0x11f31ea8`), далее `0x117b55a6 mov eax,0x11f31d34 str='-password'` и
  `0x117b55ab call 0x117b5160` (разбор переключателя). Если значение есть и `[ebx+4]` не ноль:
  `0x117b55c4 test byte ptr [0x128b59a8],1`, `0x117b55cc or dword ptr [0x128b59a8],1`,
  `0x117b55d2 push 0x11f31bbc str='******'` и `mov dword ptr [0x128b59a4],0`, `0x117b55dd call 0x10002a50`,
  `0x117b55f1 call 0x10001ec0`, `0x117b55f6 push 0x11bb76a0`, `0x117b55fb call 0x1070085d`
  (регистрация колбэка), `0x117b5606 push 0x128b59a4`. В этой же функции находятся вызовы
  `0x117b5653 call 0x11aa0670` и `0x117b565d call 0x11aa2fe0`. Вывод: пароль бунта (`-bfname`)
  обрабатывается до разбора аргументов запуска, то есть защищённый паролем бунт доступен из
  командной строки.
- **Правка блока имён полей сессии для 1.06:** имена полей реестра сессионной операции лежат связно в
  `.rdata` с `0x11fb4a00` по `0x11fb4c98`; обходитель реестра `0x103173f0` (`cmp byte ptr
  [0x128293f4],0`) резервирует запись размером `0x10 + 0x20` = 48 байта через `0x11790750` /
  `0x118e8340`. Полные адреса 1.06: `untFlags` `0x11fb4a00` (вызов `0x11347a0c`), `controllerIndex`
  `0x11fb4a0c` (вызов `0x11347a34`), `silentLogin` `0x11fb4a1c` (вызов `0x11347a5c`), `isPrimaryIndex`
  `0x11fb4a28` (вызов `0x11347a84`), `platformSpecificId` `0x11fb4a38` (цепочка `0x11342759 call
  0x103173f0`, есть и другие места), `demoname` `0x11fb4a4c`, `isInEditor` `0x11fb4a58`,
  `fullNetworkInitialization` `0x11fb4a64` (место `0x113478e0`), `execLines` `0x11fb4a80` (единственное
  место `0x1134824a`), `mapIdLow` `0x11fb4a8c`, `mapIdHigh` `0x11fb4a98`, `versionIdHigh` `0x11fb4aa4`,
  `versionIdLow` `0x11fb4ab4`, `mapIdType` `0x11fb4ac4`, `bfname` `0x11fb4ad0` (места `0x11328860`,
  `0x113482f4`), `execFilenames` `0x11fb4ad8` (место `0x11348300`), `saveGameFilename` `0x11fb4ae8`,
  `unloadWorld` `0x11fb4afc`, `SearchIdAddress` `0x11fb4b08`, `SearchSessionId` `0x11fb4b18`, `JoinGame`
  `0x11fb4b28` (место `0x11348010`), `JoinService` `0x11fb4b34`, `JoinSessionId` `0x11fb4b40`,
  `DeleteSessionId` `0x11fb4b50`, `DeleteMessageId` `0x11fb4b60`, `PlaylistId` `0x11fb4b70`,
  `MatchMakingEnabled` `0x11fb4b7c`, `SessionRefId` `0x11fb4b90`, `SessionType` `0x11fb4ba0`,
  `NetEngineType` `0x11fb4bac`, `AccountType` `0x11fb4bbc`, `SearchRanked` `0x11fb4bc8`,
  `SearchRetries` `0x11fb4bd8`, `SearchSlots` `0x11fb4be8`, `SearchNeedSlots` `0x11fb4bf4`,
  `SearchGameModes` `0x11fb4c04`, `Silent` `0x11fb4c14`, `DeleteCurrent` `0x11fb4c1c`, `WasInvited`
  `0x11fb4c2c`, `EmulatorProfileId` `0x11fb4c38`, `UseTicketRequestAttachment` `0x11fb4c4c`,
  `FollowHost` `0x11fb4c68`, `DoNATTypeDetection` `0x11fb4c74`; дальше идут поля быстрого запуска и
  возвращения игрока `mode` `0x11fb4c88`, `touched` `0x11fb4c90`, `spawnPtId` `0x11fb4c98`,
  `keepPlayerState` `0x11fb4ca4`, плюс `OperationId` `0x11fb4938`, `EngineUpdateFlag` `0x11fb4944`,
  `ranked` `0x11f45e34`, `world` `0x11f46910`, `pos` `0x11f39450`. Прежняя заметка (ссылки вида
  `SearchSessionId 0x11f90c…`, `FollowHost 0x11f90cd8`, `DoNATTypeDetection 0x11f90ce4`, `execLines
  0x11f90af0`) относилась не к тому билду: те адреса — dword-ы указательной таблицы `.rdata`, а не
  строки. Тип поля `execLines` — код `8` из `push` рядом с именем (строка/вектор); оценка «180 байт» из
  прежней заметки тоже относилась не к этому билду; по 1.06 это указательный массив (см. раздел ниже).

## Таблицы записей дескриптора сессии (2026-11-03, оба модуля 1.06)

**Как это было перечислено.** `python -I scripts/fc3_param_records.py <pe> <VA создателя> … --window 64`
сканирует `.text` на `e8 rel32` в создателя дескриптора, а затем назад на `--window` байт ищет
`push imm32` (VA строки имени) и `push imm8` (код типа). Форма регистрации в обоих модулях:
`push 3; push 0; push <VA дескриптора>; push 0; push 0x21; mov eax, <VA имени>; call <регистратор>`.
Просмотр назад может захватывать чужую границу функции, поэтому нужен `--ident-only`
(`IDENT_RE = ^-?[A-Za-z][A-Za-z0-9_.]{1,39}$`) и фильтр мест вызова по блоку регистрации:
`FC3_d3d11.dll 0x11347xxx` / `0x11348xxx`, `FC3.dll 0x11341xxx` / `0x11342xxx`. Полные выгрузки:
`local/scratch/param_recs_session_block_d3d11.txt` (63 строки) и
`local/scratch/param_recs_fc3dll_families.txt` (4118 строк).

**Семейства регистраторов (исправлено).** `FC3_d3d11.dll` 1.06: `0x11acaba0` / `0x11acac50` /
`0x11acad00` / `0x11acb320` / `0x11acaf10` — это **регистраторы обычных атрибутов движка** (они же
регистрируют `Name` `0x11f32188`, `Value` `0x11f333d4`, `Data` `0x11f32280`, `zoneId` `0x11f59698`),
поэтому таблицу сессии надо отделять по месту вызова. `FC3.dll` 1.06 (по распределению вызовов в
`0x11341000..0x11343000`): `0x11ab6800` ×25, `0x11ab6750` ×9, `0x11ab6ed0` ×11, `0x11ab6ac0` ×8,
`0x11ab68b0` ×6, `0x11ab6b70` ×2, `0x11ab6e20` ×1, `0x11ab6a10` ×1, плюс `0x1003b4b0` ×25,
`0x106f9ff0` ×21, `0x100945e0` ×9, `0x10a00be0` ×5, `0x10001ed0` ×5, `0x1030f2b0` ×2. Прежний список
(`0x11ab64c0` … `0x11ab70b0`) **неверен** — с ним перечисление даёт
`records with a name: 0   all creator call sites: 0`. `0x1030f2b0` (FC3.dll) и `0x103173f0`
(FC3_d3d11.dll) — не регистраторы: это `hkVirtual::operator new(0x1c)` (таблица `0x10bcd68`:
+0 `0x112f0e10` MemoryRealloc, +4 `0x112f0fa0` operator new, +8 `0x112f1530` MemoryDealloc).

**Список параметров — это массив 4-байтных указателей со счётчиком, а не 48-байтные записи**
(заменяет прежнюю оценку). `FC3.dll` 0x113429d1..0x11342a00 (`local/scratch/exec_records_dll.txt`):
`mov byte ptr [0x12805494], 1` → `call 0x1030f2b0` (0x113429d8) → `mov ecx, [0x1282f900]` (счётчик) →
`mov eax, [0x1282f8fc]` (база массива) → `lea eax, [eax + ecx*4]` → `push 1` → `mov esi, 0x1282f8fc` →
`call 0x1003b4b0` (**создатель exec-записей**) → `push 3; push 0; mov dword ptr [eax], edi`
(дескриптор hkVirtual пишется в смещение 0 вернутого объекта). Зеркало `FC3_d3d11.dll`
0x11348251..0x1134828b (`local/scratch/exec_records_d3d11.txt`): `mov byte ptr [0x1282a60c], 1` →
`call 0x103173f0` (0x11348258) → `mov ecx, [0x12852dd0]` → `mov eax, [0x12852dcc]` →
`lea eax, [eax + ecx*4]` → `push 1` → `mov esi, 0x12852dcc` → `call 0x10638fb0` (**создатель
exec-записей, новый якорь**) → `push 3; push 0; mov dword ptr [eax], edi` →
`push 0x48; push 0x11fb178c ('map'); mov eax, esi; call 0x11acaba0`.

**Exec-записи есть в обоих модулях:** `execLines` (FC3.dll место `0x113429ca`, `call 0x1003b4b0` в
`0x113429f7`, тип `0x01`; FC3_d3d11 место `0x1134824a`, `call 0x103173f0` в `0x11348258`, тип `0x08`) и
`execFilenames` (FC3.dll место `0x11342a7f`, `call 0x1003b4b0` в `0x11342aa0`, тип `0x01`; FC3_d3d11
место `0x113482ff`, `call 0x11348306`, тип `0x14`). Оба создателя вызываются с `push 1`, то есть как
одноэлементная коллекция — именно поэтому exec-записи не используют обычные строковые/числовые
регистраторы.

**Имена сессии и VA их строк (FC3_d3d11.dll → зеркало FC3.dll):** `abortEngineUpdateFlag 0x11fb4990` →
`EngineUpdateFlag 0x11f909b4` (регистратор `0x11ab6b70`, тип `0x08`); `login 0x11fb49c0` → `0x11f90a30`;
`password 0x11fb49d4`; `onlineKey 0x11fb49e0`; `primaryAccount 0x11fb49ec`; `accountFlags 0x11fb49fc`;
`controllerIndex 0x11fb4a0c`; `platformSpecificId 0x11fb4a38`; `demoname 0x11fb4a4c` → `0x11f90abc`;
`execLines 0x11fb4a80` → `0x11f90af0`; `mapIdLow 0x11fb4a8c` → `0x11f90afc`; `mapIdHigh 0x11fb4a98` →
`0x11f90b08`; `versionIdHigh 0x11fb4aa4` → `0x11f90b14`; `versionIdLow 0x11fb4ab4` → `0x11f90b24`;
`mapIdType 0x11fb4ac4` → `0x11f90b34`; `bfname 0x11fb4ad0` → `0x11f90b40`; `execFilenames 0x11fb4ad8` →
`0x11f90b48`; `saveGameFilename 0x11fb4ae8` → `0x11f90b58`; `SearchIdAddress 0x11fb4b08` → `0x11f90b78`;
`SearchSessionId 0x11fb4b18` → `0x11f90b88`; `JoinSessionId 0x11fb4b40` → `0x11f90bb0`;
`DeleteSessionId 0x11fb4b50` → `0x11f90bc0`; `PlaylistId 0x11fb4b70` → `0x11f90be0`;
`SessionRefId 0x11fb4b90` → `0x11f90c00`; `SessionType 0x11fb4ba0` → `0x11f90c10`;
`NetEngineType 0x11fb4bac` → `0x11f90c1c`; `AccountType 0x11fb4bbc` → `0x11f90c2c`;
`SearchRetries 0x11fb4bd8` → `0x11f90c48`; `SearchSlots 0x11fb4be8` → `0x11f90c58`;
`SearchNeedSlots / SearchGameModes / Silent / DeleteCurrent / WasInvited / EmulatorProfileId /
UseTicketRequestAttachment / FollowHost / DoNATTypeDetection / mode` в `0x11fb4bf8..0x11fb4c88`;
`map 0x11fb178c` → `0x11f8d78c`; `world 0x11f46910` → `0x11f234e0`; `spawnPtId 0x11fb4c98` → `0x11f90d08`;
только в FC3.dll `pos 0x11f15f68` (место `0x1134267f`, регистратор `0x11ab6a10`, тип `0x08`).
Коды типов обычных регистраторов: `0x11ab6750` (`map` `0x48`, `bfname` `0x4c`, `login` `0x04`,
`demoname` `0x0c`), `0x11ab6ac0` (`mapIdLow` `0x28`, `mapIdHigh` `0x20`, `versionIdHigh` `0x38`,
`versionIdLow` `0x40`, `spawnPtId` `0x18`, `SearchSessionId` `0x10`), `0x11ab6ed0` (`PlaylistId` `0x34`,
`SessionRefId` `0x20`, `SessionType` `0x38`, `NetEngineType` `0x3c`, `AccountType` `0x40`,
`SearchRetries` `0x44`, `SearchSlots` `0x48`, `mapIdType` `0x30`), `0x11ab6800` (`0x10`/`0x20`/`0x4c`/`0x4e`/`0x4f`/`0x53`/`0x54`).

**Пары, подтверждённые псевдокодом в обоих модулях 1.06** (`local/scratch/rea/pseudo-fc3dll-v2/functions/`,
`local/scratch/rea/pseudo-d3d11-v2/functions/`). Соответствия FC3.dll ↔ FC3_d3d11.dll:
`0x11342200`↔`0x11347bc0`/`0x11347c60`/`0x11347da0` (копирователь массивов, FC3_d3d11 экспортирует два
идентичных близнеца), `0x113423e0`↔`0x11347c60`, `0x11342480`↔`0x11347d00`, `0x113425c0`↔`0x11348480`,
`0x11342740`↔`0x11347fc0`, `0x113429b0`↔`0x11348230`, `0x11342af0`↔`0x11348370`, `0x1030f2b0`↔`0x103173f0`,
`0x1030f250`↔`0x10317390`, `0x1030f310`↔`0x10317450`, `0x1030f130`↔`0x10317270`, `0x1030f200`↔`0x10317340`,
`0x1030f430`↔`0x10317570`, `0x1003b4b0`↔`0x10638fb0`, `0x11ab6750`↔`0x11acaba0`,
`0x11ab6a10`↔`0x11acafc0`, `0x11ab6ac0`↔`0x11acaf10`, `0x11ab6800`↔`0x11acac50`, `0x11ab68b0`↔`0x11acad00`,
`0x11ab6e20`↔`0x11acb270`, `0x11ab6ed0`↔`0x11acb320`.

- `0x1003b4b0` / `0x10638fb0` — помощники **добавления** в вектор, аргумент = количество элементов: псевдокод
  `puVar2 = FUN_10638fb0(1); *puVar2 = uVar1;`, а в копирователе `sVar1 = DAT_12845d90 * 4;
  pvVar3 = FUN_10638fb0((int)sVar1 >> 2); memcpy(pvVar3, pvVar2, sVar1);`. Тип элемента записи —
  **4-байтовый указатель**, каждая регистрация добавляет один указатель.
- Копирователь (`FC3.dll 0x11342200`): `pvVar2 = DAT_12820c1c; if (DAT_1280548f == '\0') { sVar1 = DAT_12820c20 * 4;
  pvVar3 = FUN_1003b4b0((int)sVar1 >> 2); memcpy(pvVar3, pvVar2, sVar1); DAT_1280548f = 1; } pvVar2 = DAT_1282f884;
  sVar1 = DAT_1282f888 * 4; pvVar3 = FUN_1003b4b0((int)sVar1 >> 2); memcpy(...)`. Близнец FC3_d3d11 — такая же
  форма с `DAT_12845d8c`/`DAT_12845d90` под защитой `DAT_1282a607`, затем `DAT_12852d54`/`DAT_12852d58`.
  ⇒ именованные статические массивы — одноразовые *шаблоны*; живые списки записей именно в векторах.
- Строитель exec-записей (`FC3_d3d11.dll 0x11348230`, защита `DAT_1282a60c`; близнец FC3.dll `0x113429b0`,
  защита `DAT_12805494`, сначала вызывает `0x113423e0`): `uVar1 = FUN_103173f0(8,"execLines");
  puVar2 = FUN_10638fb0(1); *puVar2 = uVar1; FUN_11acaba0(&DAT_11fb178c /* "map" */,0x48,0,3);
  FUN_11acaf10("mapIdLow",0x28,0,3); FUN_11acaf10("mapIdHigh",0x20,0,3); FUN_11acaf10("versionIdHigh",0x38,0,3);
  FUN_11acaf10("versionIdLow",0x40,0,3); FUN_11acb320("mapIdType",0x30,0,3); FUN_11acaba0("bfname",0x4c,0,3);
  uVar1 = FUN_103173f0(0x14,"execFilenames"); puVar2 = FUN_10638fb0(1); *puVar2 = uVar1;
  FUN_11acaba0("saveGameFilename",0x50,0,3); FUN_11acac50(0x54,0,&DAT_12852dcc,0,3);` — размеры дескрипторов:
  `execLines` = 8, `execFilenames` = 0x14; `&DAT_11fb178c`/`&DAT_11f8d78c` — строка `map`.
- Аккаунт-строитель (`0x11348370` ↔ `0x11342af0`): `login` 4, `password` 8, `onlineKey` 0xc, `primaryAccount` 0x14,
  `accountFlags` 0x18, `controllerIndex` 0x1c (регистратор `0x11acb270`↔`0x11ab6e20`), `platformSpecificId` 0x20,
  плюс безымянные смещения `0x10`/`0x1d`/`0x1e` на `&DAT_12852d9c` ↔ `&DAT_1282f8cc`.
- Цепочка условий, которую обязан пройти любой дескриптор (`FC3.dll 0x1030f2b0`): `if (DAT_128042fc == '\0')
  FUN_11789a00(); if (DAT_12162beb != '\0') { iVar1 = FUN_1177f7c0(); if (iVar1 != 0) goto create; }`
  `if (FUN_118db560() == 0) return 0; create: return FUN_1030f430(size, name);`. Близнец FC3_d3d11
  (`0x10317390`): `DAT_128293f4`→`FUN_1179a990()`, `DAT_12187c6b`→`FUN_11790750()`, `FUN_118e8340()` →
  `FUN_10317450()`.
- Строитель world/точки порождения (`FC3.dll 0x113425c0`, защита `DAT_12805498`): кладёт объект, возвращённый
  `FUN_1030f200` (0, если условия не прошли), и пишет `world` 4, `pos` 8 (`&DAT_11f15f68`, регистратор
  `0x11ab6a10`), `spawnPtId` 0x18, безымянное `0x21` на `&DAT_1282f95c` и `0x20` как `iVar1 + 0x14`.
  Близнец FC3_d3d11 `0x11348480` (защита `DAT_1282a609`) пишет `abortEngineUpdateFlag` 0x14 (регистратор
  `0x11acafc0`) + безымянные `0x10`/`0x18`/`0x19`/`0x1a`/`0x1b` на `&DAT_12852d84`.
- **Семейство конструкторов дескриптора** (одинаковая раскладка слотов в обоих модулях; слот *n* =
  объект + 0x<*n*4>): `0x1030f310` ↔ `0x10317450` пишет slot1 = `"GameOpInfos"`, slot2 = помощник strlen
  `FUN_11788030` ↔ `FUN_11798fc0`, slot3 = 0 (феговый байт), slot4 = 3, slot5 = 4, slot7 = `"infos"`, slot9 =
  указатель на данные `&DAT_11f167b6` ↔ `&DAT_11f31ea8`, slot10 = `0xffffffff`, vtable `&PTR_FUN_11f90de0` ↔
  `&PTR_FUN_11fb4d70`, thunk purecall `&PTR_purecall_11f0ebec` ↔ `&PTR_purecall_11f321ac`. `0x1030f430` ↔
  `0x10317570` — та же форма, но slot1 = имя из аргументов, slot5 = `param_1`, slot7 = литерал `"command"`.
  `0x1030f130` ↔ `0x10317270` — деструктор: для слотов `0x12`/`0x13`/`0x14` выполняет
  `LOCK(); iVar1 = *piVar2; *piVar2 = *piVar2 + -1; UNLOCK(); if (iVar1 == 1) FUN_100945e0();` ↔ `FUN_10174710()`,
  затем два вызова `FUN_11788aa0()` ↔ `FUN_11799a30()` и сбрасывает vtable до `&PTR_FUN_11f0e9c4` ↔
  `&PTR_FUN_11f31f88` ⇒ встроенные атомические счётчики в объекте +0x48/+0x4c/+0x50.
- Сам объект записи (`FC3.dll 0x1030f200` ↔ `FC3_d3d11.dll 0x10317340`, **не** `0x10317450`) по ограниченному
  дизассемблеру `local/scratch/rd_fc3_1030f1f0.txt` / `local/scratch/rd_d3d_10317330.txt`: purecall vtable
  `0x11f0ebec` ↔ `0x11f321ac`, затем строковый литерал **`"Data"`** в объекте +4 (`0x11f0ecc0` ↔ `0x11f32280`),
  вызов помощника длины `0x11788030` ↔ `0x11798fc0` со значением в +8, промежуточная vtable `0x11f0edfc` ↔
  `0x11f323bc` с `+0x10 = 3` и повтор возвращённого значения в `+0x14`, `+0x18`, `+0x1c`, `+0x20`, затем
  настоящая vtable `&PTR_FUN_11f90dac` ↔ `&PTR_FUN_11fb4d3c`, и объектное поле +0x24 = `0x11341420` ↔
  `0x11346ca0`.
- Цель +0x24 — **3-байтовый thiscall-геттер**, побятно identical в обоих модулях:
  `mov al, byte ptr [ecx + 0x21]; ret` (FC3.dll `0x11341420`, FC3_d3d11.dll `0x11346ca0`). Это предикат флага,
  а не тик; ни один из двойников не экспортирован псевкодом Ghidra, поэтому pairing получен через
  `region_dump.py`.
- Пошаговый **update/execute** тик — `FC3.dll FUN_11341340` ↔ `FC3_d3d11 FUN_11346bc0` (`this` в `ECX`,
  диапазоны Ghidra `0x11341340-0x11341417` ↔ `0x11346bc0-0x11346c97`, реальный epilogue `ret 4` в `0x11341415` /
  `0x11346c95`, дальше padding с accessor-танками). Псевкод обоих идентичен построчно: флагные байты +0x55,
  +0x5f, +0x19, +0x1a, +0x5e, +0x17, +0x1c, +0x57, +0x26, +0x5d; вызывает `FUN_113401c0` ↔ `FUN_11345a40`, слот
  vtable объекта +0x54, `FUN_1133fbe0` ↔ `FUN_11345460`, `FUN_116332b0(100)` ↔ `FUN_11644220(100)`,
  `FUN_11341280` ↔ `FUN_11346b00`, пишет широкую строку **`L"ExecuteEvent"`** через `FUN_1030fb90` ↔
  `FUN_10317cd0` (снимая флаг +0x57), затем `FUN_10c47220` ↔ `FUN_10c4d740`. Последняя проверка обращается к
  синхронизатору `DAT_12805180` ↔ `DAT_1282a2f8`: читает байт `(*(синхронизатор + 4) + 0x205)`, вызывает слот
  vtable +0x28 и при успехе устанавливает **`DAT_12805e42 = 1`** ↔ **`DAT_1282afba = 1`**.
- Потребители этой флаг-пары: `FC3.dll 0x10c47320`/`0x10c473b0`/`0x10c477c0`/`0x10c47a00` ↔ `FC3_d3d11.dll`
  `0x10c4d840`/`0x10c4d8d0`/`0x10c4dce0`/`0x10c4df20` (читают и снимают `DAT_12805e41`/`DAT_12805e42` ↔
  `DAT_1282afb9`/`DAT_1282afba`). Внутри `FUN_10c473b0` ↔ `FUN_10c4d8d0` закрытый путь вызывает `FUN_1069fbe0`
  ↔ двойник и `FUN_10504b50(дескриптор, L"ExecuteEvent")` ↔ двойник — путь выполнения скриптового события,
  однократно для объекта (ставит guard-байт в объекте +0xe8).
- Смежные accessor-танки (FC3.dll ↔ FC3_d3d11.dll): `0x11341420` ↔ `0x11346ca0` (`mov al, byte ptr [ecx + 0x21]`),
  `0x11341430` ↔ `0x11346cb0` (`mov dword ptr [eax + 4], ecx`), `0x11341440` ↔ `0x11346cc0` (`mov al, byte ptr
  [eax + 0x5c]`), затем только в FC3_d3d11 `0x11346cd0` (ставит байт +0x5c), `0x11346ce0` (`add eax, 0x30`),
  pair-гатеры `0x11346cf0` (+0x28/+0x2c), `0x11346d00` (+0x18/+0x1c), `0x11346d10` (+0x10/+0x14), сеторы
  `0x11346d20` (+0x40), `0x11346d30` (+0x3c), `0x11346d40` (+0x38). Все заканчиваются `ret` и лежат в paddingе
  после тика.
- Доступные по этому же адресу accessor-танки FC3.dll: `0x11341430` (`mov dword ptr [eax + 4], ecx`) и
  `0x11341440` (`mov al, byte ptr [eax + 0x5c]`).

### Владелец реестровых таблиц: guarded-фабрика и её vftable (2026-11-05)

Тупик «у thunk-обёрток `0x118531c0` / `0x11863de0` нет E8-вызывающих, только по одной абсолютной ссылке на
каждую» **решён: это слоты виртуальной таблицы**, поэтому записи о таблице слотов в data directories PE нет —
указатель лежит в vftable в `.rdata`, которую устанавливает фабрика из `.text`.

| FC3.dll | FC3_d3d11.dll | роль |
|---|---|---|
| `FUN_111e9540` (`0x111e9540`-`0x111e9597`) | `FUN_111eeed0` (`0x111eeed0`-`0x111eef27`) | guarded-создатель: выделяет объект и ставит его vftable |
| `&PTR_FUN_11fbb2c0` (`.rdata 0x11fbb2c0`) | `&PTR_FUN_11fdf198` (`.rdata 0x11fdf198`) | vftable, которую она устанавливает |
| слоты `+0x00 0x1039ed60`, `+0x04 0x1039ed00`, `+0x08 0x104833e0` | `0x103a5e90`, `0x103a5e30`, `0x10005920` | другие виртуальные слоты |
| слот **`+0x0c` = `0x118531c0`** | слот **`+0x0c` = `0x11863de0`** | thunk «обеспечь таблицу»: строит таблицу реестров один раз, затем возвращает глобал-контейнер |
| слоты `+0x10 0x113418e0`, `+0x14 0x1033ebf0`, `+0x18 0x1039ed50`, `+0x1c 0x104833e0` | `0x11347160`, `0x1013e460`, `0x103a5e80`, `0x10005920` | остальные слоты |
| слот `+0x20 0x11853120` | слот `+0x20 0x11863d40` | соседний accessor |

Pseudocode фабрики, идентичный по строкам индексов (`local/scratch/rea/pseudo-fc3dll-v2/functions/0x111e9540.c` ↔
`pseudo-d3d11-v2/functions/0x111eeed0.c`):

```c
if (DAT_128042fc == '\0') FUN_11789a00();        if (DAT_128293f4 == '\0') FUN_1179a990();
if (DAT_12162beb != '\0')                          if (DAT_12187c6b != '\0')
  { if (FUN_1177f7c0() != 0) goto ok; }             { if (FUN_11790750() != 0) goto ok; }
if (FUN_118db560() == 0) return 0;               if (FUN_118e8340() == 0) return 0;
ok: puVar2 = FUN_11341d40();                     ok: puVar2 = FUN_113475c0();
    *puVar2 = &PTR_FUN_11fbb2c0;                     *puVar2 = &PTR_FUN_11fdf198;
    return puVar2;                                 return puVar2;
```

- Тот же тройной гейт, что и у описанных выше дескриптор-обёрток (`FUN_11789a00`/`FUN_1177f7c0`/`FUN_118db560` ↔
  `FUN_1179a990`/`FUN_11790750`/`FUN_118e8340`): фабрика лежит в той же подсистеме «инициализировать один раз»;
  двойники алкаторa — `FUN_11341d40` ↔ `FUN_113475c0`.
- Thunk слота `+0x0c` охраняется флаг-байтом, FC3.dll `0x1280562f` ↔ FC3_d3d11.dll `0x1282a7a7`: `cmp byte
  [flag],0; jne skip; call 0x11853140 / 0x11863d60; mov byte [flag],1; ret`, а вариант, который хранится в слоте,
  заканчивается `mov eax,0x128334a0` / `mov eax,0x12856970` = **вернуть глобал-контейнер**. Таблица реестров
  строится **один раз, лениво, при первом виртуальном вызове слота `+0x0c`**; `0x11853140`/`0x11863d60` —
  исполнители (построение записи + копия, выше).
- Рядом с vftable идут строки описателей классов: `CFCXGOContextNode`, `CFCXGOContextFlagsNode`, `IGameFileData`,
  `CCampaignGameFileData`, `CFCXGameModeContextNode`, `CFCXGameModeContextFlagsNode`, `CFCXGameMode` (FC3.dll
  `0x11fbb294`, `0x11fbb2a8`, `0x11fbb2e4`, `0x11fbb2f4`, `0x11fbb34c`, `0x11fbb364`, `0x11fbb384`; FC3_d3d11.dll
  `0x11fdf16c`, `0x11fdf180`, `0x11fdf1bc`, `0x11fdf1cc`, `0x11fdf224`, `0x11fdf23c`). Владелец реестровых таблиц —
  семейство **game-object / game-file-data / game-mode context**, то есть семейство, которое несёт запрос сессии;
  поэтому значения `-exec` / `-execline` попадают в параметры сессии (`execLines`), а не выполняются как консольная
  команда.
- Ссылающийся dword лежит в `.text` в обоих модулях (FC3.dll `0x111e9588` → `0x11fbb2c0`, FC3_d3d11.dll
  `0x111eef18` → `0x11fdf198`); это операнд `mov *puVar2, offset …` самой фабрики, а не отдельная таблица.
  Вторая `.text`-ссылка на соседний описатель: FC3.dll `0x1039edd4` → `0x11fbb2e4` (`IGameFileData`) ↔ FC3_d3d11.dll
  `0x103a5f04` → `0x11fdf1bc`.
- **Как доходит до фабрики.** У `FUN_111e9540` / `FUN_111eeed0` — 0 вызовов `E8` и 9 абсолютных ссылок, по одной
  на каждый элемент реестра родственных-классов in `.rdata`. FC3.dll `0x11fbaf44` (файл `0x1fba144`) ↔
  FC3_d3d11.dll `0x11fdee1c` (файл `0x1fdd41c`), шаг `0x28`, элементы `af44, af6c, af94, afbc, afe4, bb00c,
  bb034, bb05c, bb084` ↔ `ee1c, ee44, ee6c, ee94, eebc, eee4, ef0c, ef34, ef5c`; реестр лежит на `0x37c` байт
  раньше vftable. Элемент 0 FC3.dll `111e9540 111e94e0 1030d1d0 1039e3c0 104833e0 111e9fd0 111e8e10 113433b0
  111e9460 111e95a0` ↔ FC3_d3d11 `111eeed0 111eee70 103a56f0 103a5470 10005920 111ef960 111ee7a0 11348c30
  111eedf0 111eef30`: поле 0 = guarded-создатель, поле 1 = его смежная точка входа, поля 4 (`0x104833e0` ↔
  `0x10005920`), 7 (`0x113433b0` ↔ `0x11348c30`) и 9 (`0x111e95a0` ↔ `0x111eef30`) одинаковы в элементах 0-7,
  поле 2 = `0x1030d1d0` ×4 / `0x1039e640` ×3 ↔ `0x103a56f0` ×4 / `0x103a5750` ×3, поле 3 идёт по серии с шагом
  `0x50` (`0x1039e3c0,410,460,4b0,500,550,5a0,5f0` ↔ `0x103a5470,4c0,510,560,5b0,600,650,6a0`). **Элемент 8 —
  другое семейство** (FC3.dll `100519c0 1030df50 10122130 104ef020 1039e780 103feb40 102dac70 100055a0` ↔
  FC3_d3d11 `1027d850 102a8ea0 10241570 1046b300 103a5890 10104c00 10316060 10005880`). Форма — один создатель
  на девять родственных-классов — соответствует именам описателей выше (`CFCXGOContextNode`,
  `CFCXGOContextFlagsNode`, `IGameFileData`, `CCampaignGameFileData`, `CFCXGameModeContextNode`,
  `CFCXGameModeContextFlagsNode`, `CFCXGameMode`). Файл пробы: `local/scratch/fc3_region_dump.py` — выводит диапазон `.rdata` в виде dword-ов
  с декодированием names/strings (`<pe> <va_start> <va_end> <out>`); нужен image base (оба modules 1.06 —
  `0x10000000`, PE32 magic `0x10b`), потому что таблица секций хранит RVAs — FC3.dll `.rdata`
  = VA `0x11bcb000`..`0x12092d21` from file `0x1bca200`, FC3_d3d11.dll `.rdata` = VA
  `0x11be1000`..`0x120b7347` from file `0x1bdf600`. Открытые вопросы этой области: какой из девяти
  элементов владеет реестровой таблицей (`0x118531c0` ↔ `0x11863de0` — её слот `+0x0c`), кто итерирует реестр по адресам
  `0x11fbaf44` ↔ `0x11fdee1c` во время выполнения, и что собой представляет семейство элемента 8.
- Файлы проб: `local/scratch/rd_reg_table_fc3.txt`, `local/scratch/rd_reg_table_d3d.txt`,
  `local/scratch/rd_table_slot_scan.txt` (принадлежность слотов + сырые байты),
  `local/scratch/rd_snapshot_callers.txt` (guarded-одноразовые thunks). `local/scratch/rd_disasm.py` требует
  **четыре** аргумента `<pe> <start_va> <end_va> <out_file>`; с тремя он не печатает ничего.

**Открытые вопросы этой области:** ~~декомпилировать `0x10638fb0` (FC3_d3d11.dll) и `0x1003b4b0`
(FC3.dll), чтобы получить тип элемента exec-записи~~ — решено: 4-байтовые указатели, добавляются по
количеству. Подтвердить, что потребители
`FC3_d3d11.dll 0x11348360` / `FC3.dll 0x11342a2e` обходят `[0x12852dcc]` / `[0x1282f8fc]` в порядке
регистрации; кто записывает разобранную строку `-exec` в контейнер `[0x12829424]` под ключом `execLines`
(известно место вызова `0x11785e60`, возвращаемое смещение `[eax+0x28]`); ~~какая функция владеет
слот-9 указателем~~ — решено: `0x11341420` ↔ `0x11346ca0` — побятно identical flag-гатеры
(`byte [this + 0x21]`), а тик, который они охраняют — `FC3.dll FUN_11341340` ↔
`FC3_d3d11 FUN_11346bc0`; и достижим ли `Exec`
(`0x11fbda40`, указатель обработчика сохранён в `0x111f5c71`) из этого контейнера при запуске.
- Осталось: кто вызывает слот vftable `+0x0c` (`0x118531c0` ↔ `0x11863de0`) — у виртуального вызова нет формы
  ближнего `E8`, поэтому следующий шаг — вызывающие фабрики (`FUN_111e9540` ↔ `FUN_111eeed0`) и вызов создания
  сессии, который база знаний coop-anything относит к **слоту vftable `+0x74`** объекта сессии (FC3.dll
  `0x11a8d0c5`-`0x11a8d0eb`: `call 0x11341dc0`; `mov ecx,[eax]`; `mov eax,[ecx]`; `mov eax,[eax+0x74]`;
  `call eax`; деструктор сессии `0x11343640`, vftable `0x11f90644`, освобождаемые поля `[obj+0x98]`/`[obj+0x9c]`).
- Функции FC3_d3d11 `0x111eed50`, `0x111eedf0`, `0x111eec50`, `0x111eecb0` читают и пишут поля `+0x98` и `+0xa4`
  (`if (*(int *)(in_ECX + 0xa4) == -1 && *(int *)(in_ECX + 0x98) != 0) { *(undefined4 *)(in_ECX + 0xa4) =
  *(undefined4 *)(*(int *)(in_ECX + 0x98) + 0x10); … }`) — это совпадает с раскладкой `[obj+0x98]` объекта сессии; их
  pairить следующими. Дальнейший шаг: 180-байтовый struct параметров сессии в `FC3.dll 0x11f31d8c` ↔
  `FC3_d3d11.dll 0x11f54b70` либо `0x11f31a80` ↔ `0x11f548a0` — выгрузить диапазон и декодировать его dword как
  пары строка/указатель.
- Новое (та же область): являются ли эти записи контейнерами `std::vector` (триады base/count/
  capacity) — статически `[0x12852dcc]` и сосед `[0x12852dd0]` равны адресу inline-хранения
  `0x12856968`, т.е. пустой контейнер; следующий зонд — `FC3.dll 0x113429b0` ↔
  `FC3_d3d11.dll 0x11348230` и `FC3.dll 0x11341fe0` ↔ `FC3_d3d11.dll 0x11347860`.

### Таблица записей находится внутри цепочки из 57 статических контейнеров (2026-11-05)

Эти глобалы обслуживают два семейства accessor-ов; оба найдены `scripts/fc3_reloc_xref.py
--mode reloc` — режим `code` видит только формы `ModRM` с displacement и пропускает `mov reg,
imm32`, поэтому для этих глобалов надёжен reloc-режим.

- Семейство 1, живые контейнеры. Каждый accessor — двухинструкцияный thunk `mov eax, imm32` затем
  `jmp 0x10004b70` (FC3.dll) / `jmp 0x10004d70` (`FC3_d3d11.dll`), thunk'и с шагом `0x10`, возвращают
  глобалы в основном с шагом `0x18`. Цепочка, которой принадлежит таблица записей, насчитывает
  **57 accessor-ов**: `FC3.dll 0x11bb33f0` .. `0x11bb3780` с глобалами `0x1282f6cc` .. `0x1282fca8`, зеркало
  `FC3_d3d11.dll 0x11bc8950` .. `0x11bc8ce0` с глобалами `0x12852b9c` .. `0x12853178`. Внутри неё
  таблица exec-записей — `FC3.dll 0x11bb3560` → `0x1282f8fc` ↔ `FC3_d3d11.dll 0x11bc8ac0` →
  `0x12852dcc`, а таблица, добавленная к этой паре 2026-11-03 — accessor на слот раньше: `FC3.dll
  0x11bb3550` → `0x1282f8e4`/`0x1282f8e8` ↔ `FC3_d3d11.dll 0x11bc8ab0` → `0x12852db4`/`0x12852db8`.
  Прежний вариант этого раздела прочитал это окно как семейство из семи элементов (`0x11bb3510` ..
  `0x11bb3570`); это хвост данной 57-элементной цепочки, а не её полный диапазон.
- Замер по всему модулю той же формы thunk'а (`scripts/fc3_accessor_thunks.py`, скан `.text`): в
  FC3.dll
  **3228** thunk'ов `mov eax, imm32` + `jmp 0x10004b70` в **523** непрерывных цепочках; в
  `FC3_d3d11.dll` столько же **3228** в тех же **523** цепочках. Здесь важны две из них: 57-
  элементная цепочка таблицы записей выше и 19-элементная цепочка вторичного блока: `FC3.dll
  0x11bb6430` .. `0x11bb6550` (глобалы `0x128333a8` .. `0x12833564`) ↔ `FC3_d3d11.dll 0x11bcb980` ..
  `0x11bcbaa0` (глобалы `0x12856878` .. `0x12856a34`).
- Счёт patch-сайтов reloc-режима зеркален по модулям: `--mode reloc 0x1282f884` (FC3.dll) → 36
  сайтов; `--mode reloc 0x12852d54` (FC3_d3d11.dll) → 36 сайтов. Сайты группируются триадами с
  шагами `+0`, `+0x12`, `+0x27` — это три поля одного контейнера, записываемые в каждом routine:
  инициализация `FC3.dll 0x10f92e98`/`0x10f92eaa`/`0x10f92ec7` ↔ `FC3_d3d11.dll 0x10f986f8`/
  `0x10f9870a`/`0x10f98727`; consumers `FC3.dll 0x11341f28` .. `0x11342577` ↔ `FC3_d3d11.dll
  0x113477a8` .. `0x11347df7`; teardown `FC3.dll 0x113439f8`/`0x11343a0a`/`0x11343a27` ↔
  `FC3_d3d11.dll 0x11349278`/`0x1134928a`/`0x113492a7`; accessors `FC3.dll 0x113415f1` ↔
  `0x11346e71` и `0x11bb3511` ↔ `0x11bc8a71`.
- Семейство 2, вторичный блок, который заполняют все контейнеры (та же 19-элементная
  цепочка). `FC3.dll 0x11bb6440` .. `0x11bb64d0` возвращают `0x128333c0`, `0x128333d8`, `0x128333f0`, `0x12833408`, `0x12833420`,
  `0x12833438`, `0x12833450`, `0x12833468`, `0x12833480`, `0x128334a0` (шаг `0x18`, последний шаг
  `0x20`); `FC3_d3d11.dll 0x11bcb9c0` .. `0x11bcba10` возвращают `0x128568d8`, `0x128568f0`,
  `0x12856908`, `0x12856920`, `0x12856938`, `0x12856950`. `FC3_d3d11.dll 0x11b73160` ..
  `0x11b73177` разбирает один элемент этого блока: `xor eax,eax` / `push 0x11bcba10` /
  `mov [0x12856958],eax` / `mov [0x12856964],eax` / `call 0x1070085d` (освободить контейнер с
  базой `0x12856968`, передав его собственный accessor), затем `0x11b73180` `push 0x11f31b44
  "Main"; call 0x11798fc0`.
- Этот контейнер — тот же самый, который возвращает слот vftable `+0x0c`. `FC3.dll 0x11853140` ↔
  `FC3_d3d11.dll 0x11863d60` — once-init под accessors'ом (byte-guard `0x1280562f` у FC3.dll,
  `0x1282a7a7` у FC3_d3d11.dll): вызывает `FC3.dll 0x113429b0` ↔ `FC3_d3d11.dll 0x11348230`,
  читает `[0x1282f8fc]`/`[0x1282f900]` ↔ `[0x12852dcc]`/`[0x12852dd0]` с полем ёмкости
  `[0x128334a4]` ↔ `[0x12856974]`, дописывает через `FC3.dll 0x1003b4b0` (проверенный `call` в
  `0x1185317a`) ↔ `FC3_d3d11.dll 0x10638fb0` (проверенные места вызова `0x11863d9a` в once-init
  шестого контейнера и `0x11863cfa` в once-init пятого), и копирует через `FC3.dll
  0x106f9ff0` ↔ `FC3_d3d11.dll 0x10700c10` (`push edi; push ebx; push eax; call 0x10700c10; add
  esp,0xc`). Парный once-init `FC3.dll 0x118530a0` ↔ `FC3_d3d11.dll 0x11863cc0` проделывает то же
  для пятого контейнера (`[0x1282f8e4]`/`0x1282f8e8` ↔ `[0x12852db4]`/`0x12852db8`, поля
  `0x128334b8`/`0x128334bc` ↔ `0x12856988`/`0x1285698c`) через `FC3.dll 0x11341fe0` ↔
  `FC3_d3d11.dll 0x11347860`. Их вызывающие — только служебные (`0x118531a9`/`0x118531c9` и
  `0x11853109`/`0x11853129` ↔ `0x11863dc9`/`0x11863de9` и `0x11863d29`/`0x11863d49`): обе функции
  достигаются как слоты vftable `+0x0c` и `+0x20` и через их собственный once-init, а не как ближний
  вызов.

## TODO

- **Адресной аудит строк 1.06 и блок полей GameContext.** Проверено прямыми чтениями `FC3_d3d11.dll`
  по отображению `.rdata` (смещение файла = VA - `0x11be1000` + `0x1bdf600`; проверка: строка `execLines`
  в файле `0x1fb3080` = VA `0x11fb4a80`). Строка `-coop` начинается в `0x11fdc0cc`, `-numclients` —
  `0x11fb1e18`; у `-numclients` есть ссылка `0x1135381e` (в цепочке реестра сессий), а у `-splitscreen`
  и `-splitscreen4` ссылок нет. Опции спойла разобраны в трёх группах: `-spawn` `0x11aa0eb8`/`0x11aa0ecb`,
  `-spawnpos` `0x11aa0f09`/`0x11aa0f20`, `-spawnangle` `0x11aa0fbd`/`0x11aa0fd4` (функция `0x11aa0670`);
  `0x11aa15f3`/`0x11aa1606` … `0x11aa16fb`/`0x11aa1712` (функция `0x11aa1b90`) и `0x11aa2777`/`0x11aa278a`
  … `0x11aa286b`/`0x11aa2882` (третья функция разбора). Имена полей узла контекста игры идут подряд
  (`world` `0x11f46910`, `spawnAt` `0x11f4692c`, `spawnPos` `0x11f46934`, `spawnAngle` `0x11f46940`,
  `usePosAngle` `0x11f4694c`) и все четыре ссылает одно место — `0x1170fdba`, `0x1170fdcf`, `0x1170fde7`,
  `0x1170fe03`. Имена реестра сессий `spawnPtId` `0x11fb4c98` → `0x11347f0b`, `keepPlayerState`
  `0x11fb4ca4` → `0x11347f20`, `touched` `0x11fb4c90` → `0x11347e68`, `mode` `0x11fb4c88` → `0x11347f6c`
  и `0x11347f9c`. В `0x11fdbdc4`, `0x11fdbde4`, `0x11fdbe0c`, `0x11fdbe30` лежат готовые строки с
  уже подставленными значениями: `' -spawnpos=333.63,964.5,124.465'`, `' -spawnangle=0.0,0.0,0.0'`,
  `' -spawnpos=-857.626,2317.1,119.752'`, `' -spawnangle=0.0,0.0,-20.0'`; они ссылает парсер `0x11aa2fe0`
  (`0x11aa3aeb`, `0x11aa3afe`, `0x11aa394c`, `0x11aa395f`) — то есть игра уже умеет собирать полную
  командную строку запуска со спойлом. Отсутствие в 1.06 имён `sessionName`, `sessionDescription`,
  `sessionFilter1/2`, `clientName`, `serverName`, `sessionExecFile`, `execFilenames2`, `bundleName`,
  `bundleDir`, `bundlePath`, `sessionPath`, `sessionParams`, `spawn_angle` подтверждено (0 вхождений).

- **Путь spawn-данных решён (проверено дизассемболом).** Все четыре ссылки на spawn-поля GameContext
  (`0x1170fdba`, `0x1170fdcf`, `0x1170fde7`, `0x1170fe03`) — это thunk отложенной регистрации
  дескриптора `0x1170fd70` (проверка `cmp byte [0x128299c8],0`): `push <смещение>; push <VA имени>;
  mov eax,0x1282db10; call 0x11acaba0|0x11acac50|0x11acae60`. Карта полей узла `0x1282db10`: `world`
  +0x08, `mergedBigFileName` +0x10, `spawnAt` +0x0C (строка), `spawnPos` +0x14 (три float), `spawnAngle`
  +0x20 (три float), `usePosAngle` +0x2C (байт), `loadingdepActive` +0x2D. Парный thunk `0x1170fe40`
  регистрирует `networkGame`/`host` на другом структе (`0x1282daf8`). Запись происходит только в трёх
  парсерах: цепочка всегда одна — `strstr [0x11be1618]` → извлекатель значения `call 0x11a1b940` →
  `sscanf [0x11be1398]` с форматом `'%g,%g,%g'` (`0x11f39f50`) → доступ к узлу (`mov eax,[esi+0x9c]`;
  `mov edi,[eax+4]`; `mov eax,[edx+0x18]`; `call eax`; результат кэшируется в `[edi+8]`) → запись.
  `-spawn` → `call 0x11347550` (`0x11aa0eeb`, близнец `0x11aa27a3`) пишет строку со ссылками в
  узел +0x0C (двойник `0x113474e0` с `add eax,8` пишет `world` в +0x08). `-spawnpos` пишет
  `movss [eax+0x14]`, `+0x18`, `+0x1c` и ставит `mov byte [eax+0x2c],1` без перевода градусов
  (`0x11aa0f8a`–`0x11aa0f9e`, также `0x11aa16c8`–`0x11aa16de`, `0x11aa2839`–`0x11aa284d`).
  `-spawnangle` загружает `0x11f32198` = 0,0174532924 (1 градус в радианах), умножает все три
  компонента (`mulss`, `0x11aa1031`–`0x11aa1039`) и пишет `movss [eax+0x20]`, `+0x24`, `+0x28`
  (`0x11aa1014`–`0x11aa1084`, также `0x11aa1723`–`0x11aa17d0`, `0x11aa288d`–`0x11aa28b6`) — игра
  хранит **радианы**. Парсер exec также собирает целые командные строки: вариант A
  (`0x11aa3909`–`0x11aa3967`, затем `call 0x11aa2630` в `0x11aa3989`) = `' -world=fc3_main'`
  (`0x11fdbdb0`) + `' -spawnpos=-857.626,2317.1,119.752'` + `' -spawnangle=0.0,0.0,-20.0'` после
  `'Gamescom'` (`0x11fdbe00`); вариант B (`0x11aa3aaa`–`0x11aa3b06`) с `333.63,964.5,124.465` и
  `0.0,0.0,0.0`; рядом `-benchmark` (`0x11fdbe4c` → `call 0x11aa14b0` в `0x11aa39ed`), `-host`
  `0x11f31c7c`, `-client` `0x11f31d18`, `'multi_SkipIntroMovie 3'` `0x11fdbd30`,
  `'starMatch_with_debugCameras 1'` `0x11fdbd10`. **Отдельного спойла на игрока нет:** `spawnPtId`
  `0x11fb4c98` и `keepPlayerState` `0x11fb4ca4` встречаются только внутри `0x11347e40` — одноразовой
  регистрации (`cmp byte [0x1282a610],0` → `jne 0x11347f2c`), которая выделяет ровно одну запись
  `0x10+0x20` (`call 0x11790750`), добавляет её единственным `push 1` в массив по 4 байта на запись
  (`[0x12852e2c]`/`[0x12852e30]`, отдельный контейнер, не `[0x12852dcc]`/`[0x12852dd0]` с execLines)
  и регистрирует поля от `lea esi,[edi+0x14]`: `world` +4, `pos` `0x11f39450` +8, `spawnPtId` +0x18
  (`call 0x11acaf10` в `0x11347f11`), `keepPlayerState` +0x20 (`call 0x11acac50` в `0x11347f24`).
  Нет петли, индекса и перебора игровых слотов → спойл один на всех. РЕШЁНО (2026-11-02, локальная
  проверка дизассемблером по `.text` файла 1.06): адреса быстрой загрузки `0x111e1e54`/`0x111e2970`/
  `0x111e4140` — не потребители спойла, а писателя `[edi+0x430]`/`[edi+0x434]` не существует (полный скан
  `.text` не нашёл `lea ecx,[edi+0x430]`; только 4 mov-подобных обращения к `+0x430`/`+0x434` вне спойла:
  `0x10544b8d`, `0x10e6356d`, `0x10e63597`, `0x1160ab44`). `0x111e2970`/`0x111e2984` лежат внутри функции
  `0x111e27b0`, `0x111e4140` — внутри `0x111e3f30`, а `0x11057c60`/`0x10404f40` не имеют пролога в пределах
  0x900 байт. `0x111e1e54` — тонкая обёртка (`mov eax,[0x1282a7b4]; call 0x111e9bd0; ret 4`), а
  `0x111e9bd0` — чистый диспетчер (`call 0x111e7300`, `0x102745d0`, `0x11706240`, `0x11310be0`, `0x1013b1c0`,
  `0x106bd910`), spawn-смещения не трогает; сингл `[0x1282a7b4]` (91 ссылок) не содержит указателя на узел
  `0x1282db10` (0 вхождений вне `.text`). Сам узел `0x1282db10` имеет 13 ссылок — все в цепочке
  регистрации/потребления (`0x1125ed11`, `0x1170f491`, `0x1170fc5b`, `0x1170fc6d`, `0x1170fd8e`..`0x1170fe36`,
  `0x11bbb1f1`). Проверочные скрипты: `local/scratch/ql_local.py`, `ql2.py`, `ql3.py`, вывод в
  `local/scratch/out/ql_local.txt`, `out/ql2.txt`, `out/ql3.txt`.
- [x] Уточнить версия игры и путь у владельца (1.06, `H:\Uplay\Far Cry 3\`)
- [x] Подготовить тестовую копию FC3 1.06 (`H:\FarCryCoop\TestFC3\`, вне папки установки)
- [x] Изучить результаты Фазы 1 из Bantila/FarCry3Coop (см. `NOTES.ru.md`, `PLAN.ru.md`)
- [x] Решение принято (2026-11-02): отдельный форк этого репозитория `peperonid/FarCry3Coop`
    (fork от Bantila/FarCry3Coop) — рабочая копия этой игры; форк конвейера `peperonid/FarCryCoop`
    остаётся для других игр (`games/far-cry`, `games/far-cry-6`). Ветка `backup` владельца не трогать.
- [ ] Фаза 2: архитектурный спайк (неткод движка vs свой UDP)
- [ ] Изучить мод scubrah для запуска острова в ко-опе
- [ ] Зондировать структуру параметров сессии в `FC3.dll` 1.05 `0x10a8d0db` (`push <имя>; push 0x1c;
  call 0x10a46480` — helper регистрации опций, тип 8 в 1.06) и vftable слот 0x74 сессионного интерфейса —
  через них `-exec`/`-execline` попадают в запрос ко-оп сессии; размеры структуры в 1.05 подтвердить
  динамически (статическая проверка «180 байта» не подтверждена)
- [ ] Динамическая зацепка для исполнителя `execLines`: запустить тестовую копию с `-exec <файл>`
  (или `-execline`) и зафиксировать, как строка попадает в 180-байтную структуру сессии; параллельно
  разобрать в Ghidra accessor-thunkи `0x11bc8a80`..`0x11bc8ad0` и `0x10004d70`
- **Таблица регистрации launch-режимов `FC3.dll 0x1119dec0 .. 0x1119df9a` и `0x1119f910 .. 0x1119fa42`**
  (проверено 2026-11-06, `local/scratch/probe36.txt`, `probe37.txt`). `0x1119dec0` кладет id-глобалы в
  объект `[0x12804acc]`: на каждый вызов `mov eax, dword ptr [0x12804acc]` + `add eax,4` +
  `push <VA id-глобалы>` + `call 0x1029eb00` (хелпер `0x1029eb00` = регистрация id). Порядок такой же,
  как в таблице `0x1111e390` / `0x1111e860`: `0x1216caac` (`0x1119dec6`), `0x1216ca9c` (`0x1119ded8`),
  `0x1216ca90` (`0x1119deea`), `0x1216caa4` (`0x1119defc`), `0x1216caa8` (`0x1119df0e`), **`0x1216aee4`
  `-coop` (`0x1119df20`)**, `0x1216aedc` (`0x1119df32`), `0x1216af0c` (`0x1119df44`), `0x1216aeec`
  (`0x1119df56`), `0x1216aef4` (`0x1119df68`), `0x1216aefc` (`0x1119df7a`), `0x1216af04` (`0x1119df8c`),
  `pop ecx; ret` в `0x1119df99`. `0x1119f910` привязывает обработчик к id: `mov esi, dword ptr
  [0x12804acc]` + `add esi,4` + `push <VA обработчика>` + `push <VA id-глобалы>` + `call 0x1029edc0`
  (парами: `0x11152dd0`↔`0x1216caac` в `0x1119f91d`, `0x11152f50`↔`0x1216ca9c` в `0x1119f935`,
  `0x11a7a2e0`↔`0x1216ca90` в `0x1119f94d`, `0x11a5a290`↔`0x1216caa4` в `0x1119f965`, `0x11a5a0b0` ↔
  `0x1216caa8` в `0x1119f97d`, **`0x11a5a6e0`↔`0x1216aee4` (co-op, `0x1119f995` / `0x1119f99f`)**,
  `0x11a7aff0`↔`0x1216aedc` в `0x1119f9ad`, `0x11a7aa00`↔`0x1216af0c` в `0x1119f9c5`, `0x11a7ae80` ↔
  `0x1216aeec` в `0x1119f9dd`, `0x11a7ad00`↔`0x1216aef4` в `0x1119f9f5`, `0x11a7ab80`↔`0x1216aefc` в
  `0x1119fa0d`, `0x11a5a560`↔`0x1216af04` в `0x1119fa25`, `pop esi; ret` в `0x1119fa42`).
- **Конструктор co-op режима `FC3.dll 0x11a5a6e0 .. 0x11a5a772`** (обработчик, привязанный к `-coop`):
  шлюзы `cmp byte ptr [0x128042fc],0` → `call 0x11789a00` (`0x11a5a6ea..0x11a5a6f2`) и `cmp byte ptr
  [0x12162beb],0` (`0x11a5a6f7`); размер объекта `mov edx,0x10; lea ecx,[edx+0x30]` (=0x40) +
  `call 0x1177f7c0` (`0x11a5a6ff..0x11a5a707`, запасной путь `mov eax,0x10; lea edi,[eax+0x30];` +
  `call 0x118db560` в `0x11a5a710..0x11a5a718`); инициализация `[obj] = 0x11f23408` (`0x11a5a721`),
  поля `+4`..`+0x2c` обнуляются, `+0x30 = 0xffffffff` (`0x11a5a748`), `+0x34` (слово) и `+0x36` (байт)
  тоже 0; затем виртуальная таблица → **`0x11fbb838`** (`0x11a5a756`) и `mov ecx, [0x1216aee4]` (`0x11a5a75c`) →
  `mov dword ptr [eax + 0x30], ecx` (`0x11a5a762`); при отказе шлюза возвращает 0 (`0x11a5a76b`).
  Смещение `+0x30` — ровно то, что читают co-op проверки: `[0x12804acc]` → `+0x68` →
  `mov eax,[eax+0x30]` → `cmp eax,[0x1216aee4]` в `0x1111e4d4/0x1111e4e3` и
  `0x1111e907/0x1111e916/0x1111e91e`.
- **Вторая цепочка launch-режимов, вход RESOLVED: `FC3.dll 0x11a8c8b0 .. 0x11a8d110`** (ранний
  «mid-instruction» диапазон `0x11a8c944 .. 0x11a8c9c1` — внутри этой функции). Аргументы разбираются
  через `mov edi, dword ptr [0x11bcb5c0]` (`0x11a8c8bc`) + `call edi`: `-login` `0x11fb8170`
  (`0x11a8c8c2`); путь ошибки `push 0x11fb81b4` = `'Invalid parameters for -host, missing (-login)'`
  (`0x11a8c8d6`, `0x11a8c8e6`) → `call 0x10a00be0` / `call 0x10001ed0` → `xor al,al; ret 0xc`
  (`0x11a8c8f2..0x11a8c8fa`); далее `-host` `0x11f0e6ac` (`0x11a8c90b`, геттер `call 0x11a08190`),
  `-bfname` `0x11fb7d64` (`0x11a8c919`), `-dedicated` `0x11f0e7dc` (`0x11a8c927`), `-sessionuid`
  `0x11fb81f0` (`0x11a8c935`), `-deathmatch` (`0x11a8c943`), `-coop` `0x11fb81fc` (`0x11a8c95c`),
  `-domination` `0x11fb8204` (`0x11a8c976`), `-headquarters` `0x11fb8210` (`0x11a8c990`), `-firestorm`
  `0x11fb8220` (`0x11a8c9a6`), `-dash` `0x11fb822c` (`0x11a8c9c0`). Id режима попадает в локальный слот
  `[ebp+0xc]` (`-coop`: `0x11a8c96b mov ecx,[0x1216aee4]` затем `0x11a8c971 mov [ebp+0xc],ecx`;
  `-deathmatch`: `0x11a8c952 mov eax,[0x1216aedc]` затем `jmp 0x11a8c9df`; default `0x11a8c9da
  mov eax,[0x1216af0c]` затем `0x11a8c9df mov [ebp+0xc],eax`) и сохраняется в launch-объект:
  `0x11a8c9e2 mov ecx,[ebp+0xc]` → **`0x11a8c9ea mov dword ptr [esi + 0xa4], ecx`**, дальше виртуальные
  вызовы `[+0x14]` и `[+0x18]` (`0x11a8c9e5..0x11a8c9fb`), `push [ebp+0x10]; mov edi,esi;` +
  `call 0x119696d0` (`0x11a8c9fd..0x11a8ca03`), `lea edx,[esi+4]; push edx; push ebx;` +
  `call 0x11a8bdc0` (`0x11a8ca08..0x11a8ca0d`), `mov eax,[esi+0x9c]; lea edi,[ebp-0xc];` +
  `call 0x11341c60` (`0x11a8ca12..0x11a8ca1b`), `mov ecx,[edi+0x9c]; add eax,0x4c; cmp ecx,eax`
  (`0x11a8ca20..0x11a8ca2c`). Co-op ветка: `0x11a8cabb mov ecx,[ebp+0xc]` → `0x11a8cabe cmp ecx, dword
  ptr [0x1216aee4]` → `0x11a8cac4 jne 0x11a8cb17` → **`0x11a8cac6 push 0x11fb7fb8` = `-class`** →
  `push ebx;` + `call dword ptr [0x11bcb5c0]` (`0x11a8cacb..0x11a8cacc`) — `-coop` запрашивает имя
  класса режима; дальше `lea eax,[ebp+0xc]` + `mov dword ptr [ebp+0xc],0` + `call 0x11a08190`
  (`0x11a8cad9..0x11a8cae9`), поиск имени `mov eax,[esi+0x9c]` + `lea edi,[ebp+0xc]` + `call 0x11341b80`
  (`0x11a8caee..0x11a8cafa`), освобождение ссылки `lock xadd dword ptr [eax], edx` (`0x11a8cb09`) и
  `mov eax,edi; call 0x100945e0` (`0x11a8cb10..0x11a8cb12`), следующий аргумент `-spawn` `0x11fb7fc0`
  (`0x11a8cb17..0x11a8cb1d`).
- **Геттеры реестра режимов и маска доступности (проверено 2026-11-06)**: `FC3.dll 0x117094a0` и
  `0x117094d0` находят запись реестра по id режима — `ecx` = VA id-глобалы, `eax` = контейнер
  (`[0x128048c0]`): `mov edx, dword ptr [ecx]` (id), количество `mov ecx, dword ptr [eax+8]`, база
  массива `mov esi, dword ptr [eax+4]`, `lea ecx, [esi+ecx*4]`, цикл `cmp dword ptr [esi+0x20], edx`
  (`0x117094b4` / `0x117094e7`), при совпадении `mov eax, dword ptr [edx+0x24]` (`0x117094c7` /
  `0x117094fa`) — поле записи **`+0x24`**, которое `0x117094d0` проверяет маской: `test dword ptr
  [ebp+8], eax; setne al; ret 4` (`0x117094fd..0x11709504`), при промахе `xor eax,eax` и та же проверка
  (`0x11709507..0x1170950f`). Цикл шлюза по режимам — `FC3.dll 0x10f3cd30 .. 0x10f3d260`: маска из
  **`[ebx + 0xc4]`** (`0x10f3cfd0`, `0x10f3cff3`, `0x10f3d015`, `0x10f3d03c`, `0x10f3d063`), реестр
  `mov eax, dword ptr [0x128048c0]` (`0x10f3cfc9`, `0x10f3d01c`, `0x10f3d042`, `0x10f3d069`),
  кандидаты `0x1216af04` (`-dash`, `0x10f3cfd7`), `0x1216af0c` default (`0x10f3cffa`), `0x1216aeec`
  (`-domination`, `0x10f3d021`), `0x1216aef4` (`-headquarters`, `0x10f3d048`), `0x1216aefc`
  (`-firestorm`, `0x10f3d06f`); при успехе `push <VA id>` + `push edi` + `mov ecx, ebx` +
  `call 0x11258cc0` (`0x10f3d00d..0x10f3d010`), входной тест `cmp dword ptr [esp+0x20], 1`
  (`0x10f3cfc4`), конец `mov eax, edi; call 0x11257550` (`0x10f3d08a`). Это связано с `gamemodemask 128`
  в `worlds/downloadcontent/mp_dlc1/toc.rml` (обе co-op карты) — именно такую форму сравнивают поле
  записи `+0x24` и маска вызывающего `[obj+0xc4]`.
- [ ] Расшифровать, что разрешает аргумент `-class` в co-op ветке `0x11a8c8b0` (`0x11a8cac6..0x11a8cb17`)
- [ ] Найти вызывающих конструктор co-op режима `0x11a5a6e0` и кто пишет в `[0x12162beb]` / `[0x128042fc]`
  (его шлюзы)
- [x] Часть решено 2026-11-06: этот участок — цепочка поорежимной установки менеджера режимов (см.
  раздел «Объект-менеджер режимов и реестр режимов» ниже). Ещё не прочитано: начало функции
  `0x1119fa50` (400 инструкций, уже даётся в `local/scratch/probe36.txt`) и поорежимные конструкторы
  объектов `0x11a5a0b0`, `0x11a5a290`, `0x11a5a560`, `0x11a7a2e0`, `0x11a7aa00`, `0x11a7ab80`,
  `0x11a7ad00`, `0x11a7ae80`, `0x11a7aff0`
- [x] Решено 2026-11-06: это тот же объект, он устанавливается в `0x117567ce`; см. раздел
  «Объект-менеджер режимов и реестр режимов» ниже. Предположение о разных формах (регистрация кладёт
  **адреса** id-глобал вроде `push 0x1216aee4`, а co-op проверка сравнивает **значение** id)
  оказалась неверной: `+0x68` — указатель на реестр, а `+0x6c` — флаг владения.

## Объект-менеджер режимов и реестр режимов (2026-11-06, FC3.dll 1.06, `local/scratch/probe53.py` .. `probe56.py`)

- **`[0x12804acc]` устанавливается в `0x117567ce mov dword ptr [0x12804acc], esi`** (`FC3.dll
  0x117567c0 .. 0x11756810`): основной vtable `0x11f16a3c` (`0x117567c4`), второй vtable `0x11f1bdc0`
  в `+4` (`0x117567d4`) и в `+0x30` (`0x117567ed`), вложенные объекты строятся в `+8`
  (`lea ecx,[esi+8]` + `call 0x106bdde0` в `0x117567cb/0x117567db`) и в `+0x34`
  (`lea ecx,[esi+0x34]` + `call 0x106bdde0` в `0x117567ea/0x117567f4`), поля `+0x24/+0x28/+0x2c` и
  `+0x50..+0x64` обнуляются (`0x117567e0..0x11756808`), третий вложенный объект в `+0x70`
  (`lea ecx,[esi+0x70]`, `0x1175680b`). Ссылка обнуляется дважды: `0x11756f37 mov dword ptr
  [0x12804acc], ebx` после `call 0x106bde10` (`0x11756f31`) и `0x10048100 mov dword ptr [0x12804acc],
  0` внутри удаляющего деструктора `0x100480f0` (`mov dword ptr [esi], 0x11f169dc` в `0x100480fa`).
- **API регистрации `0x1029eb00` получает карту `obj+0x30`**: `mov eax, dword ptr [ebp+8]` +
  `add eax, 0x30` + `call 0x1029eb00` (`0x117567ab..0x117567b1`). Регистрация launch-режимов
  `0x1119dec0` использует то же API с `add eax, 4`; разница смещений пока не объяснена.
- **`engine\gamemodes\GameModesConfig.xml` (`0x11f16940`) имеет ровно две ссылки, обе в одной функции
  `0x117568a0`**: `mov ecx, dword ptr [0x12804308]` (`0x117568a6`) → `mov eax,[ecx]` +
  `mov edx,[eax+0x10]` (`0x117568ae`) → `push 0x11f16940` (`0x117568b5`) → `call edx` (`0x117568ba`);
  ветка «не найдено» пишет `mov dword ptr [edi], 0` (`0x117568c0`), ветка «найдено» — `push 0;
  push 0x11f16940; lea eax,[esp+0xc]; push eax` (`0x117568cd..0x117568d8`).
- **У контейнера реестра `[0x128048c0]` один создатель и один освобождающий**: создаёт `0x10048230`
  (`mov dword ptr [eax], 0x11f224c4` в `0x10048271`, поля `+4..+0x18` = 0, публикация в `0x10048289`
  и `0x10048297`); освобождается в деструкторе менеджера `0x11756e00`: `mov ecx,
  dword ptr [0x128048c0]` (`0x11756e03`) → при nonzero `mov eax,[ecx]` + `mov edx,[eax]` + `push 1` +
  `call edx` (`0x11756e1a..0x11756e20`) → `mov dword ptr [0x128048c0], ebx` (`0x11756e25`);
  собственный указатель `+0x68` освобождается через `push eax; call 0x11701470`
  (`0x11756e34/0x11756e35`) только при установленном флаге `[esi+0x6c]`
  (`cmp byte ptr [esi+0x6c], bl` в `0x11756e2f`, сброс в `0x11756e3a`). Это подтверждает путь co-op
  проверок `+0x68` и что `+0x6c` — флаг, а не указатель.
- **Установщик режима `0x11756dc0 .. 0x11756dfc` (`ret 0x10`)**: `mov edx, dword ptr [ebp+0x10]`
  (id) + `mov esi, dword ptr [ebp+8]` (менеджер) + `lea eax,[esi+0x30]` + `call 0x118cea00`
  поиск по карте (`0x11756ddc/0x11756ddf`); при попадании `push esi; lea ecx,[esp+0x18];
  call 0x11756a50` (`0x11756de8..0x11756ded`); результат — `mov al, byte ptr [esp+0x13]` (`0x11756df2`).
- **В цепочке установки `0x1119fa50 .. 0x111a0a6b` три группы** (22 вызовов `call 0x11756a50` в
  `0x111a0870..0x111a0a6a`): группа A `call 0x103d2b20` для 11 id (`0x111a0880..0x111a0966`, co-op
  `0x1216aee4` в `0x111a0944`), группа B `call 0x103d2b90` для 5 id (`0x111a097d..0x111a09d9`:
  `0x1216aedc`, `0x1216af0c`, `0x1216aeec`, `0x1216aef4`, `0x1216aefc`), группа C `call 0x103d2c00`
  для 6 id (`0x111a09f0..0x111a0a63`, добавляет `0x1216ca9c`). Co-op встречается только в группе A.
- Сервисы групп: `0x103d2b20` кладёт имя класса `CFCXConsoleService` (`0x11fc5760`) и фабтуру режима
  `0x11a746b0`; `0x103d2b90` кладёт `CFCXMultiPlayerConsoleService` (`0x11fc5568`) и фабтуру
  `0x10fad580`; `0x103d2c00` — третий вариант (`mov al, bl; ret 8` в `0x103d2c63..0x103d2c6b`). Все
  три возвращают булев результат и вызываются только из этой цепочки.
- **`0x11756c50` (`ret 0x10`) отказывает в установке, если id отсутствует в `[0x128048c0]`**
  (поле записи `+0x20`, поиск `cmp dword ptr [ebx+0x20], edi` в `0x11756c82`, промах —
  `xor al,al; ret 0x10` в `0x11756ca5..0x11756cad`); при успехе проходит шлюзы
  `cmp byte ptr [0x128042fc],0` + `call 0x11789a00` (`0x11756cb0..0x11756cb9`) и
  `cmp byte ptr [0x12162beb],0` (`0x11756cc5`), затем выделяет память
  `mov edx,0x10; lea ecx,[edx+0x10]; call 0x1177f7c0`.
- **Регистрация режимов перезапускается драйвером останова/повторной инициализации `0x111f3b30`**
  с началом `mov edi,ecx; call 0x111f22c0; cmp byte ptr [edi+0xb3],0; je 0x111f3c52`: он вызывает
  `0x1119f920` (`0x111f429b`), `0x1119fa50` (`0x111f42a0`), `0x1119dfa0` (`0x111f42a5`) после цикла
  освобождения (`lock xadd dword ptr [eax], edx` + `mov eax,[ecx]` + `mov edx,[eax+4]` + `call edx`
  в `0x111f42dd..0x111f4327`, `mov edi, dword ptr [0x12804b88]` (`0x111f42eb`), `call 0x11938250`
  (`0x111f42f5`), `call 0x1039c5b0` (`0x111f4304`)).
- Маленький аксессор `0x111f3ae0 .. 0x111f3b2b`: `mov eax,[0x12804acc]` + `cmp byte ptr [eax+0x6c],0` +
  `mov eax,[eax+0x68]` + `push eax; call 0x1039c880` + `push eax; call 0x1116d760`, далее
  `[0x12805450]` → `0x1135e720`, `[0x1280564c]` → `0x111e1c00`, `[0x128055ec]` vtable слот `+0xc`,
  `[0x1280563c]` → `0x111e44d0`.
- У `0x111a0860` и `0x111a0a70` **нет** прямых вызывающих по E8/E9: `0x111a0860` достигается
  переходом внутри `0x1119fa50`; `0x111a0a70` — thunk (`push ecx; call 0x1119f920; call 0x1119fa50;` +
  `call 0x1119dfa0; pop ecx; ret` в `0x111a0a70..0x111a0a81`), и его внутренние sites вызова
  `0x111a0a71/0x111a0a76/0x111a0a7b` не являются внешными входами, поэтому вход в него идёт через
  таблицу переходов или ссылку в данных (открыто).
- Родственный конструктор режима `0x11a746b0 .. 0x11a74745` (используется `0x103d2b20`): те же шлюзы
  (`cmp byte ptr [0x128042fc],0` → `call 0x11789a00`; `cmp byte ptr [0x12162beb],0`), выделение
  `mov edx,0x10; lea ecx,[edx+0x40]` (0x50) `call 0x1177f7c0`, инициализация `[obj] = 0x11f169e8`,
  `[+0x1c] = 0xffffffff`, `[+0x48] = 7`, итоговый vtable `mov dword ptr [eax], 0x1200cf78`
  (`0x11a74732`).
- Открыто: кто вызывает `0x117567c0` / `0x117568a0`; что хранит карта `obj+0x30` (`0x118cea00`); кто
  пишет `[obj+0x68]` и устанавливает `[obj+0x6c]`; почему `0x1119dec0` использует `add eax,4`, а
  `0x117567ae` — `add eax,0x30`; потребители регистраторов колбеков `0x1068f590` / `0x11851c40` в
  `0x103d2c6e` / `0x103d2ce0`.


## Объект реестра: выделение, цепочка конструкторов и таблица из тринадцати записей (2026-11-06, FC3.dll 1.06, `local/scratch/probe73.py` .. `probe81.py`)

- `0x111f3b30` — **не** цель таблицы переходов: единственная ссылка на него — слот `+0x44` vtable
  `0x11fba838` (`0x11fba87c`). Сканы в форме RVA для `0x011f3ae0`, `0x011f3b30` и `0x0039c250` дают
  ноль совпадений, значит реестр достигается через vtable и цепочки конечных переходов, а не через
  таблицы переходов.
- `0x11fba838` — общая vtable тринадцати подузлов реестра: ровно тринадцать sites записи, все внутри
  строителя `0x1039c250 .. 0x1039c580`, со смещениями `0x20, 0xb0, 0x140, 0x1d0, 0x260, 0x2f0, 0x380,
  0x410, 0x4a0, 0x530, 0x5c0, 0x650, 0x6e0` (шаг `0x90`). Среди её слотов — скалярный удаляющий
  деструктор `0x1039c580` в `+0x00` и `+0xac`, а также серединонные записи `0x111f3d10` (`+0x24`) и
  `0x111f3b30` (`+0x44`).
- Конструктор каждого подузла — `0x100013c0`: `mov ecx,esi; call 0x106dfa60` +
  `[esi+0x10] = 0x10238ce0` + инициализация маски из глобальной `0x1217c698`
  (`mov eax,[0x1217c698]; mov [esi+4],eax`, далее цикл по битам маски с `shl ecx,cl` / `not eax` /
  `and` / `or` / `add ecx,2` / `shr eax,1`). `0x106dfa60` — базовая инициализация: `[esi+8] = -1`,
  `[esi+0xc] = 0`, `[esi+4] = 0`, затем `0x1217b420` + `call 0x106f6fb0`, `[eax+4] = 0`, `[ecx] = 0`,
  `mov [esi],eax`, `lock xadd dword ptr [ecx],1`.
- Адреса обработчиков, которые передаются в конструкторы тринадцати записей: `0x111f1070`,
  `0x111edbd0`, `0x111f22c0`, `0x111f26c0`, `0x111f22a0`, `0x111f26e0`, **`0x111f3ae0` для записи
  `+0x380`** (site `push` — `0x1039c3e4`), `0x111f20a0`, `0x111f0a90`, `0x111f2140`, `0x111f0a30`
  трижды. Запись `+0x380` — та, у которой обработчик является аксессором кооператива `0x111f3ae0`
  (`mov eax,[0x12804acc]` + `cmp byte ptr [eax+0x6c],0` + `mov eax,[eax+0x68]`).
- Конструктор менеджера `0x1039c030 .. 0x1039c250` (`this` в `esi`): `call 0x106db0d0`; четыре группы
  инициализации (`lea edi,[esi+0x15c]` дважды с шагом `0x24` → `0x106ce850`; `lea ebx,[esi+0x1a8]`
  дважды с шагом `0x48` → `0x106ce8b0`; `lea edi,[esi+0x280]` дважды с шагом `0x84` → `0x106d3ed0`);
  затем `lea edi,[esi+0x388]; call 0x1039c250` — таблица из тринадцати записей лежит на смещении
  менеджера `+0x388`, а её указатели опубликованы в `+0x128..0x158` как `&esi+0x3a8, 0x438, 0x4c8,
  0x558, 0x5e8, 0x678, 0x708, 0x798, 0x828, 0x8b8, 0x948, 0x9d8, 0xa68`. Конечные регистраторы:
  `push 0xd; push edi; mov ecx,esi; call 0x106bc890`, `push 2; lea eax,[esi+0x280]; call 0x106bc860`,
  `push 2; lea eax,[esi+0x15c]; call 0x106bc8b0`, `push 3; push ebx; call 0x106bc8e0`; финал
  `mov eax,esi; ret`. Пары встраиваемых колбеков `(0x111edac0, 0)`, `(0x1039cc20, …)`,
  `(0x1039b990, 0)` регистрируются через `call 0x106bc7b0` со `ecx` = `&esi+0x1f0` и `&esi+0x238`.
- Перепись ссылок по всем исполняемым секциям (`local/scratch/calls.json` хранит 721 985 rel32
  call/jmp ссылок, 178 197 различных целей): у `0x1039c250` один вызывающий (`0x1039c09c`), у
  `0x1039c030` один (`0x1039b719`), у `0x1039b710` один (`0x111f4fcf`), у `0x111f3ae0` один
  (`0x111f3c54`), а у финала `0x1039d020` тринадцать (`0x1039b877..0x1039b97c`).
- Site выделения (`0x111f4f9f..0x111f501d`): после `call 0x1039a420`, `call 0x1039ab60` и общей
  пусковой проверки `cmp byte ptr [0x128042fc],0` → `call 0x11789a00` (`0x111f4fa9`, `0x111f4fb2`)
  объект создаётся через **`mov eax,0x10; mov edi,0xaf0; call 0x118db560`** (`0x111f4fb7`) —
  **размер 0xaf0**, выравнивание 0x10 — и сохраняется как `mov esi,[esp+0x14]` …
  `mov dword ptr [esi+0xd4], eax` (`0x111f4fc6`, `0x111f4fd8`) после `push esi; call 0x1039b710`
  (`0x111f4fce..0x111f4fcf`).
- Записи используются сразу же: `mov ecx,[0x12807738]; push ecx; mov ecx,eax; call 0x106eac80`
  (`0x111f4fde..0x111f4fe7`), затем `mov eax,[esi+0xd4]; mov edx,[0x12807740]; mov ecx,[eax+0x12c];` +
  `mov ecx,[ecx+0x24]; push edx; call 0x106e96c0` (`0x111f4fec..0x111f5002`) и тот же шаблон для
  следующей записи через `[eax+0x130]` с глобальной `[0x12807744]` (`0x111f5007..0x111f501d`):
  опубликованный массив `+0x128..0x158` и есть таблица диспетчера, а поле записи `+0x24` передаётся
  как `this` в `0x106e96c0` с отдельной глобальной из `[0x12807738 + n*4]`.
- Исправления к прежним заметкам: утверждение «thunk `0x11010ee0` → `0x12163234`» неверно (байты
  `0x11010ee0` — это `0c 00`, а дальше padding `0xcc`). У `0x12162beb` 14 218 совпадений в сырых
  байтах, но это immediates вида `cmp eax,0x12162beb`, а не ссылки на память, поэтому реальная
  проверка остаётся `cmp byte ptr [0x12162beb],0` внутри `0x11756c50`.
- Замечание по инструментарию: сырые сканы должны использовать raw-указатель секции
  (`pe.d[ptr:ptr+rawsz]`); прежний `probe72.py` использовал виртуальное смещение как смещение в файле
  (`pe.d[sv:sv+vsz]`), из-за чего все сканы давали ноль. `FC3.exe` отсутствует в
  `H:\FarCryCoop\TestFC3\bin\` (есть только `FC3.dll`, `FC3_d3d11.dll`, `SandBar.dll`, `SandDock.dll`,
  `binkw32.dll`, `FC3Editor.*`, `FC3Updater.exe`); рабочие копии лежат в `E:\FarCryCoop\Work\fc3\FC3.exe`.
- Открыто: кто выделяет контейнер, в поле `+0xd4` которого попадает менеджер (`mov esi,[esp+0x14]` в
  `0x111f4fc6`); что именно делают `0x118db560`, `0x106eac80` и `0x106e96c0`; какая из тринадцати
  записей является кооперативной в ран-тайме (запись `+0x380` — единственная, у которой обработчик
  является аксессором кооператива); потребители `[0x12807738]`, `[0x12807740]`, `[0x12807744]`;
  является ли пара `[0x128042fc]` / `0x11789a00` проверкой стартовых аргументов, которую нужно обойти.
## Сессия агента (2026-11-06, RU): как 1.06 превращает switch в id режима и как ищет сессию по id

`local\scratch\probe101.py`..`probe110.py` (scratch, в репозиторий не попадает). Все адреса —
`FC3.dll` версии 1.06 (`H:\FarCryCoop\TestFC3\bin\FC3.dll`, sha256
`71d58a7a4503c5c67dcd6f4b9445b5e7ac34c12043987f4c7285e13f2ed51c9b`).

### Параметр опций запуска выбирает id режима

`0x11a8c440` — парсер сетевых опций запуска (пролог
`55 8bec 83ec2c 53 8b5d14 56 8b750c 57`, `[ebp+0xc]` = argv). Использует
`mov edi,[0x11bcb5c0]` (аналог `strcmp` из C-runtime) как `push <адрес строки>; push argv;
call edi` и пишет **константу id режима** в выходной параметр. Цепочка проверена дословно:
`-deathmatch` -> `mov eax,[0x1216aedc]` (`0x11a8c529`); **`-coop` (`push 0x11fb81fc` в
`0x11a8c533`) -> `mov ecx,[0x1216aee4]` (`0x11a8c542`) -> `mov [ebp+8],ecx` (`0x11a8c548`)**;
`-domination` -> `[0x1216aeec]`; `-headquarters` -> `[0x1216aef4]`; `-firestorm` -> `[0x1216aefc]`;
`-dash` -> `[0x1216af04]`; **если ни один switch не найден — `mov eax,[0x1216af0c]`
(`0x11a8c5b1`) -> `mov [ebp+8],eax` (`0x11a8c5b6`)**. Ранее в той же функции проверяются
`-login`, `-ip` (строка ошибки `Missing -login or -ip for -client.` в `0x11fb8258`), `-online`,
`-password`, `-bfname`, `-sessionuid`. Копия той же цепочки находится в `0x11a8c8b0` (`-host` в
`0x11a8c90b`, `-coop` в `0x11a8c95c` -> `mov [ebp+0xc],ecx`), и она же — единственный вызывающий
`0x11a8c440` (вынос в `0x11a8d000`); саму `0x11a8c8b0` вызывают из `0x11a8cf45` и `0x11a8d045`.
Значит `0x11a8c440` выполняется только при запуске с сетевыми аргументами: обычный запуск
одиночной игры к нему не доходит.

### Id режимов — 32-битные хеши, они лежат в .data рядом с `0x1216a00c`

Дамп `FC3.dll .data` (после каждого id стоит `0xffffffff`), проверено `probe106.py`:
`0x1216aedc = 0x8b40f692` (-deathmatch), `0x1216aee4 = 0x43521e6f` (**-coop**),
`0x1216aeec = 0xab4fc8e2` (-domination), `0x1216aef4 = 0x9991daec` (-headquarters),
`0x1216aefc = 0xf66ffb87` (-firestorm), `0x1216af04 = 0x2100ced7` (-dash),
`0x1216af0c = 0x6c2b3868` (**режим по умолчанию, когда switch не указан**),
`0x1216aed0/0x1216aed4 = 0x9ba82025`, `0x1216af14 = 0x1577a45d`, `0x1216af18 = 0xfe80eafc`,
`0x1216af1c = 0xa9fc2652`. Соседние слоты `0x1216aeb8`, `0x1216aeb0`, `0x1216aea8` хранят
указатели на строки (`World` `0x11f0f5c4`, `PersistenceDB` `0x11fbad38`, `CampaignSave`
`0x11fbad28`), то есть блок — реестр именованных сессий «имя + хеш», та же форма регистрации,
которая уже зафиксирована для world/session-записей.
### Где используется хеш кооператива (probe107-probe112)

- `0x1133fb80` — 50-байтная проверка (`0x1133fb80`..`0x1133fbb2`, проверена byte-by-byte в
  `local\scratch\p111.txt`): `mov eax,[eax]`, затем `cmp` с `0xab4fc8e2`, `0x43521e6f` (coop),
  `0x9991daec`, `0x6c2b3868`, `0xf66ffb87`, `0x2100ced7`, после каждого `je 0x1133fbaf`; путь
  отказа `xor al,al; ret` в `0x1133fbac`, путь успеха `mov al,1; ret` в `0x1133fbaf`. Отвечает на
  вопрос "is this id one of the network mode ids" и **`0x8b40f692` (-deathmatch) в этот список не
  входит**. `0x113403e0` повторяет те же шесть сравнений в `0x113405a4`, `0x11340623`, `0x11340a26`
  и читает реестр `[0x128048c0]` в `0x113408fa`, `0x11340bdd`. После `ret` у обеих функций идёт
  `int3`-выравнивание, а `0x11204b00` и `0x10fa1710` — крупные функции (`sub esp,0xa94` у
  `0x11204b00`), то есть это полноценная настройка режима по сессии, а не один switch.
- `0x11a7f9d0` запрашивает у аксессора сессию по id: `mov ecx,[0x12804acc]; mov eax,[ecx];
  mov eax,[eax+4]; lea edx,[esp+0x10]; mov [esp+0x14],0x80608f71; push edx; call eax`, а если это
  вернёт false — `mov ecx,[0x12804acc]; mov dword ptr [esp+0xc],0x43521e6f; mov edx,[ecx];
  mov edx,[edx+4]; lea eax,[esp+0xc]; push eax; call edx`, то есть **виртуальный слот +4 объекта
  `[0x12804acc]` — это "find/lookup session by hash id"**, сначала с `0x80608f71` (ещё одно
  зарегистрированное имя, значение пока не атрибутировано), затем с хешем кооператива. Если любой
  поиск удался, код продолжает загрузку `engine\toolsconfig\AlwaysLoaded.xml`
  (`push 0x11f2fd78` в `0x11a7fa2b`). Это место, где игра может запросить coop-сессию вообще без
  аргментов запуска.
- `0x10fa1710` — это не plain mode switch, а **цепочка "имя сессии -> имя загрузочного экрана"**
  (`local\scratch\p112.txt`): имена проверяются относительно `[ebp+0xc]` через `call 0x1011cb30`,
  сопоставляя `'coop_vidar'` (`0x1200e400`) -> `'COOP_Vidar_Loading'` (`0x1200e40c`), `'coop_sleipnir'`
  (`0x1200e420`) -> `'COOP_Sleipner_Loading'` (`0x1200e430`), `'mpdlc1_aegir'` (`0x11f8a1b4`) ->
  `'COOP_Freya_Loading'` (`0x1200e3cc`), `'mpdlc1_idun'` (`0x1200e448`) -> `'Coop_Fenrir_Loading'`
  (`0x1200e38c`), все эти ветки прыгают в общий хвост `0x10fa1c22`. И только после проверок имён
  сравниваются хеши: `0x10fa1bb9` `0xab4fc8e2` (-> `push 0x1200e454 'PvP_Dom_Loading'`,
  `call 0x10a00be0`, `push 0x1200e454`, `call 0x10001ed0`), `0x10fa1bde` `0x9991daec` (->
  `'PvP_Pump_Loading'` `0x1200e464`), `0x10fa1bec` `0x8b40f692` (-> `'PvP_DeathMatch_Loading'`
  `0x1200e478`), `0x10fa1bfa` `0x6c2b3868` (-> `'PvP_TeamDeath_Loading'` `0x1200e490`), `0x10fa1c08`
  `0xf66ffb87` (-> `'PvP_FireStorm_Loading'` `0x1200e4a8`), `0x10fa1c16` `0x2100ced7` (->
  `'COOP_Dash_Loading'` `0x1200e4c0`); режим dash обрабатывается в coop-семействе (у него имя с
  префиксом `COOP_`). Цепочка заканчивается в `0x10fa1c2b`: `push edx; push ebx; call 0x110252d0`,
  затем `mov eax,[0x12804b3c]; cmp dword ptr [eax+0x70],1; jne 0x10fa1ca0` и второй блок сравнения
  id (`0x10fa1c45`..`0x10fa1c66`, где domination / headquarters / deathmatch / default / firestorm
  ведут в `0x10fa1c68`), а там `mov esi,[esp+0x14]; mov edx,[esi+0xa0]; mov eax,[edx+0x64];
  lea ecx,[esi+0xa0]; call eax` — виртуальный вызов по смещению объекта `+0xa0`, слот `+0x64`. Перед
  сравнениями хешей `0x10fa1710` использует `-online` (`push 0x11fb8234`) как строковую проверку.
- `0x11204b00` — второй диспетчер режимов: читает `[esi+0x10]` и разветвляет `0` -> `0x1120590d`,
  `1` -> fall-through, иначе -> `0x11205d99`, и сравнивает id в `0x11205732`, `0x11205753`,
  `0x11205775`, `0x11205793`, `0x112057b1`. Обе функции (`0x10fa1710` и `0x11204b00`) начинаются с
  одного и того же аксессора (`mov eax,[0x12804acc]; cmp byte ptr [eax+0x6c],0; mov eax,[eax+0x68]`).
- `0x11341dc0` (31 rel32-вызовов, например `0x10ce93c9`, `0x10edd676`, `0x10f3a0f9`, `0x10fcc522`) —
  общий getter режима/сессии: `mov eax,[edi]; mov edx,[eax+0x10]; mov ecx,edi; call edx;
  mov ecx,edi; call 0x10056690; push eax; call 0x11774ae0; mov [ebx],esi` — принимает указатель на
  id режима в `[ebp+8]` и возвращает объект (после чего вызывает его виртуальный слот +4 с `this`).
- `0x11a7f820` начинается с `cmp byte ptr [0x12804a09],0` и обходит вектор
  `[0x12820c04]`/`[0x12820c08]` (`lea edi,[ecx+eax*4]`), и `0x11a7fa12` содержит хеш
  кооператива; это ближайший проверенный цикл "обойти зарегистрированные сессии и выбрать coop".
- Отрицательные результаты: у `0x113403e0`, `0x10fa1710`, `0x11204b00`, `0x10fad5e0` и `0x10f0c770`
  нет ни одного rel32-вызывающего site — они вызываются косвенно (таблица функций или таблица
  импорта). `0x11997e50` содержит `0x8b40f692` (`0x119980f8`) и `0x6c2b3868` (`0x1199811a`) и
  вызывается ровно один раз (`0x1199837a` внутри `0x119982e0`); там нет ни `0x43521e6f`, ни
  `0x80608f71`, поэтому это branch одиночной сессии, а не кооп-ветка. Ни один из этих id не появляется
  в `engine\mp\game_mode_coop.lua` (строка `'coop'` не является mode id).
- Ловушка `cstr`-в-середине-строки: `0x11fb8218` — не начало имени switch (`0x11fb8214` — это
  `0x11fb8210 '-online'`, поэтому `0x11fb8218` читается как `rters` = хвост `...multiplayers`);
  `0x11fb8228` — тоже не строка. Из этой области реальна только `-online` (`0x11fb8234`).

### Что из этого следует для мода

Coop-режим — это не флаг, который ASI переключает в одном месте: игра разрешает **hash id** через
объект `[0x12804acc]` (виртуальный слот +4) и реестр `[0x128048c0]`, а хеш кооператива `0x43521e6f`
зашит в исполняемый файл и в таблицу данных. Самые компактные одиночные точки из найденного:
заставить ветку "switch не указан" в `0x11a8c5b1` загрузить хеш кооператива вместо `0x6c2b3868`, либо
вызвать find-by-id у аксессора прямо с `0x43521e6f` (этот шаблон уже есть в `0x11a7fa08`). Ничто из
этого не требует аргментов запуска: `0x11a7f9d0` показывает, что игра способна запросить coop-сессию
у аксессора в любой момент. Имена coop-сессий, которые использует сама игра (`coop_vidar`,
`coop_sleipnir`, `mpdlc1_aegir`, `mpdlc1_idun` и их пары `*_Loading`) — второй, основанный на именах,
путь к тем же coop-сессиям. `0x11341dc0` — тот getter, который возвращает объект сессии по указателю
на id режима.

- Script-fragile детали уже записаны в других разделах: выборщик switch->mode id `0x11a8c440` /
  `0x11a8c8b0`, таблица хешей в `FC3.dll .data` по `0x1216aedc`..`0x1216af1c`, зеркало в
  `FC3_d3d11.dll` (`0x1218ffe4`).
- Следующие шаги: разрешить, чем является виртуальный слот +4 объекта `[0x12804acc]` (REA
  pseudocode), разрешить объект по `[0x12804b3c]` со смещением `+0x70` и вызов `+0xa0`/слот `+0x64`
  в `0x10fa1710`, перечислить зарегистрированные строки имён рядом с хешами по `0x1216aeb8` /
  `0x1216aeb0` / `0x1216aea8` и выяснить, какая из них регистрируется одиночным запуском; затем
  динамический эксперимент, который запросит у аксессора coop-сессию (`0x43521e6f`) в запущенном
  процессе 1.06.
### Функции режимов запуска — виртуальные слоты, а не case в switch (probe132-probe137)

У `0x113403e0`, `0x10fa1710`, `0x11204b00`, `0x10fad5e0`, `0x10f0c770` нет вызывающего `E8`,
потому что они являются записями vftable классов в `.rdata`. `xlib.verified_xrefs` по началу
таблицы даёт 0 попаданий; из кода ссылаются только адреса слотов.

Сквозный поиск dword по всему образу (`local/scratch/p131.py`, `.text` + `.rdata` + `.data`) —
 пять владельцев и индекс слота каждой цели:

- `0x11f910c0` -> слот 5 `0x11341340`, слот 8 `0x1133fb30`, слот 12 `0x113403e0`,
  слот 13 `0x1133fe20`, слот 20 `0x1133fbd0`, слот 22 `0x11340d90`. Слот 0 `0x1030f8c0`,
  слот 1 `0x10007480`, слоты 16-19 и 21 заполнены заглушкой `0x1061fee0`.
  Устанавливает её `0x11341070` (там же `mov dword ptr [ebx+0x3c],0x11f35e98`), которая ищет
  сериализуемое имя `0x11f75a78` = `'CGameLoadingScreen'` (`push 0x11f75a78; call 0x10a00be0`,
  затем `push 0x11f75a78; call 0x10001ed0`) и делает пару `lock xadd` на счётчик ссылкой по
  `[ebx+0x3c]`/`[ebx+0x40]`.
- `0x11f91128` (устанавливается в `[esi+8]` в `0x11340ec0`, там же `mov dword
  ptr [esi+0x3c],0x11f91130`) -> слот 0 `0x1030fbf0`, слот 1 `0x1030f850`, слот 2 `0x1030fc00`,
  дальше purecall-заглушки `0x1008a7e0` / `0x1008a830` / `0x10089f80` и маленький класс
  `0x1165c760`..`0x1165c960`.
- `0x1200e608` -> слот 4 `0x1133fb30`, слот 8 `0x113403e0`, слот 9 `0x1133fe20`,
  **слот 11 `0x10fa1710`**, слот 1 `0x10fa1f30`, слоты 12-18 `0x10fa13b0 0x10fa1200
  0x10fa12e0 0x10fa11c0 0x10fa1160 0x10fa1530 0x10fa1d10`, слот 20 `0x11340560`, слот 21
  `0x10fa1170`, слоты 22-23 `0x104df010` / `0x104de9d0`. Слоты 0-10 общие с `0x11f910c0`
  (`0x10c478a0`, далее `0x10390f00 0x1005bf70 0x1133fb30 0x10c471a0 0x10c47bf0 0x10c47600
  0x113403e0 0x1133fe20 0x10c471b0`), расходятся только с 11-го слота, то есть это соседний
  класс той же иерархии — специфичный для режима вариант, несущий весь кластер методов
  `0x10fa1xxx` (набор обработчиков режима запуска).
- `0x11fb5914` (внутренность семейства vftable, заголовок которого `0x11fb5844`,
  устанавливается в `[esi]` в `0x112046a0`/`0x11204a00`) -> слот 0 `0x10390fd0`, слот 2
  `0x112073d0`, слот 3 `0x112029e0`, **слот 8 `0x11204b00`**, слот 9 `0x10391480`, слот 20
  `0x11204980`, слот 17 `0x11202bd0`. `0x11204a00` инициализирует объект: `[esi+4]=0`,
  `[esi+8]=3`, `[esi+0xc]=0`, `[esi+0x14]=0`, `[esi+0x18]=-1`, `[esi+0x1c]=-1`, `[esi+0x20]=0`,
  `[esi+0x24]=0`, заголовок самолинкующегося списка по `[esi+0x28]` (`mov [eax],eax;
  mov [eax+4],eax; mov [eax+8],0`), `push 0x400; lea ecx,[esi+0x3c]`.
- `0x1200ac6c` -> **слот 8 `0x10f0c770`**, слот 1 `0x10fcad00`, слот 7 `0x10507f50`, слот 9
  `0x10f0cbe0`, слот 10 `0x10f0baf0`, слот 12 `0x10f0c0b0`, слот 13 `0x10f0cb60`, слот 15
  `0x104cedd0`, слот 16 `0x104cedc0`, слот 18 `0x11a58e90`. Слоты 2-6, 17 и 20 заполнены
  заглушкой `0x104833e0`.
- `0x1200d820` -> **слот 8 `0x10fad5e0`**, слот 5 `0x116fb950`, слот 6 `0x10fb0570`, слот 7
  `0x10fb0ee0`, слот 9 `0x104da2a0`, слот 10 `0x10faf980`, слот 11 `0x10fad310`, слоты 12-14
  `0x10fae850 0x10fae7d0 0x10fae740`, слот 17 `0x10faf910`, слот 18 `0x10fad340`, слот 19
  `0x10fb0510`, слоты 20-21 `0x10fad330` / `0x10fad320`, слот 23 `0x104da280`.
- Исправление: `0x11f902b0`, `0x12009e48`, `0x1200c9f0`, `0x1200d7f8`, `0x11fb4a34` — это НЕ
  таблицы: `0x11f902b0` — это строка имени класса `'CGOBuilderNode'`, а `0x12009e48` — середина
  строки (`'lities'`). И `0x11f0ebec` (пишется в `0x1030d7b6 mov dword ptr [edi],0x11f0ebec`)
  тоже не vftable: это описательная область узла Builder, хвостая часть которой читается как
  `'CVideoBuilderObject'`.
- `0x11f5ad34` (73 dword-попаданий, 65 из них в `.text`, 56 разных функций, например
  `0x10048c80`, `0x10117620`, `0x111f5fe0`, `0x112046a0`, `0x11783510`) — широко общий базовый
  запись, но дамп её вывода залезает в ASCII (`'NONE'`, `'Start'`, `'Stop'`, `'Form'`, `'Spot'`,
  `'Soun'`), поэтому это запись рефлексии/сериализуемого имени, а не обычный vftable.
- Ссылки на слоты, найденные в коде (`local/scratch/p133.py`): `0x11f910c0+0x58` (слот 22) из
  `0x11340ed4` (внутри `0x11340ec0`); `0x11fb5914` слот 0 из `0x10390fdc` (`0x10390f60`), слот
  18 из `0x11204a50` (`0x11204a00`), слот 36 из `0x10fc3fd8` (`0x10fc3f30`), слот 63 из
  `0x112027d8` (`0x112027a0`); `0x1200ac6c` слот 11 из `0x10fcac1c` (`0x10fcab70`), слот 15 из
  `0x104cedd8` (`0x104cedd0`) и `0x11a58df4` (`0x11a58d70`), слот 59 из `0x11a585bc`
  (`0x11a585a0`); `0x1200d820` слот 17 из `0x10fad4b0` и слот 21 из `0x10fad54c`, оба внутри
  `0x10fad4a0`. У `0x1200e608` (той vftable, где лежит co-op) ни начала, ни одного слота из
  кода не ссылкается, значит объект создаётся конструктором, который сохраняет адрес через
  `mov [reg+disp],imm32` с регистром.
- Следствие: чтобы статически до­йти до обработчика co-op режима запуска, надо найти код,
  который сохраняет `0x1200e608` в поле объекта (форма `c7`: `mov dword ptr [reg+disp],
  0x1200e608`), а не вызов `0x10fa1710`. Гипотеза, ещё не проверена: объект co-op режима
  создаётся фабрикой, выбираемой из реестра id режимов, а не явным названным конструктором.
- `0x11789a00` — единственный найденный писатель `[0x128042fc]`: это самоохраняемая
  инициализация — `cmp byte ptr [0x128042fc],0; jne 0x11789b63`, она сохраняет три обработчика
  `0x11789840`, `0x117899e0`, `0x11789990` в таблицу по `0x121a7eb0`, вызывает функциональный
  указатель из `[0x1217bc8c]`, делает `mov dword ptr [0x120931c8],0x121a7eb0`, затем `0x11789a45
  mov byte ptr [0x128042fc],1`, и OR-ит `[0x1288c800]`. У `[0x12162beb]` есть чистый геттер в
  `0x1177eba0` (`mov al,byte ptr [0x12162beb]; ret`), а единственная запись байта — в
  `0x11774c4a` внутри `0x11774b70`, которая обходит список строк (`push 0x11f15148;
  call 0x10a00be0` -> `0x10004080`, затем `0x11f1514c`) и читает `[obj+0x14]` и `[obj+0x20]`;
  саму запись пока достичь не удалось.

### Класс объекта режима, за которым идёт кооп-потребитель (probe143-probe149)

Таблица, которую я называл `0x1200e608`, — это середина таблицы. Настоящий первичный виртаблик — `0x1200e5f8` (53 слота), а его вторичные интерфейсы — `0x1200e660` и `0x1200e668` (проверено: `FarCry3Coop-bantila/local/scratch/p143.py`, `p146.py`). Это объясняет, почему probe140 не нашёл ссылку на `0x1200e608`: код пишет `0x1200e5f8`.

Конструктор — `0x10fa1eb0`, и вызывается он ровно из одного места, `0x1119a558` внутри `0x1119a250`, то есть из функции регистрации режимов, которая уже записана в этих заметках:

```text
10fa1eb0  55                       push ebp
10fa1eb1  8bec                     mov ebp, esp
10fa1eb3  51                       push ecx                     ; локальный слот под id регистра
10fa1eb4  56                       push esi                     ; esi = this
10fa1eb5  e8b6f13900               call 0x11341070              ; базовый конструктор ставит семейство 0x11f910b0
10fa1eba  8d86a0000000             eax, [esi + 0xa0]            ; адрес подробъекта в поле +0xa0
10fa1ec1  c706f8e50012             mov dword ptr [esi], 0x1200e5f8
10fa1ec7  c7460860e60012           mov dword ptr [esi + 8], 0x1200e660
10fa1ece  c7463c68e60012           mov dword ptr [esi + 0x3c], 0x1200e668
10fa1ed5  e8f6ea2c00               call 0x112709d0              ; конструировать подробъект +0xa0
10fa1eda  33c0                     xor eax, eax
10fa1edc  898634010000             mov dword ptr [esi + 0x134], eax   ; три обнулённых поля состояния
10fa1ee2  8d4dfc                   ecx, [ebp - 4]
10fa1ee5  898638010000             mov dword ptr [esi + 0x138], eax
10fa1eeb  89863c010000             mov dword ptr [esi + 0x13c], eax
10fa1ef2  6898138212               push 0x12821398              ; глобальный объект регистра (в файле нули)
10fa1ef7  c78640010000ffffffff     mov dword ptr [esi + 0x140], 0xffffffff
10fa1f01  888644010000             mov byte ptr [esi + 0x144], al      ; сброшенный флаг
10fa1f0d  89864c010000             mov dword ptr [esi + 0x14c], eax
10fa1f13  e868971bff               call 0x1015b680              ; инициализация строки
10fa1f18  8b55fc                   edx, [ebp - 4]               ; значение, которое передал вызывающий
10fa1f1b  899640010000             mov dword ptr [esi + 0x140], edx    ; id регистра пишется в +0x140
10fa1f21  8bc6                     mov eax, esi                 ; возврат this
10fa1f23  8be5 5d c3               mov esp, ebp; pop ebp; ret
```

Деструктор `0x10fa1e30` заново ставит те же три виртаблика (из-за этого ссылки на `0x1200e5f8` выглядели как второй конструктор), затем идёт деструктор подробъекта и базовый деструктор:

```text
10fa1e30  55 8bec 83ec18 56 57     push ebp; mov ebp,esp; sub esp,0x18; push esi; push edi
10fa1e37  8bf9                     edi, ecx                     ; this
10fa1e39  8b8740010000             esi, [edi + 0x140]           ; сохранённый id регистра
10fa1e3f  50                       push eax
10fa1e40  be98138212               esi, 0x12821398
10fa1e46  c707f8e50012             mov dword ptr [edi], 0x1200e5f8      ; установка виртаблика в деструкторе
10fa1e4c  c7470860e60012           mov dword ptr [edi + 8], 0x1200e660
10fa1e53  c7473c68e60012           mov dword ptr [edi + 0x3c], 0x1200e668
10fa1e5a  e8e1491cff               call 0x10166840              ; освобождение строки (216 вызовов)
10fa1e68  8d8f44010000             ecx, [edi + 0x144]
10fa1e8e  c745ec9cff1f11           mov dword ptr [ebp - 0x14], 0x11f9cfc9
10fa1ea0  5f 5e 8be5 5d c3         pop edi; pop esi; mov esp,ebp; pop ebp; ret
10fa1ea5..0x10fa1eaf               int3 отступление
```

Слот 0 у `0x1200e5f8` — деструктор с удалением, и он показывает, откуда объект забирают из менеджера:

```text
104de9e0  55 8bec 83ec0c           точка деструктора (this в ecx)
104de9ec  8bf1                     esi, ecx
104de9ee  e83d34ac00               call 0x10fa1e30              ; тело
104de9f3  f6450801                 test byte ptr [ebp + 8], 1   ; флаг «и удалить тоже»
104dea00  83fe00 0f8410000000      esi == 0 -> пропустить, проверка границ [0x121bbff8] / [0x121a7fdc]
104dea0d  56                       push esi
104dea0e  e89d8bffff               call 0x1177f5b0              ; operator delete
104dea15  8b0d2c438012             ecx, [0x1280432c]            ; глобальный менеджер
104dea1b  e8304a5cff               call 0x106c2c50              ; шаг «убрать из менеджера»
104dea20  8bc6                     eax, esi
104dea22  e8c98affff               call 0x117774f0              ; шаг освобождения / счётчика ссылок
104dea27  8b0d2c438012             ecx, [0x1280432c]
104dea2d  e8ee495cff               call 0x106bde20              ; второй шаг менеджера
104dea32  8bc6 8be5 5d c20400      mov eax,esi; mov esp,ebp; pop ebp; retn 4
```

У `0x104de9e0` ровно одна ссылка — сам слот виртаблика, то есть объект освобождается только через виртуальный вызов. Деструктор подробъекта в поле `+0xa0` (`0x11270920`) ставит `mov dword ptr [esi], 0x11fac4a0` и читает `[esi + 0x8c]` / `[esi + 0x90]` — та же семья Accessors, что в `0x112710f0`; `0x11fac4a0` начинается с `0x10368ca0`, далее шесть `0x1008a7e0` («не реализовано»), затем `0x1008a830`.

Смысл: кооп-потребитель `0x10fa1710` — не отдельная функция, а слот 15 объекта кооп-режима; его id пишется в `+0x140` из значения, которое передаёт функция регистрации, а ручка регистра — глобал `0x12821398`.

### Кто обращается к глобальным gating-переменным напрямую (probe152)

`p152.py` разобрал ещё пять незанятых слотов `0x1200e5f8`, и все они читают gating-переменные,
уже записанные в этих заметках: так объект кооп-режима добирается до состояния сессии, не пользуясь
функциями запуска режима.

```text
10fa1f30  слот 5   mov eax, [0x12804b3c]; cmp dword [eax+0x70], 1 ; та же проверка, что в 0x10fa1710
                   mov ecx, [0x12804430]                          ; другая gating-переменная
10fa13b0  слот 16  mov eax, [0x12804acc]; cmp byte [eax+0x6c], 0  ; переменная, которую читает 0x1119a250
                   call 0x1048c910; mov edx, [0x12805180]; call 0x114cb560; call 0x1100d2f0
10fa12e0  слот 18  mov eax, [0x12804acc]; test byte [eax+0x40], 0
10fa1160  слот 19  mov eax, [0x12804acc]; cmp byte [eax+0x6c], 0
                   ... mov edi, [eax+0x68]; call 0x100fe7b0
                   mov ecx, [esi+0x14]; call 0x104dec50   ; либо, на другой ветке,
                   mov edx, [esi+0x14]; call 0x104ded10
10fa1d10           cmp byte [edi+0x144], 0                      ; флаг, который обнулил конструктор
                   push 0x12821398; call 0x1015b7b0; call 0x115e35d0
                   call 0x103a9ea0; cmp eax, [0x1216ca90]; cmp eax, [0x1216ca9c]; call 0x1117f530
```

Проверка раскладки: слоты `+0x20` (`0x10fa1f30`), `+0x30` (`0x10fa12e0`), `+0x3c` (`0x10fa1160`)
у `0x1200e5f8` совпадают с тем, куда `0x11341070` ставит `0x11f910f0`, `0x11f91128`, `0x11f91114`,
то есть кооп-объект — член семейства `0x11f910b0` с кооп-набором слотов.

### Helper выделения, который создал объект кооп-режима (probe153)

`0x118db560` закрыт: это помечающий менеджером helper деления по размерам, и именно он выделил
объект, переданный конструктору кооп-режима в `0x1119a54d`:

```text
118db560  8b0d2c438012  mov ecx, [0x1280432c]     ; глобальный менеджер как `this`
118db566  56            push esi
118db567  8bf0          mov esi, eax               ; eax = запрошенный размер
118db569  e8e276defe    call 0x106c2c50            ; шаг менеджера, тот же, что в деструкторе с удалением
118db56e  83fe08        cmp esi, 8
118db571  7718          ja 0x118db58b              ; разделение по размерам
118db573  8bc7          mov eax, edi               ; edi = размер, который задал вызывающий (`mov edi,0x150` в 0x1119a548)
118db575  e8f6c5e9ff    call 0x11777b70            ; выделение для размера <= 8
118db57a  8b0d2c438012  mov ecx, [0x1280432c]
118db580  8bf0          mov esi, eax
118db582  e89928defe    call 0x106bde20            ; шаг менеджера, второй, который тоже использует деструктор
118db587  8bc6 5e c3    mov eax,esi; pop esi; ret
118db58b  8bd7 mov edx,edi; 118db58d 8bc6 mov eax,esi; 118db58f e8acc8e9ff call 0x11777e40  ; выделение для размера > 8
118db594..118db5a1      mov ecx,[0x1280432c]; mov esi,eax; call 0x106bde20; mov eax,esi; pop esi; ret
```

То есть выделение и освобождение объекта кооп-режима обрамлены одними и теми же вызовами менеджера:
`0x106c2c50` при входе и `0x106bde20` при выходе, оба по глобалу `[0x1280432c]`. Открытый пункт NOTES
"`0x118db560` не разобран" закрыт.

### Что на деле устанавливает `0x11789a00`: собственный аллокатор игры (probe155-probe158)

Первые 0x3c байта `0x11789a00` — это одноразовый страж и установка таблицы из трёх слотов обработчиков:

```text
11789a00  cmp byte ptr [0x128042fc], 0        ; одноразовый страж (его же и пишет 0x11789a00)
11789a07  jne 0x11789b63
11789a0d  mov eax, dword ptr [0x1217bc8c]     ; слот необязательного колбэка
11789a12  mov dword ptr [0x121a7eb0], 0x11789840
11789a1c  mov dword ptr [0x121a7eb4], 0x117899e0
11789a26  mov dword ptr [0x121a7eb8], 0x11789990
11789a30  test eax, eax
11789a32  je 0x11789a36
11789a34  call eax                             ; вызывает колбэк, если он установлен
11789a36  mov eax, 1
11789a3b  mov dword ptr [0x120931c8], 0x121a7eb0   ; публикует указатель таблицы в глобале .data
```

То есть установчик записывает три адреса обработчиков в таблицу `0x121a7eb0`/`0x121a7eb4`/`0x121a7eb8`,
публикует указатель на неё в глобале `[0x120931c8]` и вызывает то, что лежит в `[0x1217bc8c]`.
Перекрёстные ссылки: у адресов обработчиков `0x11789840`, `0x117899e0`, `0x11789990` по одной ссылке — сам
сайт установки. У адреса таблицы `0x121a7eb0` две ссылки: сайт установки и `0x11789a3b`. Слот `[0x1217bc8c]`
читается в `0x10c56bf8`, `0x10c56ce4`, `0x10c56cf8`, `0x10c56d7a` и
затрагивается в `0x106ed8bc`, `0x106efaa7`.
Поиск RTTI для `0x11fc6268` и `0x1200e5f8` не удался: их слоты `-4`/`-8` содержат адреса кода или не-указатели
(`0x11fc6268-4 -> 0x104833e0`, `0x11fc6268-8 -> 0x11746490`, `0x1200e5f8-8 -> 0x66006e`), поэтому ни одна из
таких таблиц не является обычной первичной vftable MSVC с CompleteObjectLocator.

Probe158 уточняет метку: `0x11789a00` — это инициализация собственного аллокатора игры, а не сайт установки
кооп-режима. Он лениво вызывается из `0x11789b70` (`call 0x11789a00` в `0x11789b81`, размерный путь
`operator new`) и из `0x117898c0` (`call 0x11789a00` в `0x117898d3`, путь `operator delete`), оба под
`cmp byte [0x128042fc],0`. Значит `[0x128042fc]` означает «аллокатор инициализирован», а служебные
глобалы арены — `[0x121bbff8]`, `[0x121a7fdc]` и `[0x121a7fe0]`: `0x1177f560` выбирает слот арены
через `sub eax,[0x121bbff8]`, `shr eax,0x10`, `lea esi,[eax+eax*4]`, `lea esi,[esi*4+0x121a7fe0]`.
Прежние утверждения NOTES о `[0x128042fc]` как о страже выбора режима запуска теперь читаются с этой поправкой.

### Кто строит режимный менеджер и что он регистрирует (probe159-probe161)

`0x111f4fc6` — хвост настройки режимного менеджера. Он забирает контейнер из `[esp + 0x14]` (`esi`), создаёт
менеджером `call 0x1039b710` (`0x111f4fcf`), сохраняет его в поле контейнера `[esi + 0xd4]` (`0x111f4fd8`), затем
регистрирует на нём три вещи:

```text
111f4fde  mov ecx, [0x12807738] ; push ecx ; mov ecx, eax ; call 0x106eac80    ; аргумент конструктора менеджера
111f4fec  mov eax, [esi + 0xd4] ; mov edx, [0x12807740]
111f4ff8  mov ecx, [eax + 0x12c] ; mov ecx, [ecx + 0x24] ; push edx ; call 0x106e96c0
111f5007  mov eax, [esi + 0xd4] ; mov edx, [0x12807744]
111f500d  mov ecx, [eax + 0x130] ; mov ecx, [ecx + 0x24] ; push edx ; call 0x106e96c0
111f5022  mov ecx, [esi + 0xd4] ; push 0 ; push esi ; call 0x106e46a0
```

То есть подсобъекты менеджера живут в `[менеджер + 0x12c]` и `[менеджер + 0x130]`, каждый достаётся через своё поле
`+0x24`, и оба регистрирует `0x106e96c0` с глобалами `[0x12807740]` и `[0x12807744]`; финальный `call 0x106e46a0`
передает менеджеру сам контейнер (`push 0; push esi`). Функция настройки возвращает `1` в `0x111f508c` (`ret 4`).
Следующая функция на `0x111f5090` — парный сброс: она обходит массив с корнем `[0x12805260]` (счётчик в `[eax + 0xc]`,
элементы в `[eax + 8]`, каждый элемент освобождается через `call 0x11442150`), освобождает сам массив через
`call 0x118830a0`, затем закрывает `[0x128043f8]` через `call 0x11739ed0`, `[0x12804b14]` через `call 0x1161fef0`,
`[0x12804b18]` через `call 0x1161ccc0` и `call 0x1161e1b0`, и `[0x128043c8]` через `call 0x11742100`.

### Куда в таблицу режимов попадает coop-идентификатор (probe172-probe190)

`0x11199e80` — это не установщик. probe186 разбирает его от выровненной границы функции: короткий трюх, который
обращается к объекту в `[ecx + 0x14]`:

```text
11199e80  push ebp ; mov ebp, esp ; push esi
11199e84  mov esi, [ecx + 0x14] ; test esi, esi ; je 0x11199e95
11199e8b  push edi ; mov edi, [ebp + 8] ; call 0x1133fd30
11199e94  pop edi ; pop esi ; pop ebp ; ret 4
11199e9a  int3 x6
```

`0x11199ea0` — отдельная функция, и к таблице режимов она не относится: она грузит FEU-файл
`'UI\Singleplayer\Menu\Loading\loading.feu'` (`0x11fc6138`, пушится в `0x11199eab` и `0x11199ec3`), обнуляет
`[ebx + 0x10]`, вызывает `0x10a00be0` и `0x10001ed0`, обращается к `[ebx + 0x14]` -> `[eax + 8]` (слот 2 таблицы
вызовов, с `push esi` как выходным параметром), освобождает ссылку через `or ecx, 0xffffffff` /
`lock xadd dword ptr [eax], ecx` и `call 0x100945e0`, и в конце собирает на стеке
`{0x11f373cc, 0x11199d80, 0, 0, edx}` и вызывает `0x118b1810` с `ecx = 0x11fc6164`. У `0x128040c0` и `0x6f1e5243`
ноль проверенных перекрёстных ссылок, поэтому строки `[edi] = 0x128040c0`, `[edi + 4] = 0x2e0000`,
`[edi + 8] = 0x43521e6f` и формулировка про «перевернутый по байтам id» были артефактами разбора на середине
инструкции, их нет.

probe188 насчитывает 11 проверенных ссылок на coop-id `0x43521e6f`. Настоящие места в коде: `0x10f0c7e8`
`mov dword ptr [esp + 0x6c], 0x43521e6f` (рядом `[esp + 0x54] = 0x11fafe90`), `0x10f4cb0a`
`mov dword ptr [esp + 0xb8], 0x43521e6f` (рядом `[esp + 0xa0] = 0x11fafe90`), `0x10f9260a`
`cmp dword ptr [esp + 0xc], 0x43521e6f` / `jne 0x10f9267d` сразу после `push edx` / `call eax` (запрос id режима,
который возвращает id на стеке), `0x10fa1aa4` `cmp eax, 0x43521e6f` / `jne 0x10fa1bb8`, два писателя `0x1127995f`
`mov dword ptr [0x12891ca0], 0x43521e6f` и `0x11279adf` `mov dword ptr [0x12891ca8], 0x43521e6f` (каждый под
проверкой `test byte ptr [0x12891ca4], al` / `or dword ptr [0x12891ca4], eax` и зеркала `0x12891cac`, и каждый
затем читает `mov ecx, [ebx + 0x8c0]`), и две цепочки сравнений id режима `0x1133fb80` (`mov eax, [eax]` ;
`cmp eax, 0xab4fc8e2` ; `je 0x1133fbaf` ; `cmp eax, 0x43521e6f` ; `je 0x1133fbaf` ; `cmp eax, 0x9991daec`) и
`0x113405a0` (`mov eax, [ebx + 0x4c]`, затем такая же тройная проверка с `je 0x113405cd`). Остальные вхождения —
`0x11a7f820` и ячейки данных `0x1216a00c`, `0x1216aa40`, `0x1216aee4`, `0x12173ff4` внутри блока `0x11bcac20`.

Счётное поле, которое прежняя версия этого раздела приписывала accessor'у режимов, лежит внутри функции пау-меню
`0x11007920`-`0x11007c70` (probe189): она вызывает `0x11168cf0`, читает `[0x12804acc]`
(`cmp byte ptr [eax + 0x6c], 0`), грузит `'UI\Singleplayer\Menu\Pause\M_PauseMenu.feu'` (`0x11fd18fc`) через
`call 0x117872f0`, читает `[0x12804ac0]` (`lea edi, [eax + 0x38]`) и вызывает `0x103a2d50`, затем в `0x110079ea`
`mov edx, [0x1280437c]`, в `0x110079f0` `mov eax, [ebx + 0xc]`, в `0x110079f3` `mov ecx, [edx + 0xc]`; `0x11007a10`
пушит `0x11fd1928` (`'Pause_%d'`, вторая ссылка на него — `0x11169c43`), `0x11007a2c` `lea edi, [eax + 0xc]`,
`0x11007a53`-`0x11007a5a` читают `[esp + 0x20]` -> `[edx + 4]` -> `[eax + 0xd0]`, `0x11007a60` читает `[0x12804a50]`,
`0x11007a6b` `call 0x116504b0`, `0x11007a9d` `mov ecx, [eax + 0xc]`. `0x110079e0` и `0x11007a00` — адреса внутри
функции, у них ноль проверенных ссылок; это не точки входа хелперов. probe175 сохраняет прежний вывод: у
`0x11fb5040`, `0x11fb5044`, `0x11fb5048`, `0x11fb504c` нет ни одной проверенной ссылки и нет disp32-мест, поэтому
прежняя оценка размера таблицы режимов была неверной.
Исправлено (2026-11-07, `local/scratch/p210*.py`-`p227*.py`, см. раздел «Переписи глобалов по месту исправления
`.reloc`» ниже): абзац «`[0x12162b40]` инициализирует `0x1137f6c0`, который также пишет
`[0x12162b40] = 0x11f1071c`, `[0x1285c450] = 0x11f1074c`, `[0x1285c448] = 0x10413200`,
`[0x1285c444] = 0x11f10798`, `or [0x1285c44c], 1`, `call 0x11788030`» не подтверждён и отменён: у
`0x12162b40`, `0x1285c448`, `0x1285c44c`, `0x1285c450` и `0x1285c454` ноль мест исправления в `.reloc`
(у `0x1285c444` — два), `0x11f1071c`, `0x11f1074c`, `0x11f10798` и `0x10413200` не являются сохранённым
значением ни в одном месте исправления, а `0x1285c444`-`0x1285c454` не имеют смещения в файле
(`.data` = VA `0x12093000`, виртуальный размер `0x8051e0`, сырой размер всего `0xe7c00`, то есть этот
диапазон — обнуляемая BSS). Что подтверждается о `0x1137f6c0`: это одноразовая инициализация стражей,
которая пишет `[0x1280493c] = 0x11f921e8`, `[0x1280d49c] = 0x11f1687c`, `[0x1280d4a0] = 0x11f16894`,
`[0x1282e598] = 0x11f168a8` (плюс `[0x1282e594]`) и вызывает `0x116c1bb0`, `0x1003b4b0`, `0x106f9ff0`.
accessor-функции: `0x111854b0` = `mov eax, [0x12189644]` / `ret 4`, `0x11340c90` =
`mov eax, [0x1217bc8c]; push 1; push eax; call 0x10c569d0`, `0x11185510` = `mov eax, [0x1280443c]`,
затем `jmp 0x10f0c4c0`.

`probe172.py` нашёл 15 вхождений coop-ида `0x43521e6f` как disp32, но проверенные перекрёстные ссылки (probe188)
дают 11 из 15: код в `0x10f0c7e8`, `0x10f4cb0a`, `0x10f9260a`, `0x10fa1aa4`, `0x1127995f`, `0x11279adf`,
`0x1133fb80`, `0x113405a0`, `0x11a7f820` и ячейки данных `0x1216a00c`, `0x1216aa40`, `0x1216aee4`, `0x12173ff4`
внутри блока `0x11bcac20`. Бывшие «слот 15 объекта режима» и «слот прогресса» — артефакты разбора на середине
инструкции.

### Переписи глобалов по месту исправления `.reloc` (2026-11-07, `local/scratch/p199*.py`-`p227*.py`, `scripts/fc3_reloc_xref.py`)

Метод (единственный надёжный способ перечислить ссылки глобала в этом бинарнике): в FC3.dll **772159** записей
`.reloc`; каждая HIGHLOW-запись — это место исправления, сохранённое слово которого есть адрес, употреблённый в
каком-то disp32-операнде, поэтому «места исправления со значением G» и есть полный список ссылок глобала G. У
глобала, который не используется в коде, ноль таких мест. Все места перечисленных ниже глобалов лежат в `.text`, и
проверка по выровненным инструкциям воспроизводит число мест ровно: `0x12804acc` 4614 = 4614, `0x12804ac0` 1129 =
1129, `0x12804a50` 186 = 186, `0x1280437c` 1776 = 1776, `0x1217bc8c` 7 = 7, `0x12162beb` 14218, `0x128042fc` 14905.

Места записи, прямо из дампов:

| глобал | места записи | что делает запись |
|---|---|---|
| `[0x1280437c]` | `0x11757eda` `mov [0x1280437c], ebx`; `0x1175b58b` `mov [0x1175a7e0-процедуре]` → `mov [0x1280437c], eax` | `ebx` — нулевое значение, используемое процедурой освобождения `0x11757b80`; `0x1175b58b` (в процедуре, начинающейся с `0x1175a7e0`) — единственная найденная устанавливающая запись |
| `[0x12804acc]` | `0x10048102` `mov [0x12804acc], 0`; `0x117567ce` `mov [0x12804acc], esi`; `0x11756f37` `mov [0x12804acc], ebx` | 3 записи на 4614 мест; остальные 4611 — чтения |
| `[0x12804ac0]` | `0x11629dd6` `mov [0x12804ac0], ebx`; `0x1162a703` `mov [0x12804ac0], eax`; `0x1162a70a` `mov [0x12804ac0], ebx` | 3 записи на 1129 мест |
| `[0x12804a50]` | `0x100bf8b7` и `0x100bf8c7` (`mov [0x12804a50], eax` в процедуре, начинающейся с `0x100bf830`) | объект меню паузы создаёт `0x100bf830`; остальные из 186 мест — чтения |
| `[0x1217bc8c]` | `0x106ed8bb` `mov [0x1217bc8c], ebx` (сброс) и область `0x106efaa8`, сохраняющая статический объект `0x106b71b0` | 2 записи на 7 мест; читатели `0x11340c90`, `0x11342740`, `0x112e319b`, `0x112e31b2` |
| `[0x128042fc]` | `0x11789a45` `mov byte ptr [0x128042fc], al` | единственная запись; остальные 14904 мест — чтения вида `cmp byte ptr [0x128042fc], bl` |

Процедура освобождения `0x11757b80` (ПРОВЕРЕНО, `local/scratch/p200_out.txt`, `p207_out.txt`): для каждого из
`[0x127bc324]`, `[0x12804384]`, `[0x1280437c]`, `[0x1280440c]`, `[0x12804430]`, `[0x128043b4]`, `[0x128042e4]`, …
выполняется `mov ecx, [g]` / `cmp ecx, ebx` / `je skip` / `mov edx, [ecx]` / `mov eax, [edx]` / `push 1` / `call eax`
(Release(1) через слот 0 виртуальной таблицы), а затем `mov [g], ebx`. То есть глобал, обнуляемый там, именно
освобождается, а не просто очищается.

`0x1174c070` — процедура поиска элемента контейнера по ключу (ПРОВЕРЕНО, `local/scratch/p213_out.txt`):
`mov eax, [ebp+8]` → `mov eax, [eax+0xc]` → `test eax, eax; je 0x1174c120` (счётчик нулевой — не найдено), далее
`mov edx, [ecx+8]` (массив элементов), `mov ecx, [edx+edi*4]`, `mov eax, [ecx]`, `mov eax, [eax+0x10]`,
`lea edx, [esp+0x10]`, `push edx`, `call eax` (слот 4 виртуальной таблицы элемента), затем `mov eax, [eax]`,
`mov ecx, [eax]`, `mov eax, [eax+4]`, `cmp ecx, [ebp+0xc]`, `cmp eax, [ebp+0x10]`. Раскладка контейнера поэтому:
`+8` = массив элементов, `+0xc` = счётчик.

`0x1174c070` достигается из 299 мест `[0x1280437c]`; прочие частые цели вызова после загрузки контейнера —
`0x116f56a0` (97), `0x1013c1f0` (84), `0x1174b660` (77), `0x116eda40` (66), `0x100945e0` (45), `0x1024be80` (45),
`0x1174c1b0` (40), `0x11788030` (38), `0x116f0a40` (36) — всего 425 различных целей (`local/scratch/p218_out.txt`).
Шаблон `mov ecx, [0x1280437c]` с последующим `call` нигде нет (probe222), поэтому контейнер всегда передаётся
процедуре аргументом, а не как `this`.

### Семейные записи реестра (переписи в одном окне инструкций)

Запись сразу `[0x1217bc8c]`, `[0x12804acc]`, `[0x12804ac0]`, `[0x12804a50]` и `[0x1280437c]` в пределах одного
окна инструкций встречается ровно в двух местах — `0x11002390` и `0x118586d0` — и там, и там это
`0x116eda40 push ecx / push ebx / call 0x1101a150`, то есть три аргумента, а не пять. Значит, все пять глобалов
принадлежат самому классу реестра, а не списку параметров, и каждая запись — одно поле этого класса
(`local/scratch/p227_out.txt`). `0x118586d0` находится внутри процедуры, начинающейся с `0x118580f0`, а
`0x11002390` — цель перехода (предшественники `0x11002041`, `0x110021f2`) внутри процедуры, начинающейся с
`0x11002000`.

Ни одной записи в `[reg + 0xc]` в пределах 0x80 от любой загрузки `[0x1280437c]` нет (probe216/probe217): автор
счётного поля по-прежнему не установлен.

Уроки этой работы: сплошная линейная расшифровка всего `.text` рассинхронизируется и придумывает формы
`add reg, imm` / `or reg, imm`, в которых disp32 и есть глобал (откуда взялась старая оценка «2400+ записей»);
оценка по перекрывающимся окнам функций завышает число (1027 окон → 1765 записей для глобала с 1776 местами);
`detail.canonical` у capstone бросает `AttributeError` на некоторых инструкциях (употребляйте `i.op_str`);
`xlib.enclosing(starts, va)` принимает список начал первым аргументом.

Два исправления этого раздела:

- процедура меню паузы занимает `0x11007920`-`0x11007c66` (`ret` в `0x11007c66`, заполнение `0xCC` до `0x11007c6f`,
  следующая процедура начинается с `0x11007c70`), а не `0x11007c70`;
- `0x11185b9a` есть `call 0x11789a00`, а не чтение счётчика; `0x11007a9d` читает `[eax + 0xc]`, где `eax` пришёл из
  цепочки `[esp + 0x20]` → `[edx + 4]` → `[eax + 0xd0]`, а не из контейнера. Доказанные чтения счётчика именно из
  контейнера: `0x110079f3` (`mov ecx, [edx + 0xc]` при `edx = [0x1280437c]`) и `0x1174c070`
  (`mov eax, [eax + 0xc]` при `eax` = аргумент-контейнер).
- Открытые цели: найти, кто пишет в `[0x12162beb]`; определить класс, у которого виртаблик
  `0x11fc6268` (соседние строки называют `CFCXGOBuilderCommon`, то есть это класс из
  `CFCXGOBuilder*`) и что означают его восемь слотов; кто пишет счётное поле `[[0x1280437c]+0xc]`
  (его проверенные чтения — его доказанные чтения — только `0x110079f3` и `0x1174c070`; кто вызывает устанавливающую запись `0x1175b58b`
(процедура `0x1175a7e0` пока не приписана), тоже открыто); владелец
  контейнера, принимающего менеджер в `0x111f4fc6`; что делают `0x106eac80` и `0x106e96c0`; coop-запись
  среди тринадцати реестровых строк. Закрыто в этой сессии: `[0x128042fc]` (`0x11789a00` в
  `0x1119a53e`), `0x118db560` (хелпер выделяния памяти), `[0x121a7eb0]`-`[0x121a7eb8]` + `[0x120931c8]`,
  читатели `[0x1217bc8c]`, читатели `[0x12807738]`/`[0x12807740]`/`[0x12807744]` (`0x111f4fde`,
  `0x111f4ff2`, `0x111f500d`, а также места записи `[0x12804acc]`, `[0x12804ac0]`, `[0x12804a50]`, `[0x1217bc8c]`, `[0x1280437c]`). Двуязычные NOTES + commit на каждое новое наблюдение.

## Путь установки кооп-id, проверенный по сырым байтам (2026-11-07, сессия агента, `local/scratch/p271*.py`..`p282*.py`)

Продолжение прохода 2026-11-07 по авторам записей, закрывающее четыре открытых вопроса из раздела
«Атрибуция авторов записей и проверённые рёбра вызовов». Каждое утверждение ниже прочитано из сырых
байтов FC3.dll на проверенном начале функции; `local/scratch/calls.json` по-прежнему ненадёжен (см.
отозванную цепочку в конце).

- **Кооп-id `0x43521e6f` устанавливается во ВРЕМЯ РАБОТЫ, это не статическое значение глобала.**
  Глобал `[0x12891ca0]` лежит в `.data` за пределами размера файла (виртуальное начало `0x12093000`,
  raw-размер `0xe7c00` → как BSS, начальное значение 0). `0x11279910` пишет его:
  `mov dword ptr [0x12891ca0], 0x43521e6f` на `0x1127995f`, под защитой `test byte ptr [0x12891ca4], al`
  / `jne 0x11279969` (`0x11279951`/`0x11279957`) и штампа инициализации `or dword ptr [0x12891ca4], eax`
  (`0x11279959`). Парный глобал `[0x12891ca8]` получает тот же id на `0x11279adf`. (пробы p278, p280)
- **Где `0x43521e6f` встречается как литерал:** записи таблицы mode-id `.data 0x1216a00c`, `0x1216aa40`,
  `0x1216aee4`, `0x12173ff4` (уже записаны) плюс sites в `.text`: `0x10f0c7ec`, `0x10f4cb11`, `0x10f9260e`,
  `0x10fa1aa5`, `0x1133fb8a`, `0x113405ab`, `0x1134062a`, `0x11340a2d`, `0x11a7fa12`. (проба p278)
- **`0x11279910` — хелпер, который дважды вызывает одна бо́льшая рутина, а не верхнеуровневый триггер.**
  Его единственные два `call`-сайта — `0x11279fd2` (внутри `0x11279fc0`) и `0x1127a16f` (внутри `0x1127a0f0`);
  линейная декодировка показывает, что рутина идёт `0x11279910..0x1127ad0e` и разделена `ret` на `0x11279a8a`
  и `0x11279c0a`. У вызывающего `0x11279fc0` нет прямого вызывающего; `0x1127a0f0` вызывается из `0x11a5870b`
  внутри функции `0x11a58700`. (пробы p273, p276, p280)
- **Настоящий триггер — виртуальная диспетчеризация.** У `0x11a58700` нет прямого `call`; значение —
  указатель, хранимый в `.rdata 0x1200ad14`, слот таблицы диспетчеризации `0x1200ad00..0x1200ad2c`, чьи
  соседи `0x11277c20`, `0x11278160`, `0x11279700` — то же семейство `0x1127xxxx`, что и `0x11279910`.
  Значит установка кооп-id срабатывает через виртуальный метод объекта этой таблицы. (пробы p281, p282)
- **`0x11b2a610` (сброс mode-id в `-1`) — виртуальный метод объекта, чей vtable нигде статически не хранится.**
  Это слот `+0x2b8` таблицы из 200 записей `0x11bd2b04..0x11bd2e24` (таблица аксессоров `0x11b29040..0x11b2a9c0`,
  шаг `0x20`). Основание `0x11bd2b04` НЕ встречается нигде в образе — ни как ссылка кода, ни даже как
  хранимый указатель, — поэтому указатель vtable ставится на живой объект во время работы. Глобал
  `[0x121e5a38]` сейчас содержит сторожевое значение `0xc9700a6a`, а НЕ vtable, так что это не указатель
  кооп-менеджера, как предполагала прошлая сессия. (пробы p271, p272, p274)
- **`0x116e7f70` (teardown `Release(1)` для `[0x12804a50]`) — слот `+0xc` таблицы из 19 записей
  `0x11f26488..0x11f264d4`.** Основание этого vtable ДЕЙСТВИТЕЛЬНО ставится в коде:
  `mov dword ptr [ebx], 0x11f26488` на `0x116e8127` (конструктор `0x116e7fb0`) и `mov dword ptr [edi], 0x11f26488`
  на `0x116e82ea` (конструктор `0x116e82e0`, вызывается из `0x1174676c`). Значит `[0x12804a50]` — объект класса
  `0x11f26488`, и `0x116e7f70` выполняется при его разрушении. (пробы p272, p273)
- **Отозванная цепочка.** Ребро прошлой сессии «`0x11279910` → `0x11554c40` → `0x11554b70`» decoding не выдерживает:
  на проверенном начале `0x11554b70` попадает в середину инструкции и даёт мусор (`add al,0xdb; inc eax; ...`),
  поэтому эта цепочка **не подтверждена** и отзывается.

Новые открытые вопросы: какой объект владеет таблицей диспетчеризации `.rdata 0x1200ad00` и кто вызывает
`0x11a58700`; какой живой объект несёт vtable `0x11bd2b04` (владелец сброса mode-id) — это требует
конструктора, пишущего этот vtable, или дампа кучи во время работы, поскольку статически он не хранится;
и является ли `[0x121e5a38] = 0xc9700a6a` кучным канибалом, а не указателем менеджера.

## Таблица диспетчеризации `0x1200ad00` принадлежит `CFCXPlaylistService` (2026-11-07, агент, `local/scratch/p283*.py`)

Закрывает «какой объект владеет таблицей диспетчеризации `.rdata 0x1200ad00` и кто вызывает вирт-метод
`0x11a58700`» из прошлого раздела. В FC3.dll **нет MSVC-RTTI** (слот `-0x4` равен 0; единственные строки
`.?AV` в файле — сериализация Havok). FC3 использует **собственный RTTI: слот vtable `+0x04` — геттер
class-info**, делающий `push <строка_имени>; call <getname>`. Цепочка (проверено по сырым байтам):

- `IGameModeService` (базовый vtable `0x11f169e8`, геттер `0x10048190`) → `CPlaylistService`
  (vtable `0x11fab790`, геттер `0x10362330`, строка имени `0x11f8d98c`, дескриптор `.data 0x1285e0ec`)
  → **`CFCXPlaylistService`** (владелец искомой таблицы; строка имени `0x11fc544c`, push на `0x103d1659`,
  дескриптор `.data 0x12863890`, геттер `0x103d1640`).
- **Границы целевого vtable:** `.rdata 0x1200ad00..0x1200ad50`, ровно 21 слот (`+0x00..+0x50`), с двух
  сторон ограничен нулевыми dword (`0x1200acfc`, `0x1200ad54`). Слот `+0x48` возвращает строки имён
  плейлистов: `"UserPlaylist"` (`0x1127a2b1`), `"OfflinePlaylist"` (`0x1127a2cf`), `"PrivateCoopPlaylist"`
  (`0x1127a2e6`), `"MapArchivePlaylist"` (`0x1127a2fd`), `"BetaTestPlaylist"` (`0x1127a314`) — то есть
  рутина установки кооп-id `0x11279910` (келли слотов этого класса `0x11277c20`/`0x11278160`/`0x11279700`)
  достигается от объекта **сервиса плейлистов**: выбор *PrivateCoopPlaylist* (или похожего) и вызывает
  установку кооп-id.
- **Конструктор `0x11a585a0`** ставит vtable: `mov dword ptr [esi], 0x1200ad00` на `0x11a585b3` (далее
  дочерние vtable `[esi+0x50]=0x1200ad58`, `+0x54=0x1200ad9c`, `+0x58=0x1200ada8`, `+0x60=0x1200ae10` и
  `[esi+0x8c8]=0x11fbcc20`). Базовый конструктор `0x11278470` сначала пишет `0x11f169e8`, затем на
  `0x11278526` — `mov [ebx], 0x11fab790`. Деструктор `0x11a58440` снова пишет `0x1200ad00` на `0x11a5845f`
  (стандартное поведение MSVC-деструктора).
- **Фабрика `0x11a58670`**: `mov eax,0x10; mov edi,0x900; call 0x118db560` → **размер класса 0x900**, затем
  `call 0x11a585a0`. Единственный путь создания — **регистрация в реестре классов**: `push 0x11a58670` на
  `.text 0x111a0541` внутри `0x1119fa50`, сразу после `call 0x103d1640` (геттер class-info) и
  `call 0x118ce980` (регистрация в глобальном реестре `[0x12804b1c]`).
- **Глобал с экземпляром отсутствует:** значение `0x1200ad00` встречается в файле ровно дважды, оба раза
  imm32 в `.text` (`0x11a585b5` конструктор, `0x11a5845f` деструктор). Экземпляр живёт в куче; указатель
  держит (BSS, инициализируемый в рантайме) реестр классов `[0x12804b1c]`.
- **Кто вызывает вирт-метод `0x11a58700` — статически не resolv-ится, с доказательством почему.** Это слот 5
  (`+0x14`), переопределение (в базовой таблице `0x11fab790+0x14` стоит `0x10362e70`). Тело:
  `mov esi,ecx; call 0x1127a0f0; push esi; call 0x103fe6c0; mov [esi+0x8cc],eax` и связывает узел
  `[esi+0x8c8]` в список `[eax+0xe8]` («attach»; парный слот `+0x18` (`0x11a58380`) делает detach через
  `0x1115e4a0`). Классическая форма `call dword ptr [ecx+0x14]` (`FF 51 14`) в DLL **отсутствует** (0
  совпадений); все формы `call [reg+0x14]` в `.text` идут через слои стека (`ebp`/`ebx`/`esp` функторы,
  245 сайтов, ни одного vtable). Реальный вирт-диспатч в этой сборке — пара `mov reg,[obj+0x14]; call reg`,
  таких пар 3073, и без рантайм-карты типов их типу не отнести. **Следующий зонд — динамический:**
  брейкпоинт фабрики `0x11a58670` (или записи в реестр `0x118ce980`), дамп `[instance]` и трассировка
  возвратов вызова слота `+0x14` на живом процессе.

## `0x11bd2b04` — НЕ vtable, а таблица указателей на функции инициализации; настоящий автор записей mode-id (2026-11-07, агент, `local/scratch/p285*.py`..`p287*.py`)

Закрывает «какой живой объект несёт vtable `0x11bd2b04` (владелец сброса mode-id)» из раздела про
кооп-id. Запуск исследователя упёрся в watchdog 30 минут; результат восстановлен по сырым байтам
пробами p285–p287. Поправка к заметке 2026-11-07 об авторах записей:

- **`0x11bd2b04` — не vtable класса.** Это массив из ~200 *маленьких независимых функций-заглушек* в
  `.rdata` (`0x11bd2b04..0x11bd2e24`, слоты `0x11b29040..0x11b2a9c0`), а не таблица методов класса.
  Доказательство: (1) base-dword `0x11bd2b04` встречается в файле **0 раз** (ни ссылки кода, ни
  хранимого указателя) — у настоящей vtable всегда есть хотя бы `mov [this], <vtable>` imm32 в
  конструкторе (для сравнения: реальный vtable `CFCXPlaylistService` `0x1200ad00` имеет ровно две
  такие записи); (2) элементы — не методы: напр. `+0x00` (`0x11b29040`) =
  `call 0x10024dc0; push 0x11ba38f0; call 0x106f9c37; ret`, `+0x04` (`0x11b29060`) обнуляет глобалы
  `[0x12806178]`/`[0x12806184]` — никто не читает `this`/`ecx`. Достигается через PE data-directory /
  механизм статической инициализации CRT, а не через указатель на объект.
- **Рутина сброса `0x11b2a610` (запись таблицы на `+0x2b8`, файл `.rdata 0x11bd2dbc`) — голая функция
  инициализации**, не метод: `or eax, 0xffffffff; mov [0x12807738], eax; ... mov [0x1280775c], eax; ret`
  (десять dword `0x12807738, 3c, 40, 44, 48, 4c, 50, 54, 58, 5c` ставятся в `-1`). Без аргументов и
  побочных эффектов → выполняется один раз при инициализации модуля, подготавливая массив значением `-1`.
- **Единственный рантайм-автор записей этих десяти глобалов — `0x117884f0`** (структурный скан `.text`:
  70 обращений к блоку, ровно 5 записей, все в этой одной функции). Вызывается из единственного
  `e8`-сайта `0x10c56ee8` внутри рутины, которая выделяет через `0x118db560` и сохраняет созданный
  объект в глобал `[0x12805e24]`. `0x117884f0` читает упакованное 16-битное поле `[0x1217c688]`
  (BSS default `4`), раскладывает его биты в десять слотов по-битными циклами и пишет через хелпер
  `0x10037bc0(global_va, &value, index)`; также использует счётчик `[0x1217af10]-[0x1217b2fc]`
  (BSS defaults `83`/`0x7FC9xxxx`). У остальных пяти глобалов (`0x12807738/3c/40/44/5c`) **вообще нет
  автора записей**, кроме инициализатора `0x11b2a610`.
- **Последствие для ярлыка «mode/session id».** Прежняя заметка называла `[0x12807738..0x1280775c]`
  «блоком mode/session id». Этот проход показывает, что блок — фиксированный массив из 10 dword,
  подготавливаемый `-1` и пересчитываемый в рантайме из упакованного feature/resolution-битфилда; путь
  установки кооп-id (`0x11279910` → `[0x12891ca0/0x12891ca8]`) — это *другой* набор глобалов. Являются ли
  эти десять dword id сессии или таблицей возможностей видео/режима — нужен отдельный зонд `[0x1217c688]`;
  отмечено, не решено. (Чтения конструктора менеджера 2026-11-06 `0x111f4fde/0x111f4ff2/0x111f500d`
  глобалов `[0x12807738]/[0x12807740]/0x12807744]` остаются в силе — читатели есть, автор записей `0x117884f0`.)

Открыто: (a) вызывающий вирт-метода `0x11a58700` — по-прежнему не resolv-ен, нужна рантайм-трассировка
(см. прошлый раздел); (b) опознать `[0x1217c688]` и смысл массива `[0x12807738..0x1280775c]`; (c) что
запускает таблицу инициализации `0x11bd2b04` (обходчик CRT `__initterm` / слот DllMain движка `[0x11e6c3dc]`).

## FC3.dll включён ASLR — любой жёстко зашитый адрес надо превращать в base+RVA (2026-11-07, агент, `pefile` на копии TestFC3)

Критично для сборки мода (хуки H1/H2). `pefile` на `H:\FarCryCoop\TestFC3\bin\FC3.dll`:
- `machine=0x14C` (x86), `ImageBase=0x10000000`, `DllCharacteristics=0x0140` → бит `0x40` (DYNAMIC_BASE)
  **установлен**, и директория таблиц базовых перемещений **присутствует**. Значит DLL *будет*
  перемещаться в рантайме, когда 0x10000000 занят — все адреса в этом файле это только VA в предпочтительной базе.
- Следствие: ASI/загрузчик обязан получать живую базовую точку модуля FC3.dll (`GetModuleHandle("FC3.dll")`)
  и прибавлять RVA, а никогда не зашивать `0x12891ca0` и т.п. Уже нужные RVA (VA − 0x10000000):
  `[0x12891ca0]→0x2891ca0`, `[0x12891ca8]→0x2891ca8`, `[0x12807738..0x1280775c]→0x2807738..`,
  vtable `0x1200ad00→0x200ad00`, таблица инициализации `0x11bd2b04→0x1bd2b04`, рутина установки
  `0x11279910→0x1279910`, метод `CFCXPlaylistService` `0x11a58700→0x1a58700`.
- `Subsystem=2` (GUI). Рабочая копия подтверждена как 1.06 (`FC3.dll` 40 720 424 байта, 2026-11-01).

## Цепочка вызовов установщика co-op + обвязка сервиса Playlist (сессия 4, статические зонды p290–p295)

Зонды `local/scratch/p29{0..5}_*.py` (+ `.out`) на `H:\FarCryCoop\TestFC3\bin\FC3.dll`. Делегат-исследователь
получил задачу закрыть последнее звено диспетчеризации установщика co-op; он упёрся в лимит 30 минут (SIGTERM),
но его зонды отработали. Находки:

- **У установщика co-op `0x11279910` ровно два прямых статических вызывающих**, оба — методы объекта
  сервиса плейлистов (`this` лежит в `edi`/`esi`, рядом пишутся члены `[+0x8c0]`,`[+0x8c4]`):
  - `0x1127a16f` внутри рутины `0x1127a0f0` (реализация базового слота `+0x14`; подряд `call 0x11279a90`
    затем `call 0x11279910`, дальше ставит члены `[+0x488]=2`, `[+0x4b0]=0x32`, `[+0x4b4]=0xa`, `[+0x4b8]=5`).
    `0x1127a0f0` — это и есть рутина, которая реально двигает установку co-op id.
  - `0x11279fc0` (слот 0 дочерней vtable `0x1200ad9c` → установщик co-op).
- **`0x11a58700` — НЕ вызывающий установщика** — подтверждено заново. Это ветка ошибки
  `CFCXPlaylistService not initialized` (см. более раннюю заметку); её единственная роль в цепочке — слот 2
  vtable `0x1200ad00`. Прежняя связка «`0x11a58700 → 0x1127a0f0`» заменена: реальный по-тикальный драйвер —
  это метод слота `+0x14` `0x1127a0f0` на сервисе плейлистов, диспетчируемый обобщённо.
- **Кто создаёт сервис**: рутинa регистрации `0x111a04f0`… вызывает геттер `0x103d1640` (гейт синглтона
  `[0x1286388c]`, экземпляр-глобал `0x12863890`) и регистрирует обработчики слота через `0x118ce980`
  (кладёт обработчик `0x11a58670`, затем `call 0x118ce980`), плюс create/lookup `0x11756a50` на контейнере
  сервисов `[0x12804acc]`. Обработчик `0x11a58670` лежит рядом с веткой ошибки `not initialized`
  `0x11a58700` (тот же объект, область слота 0x14).
- **Имена реестра сервиса плейлистов** (`.rdata`, семейство `NetObject.PlaylistService`):
  `CPlaylist`@`0x11fab6a4`, `CPlaylists`@`0x11fab6b0`, `CPlaylistServiceMemento`@`0x11fab6bc`,
  `NetObject.PlaylistService`@`0x11fab6de`, `UserPlaylist`@`0x11fab6f0`, `OfflinePlaylist`@`0x11fab700`,
  **`PrivateCoopPlaylist`@`0x11fab710`**. `UserPlaylist`/`OfflinePlaylist`/`PrivateCoopPlaylist` упоминаются
  вместе в `0x1127a2b2`/`0x1127a2d0`/`0x1127a2e7` — то есть сразу после вызывающего установщик co-op
  `0x1127a0f0`. **`PrivateCoopPlaylist` — вероятный тип плейлиста co-op-сессии**; в задел на будущее (что его
  выбирает и образуют ли пару co-op id `0x43521e6f` с ним).
- **Вердикт по последнему звену диспетчеризации (кто дёргает слот `+0x14`)**: **статически не разрешается за
  разумное время.** Обобщённый скан (p295) вида `mov r,[base+0x14]; call r` даёт сотни мест в `.text` (идиома —
  обобщённый тик-диспетчер движка), поэтому по одному лишь паттерну не сужается. Нужен рантайм-трасс: брейкпоинт
  на `0x1127a0f0` (или на установщике `0x11279910`), снять стек адресов возврата и `this` (`edi`) — это покажет
  планировщик, который тикает сервис плейлистов. Это задача владельца (отладчик), а не статическая.
- Влияние на план мода: H1 (запись id в `[base+0x2891ca0]/[base+0x2891ca8]`) **не затронут** — мы ставим id
  постфактум, диспетчер нам не нужен. `PrivateCoopPlaylist` на `0x11fab710` — новая зацепка для настройки
  хост-стороны сессии.

## Являются ли G1/G2 живым состоянием ко-опа? Вердикт H1 (сессия 5, статические зонды p300–p311)

Зонды `local/scratch/p30{0,0b,1,2,3}_*.py`, `p310_consumers.py`, `p311_modefunc.py` (+ `.out`) на
`H:\FarCryCoop\TestFC3in\FC3.dll`; сверено с делегатом-исследователем `del_mw6w8qqd_bsky`
(таймаут 30м, `.out` пуст, но его размышления и зонды подтверждают). Это УТОЧНЯЕТ и частично
ИСПРАВЛЯЕТ заметку сессии 4 («H1 не затронут»). Новое, решающее:

- **G1=`0x12891ca0` / G2=`0x12891ca8` — НЕ живое состояние режима.** Это локальные `static const`
  константы-ключи запроса, которые MSVC вынес в `.data` (каждая с байтом-флагом инициализации
  `0x12891ca4` / `0x12891cac`). Скан dword-значений (p300/p300b): у каждой ровно **3 ссылки во всём
  `.text`, и все они внутри двух установщиков ко-опа `0x11279910` / `0x11279a2b`** (адреса
  `0x11279961/65/2b` для G1, `0x11279ae1/e5/ab` для G2). Игровая логика/диспетчер не читают их по
  адресу. Поэтому запись в них из ASI **не может переключить текущий режим** — это правит лишь
  константы, которые установщик использует как ключи поиска. (В сессии 4 «H1 не затронут» было
  слишком оптимистично: H1 не вреден, но он **недостаточен и проверяет не ту переменную**.)
- **Идентификатор ко-опа `0x43521e6f` упоминается в 11 разных местах `.text`** (p300b):
  `0x10f0c7ec, 0x10f4cb11, 0x10f9260e, 0x10fa1aa5, 0x11279965(установщик), 0x11279ae5(установщик),
  0x1133fb8a, 0x113405ab, 0x1134062a, 0x11340a2d, 0x11a7fa12`. Это и есть настоящие потребители.
- **Живой идентификатор текущего режима = поле объекта `[this + 0x4c]`.** По адресу `0x113405a0`
  (`mov eax,[ebx+0x4c]`) код разветвляется по текущему режиму, сравнивая его с семейством из
  **шести хеш-ид режимов** — `0xab4fc8e2, 0x43521e6f(CO-OP), 0x9991daec, 0x6c2b3868, 0xf66ffb87,
  0x2100ced7` — и ко-опный ведёт к `FCXMainMenu` + команде `IngameToLobby` (`0x113405cd`..
  `0x11340600`). `ebx` — это `this` менеджера режимов. Именно это поле, а не G1/G2, есть переключатель
  ко-опа. Шесть идентификаторов НЕ совпали с обычным FNV-1a от названий режимов (хеш нестандартный)
  — расшифровать имена соседних нужно отдельно.
- **Лучшие статические «текущий режим», чем G1/G2** (находка делегата, согласуется с p310):
  слот `.data` `0x1216aee4` хранит `0x43521e6f` **статически (никогда не пишется из `.text`)** и
  читается/сравнивается ~15 раз как глобальное значение (`cmp eax,[0x1216aee4]`, `mov ecx,
  [0x1216aee4]`); аналогично `0x1216ca90` хранит `0x80608f71` (ид компании/одиночной игры), читается
  20+ раз. Эти ведут себя как константы режима, а не как изменяемое рантайм-состояние.
- **Настоящий владелец изменяемого состояния** (делегат, требует подтверждения в рантайме): живой
  контейнер записей плейлиста/сессии `[service + 0x8c0]` (service — синглтон `CFCXPlaylistService`,
  глобальная переменная экземпляра `0x12863890`), плюс реестр id→маска `[0x128048c0]` и контейнер
  сервисов `[0x12804acc]`. Ко-оп-сессия — запись `PrivateCoopPlaylist` (`0x11fab710`) в этом контейнере.

**Влияние на план**: H1 (запись ASI в G1/G2) понижен с «включает ко-оп» до «безопасный диагностический
зонд, который по построению ДАСТ НЕОДНОЗНАЧНЫЙ результат» — движок сам держит там `0x43521e6f`, так
что запись того же значения ничего не доказывает, а переключатель режима читает `[this+0x4c]`.
Перспективное направление — **живой контейнер плейлист-сервиса `[service+0x8c0]`** и **поле менеджера
режимов `+0x4c`**; оба требуют трассировки в рантайме (отладчик владельца), а не офлайн-записи.


## Шесть хешей игровых режимов: форма диспетчеризации и неразгаданный хеш (сессия 6, статические зонды p312–p315)

Зонды `local/scratch/p312_hashcrack.py`, `p313_alg.py`, `p314_dispatch.py`, `p315_je.py` (+ `.out`) на
`H:\FarCryCoop\TestFC3\bin\FC3.dll`, 2026-11-08. Продолжают вывод сессии 5: живой id текущего режима — это
поле менеджера режимов `[ebx + 0x4c]` (менеджер режимов `this` в `ebx`).

- **Диспетчеризация режима в `0x113405a0` — цепочка сравнений, а не таблица переходов** (p315_je, единственная
  полностью декодированная из трёх цепочек): `0x113405a0 mov eax,[ebx+0x4c]`, затем шесть `cmp eax, <id>` +
  условные переходы: `0xab4fc8e2 je 0x113405cd`, `0x43521e6f`(CO-OP)` je 0x113405cd`, `0x9991daec je 0x113405cd`,
  `0x6c2b3868 je 0x113405cd`, `0xf66ffb87 je 0x113405cd`, `0x2100ced7 jne 0x11340605` (то есть при равенстве
  *проваливается* в `0x113405cd`). **Все шесть id режимов ведут в один блок `0x113405cd`**, со строками
  `FCXMainMenu` + `IngameToLobby`; текущий режим, не равный ни одному из шести, уходит в `0x11340605`. ⇒ эта
  цепочка — *проверка принадлежности*: «живой режим — один из этих шести (с меню/лобби) → главное меню /
  IngameToLobby». CO-OP входит в эти шесть.
- **Две соседние цепочки** в `0x11340622..` и `0x11340a25..` сравнивают `[ebx+0x4c]` с теми же шестью id, но с
  другими целями (p314_dispatch, 750 инструкций декодировано на `0x11340400..0x11340d00`). В обеих только
  `0x2100ced7` даёт большое окно после сравнения (327 / 237 инструкций) со строками загрузки карты `CustomMap`,
  `UI\Multiplayer\Textures\Menu\Loading\Worlds\`, `_01_1.xbt`, `\1\`; у остальных пяти id окна по 2 инструкции.
  ⇒ `0x2100ced7` — режим, который грузит текстуры загрузочного экрана по мирам (загрузчик в стиле
  мультиплеера/аркады); остальные пять идут по короткому пути.
- **Шесть хешей режимов — НЕ распространённая хеш-функция строки.** Прогнано (p312, p313) по словарю
  кандидатов (варианты CO-OP / Campaign / Hike / Arcade / HackThe / Expedition / Matchmaking, имена движка с
  точками, `PrivateCoopPlaylist`/`OfflinePlaylist`/`UserPlaylist`) против **FNV-1a, FNV-1, djb2, djb2x, sdbm,
  murmur-less** — **0 попаданий**. Опорные значения: `fnv1a("CO-OP")=0x91c67ca9`, `djb2("CO-OP")=0x0ce785c3`,
  `sdbm("CO-OP")=0x38ef15a2`; ни одно не равно `0x43521e6f`. ⇒ хеш id в Dunia самодельный; имена режимов
  хешируются на этапе *сборки* (id лежат в `.data`, никогда не пишутся из `.text`, см. сессию 5), поэтому чтобы
  назвать пять соседних id, нужен либо восстановленный из движка алгоритм хеша, либо таблица имя↔id из
  `GameModesConfig.xml`, а не офлайн-подбор.

**Влияние на план**: подтверждает сессию 5 — переключатель читает `[ebx+0x4c]`; CO-OP (`0x43521e6f`) — один из
шести id, общих для пути IngameToLobby/меню, а `0x2100ced7` — единственный id режима, грузящий текстуры по
мирам. *Статическая* ветка по диспетчеризации режимов исчерпана. Следующий реальный шаг — трассировка в
рантайме (отладчик владельца): кто пишет `[ebx+0x4c]` (поставить точку останова там, снять автора записи и
`this`), и/или восстановление хеша id Dunia, чтобы назвать пять соседних id.

---

## Сессия 7 (2026-11-08): офлайн-проект Ghidra + декомпилированный механизм переключения co-op-режима (агент-сессия, REA/Ghidra headless)

**Провенанс.** После проверки MCP-инструментов coop-anything / supermemory / REA (см. `docs/tools/`)
разработка продолжилась с новой возможностью: офлайн-проект Ghidra `FC3_106` (построен 2026-11-08 через
`analyzeHeadless`, анализ `-default`, ~2 ч, 647 МБ `.rep`) теперь позволяет выгружать псевдокод для
любого RVA версии 1.06 без запуска игры. Проект лежит в черновике
`H:\FarCryCoop\scratch\ghidra\proj\FC3_106` (не коммитится). Переиспользуемый рецепт:
`analyzeHeadless <каталогПроекта> FC3_106 -process "FC3.dll" -noanalysis -scriptPath <скрипты>
-postScript <скрипт.java>` — загружает сохранённый анализ и запускает скрипт примерно за 3 минуты
(без повторного анализа). Проверено на `DecompileH3.java`, вывод
`H:\FarCryCoop\scratch\ghidra\out\decomp_H3.txt`. Владелец параллельно открыл тот же проект в GUI Ghidra —
только чтение, конфликта нет.

### Что декомпилировано (`FUN_` = имена Ghidra по умолчанию = RVA 1.06)

- **Диспетчер режимов `FUN_11340560`** (содержит цепочку сравнений на `0x113405a0`, тело
  `[0x11340560,0x113409cd]`, `__thiscall`, `param_1` = `this` менеджера режимов). Ключевые строки:
  - `iVar13 = param_1[0x13]` — `param_1` это `int*`, значит читается **`[this+0x4c]` = id текущего
    режима**. Шесть сравниваемых id точно равны `-0x54b0371e`(=`0xAB4FC8E2`), `0x43521e6f`(CO-OP),
    `-0x666e2514`(=`0x9991DAEC`), `0x6c2b3868`, `-0x9900479`(=`0xF66FFB87`), `0x2100ced7` — подтверждает
    находку сессии 6.
  - Если `[this+0x4c]` равен одному из шести И строка назначения равна `FUN_11788030("FCXMainMenu")`,
    цель заменяется на `0x63ddbbcb` и логируется `"IngameToLobby"`. Значит `0x63ddbbcb` — это id
    **лобби**, в которое попадаем при выходе из co-op-сессии главного в меню.
  - `(**(code **)(*param_1 + 0x5c))(&target)` — **виртуальный метод со смещением `+0x5c` в таблице
    функций менеджера режимов и есть реальный метод «переключить режим»**; вызывается с выбранном id.
  - `iVar13 = param_1[0x1d]` читает `[this+0x74]` (флаг-гейт); если выставлен и цель — один из шести
    или лобби, и `param_5 == 2`, загрузчик собирает
    `"UI\Multiplayer\Textures\Menu\Loading\Worlds\" + "_01_1.xbt"` (текстура загрузки мира, путь
    `0x2100ced7`). Существование проверяется через `(*DAT_12804308)->vtable+0x10`.

- **Init сервиса плейлистов `FUN_1127a0f0(int this)`** — метод активации/инициализации сервиса:
  - `this[0x8c0] = FUN_1025f3f0(this)`; `this[0x8c4] = FUN_1032fbd0(this)` — создают контейнер,
    хранимый в **`[service+0x8c0]`** (и компаньон в `+0x8c4`); подтверждает, что поле `0x8c0`
    заполняется во время выполнения (не мёртвое, как подозревала сессия 5).
  - `[container]->vtable+0x60(this+0x54)` регистрирует слушателя в `this+0x54`; затем в массиве
    слушателей `[FUN_1031c5d0(this)+0xe0/+0xe4]` ищется/дописывается `this+0x60` (`FUN_1003b4b0(1)` = new).
  - Вызывает `FUN_11279a90(this)` затем **`FUN_11279910(this)`** (инсталлер co-op, два варианта).
  - Потом выставляет поля настройки: `[this+0x488]=2`, `[this+0x503]=0`, `[this+0x4b0]=0x32`(50),
    `[this+0x4b4]=10`, `[this+0x4b8]=5`.

- **Инсталлер co-op `FUN_11279910(int this)`** (тело `[0x11279910,0x11279a8c]`) — разрешает co-op-сессию:
  - Ленивая инициализация: `if ((_DAT_12891ca4 & 1)==0){ _DAT_12891ca4 |= 1; _DAT_12891ca0 = 0x43521e6f; }`
    — подтверждает демоторсию H1 из сессии 5: `0x43521e6f` это просто **ключ запроса co-op**, кладёмый в
    `_DAT_12891ca0` один раз, а не живой переключатель режима.
  - `FUN_113224e0(&DAT_12891ca0)` ищет записи по этому ключу в массив результата
    (`local_14`, количество `local_10[0]`, шаг 3 указателя).
  - Для каждой записи собирает объект на `&PTR_FUN_11f94d08`, вызывает `FUN_112916e0()`, затем
    `(**(code **)(**(int **)(this+0x8c0) + 0x5c))(&obj, uVar2, 0)` — то есть **вызывает слот таблицы
    функций контейнера `+0x5c`, чтобы добавить разрешённую co-op-запись в `[service+0x8c0]`**; при успехе
    ещё `FUN_11258c40(this+0x204, …)`.
  - `FUN_11279fc0(this+0x54)` — тонкая обёртка, перезапускающая инсталлер для слушателя в `this+0x54`
    (`FUN_11279a90(p-0x54); FUN_11279910(p-0x54)`).

- **Геттер синглтона сервиса плейлистов `FUN_103d1640`** (тело `[0x103d1640,0x103d1670]`):
  `if ((_DAT_1286388c & 1)==0){ FUN_10302770(); FUN_10037ef0("CFCXPlaylistService"); }
  return &DAT_12863890;`. То есть **экземпляр синглтона — это сам объект по адресу `0x12863890`**
  (C++ magic-static под защитой `_DAT_1286388c`), а не указатель, хранящийся там. Поправка для
  Frida-пробы: `this` сервиса = `base + (0x12863890 - 0x10000000)` напрямую; НЕ делать `readPointer()`.
  У `0x11fab710` (PrivateCoopPlaylist) нет тела функции — это область vtable/данных, на которую ссылается
  инсталлер, что согласуется с сессией 4.

### Конкретные рычаги фазы 2, теперь выведенные из статического анализа

1. **Наполнить co-op-сессию** без UI: вызвать путь инициализации сервиса
   `FUN_1127a0f0(service)` (где `service = 0x12863890` как `this`) — он строит контейнер `[+0x8c0]` и
   запускает `FUN_11279910`, добавляющий co-op-записи; либо точнее — разрешить запись по ключу
   `0x43521e6f` через `FUN_113224e0` и добавить её через `vtable+0x5c` контейнера.
2. **Переключиться в co-op-режим**: выставить `[modeManager+0x4c] = 0x43521e6f` и вызвать
   `modeManager->vtable[+0x5c](0x43521e6f)`. `[modeManager+0x74]` гейтит ветку текстур загрузки.
   `this` менеджера режимов пока доступен только во время выполнения (через отладчик/Frida), но метод и
   смещение теперь закреплены, поэтому трассировка — это одна точка останова, а не блуждание.

### Новый Frida-скрипт
`scripts/fc3_h3_trace.js` (закоммичен вместе с этой секцией): читает живой `[this+0x4c]` из менеджера
режимов, контейнер `[service+0x8c0]` и логирует слоты сервиса плейлистов. ВАЖНО: его строка `service`
должна использовать `0x12863890` как `this` напрямую (см. поправку геттера выше), а не `readPointer()`.

### Дополнение к сессии 7 — ABI виртуального переключателя подтверждён дизассемблером (headless `DisasmSwitch.java`)

Мы дизассемблировали `FUN_11340560` из офлайн-проекта `FC3_106` (`scripts/ghidra/DisasmSwitch.java`,
вывод `H:\FarCryCoop\scratch\ghidra\out\disasm_switch.txt`, 364 инстр.). Место вызова vtable `+0x5c` —
`0x11340605`, соглашение вызова — обычный MSVC **thiscall** (this в ECX, единственный аргумент в стеке):

```
11340605  MOV EDX,[EBX]          ; EDX = this->vtable            (EBX = this менеджера режимов)
11340607  MOV EDX,[EDX+0x5c]     ; EDX = vtable[+0x5c]           (указатель функции)
1134060a  LEA EAX,[ESP+0x10]     ; EAX = &target_id (4-байтовая локальная на стеке)
1134060e  PUSH EAX               ; кладём единственный аргумент &id
1134060f  MOV ECX,EBX            ; ECX = this  (thiscall)
11340611  CALL EDX               ; переключение режима
11340613  MOV EDX,[EBX+0x74]     ; после: гейт [this+0x74]
```

На входе в функцию `MOV EBX,ECX` (`0x1134056a`) показывает, что сам диспетчер получает `this` в ECX.
Значит `NativeFunction(slot,'int',['pointer','pointer'],'thiscall')` в `switchCoop`, вызываемый как
`(this=mm, &id)`, корректен: Frida-`thiscall` кладёт арг1 в ECX, остальное — в стек. `[this+0x4c]`
читается на `0x113405a0` (`MOV EAX,[EBX+0x4c]`); идущее после переключения цепочка сравнения шести id —
это цепь `0x11340622` (совпадает с «тремя цепями» сессии 6). **Остаточный риск не в ABI, а в контексте:**
`switchCoop` зовёт виртуал переключателя напрямую, вне диспетчера, который на входе ещё выполняет
`(**(code**)(*param_1+0x20))()` и другую обвязку — поэтому живой тест может повести себя неверно или
упасть по причинам, не связанным с регистральным соглашением. Отсюда сначала dryRun + офлайн-экземпляр.

## Сессия 8 (2026-11-08): живой запуск на DX9 + объекта менеджера режимов нет в меню (агентская сессия, Frida + REA/Ghidra headless)

Цель: получить живой `this` менеджера режимов (ECX/EBX в точке диспатча), чтобы можно было вести
`switchCoop`, и прочитать живой контейнер `[service+0x8c0]`. Вся сессия — на рабочей копии владельца
`H:\FarCryCoop\TestFC3\` (реальная установка Uplay не тронута), 1.06 `FC3.dll`.

### Игру пришлось перевести на DX9-сборку, иначе FC3.dll вообще не грузится
Рабочая копия Steam по умолчанию запускает **DirectX 11** бинарник `farcry3_d3d11.exe`, который **не**
грузит `FC3.dll` (в DX11 идёт `FC3_d3d11.dll`), поэтому все адреса трейсера были вне отображения.
**DX9**-бинарник `farcry3.exe` (заглушка 60672 байта, хеш `73a2870f827d3f305681f2198f232bf2f08172097411091543a7f3e5539f9641`)
**грузит** `FC3.dll` — наша личность 1.06. `scripts/fc3_h3_run.py` теперь по умолчанию берёт `farcry3.exe`
и отказывается цепляться к `_d3d11`. Живой базис модуля меняется от запуска к запуску (этот запуск
`0x798a0000`; `A(x)=base+(x-0x10000000)`).

### UI ко-опа гейтится онлайн; офлайн игра обрывает переход до смены режима
Владелец запустил `scripts/fc3_h3_run.py --watch 90` и зашёл в меню мультиплеера/ко-опа, но игра показала
внутриигровую ошибку **«Служба сетевой игры больше недоступна»** (нет игрового сетевого сервиса) — Ubisoft-нетплей
офлайн недоступен — и **обрвала переход ещё до смены режима**. Хук диспатча на `0x113405a0` так и не сработал
(`WATCH DONE ... NONE - no mode transition fired`). То есть в ко-оп офлайн нельзя попасть через UI; внутренний
подход H3 — это ровно обход того гейта, но ему всё равно нужен живой `this` менеджера режимов.

### Диспетчер вызывается ТОЛЬКО виртуально (headless `DumpCallers.java`)
`scripts/ghidra/DumpCallers.java` (офлайн-проект `FC3_106`) показывает, что у `FUN_11340560` (диспетчер; точка
диспатча `0x113405a0`, `thiscall this` = менеджер режимов) **ноль прямых вызовов** — оба его кросс-рефа это DATA,
и оба это **слоты таблиц виртуалов**: `0x1200e658` (база `0x1200e620`, 15 слотов) и `0x11f91120` (база `0x11f910e8`,
16 слотов, часть слотов — purecall-заглушка `0x1061fee0` => абстрактная/интерфейсная таблица). В обеих таблицах
`FUN_11340560` стоит на слоте **`+0x38`** (см. `scripts/ghidra/DumpVtable.java` -> `out/vtable_mode.txt`). В таблице
хранится **вход** функции `0x11340560`, а не середина функции.

### Живого экземпляра менеджера режимов в меню нет (два независимых скана, оба пусты)
- `scanmm` (скан кучи по id, `[obj+0x4c]` == одно из шести id): нашлись только три **дескриптора** режимов с id
  `0x6c2b3868` (виртуалы `0x1f1a128`/`0x1f3a8b8`/`0x1f6aacc`), а не менеджер.
- `scanmmv` (скан кучи на живой `vptr == A(0x1200e620)` или `A(0x11f910e8)`): **0 экземпляров**.
- `modevt` (`findModeVtablesByDispatch`, преемник `scanModeManagerByVtable`, добавлен и исправлен в этой сессии):
  сканирует читаемые диапазоны **образа** на указатель входа функции `0x11340560` (сам находит все таблицы,
  диспатчащие через неё, базовую и производные), затем ищет в `rw-`-куче живые объекты каждой. Результат: ровно
  **2** найденные таблицы образа — `A(0x1200e620)` и `A(0x11f910e8)` — что подтверждает статику, но **0 живых
  экземпляров** обеих.

Вывод (детерминированный): **пока игра сидит в главном/ко-оп меню, объект ни одного из двух классов-реализаторов
диспатчера не создан.** Менеджер режимов конструируется только вокруг реальной активации режима. Единственный
детерминированный способ прочитать `this` — поймать диспетчер живьём при переходе, который игра **может** сделать
офлайн: **загрузка одиночного мира** (Главное меню -> Продолжить / Загрузить сохранение), а не заблокированный
офлайн ко-оп. Контейнер `[service+0x8c0]` (плейлист ко-опа, объект-синглтон по `0x12863890`) тоже перепроверен —
в меню всё ещё `0x0`.

### Инструменты этой сессии (закоммичены, запушены в форк агента)
- `scripts/fc3_h3_run.py`: авто-режим `--watch N` (цепляние, опрос `lastMode` 1 Гц, лог `[MODECAP]`, авто-отцеп);
  команды `scanmm`, `scanmmv`, `modevt`.
- `scripts/fc3_h3_trace.js`: `scanModeManager` (скан по id), `scanModeManagerByVtable` (скан по статич. виртуалу),
  `findModeVtablesByDispatch` (`modevt`: поиск таблиц по образу + скан экземпляров в куче, кэширует первый живой
  экземпляр в `lastMode` для `switchCoop`). `ADDR.mmDispatchFn = 0x11340560` (значение слота).
- `scripts/ghidra/DumpCallers.java`, `scripts/ghidra/DumpVtable.java` + `run_dump_vtable.bat` (офлайн-переиспользование).
Коммиты (форк агента `main`): `b74c165` (добавлен modevt), `a3aac57` (исправлен modevt: искать вход в образе,
экземпляры в куче). Запись supermemory `jiAFbWDzn3UFD5x3X5Uj9g`.

### Сессия 8c (2026-11-08): живая таблица виртуалов, а «переключатель» +0x5c — лишь установщик id (H3a понижен)

Захват `--watch` + загрузка одиночки повторился, и новый авто-`[MODEPROBE]` дал раскладку живого менеджера
режимов (база запуска `0x798a0000`, `this`=`0x298db6d0`):

- `curMode` `[this+0x4c]` = `0x80608f71` в этом запуске (в прошлом — `0x83AE70EF`) -> `[this+0x4c]` НЕ стабильный
  id режима и никогда не входит в шесть «диспатчерных» id.
- `[this+0x20]` = `0x0`, `[this+0x74]` = `0x100dbd00` (указатель в модуле, т.е. «гейт» — живой член, поэтому
  ветка загрузочных текстур диспатчера выполняется).
- **первичная таблица виртуалов = `0x7a56e5f8` -> Ghidra `0x1200e5f8`** (в образе). Две таблицы, которые скан
  `modevt` упорно выдавал (`0x1200e620`, `0x11f910e8`), — это НЕ vptr объекта: `0x1200e620` есть **вторичный**
  подобъект базового класса того же объекта по первичной+`0x28` (множественное наследование). Именно поэтому
  `scanmmv`/`modevt` находили 0 экземпляров: `+0`-vptr объекта — это первичная таблица `0x1200e5f8`, которую эти
  сканы не искали. Диспатчер `FUN_11340560` стоит на **первичном `+0x60`** (`0x1200e658`), что совпадает с
  `+0x38` вторичной таблицы (`0x1200e620+0x38`) — это совпадение и заставило скан с предположением «+0x38»
  выдать ложную базу.

Целевые значения слотов первичной таблицы (прощупано на живую, RVA Ghidra): `+0x20 -> 0x1133fb30` (не функция —
thunk-слот), `+0x38 -> 0x10c471b0`, **`+0x5c -> 0x1030f8a0`** (виртуал, который диспатчер зовёт как «переключатель»),
`+0x60 -> 0x11340560` (сам диспатчер).

Декомпиляция (офлайн `FC3_106`, `scripts/ghidra/DecompileModeSwitch.java` -> `out/decomp_modeswitch.txt`):

```
void __thiscall FUN_1030f8a0(int this, undefined4 *param_2)   // vtable[+0x5c]
{
  *(undefined4 *)(this + 0x4c) = *(undefined4 *)(this + 0x48);   // prev = cur
  *(undefined4 *)(this + 0x48) = *param_2;                        // cur  = targetId
  return;
}
```

**Значит «виртуал-переключатель» `vtable[+0x5c]` — это двухстрочная перестановка id, а не переход.** Он кладёт
целевой id в `[this+0x48]` и сдвигает старый в `[this+0x4c]`; он НЕ грузит мир, НЕ строит сессию и НЕ трогает
сервис плейлиста. Следствие для H3a: `switchCoop` (записать `[this+0x4c]=CO-OP` + вызвать `vtable[+0x5c](&CO-OP)`)
безвреден (на этом пути не упасть, поэтому владельцу НЕ надо рисковать), но **бесполезен для входа в co-op** —
задаёт лишь два поля id. `[this+0x48]` — «текущий/целевой» id, `[this+0x4c]` — «предыдущий»; диспатчерное сравнение
шести id и ветка загрузочных текстур их потребляют, а реальная работа (загрузка карты/мира, подъём сессии)
происходит в потребителях `[this+0x48]` и у *вызывающего* диспатчер — который дёргает виртуал диспатчера
(`vtable[+0x60]`) с `(param_2=&destId, param_3=refcounted ptr, param_4, param_5)` и статически по xref не находится
(непрямой вызов через объект). Прямых вызовов у диспатчера ноль; зовут его только объекты этого класса через виртуал.

Это понижает H3a как механизм входа в co-op. Новые зацепки: (1) найти потребителей `[this+0x48]` / вызывающих
виртуал диспатчера `+0x60`, чтобы locate код, реально реагирующий на co-op целевой id; (2) контейнер co-op
`[svc+0x8c0]` в мире всё ещё `0x0`, поэтому co-op-сессию/плейлист (и её сетевой предпосылка-нетплей) надо поднять
до того, как co-op целевой id что-то сделает — а офлайн это заблокировано гейтом сетевого сервиса Ubisoft. Чистый
co-op-переход, скорее всего, надо **снимать онлайн** (смотреть реальный заход 2p) и только потом рассуждать о
офлайн/4p-реконструкции.

### Сессия 8d (2026-11-08, офлайн Ghidra, H4b): настоящий обработчик смены режима в co-op и его предусловия

Офлайн-путь (владелец выбрал H4b: онлайн-кооп недоступен). Переиспользован уже проанализированный
Ghidra-проект `FC3_106` (без повторного анализа; обёртка `scripts/ghidra/run_headless.py <Script.java>
<лог>`). Два новых скрипта: `FindModeConsumers.java` (все функции, которые загружают id режима как
скалярную константу, + ссылки на таблицы виртуалов менеджера) и `DecompileConsumers.java`
(декомпиляция найденного). Вывод: `H:\FarCryCoop\scratch\ghidra\out\decomp_consumers.txt`.

**Вселенная констант id режима (13 из 128384 функций загружают один из id как константу).** Ключ
ко-опа `0x43521e6f` встречается в: `FUN_10f0c770`, `FUN_10f4ca20`, `FUN_10f92420`, `FUN_11279910` /
`FUN_11279a90` (установщик H1, уже известен), `FUN_11a7f9d0`, диспатчере `FUN_11340560`, его
функции-загрузчике `FUN_113409d0` и обработчике `FUN_10fa1990`. Полный набор из шести id
{`0xab4fc8e2`,`0x43521e6f`,`0x9991daec`,`0x6c2b3868`,`0xf66ffb87`,`0x2100ced7`} загружают:
`FUN_10fa1990`, `FUN_11204b00` (пять, без ключа ко-опа), `FUN_11340560`, `FUN_113409d0`. Лобби-id
`0x63ddbbcb` только в `FUN_113401c0` и `FUN_11340560`.

**Идентичность класса менеджера режимов (первичная таблица виртуалов `0x1200e5f8` имеет ровно две
ссылки, обе DATA):** `FUN_10fa1e30` (деструктор/`__fastcall`) и `FUN_10fa1eb0` (конструктор) пишут
`*obj = &PTR_FUN_1200e5f8`. Раскладка объекта конструктора (индексы dword, байтовое смещение = idx*4):
`[*0]` vptr `0x1200e5f8`; `[2]`(+0x08) = `&PTR_LAB_1200e660`; `[0xf]`(+0x3c) = `&PTR_LAB_1200e668`;
вторичный базовый похоъект конструируется в `obj+0x28` функцией `FUN_112709d0` (объясняет, почему
ранее найденный вторичный `0x1200e620` лежит в первичная+0x28); поля `[0x4d]`,`[0x4e]`,`[0x52]`,
`[0x53]`=0, `[0x51]`байт=0, `[0x50]`=-1, затем заполняется хэндлом, скопированным из глобала
`DAT_12821398` через `FUN_1015b680`. Слоты виртуала (подтверждено): `+0x50` геттер, `+0x5c` =
`FUN_1030f8a0` (перестановка id), `+0x60` = `FUN_11340560` (диспатчер). То есть вывод «vtable+0x5c —
лишь установщик id» остаётся в силе; это полная раскладка класса.

**Настоящий обработчик смены режима — `FUN_10fa1990`** (`__thiscall(this=менеджер, param_2, param_3)`),
лежит на той же странице, что конструктор и сравнение с шестью id. Поток:
- увеличивает счётчики ссылок у `param_2` (обёртка целевого id режима) и `param_3` (объект-дескриптор),
  присваивает `local_c = this`;
- вызывает **`FUN_11340d00(param_2, param_3)`** — ЯДРО перехода, которое действительно применяет новый
  режим;
- вызывает `this->vtable[+0x50](&local_10)`, чтобы прочитать разрешение текущего/нового id режима в
  `iStack_14`;
- читает центральный объект `DAT_12804acc`: условие `[DAT_12804acc+0x6c]`, хэндл `[DAT_12804acc+0x68]`,
  передаваемый в `FUN_103a9ea0` (поиск сессии/хэндла);
- затем ветвится по разрешённому id и выбирает ТЕКСТ ЗАГРУЗОЧНОГО ЭКРАНА: **`iStack_14 == 0x43521e6f`
  (CO-OP) -> пишет `"Coop_Fenrir_Loading"`** (Fenrir = кодовое имя ко-опа); `-0x54b0371e` ->
  `"PvP_Dom_Loading"`; прочие спец-id просто идут дальше. Для ко-опа также трижды читает `param_3+0xC`
  через `FUN_10003f00` (предикат имени/строки) и проверяет **`FUN_1011cb30()`** (предикат
  доступности/включённости ко-опа, вызывается до 5 раз).
- в конце `FUN_110252d0(...)` и, если `[DAT_12804b3c+0x70]==1`, два виртуальных вызова через
  `*(int*)(local_10+0xa0)+0x64/0x6c`.

Его функция-загрузчик **`FUN_113409d0`** (`this, param_2=destId, param_3, param_4`) — это НАСТРОЙКА
экрана загрузки мультиплеера/ко-опа: если `*param_2` равен одному из шести id, ставит байт
`[this+0x44]=1`, сохраняет `param_3` в `[this+0x90]` (со счётчиком ссылок), грузит
`"UI\Multiplayer\Textures\Menu\Loading\Worlds\"` + `"_01_1.xbt"`, затем `FUN_117872f0(...)` и
`FUN_103a2d50(...)`.

**Ответ на вопрос H4b (есть ли ОДНА функция, поднимающая co-op-мир по целевому id, и что ей нужно
кроме `this`):** единственный вход — это **`FUN_10fa1990`** (ядро `FUN_11340d00`), А НЕ запись в
`[this+0x48]` + `vtable[+0x5c]`. Кроме `this` нужно: (a) `param_2` = обёртка id CO-OP (`0x43521e6f`),
(b) `param_3` = co-op **объект-дескриптор**, у которого в `+0xC` лежит строка имени карты/мира
(проверяется `FUN_10003f00`), (c) предикат доступности `FUN_1011cb30()` должен вернуть true, и
(d) живой **хэндл сессии**, доступный из `DAT_12804acc+0x68` / co-op-плейлиста `[svc+0x8c0]`. Пункты
(c) и (d) — это и есть офлайн-стена: `FUN_1011cb30` отражает доступность ко-опа, а хэндл/плейлист
порождаются нетплеем, который офлайн выключен («служба больше недоступна»), и `[svc+0x8c0]` остаётся
`0x0` даже в загруженном мире. Поэтому даже прямой вызов `FUN_10fa1990(this, coOpId, desc)` офлайн
дойдёт до `"Coop_Fenrir_Loading"` и дальше не найдёт ни сессии, ни карты для загрузки. **Итог H4b:
офлайн нет самодостаточного запуска ко-опа, который можно было бы перехватить; дескриптор и сессия
создаются онлайн-флоу лобби, который офлайн ненаблюдаем.** Следующие кандидаты для статического
чтения — `FUN_11340d00` (ядро перехода) и `FUN_1011cb30` (предикат доступности), чтобы понять, сможет
ли поддельный дескриптор обойти предикат.

### Сессия 8e (2026-11-08, офлайн Ghidra): ядро перехода и «предикат доступности» НЕ завязаны на нетплей (офлайн-кооп не заблокирован на уровне режимов)

Продолжение H4b офлайн (по просьбе владельца): декомпилировать `FUN_11340d00` (ядро перехода) и
`FUN_1011cb30` (раньше считался предикатом доступности ко-опа) и решить, сможет ли поддельный
дескриптор `param_3` поднять co-op-мир офлайн. Скрипт `DecompileCore.java` (цели 11340d00, 1011cb30,
10003f00, затем 117872f0, 103a2d50, 11788030); вывод `decomp_core.txt` / `decomp_core2.txt`.

**Поправка к сессии 8d:** `FUN_1011cb30` — НЕ гейт доступности/нетплея. Это тривиальный предикат
пустой строки, вызываемый из 30+ generic-мест:
```c
bool __fastcall FUN_1011cb30(int *param_1) {        // не void; аргумент в ecx/стеке
  if (*param_1 == 0) return *in_EAX == '\0';
  return FUN_10003f00(*param_1 + 0xc) == 0;         // "имя-строка дескриптора в +0xC пуста?"
}
```
Значит в co-op-ветке `FUN_10fa1990` вызовы `FUN_1011cb30()` просто перечитывают поля имени
дескриптора, а не проверяют сеть.

**`FUN_11340d00` (ядро перехода) — тонкая обёртка с флагом**, без нетплея:
```c
void __thiscall FUN_11340d00(int this, int *destId, int *descriptor) {
  if (*(char *)(this + 0x19) == 0) {                // условие: переход ещё не идёт
    refcount destId, descriptor;
    FUN_113409d0(this, this + 0x48, destId, descriptor);   // загрузчик; 2-й арг = &this->modeId
  }
  *(undefined1 *)(this + 0x70) = 1;                 // флаг "запрошена смена режима"
  ... очистка счётчиков ссылок
}
```
Единственный вызывающий — `FUN_10fa1990` (+ одна DATA-ссылка на 0x11f910cc = слот виртуала во
вторичном кластере).

**Две функции загрузки, которые вызывает загрузчик — generic-хелперы движка, не вызовы сессии:**
- `FUN_117872f0` читает глобал `DAT_12804324` (глобал текущей игры/мира-строки); если задан, копирует
  строку и разрешает её через `FUN_11787e80` (возвращает пару id в EDI, иначе `{0xffffffff,0xffffffff}`).
- `FUN_103a2d50(param_1=&out, param_2=keyPair)` — хэш-табличный поиск: `idx = ((param_2 ^ 0xdeadbeef)
  * ...) % buckets` в `unaff_EDI + 0xc`, идёт по списку корзины, сравнивая пару ключей
  (`piVar3[2]`,`piVar3[3]`), возвращает указатель на запись (или `{0,0}`). Generic-реестр find-by-id.

**Ответы на три вопроса владельца:**
1. **От чего зависит `FUN_1011cb30`:** только от того, что строка в `+0xC` дескриптора непустая. Тривиально
   выполняется корректным дескриптором; это НЕ гейт нетплея/онлайна, так что «подделать true офлайном» —
   вообще не та задача.
2. **Что делает `FUN_11340d00` при co-op id:** проверяет `[this+0x19]==0`, увеличивает счётчики ссылок
   id/дескриптора, вызывает загрузчик `FUN_113409d0` (тот сверяет целевой id с шестью спец-id и готовит
   экран загрузки мультиплеера/ко-опа + текстуры Worlds), и ставит `[this+0x70]=1`. Сетевого кода нет.
3. **Сможет ли поддельный дескриптор протащить co-op-мир офлайн?** **Уровень режимов офлайн не
   заблокирован** — ни `FUN_10fa1990`, ни `FUN_11340d00`, ни `FUN_113409d0`, ни `FUN_117872f0`, ни
   `FUN_103a2d50` не обращаются к сетевому сервису. Отказ «служба недоступна» находится ВЫШЕ, в
   онлайн-лобби, которое (а) офлайн не пропускает дальше и (б) обычно строит `param_3` и заполняет
   глобалы сессии. То есть офлайн-препятствие — это не жёсткая проверка, а *отсутствующие входы*:
   валидный co-op-дескриптор `param_3` (его класс/виртуал + раскладка имени-строки в `+0xC` пока не
   размечены) и согласованные глобалы сессии (флаг `DAT_12804acc+0x6c`, хэндл `+0x68`, строка мира
   `DAT_12804324`). Даст ли вручную собранный дескриптор **играбельный** co-op-мир (в отличие от
   зависания на асинхронной загрузке, ожидающей данных сессии) — покажет только живой эксперимент.
   Следующая конкретная офлайн-зацепка: разметить класс объекта-дескриптора (его виртуал + поле-строку
   `+0xC`) через онлайн-продюсера лобби, ИЛИ проверить, даст ли строка одиночного мира в `DAT_12804324`
   разрешить `FUN_117872f0` загрузку карты.

### Сессия 8f (2026-11-08, оффлайн Ghidra): дескриптор `param_3` — это запись глобального синглтона-списка режимов `DAT_128048c0`

Ответ на вопрос «какой объект передаётся как `param_3`»: это **запись-дескриптор режима**, живущая в
глобальном синглтоне-списке, а НЕ объект, создаваемый заново на каждый вызов. Скрипты
`TraceDescriptor.java`, `TraceRegistry.java`, `DecompRegistry.java` (xref + декомпиляции).

**Вход в смену режима — это слот виртуальной таблицы:** у `FUN_10fa1990` ровно один xref — DATA-слот в
`0x1200e604`, т.е. **`+0x0C`** первичной vtable менеджера режимов `0x1200e5f8`. Значит вход в кооп
вызывается как `mgr->vtable[+0x0C](destId, descriptor)` (виртуально; статического вызывающего нет —
та же причина, что и у диспетчера). `FUN_10fa1990(this, param_2=destId, param_3=descriptor)`
увеличивает счётчики ссылок обоих, вызывает `FUN_11340d00(param_2, param_3)`, читает разрешённый id
через `this->vtable[+0x50]`, далее ветка по id (`0x43521e6f` -> "Coop_Fenrir_Loading").

**Раскладка дескриптора (`param_3`)** (по всем его потребителям): `+0x00` встроенный счётчик ссылок
(LOCK/`+1`/`-1` в каждом держателе), `+0x0C` **имя-строка** (`char*`, проверяется `FUN_10003f00`/`FUN_1011cb30`),
`+0x20` **dword id режима**. В `FUN_113409d0` загрузчик СОХРАНЯЕТ использованный дескриптор в `[mgr+0x90]`
(со счётчиком) и вызывает `**(*mgr+0x60))(destId,&x,&descriptor,1)` (повторный диспатч).

**Откуда берётся дескриптор — глобальный синглтон-список режимов `DAT_128048c0`:**
```c
piVar4 = *(int **)(DAT_128048c0 + 4);            // указатель на данные списка (записи)
piVar1 = piVar4 + *(int *)(DAT_128048c0 + 8);    // конец = база + размер
for (; piVar4 != piVar1 && *(int*)(*piVar4 + 0x20) != *param_2; piVar4 = piVar4 + 1) {}
```
Т.е. `DAT_128048c0` — менеджер, внутренний массив которого в `+0x04` (данные) / `+0x08` (размер);
загрузчик **линейно ищет запись у которой `+0x20` == целевой id режима**. Найденная запись и есть дескриптор.

**Жизненный цикл синглтона:** `DAT_128048c0` создаётся лениво в `FUN_10048230` (выделение через фабрику
синглтонов `FUN_118db560`, `*obj = &PTR_FUN_11f224c4` (vtable менеджера списка), обнуление `+0x00..+0x18`,
публикация) и уничтожается в `FUN_11756e00` (**сворачивание/shutdown**: `(**(*obj))(1)` delete + обнуление,
заодно чистит `DAT_12804acc`). Значит это НЕ место онлайн-пополнения; реальная регистрация записей режима
идёт через vtable менеджера списка `0x11f224c4` (виртуальный аддер — статически не выводим, нужен живой чтение).

**Итог для «собрать дескриптор вручную»:** валидный co-op-дескриптор = объект с `+0x20 = 0x43521e6f` и
`+0x0C = имя карты/мира кооп`, присутствующий в списке `DAT_128048c0`. Решающий вопрос теперь эмпирический
и дёшево проверяется **вживую**: содержит ли запущенная DX9-игра оффлайн запись `+0x20 = 0x43521e6f` в
списке `DAT_128048c0`? Если да — можно вручную вызвать `mgr->vtable[+0x0C]` с этой записью; если нет —
регистрация co-op-записи и есть настоящий оффлайн-гейт. Подготовлен `dumpModes` (RPC трейсера) для
перечисления записей списка `DAT_128048c0` (`{id@+0x20, name@+0xC}`) на живой сессии. Глобалы пишутся
ровно 3 местами каждый: `DAT_128048c0` = {`FUN_10048230` ctor, `FUN_11756e00` dtor, `FUN_11756e00`};
`DAT_12804acc` = {`FUN_100480f0`, `FUN_117567c0`, `FUN_11756e00`}; `DAT_12804b3c` = {`FUN_10136900`,
`FUN_11629c30`}.

### Сессия 8g (2026-11-09, ЖИВОЙ запуск, сам): запись режима CO-OP УЖЕ ЕСТЬ в офлайн-реестре режимов

Полный живой цикл сделан мной сам (для него клики в игре не нужны): запустил офлайн-копию
`H:\FarCryCoop\TestFC3\bin\farcry3.exe` (прямой exe, cwd `bin`, DETACHED_PROCESS), дал загрузиться,
затем прогнал `scripts/fc3_h3_run.py` с пайпом в stdin `dump\nmodes\nquit` (frida 17.26.2). Команда
`modes` НЕ требует действий в игре, поэтому — в отличие от снятия менеджера через хук диспатча — она
полностью автоматизируется агентом.

**Решающий ответ на вопрос сессии 8f:** живой глобальный синглтон-список режимов `DAT_128048c0`
**заполнен 16 записями ОФФЛАЙН**, и **запись с индексом 7 имеет `+0x20 = 0x43521e6f` (CO-OP)**. Значит
вход в кооп НЕ гейтится онлайном на уровне реестра — дескриптор co-op-режима уже существует в запущенной
офлайн-игре. Ручной заход через `mgr->vtable[+0x0C](destId, descriptor)` с этой записью не требует
онлайн-захода в 2p-кооп.

Живой снимок (этот прогон, база плавает): менеджер `this` runtime `0x10270a60`, vtable `0x7aa024c4`
(= Ghidra `0x11f224c4`, совпадает со статическим конструктором), счётчик по `+0x08` = `16`. Все 16 id
режимов (`+0x20`) по порядку: `0x7520e174, 0x83ae70ef, 0xcd0b222f, 0xcb5df48c, 0x863659d2, 0x9216b3de,
0x80608f71, 0x43521e6f[COOP], 0xff56cf71, 0xc8ab0853, 0x8b40f692, 0x6c2b3868, 0xab4fc8e2, 0x9991daec,
0xf66ffb87, 0x2100ced7`. Присутствуют все шесть id диспетчера плюс `0x80608f71` (ранее наблюдавшийся
живой текущий id режима).

**Поправка раскладки:** чтение `+0x0C` как `char*` дало «(unreadable)» для всех записей, значит `+0x0C`
— НЕ имя-строка для этих записей списка (имя `+0xC` из заметки сессии 8f относится к использованию
`param_3` внутри `FUN_10fa1990`, а не к структуре записи реестра по тому же смещению). Подтверждённое
поле остаётся `+0x20` = id режима; `+0x00` = счётчик ссылок. Дальше: выяснить реальные поля записи
(особенно строку карты/мира и данные режима, которые читает загрузчик), чтобы уметь вести co-op-запись.

**Ограничение подтверждено:** игра запущена ПРЯМО (не через Ubisoft Connect), поэтому работает офлайн;
frida-attach делать только к таким офлайн-экземплярам (античит/страж мьютекса). Ubisoft Connect был
запущен (UplayWebCore.exe ×6), но прямой запуск `farcry3.exe` поднимает свой офлайн-экземпляр.

### Сессия 8h (2026-11-09, ЖИВОЙ): надёжное снятие менеджера режима + ручной вызов виртуала смены режима безопасен, но оффлайн это no-op

Два конкретных результата живого самостоятельного прогона (оффлайн `farcry3.exe` на этом ПК).

1. **Надёжное снятие менеджера, без смены режима.** `scanModeManagerByVtable` теперь включает
   ПОДТВЕРЖДЁННУЮ первичную vtable `0x1200e5f8` (добавлена как `ADDR.mmVtable0`). Один скан кучи по vptr
   вернул ровно один экземпляр: живой менеджер режимов `this = 0x294dd3a0`, `[this+0x4c] = 0x83ae70ef`,
   vtable `0x7aaee5f8` (= `0x1200e5f8`). Это наконец даёт менеджер без ловли настоящей смены перехода
   (старый скан смотрел только на ложные вторичные базы `0x1200e620`/`0x11f910e8`).

2. **RPC `coopEnter` (`coop dry|go`)** вызывает `modeManager->vtable[+0x0C]` с `(&id-CO-OP, descriptor)`
   и сам в сессии находит живую co-op-запись реестра (запись `DAT_128048c0` с `+0x20 == 0x43521e6f`).
   Сухой прогон подтвердил слот `+0x0C -> 0x79a81990` = Ghidra **`FUN_10fa1990`** (настоящий обработчик
   смены режима, а не no-op-сеттер `+0x5c` = `FUN_1030f8a0`, который зовёт `switchCoop`).

3. **Живой `coop go` — результат:** вызов ВЕРНУЛСЯ (без краша; игра жива, pid 14932, ~548 МБ) с
   `ret = 0x1026...`, но **`[this+0x4c]` НЕ изменился (`0x83ae70ef` до и после)**. То есть вызов виртуала
   смены режима из треды Frida БЕЗОПАСЕН, но САМ текущий режим не переключает. Обработчик ведёт учёт/
   счётчики ссылок; реальный переключатель опрашивается/ведётся позже на главном треде обновления игры
   (а для co-op-ветки почти наверняка нужен объект co-op-сессии, который оффлайн не создаётся). Внешний
   драйвер упал по таймауту лишь потому, что чтение RPC подолгу блокировалось после вызова; сам скрипт
   залогировал `ret` и чистый `detaching`.

Следующая зацепка: найти, ЧТО потребляет отложенную цель обработчика на главном треде (какое поле
`[this+...]` оно читает на следующем кадре) и можно ли пред-заполнить оффлайн co-op-сессию, вместо
слепого вызова входного виртуала.

### Сессия 8i (2026-11-09, ОФФЛАЙН Ghidra FC3_106 + ЖИВОМ: топология вызовов смены режима полностью снята; оффлайн-блокер — объект netplay-сессии, а не гейт по id/полю

Продолжил оффлайн-зацепку H4b (онлайн-кооп владельцу недоступен, поэтому снять реальный join нельзя).
Совместил кэшированную декомпиляцию FC3_106 с новыми живыми чтениями. Добавил три RPC во
`scripts/fc3_h3_trace.js` + команды в `scripts/fc3_h3_run.py`: `mmFields`/`mmf` (читает поля
менеджера режимов, по которым идёт путь перехода), `loadCoop`/`loadcoop dry|go` (пишет отложенную
цель, затем вызывает загрузчик напрямую), `netgate`/`ng` (читает гейт доступности co-op).
`scripts/ghidra/DecompTransition.java` перечисляет CALL-перекрёстные ссылки трёх функций перехода.

Топология вызовов (статика, FC3_106):

- `FUN_10fa1990` = **modeManager->vtable[+0x0C]** (подтверждено: единственная xref — DATA-слот по
  `0x1200e604` = первичный втабл `0x1200e5f8` + 0x0C). Прямых CALL-перекрёстных ссылок нет -> вызывается
  чисто через диспетчеризацию втаблицы. Он считает ссылки `(param_2, param_3)`, вызывает
  `FUN_11340d00(piVar4, piVar5)`, вызывает `vtable[+0x50](&local_10)` (который и даёт id цели
  `iStack_14`, по которому идут ветки), затем гейтит всю настройку CO-OP/PvP условием
  `*(char*)(DAT_12804acc + 0x6c) != 0` (**байт «сессия доступна» для co-op/netplay**). Для
  `iStack_14 == 0x43521e6f` (CO-OP) читает строку дескриптора по `param_3 + 0x0C` и логирует
  `"Coop_Fenrir_Loading"`; соседние id логируют `"PvP_Dom_Loading"` и т.д.
- `FUN_11340d00` = **драйвер постановки в очередь** (единственный вызывающий загрузчик).
  `if (*(char*)(this + 0x19) == 0)` (гейт «переход уже идёт») -> `FUN_113409d0(this, &this[0x48], piVar2,
  piVar3)`; затем ставит `this[0x70] = 1`. **ОТЛОЖЕННЫЙ ЦЕЛЕВОЙ ID РЕЖИМА лежит в `modeManager + 0x48`**
  (передаётся загрузчику по адресу). Также стоит как втабличный слот по `0x11f910cc`.
- `FUN_113409d0` = **сам загрузчик** (единственный CALL-вызывающий — `FUN_11340d00`). Читает id цели
  через `iVar2 = *param_2` (то есть `[this + 0x48]`); сохраняет дескриптор в `this + 0x90`
  (`param_1 + 0x24`, здесь `param_1` — `int*`, поэтому смещение умножается на 4); если id входит в
  `{0xAB4FC8E2, 0x43521e6f (CO-OP), 0x9991DAEC, 0x6c2b3868, 0xF66FFB87, 0x2100CED7}`, ставит байт-флаг
  «загрузка» по `this + 0x44` (`*(undefined1*)(param_1 + 0x11)`) и логирует
  `"UI\Multiplayer\Textures\Menu\Loading\Worlds\"`. **CO-OP-ветка привязана к `[this+0x48]`, а не к
  аргументу.** (Следите за разницей `int*` против сырых байтов: в `FUN_11340d00` `param_1` — сырой
  `int`, поэтому `+0x19`/`+0x70` — сырые байтовые смещения; в `FUN_113409d0` `param_1` — `int*`, поэтому
  `+0x11`/`+0x24` у декомпилятора это байты `0x44`/`0x90`.)

Живые результаты (оффлайн `farcry3.exe`, менеджер найден `scanmmv` по втаблице `0x1200e5f8`):

- `mmf` на живом менеджере (`this = 0x29256950`): `pending48 = 0x83ae70ef` (= `cur4c`) -> подтверждает,
  что `+0x48` и есть поле цели; байт гейта «переход идёт» `+0x19 = 0` (открыт); удерживаемый дескриптор
  по `+0x90 = 0x78de4500`. `loadcoop dry` находит живой реестровыйco-op-элемент `0x10253d00`.
- `netgate`: **`DAT_12804acc + 0x6c = 0x1` — гейт «сессия co-op доступна» ОТКРЫТ оффлайн.** Это
  ОПРОВЕРГАЕТ прежнюю догадку, что оффлайн-гейт блокирует co-op-ветку. Хэндл `+0x68 = 0x1033ca00`.
- `loadcoop go`: записать `this+0x48 = 0x43521e6f`, затем вызвать загрузчик `FUN_113409d0(this,
  &this+0x48, descriptor, 0)` из треды Frida. Игра ВЫЖИВАЕТ (без краша), `[this+0x48]` остаётся CO-OP, но
  текущий режим `[this+0x4c]` остаётся `0x83ae70ef` — режим НЕ переключается. (Frida x86 отвергает строку
  abi `'cdecl'`; опускайте аргумент abi, чтобы получить cdecl-семантику.)

Вывод: вся подсистема смены режима на месте и её CO-OP-путь статически достижим (гейт открыт, co-op-элемент
реестра существует, у загрузчика есть CO-OP-ветка по `[this+0x48]`). Но вызов обработчика (`vtable+0x0C`)
или загрузчика напрямую из треды Frida выполняет лишь учёт и ставит флаг «загрузка»; реальная подготовка
мира/сессии происходит позже на главном треде игры и требует настоящего **объекта co-op-сессии**, который
создаёт только netplay-join. Одними id/полями этот оффлайн не подделать. **Истинный оставшийся блокер —
слой netplay/сессии, а не id режима или гейт поля.** Следующая зацепка (если брать): сконструировать /
пред-заполнить объект co-op-сессии, который ждёт шаг загрузчика на главном треде — гораздо более глубокая
работа в netplay-коде, на критическом пути любой оффлайн-попытки 4-игрока.

## Сессия 9 (2026-11-09): сетевой объект сессии, который потребляет загрузчик — вердикт о возможности собрать офлайн (агент-сессия, офлайн Ghidra FC3_106 + живой Frida)

Запрос владельца (2026-11-09): проследить, какой объект netplay/сессии потребляет шаг загрузчика на
главном треде после `this+0x48 = CO-OP`, найти его конструктор, поля и место создания при
netplay-join; определить, можно ли сконструировать/пред-заполнить его офлайн.

Метод: переиспользование офлайн-проекта Ghidra `FC3_106` (`python -I H:\FarCryCoop\scratch\ghidra\scripts\run_headless.py <Script>.java <лог>`, ~30 с, без повторного анализа). Новые скрипты в `H:\FarCryCoop\scratch\ghidra\scripts\`: `DecompSession.java` (декомпилирует хелперы гейта сессии) и `DecompSession2.java` (писатель слота сессии + читатель на пути перехода). Декомпиляции в `H:\FarCryCoop\scratch\ghidra\out\decomp_session.txt`, `decomp_session2*.log`.

### Цепочка, которая потребляет объект сессии (RVA 1.06, thiscall this = менеджер режимов, если не указано иное)
- `FUN_113409d0(this, &this+0x48, desc, p4)` = загрузчик. Читает `*(&this+0x48)` = ожидаемый id режима. Если он из шести (в т.ч. CO-OP `0x43521e6f`) — ставит флаг загрузки `this+0x44=1` и строит UI `Loading\Worlds\`, затем вызывает `FUN_117872f0()` и **поиск по хеш-карте `FUN_103a2d50(&out, &pending)`**. Настоящая отправка происходит только **если `out != 0 && *(out+0x10) != 0`** -> `(*(this->vtable+0x60))(&pending, &p4, &desc, 1)`; иначе уходит на **офлайн/локальный путь `FUN_113400f0`** (вызывающие `FUN_113400f0` — только `FUN_113409d0` и диспетчер `FUN_11340560`).
- `FUN_103a2d50(this, out_pair, key)` = зонд хеш-карты: `this+0x8` = число корзин, `this+0xC` = массив корзин; `hash(key) = (key ^ 0xdeadbeef)` свёрнутый через `ldiv(.., 0x1f31d)`; идёт по цепочке, сравнивая `node+0x08/+0x0C` с ключом; при попадании возвращает ноду, значение которой по `+0x10` должно быть не-null для реальной отправки. Это вторая структура, заполняемая netplay.
- `FUN_10fa1990(this, &id, desc)` = обработчик смены режима (`vtable+0x0C` менеджера). После постановки в очередь читает **активную сессию** `iVar2 = FUN_103a9ea0(*(DAT_12804acc+0x68))`; ветка CO-OP дополнительно требует `iVar2+0x1c в {DAT_1216ca90, DAT_1216ca9c}` и `iVar2+0x8c != -1 && iVar2+0x90 != -1` (id хоста, id участника), затем вызывает `FUN_111854f0(iVar2+0x8c, iVar2+0x90)` и `FUN_110252d0(iVar2, &stack)`. Пишет лог `"Coop_Fenrir_Loading"`.
- `FUN_103a9ea0(container)` = поиск АКТИВНОЙ netplay-сессии: `container` — объект в `DAT_12804acc+0x68`; его массив сессий в `container+0x8`, число в `container+0xC` (кэшированный курсор `DAT_1217a7e8` ускоряет обход); для каждого элемента `e` вызывает `e->vtable[+0x04]()` -> инфо-структуру; элемент активен, когда `info+0x4 > 3` **и** `info+0x14 == FUN_103a9c70()+0x14`. `FUN_103a9c70()` возвращает лениво инициализируемый синглтон сервиса (`&DAT_128611f8`, инициализация через `FUN_1025f040`, помечен «CFCXMusicService») — сравнение это сверка идентичности сессии и сервиса.
- `FUN_111854f0(sessionMgr, hostId, memberId)` = настраивает ко-оп сессию на синглтоне менеджера сессий (трогает `+0x800=hostId`, `+0x340` текущий хост с проверкой `vtable+0x14c` через `DAT_12805200`, `+0x348` список участников, строится через `FUN_1146ad50` и виртуальные аддеры у `(+0x348)->vtable+0x74`).
- `FUN_110252d0(game, out)` = читает **ростер игроков объекта ко-оп-игры**: `+0x50`/`+0x54` = два индекса слотов игроков (`-1` = пусто), `+0x70` = массив игроков (шаг `0x1c`), `+0x74` = число; для каждого слота разрешает указатель игрока и вызывает `FUN_10041e00` (предикат «игрок присутствует») и возвращает 1, когда слот разрешился. Этот объект — заполненная мультиплеерная игра, а не локальная заглушка.

### Где создаётся контейнер сессий
У `DAT_12804acc+0x68` ровно ОДИН писатель: **`FUN_10044000`**. Он получает объект из
фабрики/пула (`FUN_1177f7c0()`, когда `DAT_12162beb` выставлен, иначе `FUN_118db560()`); если фабрика
вернула null — пишет `0` в слот и выходит; иначе ставит объекту vtable `&PTR_FUN_11f3b260`,
обнуляет поля (`+0x4=0`, `+0xC=0`, `+0x14=0`) и ставит `+0x10=5000`, запускает два под-инициализатора
(`FUN_106bee30`, `FUN_106bf2e0`) и устанавливает объект в `DAT_12804acc+0x68`.
То есть **провайдер/менеджер** сессий существует с момента загрузки (под гейтом фабрики, которая
может упасть), а `FUN_103a9ea0` читает его массив/число сессий. Сами **записи** сессий, объект
ко-оп **игры**, слоты участников менеджера ко-оп-сессий и записи хеш-карты `FUN_103a2d50`
заполняются **рукопожатием входа в netplay**, а не каким-либо офлайн/меню-кодом.

### Живое подтверждение (офлайн `farcry3.exe`, DX9, мой собственный прямой запуск)
Добавлены read-only RPC в `scripts/fc3_h3_trace.js` + команды в `scripts/fc3_h3_run.py`:
`sessions`/`sess` (дамп массива/числа контейнера) и ранее добавленный `netgate`. Офлайн байт
доступности `DAT_12804acc+0x6c == 1` (открыт), но список сессий читается как мусор/не задан
(указатель массива `0x2f`), что согласуется с **отсутствием записей сессий офлайн**.

### Вердикт (ответ на вопрос владельца)
- Объект, который потребляет загрузчик, — это **netplay-сессия / объект мультиплеерной игры**,
  достижимый только через провайдера сессий в `DAT_12804acc+0x68` (vtable `PTR_FUN_11f3b260`) и
  хеш-карту `FUN_103a2d50`; реальный экземпляр должен нести сессию с `info+0x4 > 3`, совпадающей
  идентичностью сервиса, ко-оп родом (`DAT_1216ca90`/`DAT_1216ca9c`), валидными id хоста/участника
  (`!= -1`) и объект игры с заполненными слотами игроков с шагом `0x1c`.
- Его контейнер строится при загрузке функцией `FUN_10044000`, но **сами сессии создаются только
  путём входа в netplay**. **Нет локального/меню-аддера, который вставляет сессию офлайн.**
- Значит, объект сессии **нельзя осмысленно пред-заполнить офлайн** записью id/полей: реальная
  отправка загрузчика жёстко привязана к живой netplay-сессии + записи хеш-карты. Офлайн-вход в
  4-игроков ко-оп через манипуляцию id/полями **недостаточен**. Следующий реальный шаг — в **слое
  netplay** (что заполняет массив сессий провайдера при входе), т.е. путь fake-world /
  эмуляции локального сервера из плейбука хаба, а не дальнейшее тыканье полей менеджера режимов.

Ghidra 12.1.4 java-подводные камни снова: `getFunctionContaining` требует `currentProgram.getFunctionManager().getFunctionContaining`, если нет wildcard-импорта `ghidra.program.model.symbol.*`; никогда не вызывать `Long.toHexString` на `Function.getEntryPoint()` (возвращает `Address`, не `Long`) — использовать `Address.toString()`.

## Сессия 10 (2026-11-09): получены два комьюнити co-op-мода, развёрнут vanilla 1.05, первые байтовые диффы (агент-сессия)

Запрос владельца (2026-11-09): в `H:\FarCryCoop\Downloads` владелец положил два разных co-op-мода —
`FarCry 3-OpenWorldCo-op(Patch1.5)` (Nexus mod 220) и `patch_solo_offline_coop_vanilla-262`
(Nexus mod 262) — плюс папку `FarCry3-1.05` (файлы для понижения 1.06 -> 1.05). Просил (a) развернуть
ОТДЕЛЬНУЮ версию 1.05 из копии TestFC3 и (b) продолжить исследование с учётом опыта модов + наших
находок + моих предложений.

### Собрана vanilla-установка 1.05 (отдельная, неразрушающая)

- Собрана `H:\FarCryCoop\TestFC3_105` как **отдельная 1.05-установка** из рабочей 1.06-копии,
  сохранив TestFC3 (1.06) для нашей Frida-работы. Метод (фоновый `robocopy`, лог
  `H:\FarCryCoop\scratch\downgrade_105.log`): копирование TestFC3 -> TestFC3_105 с `/E /XD bin`,
  затем `robocopy H:\FarCryCoop\Downloads\FarCry3-1.05\Bin TestFC3_105\bin /MIR` (bin зеркалится на
  1.05, удаляя 1.06-only `upc_r1_loader.dll`). Игровые данные 1.06 (`data_win32\patch.dat`
  `5a788dd5f7be`, 202 МБ) оставлены без изменений — обновление 1.05->1.06 затрагивает только Bin.
- Проверен чистый vanilla 1.05 в TestFC3_105\bin: `farcry3.exe` md5 `3cf63ffd73d7`,
  `farcry3_d3d11.exe` `df7fc8a341ce`, `FC3.dll` `5ff045331557` (29 994 856 Б),
  `FC3_d3d11.dll` `46bcc0975905` (30 057 832 Б), `uplay_r1_loader.dll` `8313de5eb4f4`,
  `ubiorbitapi_r2_loader.dll` `ba6015e566c9`. 19 файлов в bin. `upc_r1_loader.dll` (1.06) удалён.
- ЗАМЕТКА: 1.06 `FC3.dll` = 40 720 424 Б против 1.05 29 994 856 Б — существенно другой бинарник,
  поэтому наша 1.06 Ghidra-карта (сессия 8/9) напрямую НЕ переносится; для анализа 1.05/модов надо
  собрать Ghidra-проект `FC3_105`.

### Что это за моды (по их README + хешам бинарей)

- **solo_offline_coop (mod 262, v1.01, «based on version 1.05v2»):** позволяет одному игроку запускать
  и играть **одному в режиме Co-op** (Private Session, Public Session, а после обновления 1.01 и
  Local Session), офлайн, DX9 и DX11. Ставится заменой `bin\FC3.dll` + `FC3_d3d11.dll` (бэкап
  оригиналов) и требует «The Dependencies» = `ubiorbitapi_r2_loader.dll` + `uplay_r1_loader.dll` в
  bin и `uplay_r14.dll` в папке Ubisoft Connect. По LAN — нельзя. Другие клиенты МОГУТ подключиться.
  Только стандартный набор оружия. Автор говорит, что co-op-режим «полагается на специфический файл,
  который есть только в легитимной копии игры, даже когда мод работает офлайн» — т.е. компоненты
  сессий orbit/Uplay.
- **OpenWorldCo-op (mod 220, Patch 1.5):** total-conversion открытый мир в co-op. Установка =
  скопировать всю папку «Far Cry 3» (bin FC3.dll + `data_win32\patch.dat/patch.fat`, 3.38 ГБ) поверх
  игры. Одиночная игра + ванильные co-op-карты недоступны при установленном моде. Играть: создать
  **приватную co-op-сессию из главного меню** и выставить главу **«ROOK ISLANDS» / «fc3_main»**.

### Где на самом деле co-op-патч (сравнение хешей бинарей)

- `FC3.dll` md5: vanilla 1.05 `5ff045331557`; **solo262 `5ff045331557` = ИДЕНТИЧЕН vanilla** (solo
  НЕ патчит FC3.dll); **OpenWorld220 `927a1a30c51d` = патченый 1.05** (тот же размер, точечные правки).
- `FC3_d3d11.dll`: vanilla `46bcc0975905`; solo262 идентичен; OpenWorld220 `07abaf666a6d` патчен.
- `uplay_r1_loader.dll`: vanilla 1.05 `8313de5eb4f4`; **ОБА мода `dacd14c07775`** (тот же размер
  294 400). Байтовый дифф (`H:\FarCryCoop\scratch\loader_uplay_r1_diff.txt`): отличается **ровно ОДНИМ
  байтом** на файловом смещении `0x3B030` (`00` -> `34` = ASCII '4'), прямо перед строками имён
  экспорта `UPLAY_Init` / `UPLAY_Startup...`. То есть лодер-шим — тонкий хук-лодер; реальный
  офлайн-эммулятор co-op — **`uplay_r14.dll`** (4 808 512 Б, md5 `6c75cb01cef6`), лежащий в корне
  мода и ОТСУТСТВУЮЩИЙ в ванильном 1.05 Bin и в TestFC3 — это должен быть шим Uplay-API,
  подделывающий co-op-сессию, чтобы игра запускала co-op офлайн. **Этот файл — главная следующая
  RE-цель.**
- `ubiorbitapi_r2_loader.dll` байт-идентичен vanilla во всех наборах (`ba6015e566c9`) — это просто
  легитимная «зависимость», не патчена.

### Карта патчей FC3.dll OpenWorldCo-op (дифф vanilla 1.05 vs OpenWorld220, файловые смещения)

Полный дифф: `H:\FarCryCoop\scratch\fc3_openworld_vs_105_diff.txt` (100 отличающихся байт, 27 групп).
Существенные правки:
- **Переопределение карты/главы на `0x15345D0`:** строка карты по умолчанию для co-op-сессии
  `mpdlc1_aegir` (ванильная co-op DLC-карта) заменена на **`fc3_main`** (одиночный открытый мир). Это
  ядро мода — co-op идёт по миру кампании (совпадает с readme «fc3_main»).
- **Два хука NOP-5 -> CALL** (внедрение кода в существующий поток): на `0x8C406B`
  `90 90 90 90 90` -> `e8 99 fe ff ff` (call rel -0x167) и на `0x8C5036` `90*5` -> `e8 ce ee ff ff`
  (call rel -0x1332). Стоят в 5-байтовой выравнивающей паузе внутри функций (после пролог `55 8b ec`)
  и перенаправляют в существующие рутины — движковые co-op-внедрения.
- **~20 float-констант тюнинга** (совпадает с changelog «Reduced entity streaming radius»,
  «Decreased AI health»): напр. `0x15343B0` (блок 64 Б из double/float), `0x14F2A30`, `0x1535D59`,
  `0x155239C`, `0x1552618`, `0x1552AB8` (значения спавна/стриминга/радиуса переписаны).
- **Пачка порчи первых букв строк `F`/`C` -> `X`** (`FOV`->`XOV`, `Coop`->`Xoop`, `CRadio`->`XRadio` на
  `0x151BFAD`, `0x15D6620`, `0x1569A18`, ...): моддер переименовал строки ресурсов/UI, чтобы некоторые
  фичи/поиски ассетов падали — используется для отключения ванильного co-op-only UI/фич.

### Стратегический вывод / следующие шаги

Оба мода доказывают, что офлайн co-op на **1.05** достижим: solo262 целиком на **слое
лодер-шима** (`uplay_r14.dll` подделывает сессию, FC3.dll не тронут), OpenWorld220 дополнительно
**движковыми патчами** (переопределение карты `fc3_main` + NOP->CALL хуки + тюнинг). Наш блокер
netplay-объекта сессии на 1.06 (сессия 9) — ровно то, что `uplay_r14.dll` обходит. Дальше: (1)
собрать Ghidra `FC3_105` и найти `mpdlc1_aegir`/строку сессии и места вызова лодера; (2)
реверс-инжинирить `uplay_r14.dll` (офлайн-эммулятор co-op) — какие API сессий Uplay/orbit он
заглушает; (3) проверить, запустив `TestFC3_105\bin\farcry3.exe` (офлайн напрямую, наш метод),
опционально с набором лодеров solo262 для повтора solo-offline co-op, затем проектировать
расширение на 4 игроков. Все пути — только офлайн / рабочие копии (золотое правило 2 AGENTS).


## Сессия 11 (2026-11-09): копия 1.05 запускается офлайн; набор лодеров solo262 ставится чисто

Цель: проверить, что новая ванильная рабочая копия 1.05
`H:\FarCryCoop\TestFC3_105\bin\farcry3.exe` запускается офлайн прямым методом
(`DETACHED_PROCESS` 0x8, cwd = `bin`), затем временно поставить набор лодеров из
`patch_solo_offline_coop_vanilla-262` и проверить, что игра по-прежнему стартует, — чтобы
подготовить воспроизведение solo-offline co-op. Сначала бэкапы; только офлайн; только TestFC3_105.

Бэкапы: `H:\FarCryCoop\TestFC3_105\bin_backup_vanilla105\` хранит пять оригинальных файлов
(`FC3.dll`, `FC3_d3d11.dll`, `uplay_r1_loader.dll`, `ubiorbitapi_r2_loader.dll`, `farcry3.exe`);
восстановление — скопировать их обратно в `bin\`.

Тест-харнес: `H:\FarCryCoop\scratch\fc3_win.py <tag> <bindir> [keep]` (убивает запущенный
`farcry3.exe`, стартует DETACHED с cwd=bin, каждые 5с в течение 50с ищет видимое окно с
заголовком, содержащим «Far Cry», размером >= 120x120, по желанию делает скриншот, затем убивает
игру, если не задан `keep`). Скриншоты делаются через PowerShell-хелпер
`H:\FarCryCoop\scratch\shot.ps1` (System.Drawing), потому что Pillow не установлен.

### Находка A — ванильная 1.05 стартует офлайн (прямой метод)

`farcry3.exe` — маленький лаунчер-стаб: запущенный нами процесс выходит с rc=0 примерно за 5с, но
при этом перезапускает настоящую игру соседним процессом. Окно `Far Cry(R) 3` 1920x1080
присутствует примерно с 10с и дальше на 50с+ (подтверждено перечислением окон), процесс жив на
50с. Работают шесть процессов-помощников `UplayWebCore.exe` (веб-ядро Ubisoft Connect). Вывод:
сборка 1.05 действительно запускается офлайн до главного окна; прошлый вывод для 1.06 «окна нет,
выход rc=0» был артефактом харнеса, следившего за неверным (стабовым) PID. Значит, наш прямой
метод запуска работает и на копии 1.05.

### Находка B — набор лодеров solo262 ставится, и игра по-прежнему стартует

В `TestFC3_105\bin` установлены: `uplay_r1_loader.dll` -> пропатченный md5 `dacd14c07775` (из
`Far Cry 3\bin\uplay_r1_loader.dll`) и `uplay_r14.dll` md5 `6c75cb01cef6` (4808512 Б, эмулятор
соло-кооп, из корня мода). Два других лодера в bin уже верные (`ubiorbitapi_r2_loader.dll` =
`ba6015e566c9`, совпадает с зависимостями мода); `FC3.dll` и `FC3_d3d11.dll` оставлены ванильными,
потому что соло-мод их не патчит. С этими двумя файлами `farcry3.exe` снова стартует в окно
`Far Cry(R) 3` 1920x1080 и жив как минимум 50с — замена лодеров не ломает запуск. По README мода
`uplay_r14.dll` обычно кладётся рядом с лаунчером Ubisoft Connect; для прямого запуска достаточно
положить его в `bin` игры (порядок поиска DLL). Замена лодеров по-прежнему временная; ванильные
версии восстанавливаются из `bin_backup_vanilla105`.

### Пока не проверено — вход в соло-кооп сессию

То, что игровое меню теперь ведёт в соло-кооп сессию (Play -> Co-op -> Private Session -> Start),
— ручное действие в меню, которое харнес выполнить не может (полноэкранный режим, нет PIL, нельзя
надёжно слать ввод в полноэкранную exclusive-игру, не побеспокоив живой рабочий стол владельца).
Запуск с лодерами и стабильность процесса зелёные; фактический вход в сессию требует одного
ручного прогона на экране владельца. Это ближайший шаг воспроизведения, и он на стороне владельца.


### Сессия 13 (2026-11-09, агент) — механизм офлайн-запуска, junction и полная установка solo262 на копию 1.05

Цель: заставить рабочую копию реально запускаться и воспроизвести solo-офлайн-кооп мода `patch_solo_offline_coop_vanilla-262` (nexus 262), который прошлые сессии запустить не могли. Владелец разрешил и запись на диск C:, и понижение до 1.05 («Разрешаю оба шага», 2026-11-09).

Почему копия «никогда не запускалась» (корень, подтверждён Frida): `bin\farcry3.exe` (203 816 байт) и `farcry3_d3d11.exe` — это **заглушки-лаунчеры** Ubisoft Connect, а не игра. Настоящий движок — `FC3.dll`, который грузит `uplay_r1.dll` / `upc_r1_loader.dll` внутри живого процесса Ubisoft Connect (`C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\upc.exe`). Прямой `Popen` заглушки копии поднимает **настоящую** установку, т.к. лаунчер выбирает игру по собственной базе (ключ реестра InstallDir читает только `FC3Updater.exe`, а не upc), и перепривязка реестра (даже с правами админа) путь запуска **не** меняет.

Метод junction (единственный рабочий и обратимый): направить NTFS junction `H:\Uplay\Far Cry 3` на копию — тогда кнопка Play в upc запускает копию, а лаунчер всё ещё видит зарегистрированный путь. Скрипты (`H:\FarCryCoop\scratch\`): `use_copy_junction.bat` (админ; убивает игру/лаунчер; `ren` настоящей папки в `Far Cry 3.OFFICIAL` — только метаданные, данные не двигаются; `mklink /J "H:\Uplay\Far Cry 3" "H:\FarCryCoop\TestFC3_105"`), `undo_junction.bat` (проверка `fsutil reparsepoint query`, `rmdir` только ссылки, никогда цели, обратный `ren`). Проверено: после junction + Play в upc путь главного модуля живого `farcry3.exe` = `H:\FarCryCoop\TestFC3_105\bin\farcry3.exe`.

Solo262 нужен 1.05, не 1.06: на 1.06 `farcry3.exe` грузит `uplay_r1.dll` напрямую и никогда не грузит шим `bin\uplay_r1_loader.dll`, поэтому до `uplay_r14.dll` дело не доходит (в README мода: «в последней версии эти файлы убрали»). Итоговое состояние `H:\FarCryCoop\TestFC3_105` (все md5 сверены с пакетом мода): `bin\FC3.dll` 5ff045331557, `bin\FC3_d3d11.dll` 46bcc0975905, `bin\uplay_r1_loader.dll` dacd14c07775, `bin\ubiorbitapi_r2_loader.dll` ba6015e566c9, `bin\uplay_r14.dll` 6c75cb01cef6, `data_win32\patch.dat` 212 002 032 байта (md5 157f2d7682a5, источник==назначение; значение 8797f53343a3 из более ранних заметок — это sha256[:16], а не md5), `data_win32\patch.fat` md5 850412635760. Шаг на C: — `uplay_r14.dll` (6c75cb01cef6) в папку лаунчера — требует прав администратора (прямое копирование даёт PermissionError 13); в папке лаунчера иначе лежат `uplay_r1.dll` 577501e23fa4 и т.п., а `uplay_r14.dll` **не** было, так что добавление чисто аддитивно. Скрипты: `install_uplay_r14_launcher.bat` (админ, аддитивное копирование, откат = удалить этот файл) и `uninstall_solo262.bat` (админ; удаляет файл на C: + 3 DLL-зависимости в bin и восстанавливает `FC3.dll`/`FC3_d3d11.dll`/`patch.dat`/`patch.fat` из `TestFC3_105\_backup_106_before_solo262\` — бэкап до-модового 1.06; md5 FC3 5742de2aaa76, FC3_d3d11 916c6d4b876d, patch.dat 5a788dd5f7be, patch.fat c829e677c352).

Разведка `uplay_r14.dll` (офлайн Ghidra, проект `FC3_uplayr14`, `DumpImportsExports.java` → `out\uplayr14_imports.txt`, 505 совпавших строк): это **полный внутрипроцессный эмулятор SDK Uplay/orbit** — встроенные пути Jenkins это `...\client\products\uplay_r1\src\Uplay\*.cpp`, а наружу он отдаёт всю поверхность UPLAY_*, которую импортирует игра: `UPLAY_Startup/Start/Init`, `UPLAY_USER_GetTicketUtf8/GetProfile/SetGameSession/ClearGameSession`, `UPLAY_FRIENDS_*` (IsFriend/GetFriendList/InviteToGame… «InviteToGame: Game session must be set before inviting to game»), `UPLAY_CHAT_Init`, `UPLAY_PARTY_Init`, `UPLAY_SetGameSession`, плюс имена IPC-каналов `uplay_ipc_pipe_`, `uplay_api_process_ipc_pipe_`, `orbit_orbit_pipe_name`. Вывод: этот DLL подменяет бэкенд Ubisoft локальной фейковой платформой (каналы + заглушки) — ровно тот шаг «эмулировать сетевой слой», к которому вёл вывод офлайн-H4b (сессия 9). Объект co-op-сессии игры наполняется этими вызовами UPLAY_*; для соло эмулятор возвращает сессию из одного игрока. Расширение до четырёх реальных пиров — настоящая цель проекта (сетевой слой, хабовские `fake-world-testing`/`networking`). Процедура живого теста — в `docs/solo-coop-test.md` / `docs/solo-coop-test.ru.md`.


### Сессия 13b (2026-11-09, агент) — РУБЕЖ: офлайн соло-кооп подтверждён рабочим на копии

Владелец выполнил шаг от администратора (`install_uplay_r14_launcher.bat` -> `uplay_r14.dll` в папку лаунчера Ubisoft Connect), запустил через Ubisoft Connect по junction и сообщил дословно (2026-11-09): «ЗАпустил соло кооп он работает». То есть полный офлайн-путь соло-коопа теперь воспроизведён от начала до конца на `H:\FarCryCoop\TestFC3_105` (1.05 + набор лоадеров solo262), что подтверждает установку сессии 13 и механизм запуска сессий 11/13 (заглушка-лаунчер -> junction -> Play в upc -> `uplay_r1_loader.dll` -> `uplay_r14.dll`, фейковая платформа Uplay/orbit).

Значение для цели кооп-кампании: офлайн-путь коопа доказан; разрыв до 4-игроковой КАМПАНИЙНОЙ кооп-игры теперь точно в двух вещах: (а) карта — solo262 запускает штатную кооп-карту (он не патчит `mpdlc1_aegir`->`fc3_main`, как это делает OpenWorld220), и (б) реальные игроки — `uplay_r14.dll` возвращает сессию из одного игрока, поэтому друзья не могут подключиться; расширение этого эмулятора на несколько реальных пиров — конкретная следующая работа (сетевой слой, хабовские `fake-world-testing`/`networking`). Критический путь H6 шаг 3 в PLAN — СДЕЛАН.


### Сессия 14 (2026-11-09, агент) — H7a: селектор кооп-карты найден и пропатчен на кампанийный мир

Цель: заставить кооп-сессию грузить одиночный кампанийный мир вместо штатного кооп-острова той же однострочной правкой, что делает мод OpenWorld220. Офлайн-сканирование нашего ванильного 1.05 `FC3.dll` (`H:\FarCryCoop\TestFC3_105\bin\FC3.dll`, md5 `5ff045331557…`, 29 994 856 байт) подтвердило: строка стартового кооп-мира `mpdlc1_aegir` лежит по **смещению файла `0x15345D0`** — ровно то смещение, что показал дифф OpenWorld220. Соседние байты: `mpdlc1_aegir` (12 символов) + 6 нулей, затем `80 40` (число) и строка `NetObject`, то есть поле имени шириной 12 и с null-терминатором. Вторая, несвязанная кооп-строка `mpdlc1_idun` находится в `0x15A2568` (в списке "Loading / COOP_Sleipner") — не тронута. Идентификатор кампанийного мира `fc3_main` встречается ещё в 8 местах (например `worlds/fc3_main/fc3_main.dat`), но селектор старта коопа — это `0x15345D0`.

Патч: перезаписать 12 байт по `0x15345D0` на `fc3_main\0\0\0\0` (та же ширина, чистый null-терминатор). Написан инструмент `scripts/h7a_coopmap_patch.py` (подкоманды `status`/`apply`/`restore`; `apply` сначала пишет резервную копию рядом `FC3.dll.bak_h7a` и убивает игру; `restore` откатывает). Применён к копии: md5 FC3.dll `5ff045331557…` -> `e4516487fd07…`; побайтовый дифф с резервной копией — **ровно 12 байт** (`0x15345D0..0x15345DB`), размер файла не изменился, `mpdlc1_idun` цела. Откат: `python -I scripts\h7a_coopmap_patch.py restore`.

Открытый вопрос для живого теста: `data_win32` копии — это `patch.dat` мода solo262 (212 МБ, на ванильной базе), в нём есть ассеты базового кампанийного мира, поэтому `fc3_main` должен грузиться; но спавн/миссии коопа внутри кампании не гарантированы (OpenWorld220 несёт собственный `data_win32` на 3.38 ГБ и велит ставить главу коопа "ROOK ISLANDS"/`fc3_main`). Далее — владелец запускает копию и заходит в соло-кооп, чтобы проверить, грузится ли кампанийный мир. Если это сломает ранее работавший соло на острове, `restore` его вернёт. Это шаг для одного игрока (пока соло); реальные игроки остаются в H7b.


### Сессия 15 (2026-11-09, агент) — H7a уточнено: кооп грузит «кооп-миссию», а не открытый мир; установлен OpenWorld 1.5

Итог живого теста однострочного патча H7a (владелец): кооп НЕ загрузил открытый кампанийный остров; вместо него стартовала штатная **кооп-миссия**. Диагноз: ванильный кооп — миссийный по своей природе; перемены одной строки мира `mpdlc1_aegir`->`fc3_main` по `0x15345D0` мало — открытый кооп-мир требует полностью пропатченного FC3.dll (два хука `NOP5->CALL` в `0x8C406B`/`0x8C5036` и ~20 тюнинг-констант с плавающей точкой, которые несёт народный мод) плюс модифицированного `fc3_main_vistas.dat`.

Проверка данных: наша копия УЖЕ несёт полный кампанийный мир (`worlds\fc3_main\fc3_main.dat` 3,49 ГБ + все 7 языковых `.dat` + сток-`fc3_main_vistas.dat` 152 МБ) и `multicommon` — то есть рельеф/объекты кампании на месте; не хватало **вист открытого кооп-мира** (мод несёт `fc3_main_vistas.dat` на 3,06 ГБ) и логики пропатченного FC3.dll. Вывод: патч H7a строки — это *селектор* карты, но *поведение* открытого мира — это пропатченный FC3.dll мода + висты, то есть сам мод OpenWorld, а не правка в один байт.

Действие (владелец разрешил добавить эти файлы): установлен OpenWorld Co-op Patch 1.5 (`H:\FarCryCoop\Downloads\FarCry 3-OpenWorldCo-op(Patch1.5)`, nexus 220) поверх тестовой копии `H:\FarCryCoop\TestFC3_105` через `H:\FarCryCoop\scratch\install_openworld.py`. Что легло (md5 после -> до):
- `bin\FC3.dll` `e4516487…`(ручной патч h7a) -> `927a1a30c51d` (модостроение открытого мира)
- `bin\FC3_d3d11.dll` `46bcc097…` -> `07abaf666a6d`
- `bin\uplay_r1_loader.dll` `dacd14c07775`, `bin\ubiorbitapi_r2_loader.dll` `ba6015e566c9` (без изменений — идентичны solo262; OpenWorld 1.5 несёт тот же офлайн-лоадер коопа)
- `data_win32\patch.dat` `96f74843…` -> `90482fbeee7e` (192 МБ мод), `patch.fat` `850412635760` -> `2bae1147067d`
- `data_win32\worlds\fc3_main\fc3_main_vistas.dat` `87151f18…`(152 МБ сток) -> `cb5da2c2d18c` (3,06 ГБ вистов открытого мира мода), `fc3_main_vistas.fat` `a6ebc6e7` -> `858bf128a3c6`

Резервные копии каждого перезаписанного файла в `H:\FarCryCoop\scratch\backup_pre_openworld\` с `manifest.json` (bin FC3/FC3_d3d11/лоадеры, patch.dat `157f2d76`, висты `87151f18`). Откат: вернуть их назад (а `h7a_coopmap_patch.py restore` откатит только FC3.dll со строковым патчем, но не висты/patch.dat). `uplay_r14.dll` остаётся в папке лаунчера (C:) — по-прежнему офлайн-включатель сессий, нужный лоадеру мода. README мода предупреждает, что пока мод стоит, одиночная игра и ванильный коп недоступны (подходит — это выделенный тестовый стенд).

Далее: владелец запускает через upc (связанная копия) -> главное меню -> создать **ЧАСТНУЮ кооп-сессию** -> выставить главу **ROOK ISLANDS / fc3_main** и сообщает, загрузился ли открытый кампанийный мир. Это по-прежнему соло для одного игрока (H7a); реальные игроки остаются в H7b.

### Сессия 16 (2026-11-09, агент) — живой тест OpenWorld 1.5 провалился как и предсказывали; откат к рабочей оффлайн-соло-кооп (остров); H7b становится критическим путём

Живой тест установки OpenWorld 1.5 (сессия 15) владельцем: после интро кооп НЕ загрузил открытый кампанийный остров. Вместо этого появился штатный браузер/миссия кооп, а оффлайн/соло-путь не показал выбор главы «ROOK ISLANDS» (о котором пишет README мода) — нажатие кооп сразу уходило в интро. Диагноз (подтверждает заметку стратегии из сессии 15): OpenWorld Co-op — это **total-conversion под розничную 1.05** (его README требует заменить всю папку `Far Cry 3` включая `data_win32`) и это **онлайн-кооп** мод для реальных друзей Uplay. Поэтому он (а) не работает подкладыванием `patch.dat` + вист + `FC3.dll` на наш **1.06-фундамент** junction-копии (висты открытого мира на 3,06 ГБ пытаются стримиться против несовместимого 1.06 `fc3_main.dat`, поэтому большой мир встаёт), и (б) упомянутый в нём ползунок выбора главы относится к **онлайн**-браузеру кооп-сессий, которого оффлайн/соло-путь (`uplay_r14`) не даёт. Итог: OpenWorld **ортосионален** нашей цели оффлайн-кооп на 4 игроков — это одиночный/онлайн кампанийный кооп, а не оффлайн-движок на 4 игроков.

Откат выполнен агентом (владелец был у консоли; обратимые файловые операции только на `H:`, бэкапы целы, файлы репозитория не тронуты). Из `H:\FarCryCoop\scratch\backup_pre_openworld\` в `H:\FarCryCoop\TestFC3_105` восстановлена базовая конфигурация «до OpenWorld»:
- `bin\FC3.dll` -> `e4516487fd07` (1.05 со строковым H7a-патчем, грузит островной кооп), `bin\FC3_d3d11.dll` -> `46bcc0975905` (ванилла 1.05).
- `data_win32\patch.dat` -> размер 212002032 (до OpenWorld), `patch.fat` восстановлен.
- `data_win32\worlds\fc3_main\fc3_main_vistas.dat` -> **152925506 (родная виста 1.06, 152 МБ)**; мод OpenWorld заменил её на ~3,06 ГБ. Путь висты внутри копии — `data_win32\worlds\fc3_main\fc3_main_vistas.dat` (не в топ-уровне `worlds\`). `fc3_main_vistas.fat` восстановлен.
- лодеры solo262 в `bin` (`uplay_r1_loader.dll` `dacd14c07775`, `ubiorbitapi_r2_loader.dll` `ba6015e566c9`) и `uplay_r14.dll` (папка лоадера на C: + bin копии) оставлены — это рабочий оффлайн-движок кооп.

Итак `TestFC3_105` снова в состоянии: **1.06-фундамент + оффлайн-лодеры solo262 + остров**, то есть милесто сессии 13b. Владелец перезапустил и подтвердил (2026-11-09): «Перезапустил игру после откатa — островной соло-кооп снова заводится как раньше». Оффлайн-соло-кооп на острове снова воспроизведён.

Решение: понизить приоритет ветки «кампанийный мир через OpenWorld» — чтобы реально погонять открытый мир OpenWorld, нужна **полноценная установка 1.05** как фундамент (есть в `H:\FarCryCoop\Downloads\FarCry3-1.05`: 1.05 `bin` + 34 ГБ данных, `fc3_main.dat` = 1.05 `5879957b`, `patch.dat` 212002032), а это отдельный большой заход и всё равно одиночный/онлайн кооп. Настоящий путь к цели проекта (оффлайн-кампанийный кооп на 4 игроков) — **H7b**: на этом же острове, где оффлайн-кооп уже загружается, расширить эмулятор Uplay/orbit из `uplay_r14.dll` (его `UPLAY_USER_SetGameSession`, `UPLAY_FRIENDS_*`, `UPLAY_CHAT/PARTY_Init`, локальные IPC-каналы `uplay_ipc_pipe_`/`uplay_api_process_ipc_pipe_`), чтобы он сводил несколько реальных локальных игроков вместо сессии «только я» (по хабовым `fake-world-testing`/`networking`). Далее: начать H7b — разобрать поверхность сессий/FRIENDS/IPC в `uplay_r14`, чтобы понять, куда присоединяется второй игрок.

### Сессии 17–18 (2026-11-09, агент) — попытки многоплеера H7b (OpenWorld — только онлайн)

H7b (настоящий второй игрок в офлайн-коопе) проверяли установкой мода **OpenWorld Co-op 1.5** и чтением его устройства. Вывод: OpenWorld — это **тотал-конверсия кооператива на розничной 1.05, только онлайн**, для настоящих друзей в Uplay; это одиночный/онлайн-кооп кампании, ортогональный нашей цели «4 игрока офлайн». Пути к офлайн-мультиплееру там нет. (Подробности — в памяти проекта.)

### Сессия 19 (2026-11-09, агент) — офлайн-кооп грузит одну из **9 жёстко заданных миссий**; остров не является стартовым миром

- **Офлайн-кооп = штатный набор DLC-миссий на двоих, зашитый в код.** 9 выбираемых кооп-уровней (`coop_freyja / coop_loki / coop_idun / coop_sifr / coop_aldrið / coop_vidar / coop_natti / coop_einbyi / coop_aegir`) заданы **статическим массивом из 9 фиксированных строк `char[24]`** в FC3.dll (в FC3.dll 1.06 = solo262 найдено в `.rdata` `0x1860920`..`0x1860A50`). `FUN_10042060` читает `session+0x54` (это **индекс** слота сессии, не id мира) и ищет имя по этой таблице через `FUN_10039e10`. Загрузчик `FUN_113400f0` берёт `session+0x10` (текущая строка мира) как грузимый мир. Таблицы-«пикера» кооп-уровней, управляемой данными, в FC3.dll **нет** — 9 имён это фиксированный пул; 5 DLC-ных (`coop_aldrið/natti/einbyi/vidar/aegir`) берутся из `patch.dat`, 4 (`freyja/loki/sifr/idun`) из `common.dat`.
- **Острова (`fc3_main`) в этом пуле нет** → офлайн-кооп не может стартовать там. `fc3_main` встречается в `patch.dat` 60 раз (обычный одиночный мир), но отсутствует в таблице старта кооператива. «Глава → ROOK ISLANDS» из README OpenWorld — это собственная кастомная функция его онлайн-кооператива (его FC3.dll), **не** опция solo262.
- **Причина регресса меню в офлайн-соло — `patch.dat`.** Бисект «главное меню не грузится с гибридом»: офлайн-соло-меню требует **SOLO262 patch.dat** (212 002 032 Б); patch.dat от OpenWorld (207 817 304 Б) уводит игру в онлайн и вешает меню, хотя uplay_r14 пишет «NetworkManager initialized successfully». FC3.dll на зависание не влияет (соло patch.dat + FC3.dll H7a/OpenWorld грузятся оба). Значит две аварии не пересекаются: **patch.dat → офлайн-меню; FC3.dll+depload → мир-остров.**
- **H7a (строчный патч острова)**: в FC3.dll стартовый мир кооператива читается из фиксированной строковой ячейки (`0x1860a80`, `mov ecx,imm32;call FUN_113400f0`; 24-байтная строка по `0x1860aa8`). Патч `"coop_freyja"→"fc3_main"` заставляет загрузчик запросить `fc3_main` — грузится до 83 % и игра входит в **играбельное состояние (идёт смена времени суток)**, но это **не отрисованный открытый мир** (интро-оверлей миссии/волн, а не остров). То есть H7a = запуск в играбельное состояние, но не настоящий остров.

### Сессия 20 (2026-11-09, агент) — работа с `patch.dat` (Gibbed.Dunia2) + дифф; настоящий критический путь — **слой хоста сессии**

- Владелец дал набор инструментов **Gibbed.Dunia2** в `H:\FarCryCoop\Downloads\dunia2-r178_b113` (github.com/gibbed/Gibbed.Dunia2). `bin\Gibbed.Dunia2.Unpack.exe --ns -v <patch.fat> <out>` работает на этом ПК (.NET есть); `Pack.exe` пакует обратно; `ConvertBinaryObject.exe` делает bobj↔xml; LZO через `lzo_32/64.dll`. `patch.dat/.fat` = большой файл «Domino» от Ubisoft (магик `-- {\v/} Domino `). Распакованы оба: соло → `scratch\patch_top` (431 файл), OpenWorld → `scratch\patch_ow_top` (3316 файлов).
- **Дифф (OpenWorld против соло)**: +2910 файлов только у OpenWorld (в основном `__unknown\game\*.fcb`, `__unknown\scripts\*.lua`, `__unknown\gfx\*.xbt`, `__unknown\misc\*.profile.xml`). Изменено: `worlds\fc3_main\generated\fc3_main_depload.dat` **1 353 370 → 2 923 685 Б** (OpenWorld почти удваивает загрузку зависимостей острова = его кооп-сущности, главный подозреваемый по регистрации острова); `generated\nomadobjecttemplates.fcb` 2,6 МБ → 1,04 МБ; все `domino\library\sp\lib_defend.outpost_{easy,med,hard,nowave}_core2_*.lua` сжимаются ~46–60 КБ → ~18 161 Б (переписаны библиотеки целей кооп-миссий); среди соло-only файлов — `ui\multiplayer\menu\multimain.feu` и 136 МБ `ui\multiplayer\video\fc3coopintro.bik` (OpenWorld приносит свои/удаляет их).
- **ГЛАВНЫЙ ВЫВОД — причина «только онлайн» у OpenWorld это НЕ конфиг-файл.** Поиск по ключевым словам во всех `__unknown\scripts` OpenWorld (`uplay/online/session/host/steam`) **пуст**. OpenWorld уводит в онлайн потому, что остров-кооп запускается через **нативный путь хоста многопользовательской UPLAY-сессии** игры; `uplay_r14` подделывает эту сессию лишь ровно настолько, чтобы войти в **одиночную/офлайн кооп-миссию**, но не чтобы хостить настоящую кооп-игру с игроками. Поэтому **остров с друзьями (B) и второй игрок (H7b) — это ОДНА И ТА ЖЕ задача**: научить фейковую офлайн-сессию хостить настоящую кооп-игру. **Слой хоста сессии — единственный критический путь.** Дальше: реверс нативного кооп-хоста → инициализации UPLAY-сессии (FC3.dll) и того, где `uplay_r14.dll` подделывает её для соло, чтобы найти точку офлайн-хоста.


## Сессия 22 (агент, 2026-11-09) — стена офлайн-хоста сведена к входу в Rv GameSession

Ghidra FC3_106 только на чтение + статический трассировщик лоадеров (supermemory `Cz8Ja9zSjzAEGHfJi4K1xq`,
`nvjxCfpQn79eavDMBirw1P`, `chzyBsC2o83CHAcLdYT3Uu`, `KcD1dL5WTEUN7f5fUd4hYA`; артефакты
`H:\FarCryCoop\scratch\ghidra\out\party106\{strs.txt,deep.txt,final2.txt}`,
`local\scratch\out\{fc3_party_glue.txt,fc3_rv_strings.txt}`).

- Хост кооп-игры — это нативный путь группы Uplay + RendezVous GameSession. Контроллер группы FC3
  вызывает `UPLAY_PARTY_*` (RVA 1.05; якорь игровой сессии 1.06 — `DAT_12805180`). Игра проверяет
  **список участников Rv GameSession** (`E_SESSION_ERROR_RENDEZVOUS_GAMESESSION_*`:
  `HOSTORPARTICIPANTREQUIRED`, `PARTICIPANTNOTCONNECTED`, `HOSTPRIVILEGEREQUIRED`,
  `E_SESSION_ERROR_PARTY_NOT_HOST`), а не только список Uplay.
- Достоверный список участников кооп = внутренний массив провайдера, строит его `FUN_11273650`: число
  в `provider+0x38`, база массива в `provider+0x3c`, каждый элемент 0x20 байт, id участника в элементе
  по `+0x14`. Гейт входа `FUN_11218480` сверяет это же число. Геттер провайдера `FUN_103660e0`
  возвращает провайдер, только если тип группы `> 2` и id группы `== DAT_1285fe3c`. Проверка
  хоста/лидера: `FUN_1006f990() == *(session + 0x120)`. `MaxPartySize` — конфиг-переменная по
  смещению `0xa88`.
- Вывод: подделка массива участников провайдера даёт одноместный-экземпляр-со-многими-слотами (соло/
  тесты/ИИ-подобные доп. слоты). Два живых человека офлайн по-прежнему требуют, чтобы второй экземпляр
  ВОШЁЛ в живую Rv GameSession (`CJoinGameSessionParam` `FUN_10207af0`); loopback/UDP Rv-вход пока не
  найден. Эта плоскость данных и остаётся твёрдой стеной для «остров с друзьями» / офлайн 2-4.


### Дополнение к сессии 22 — вердикт по транспорту: сетевой слой коопы самого движка привязан к сервису (офлайн-входа нет)

Независимый скан строк/API `uplay_r14.dll` 1.05 (`H:\FarCryCoop\TestFC3_105\bin`, 4 808 512 Б) и
полный проход Ghidra сходятся: **в сетевом стеке игры нет LAN / broadcast / loopback / bind / listen /
Winsock / p2p / relay-транспорта.** Подробности (артефакты
`H:\FarCryCoop\scratch\ghidra\out\rvc2\*.txt`, `rv_transport.txt`, `uplayr14_strings_rv.txt`;
supermemory `ry8sddUUPksVT5PKJv4FZs`):

- У `uplay_r14.dll` нет таблицы экспорта; FC3 привязывает его через `GetProcAddress("OrbitApi_InterfaceRequest")`.
- Все операции GameSession (`CreateSession`/`JoinSession`/`RegisterHost`/`SendChatMessage`/…) — это слоты
  vtable объекта `CGameSessionAPI` (слоты 19/21/25/26/31/33/40/43/54 …), вызываемые через трэнки FC3
  (`RVCreateGameSession` @ 0x10cf6790, `RVJoinGameSession` @ 0x10cf6690, …).
- Rv `SessionFactory.cpp` жёстко ассертит `!_multiplayer->IsStandalone()`; FC3 вызывает `RvInit` в
  `FC3.exe+0x644879` — standalone-сборка валит фабрику сессий.
- Единственный примитив соединения — `connectToNamedPipe` → канал сервиса Orbit/Uplay. Никакого socket
  connect, никакого listen. Сессии привязаны к сервису.
- Следствие: «остров с друзьями» / «офлайн 2-4 живых человека» НЕ достижимы через собственный транспорт
  движка. Что движок поддерживает офлайн — это одноместный экземпляр с многими слотами (подделка
  достоверного массива участников провайдера). Настоящему второму человеку нужен внешний транспорт
  (транспорт B в PLAN): свой слой, заново реализующий рукопожатие Rv `GameSession` /
  `CParty*NetMessage` — это перезапуск сети, а не патч. (Также подтверждает «LAN: нет» от автора solo262.)


## Сессия 23 (2026-11-10): LAN/loopback-обиск коопы FC3 + запуск сессии из командной строки = найден офлайн-путь

Цель (m03668 / m04365): остров с друзьями И офлайн 2-4 живых человека. Реверс FC3.dll 1.06 только на
чтение, офлайн-проект Ghidra `FC3_106`. Это отменяет вердикт сессии 22 «офлайн недостижим транспортом
движка»: тот вердикт смотрел только `uplay_r14.dll` (фронтенд Orbit), а не собственный сетевой код движка
`storm::echo`. Артефакты `H:\FarCryCoop\scratch\ghidra\out\coopnet\{cli_args.txt,lan_cfg.txt,
session_msgs.txt,party_api.txt}`, `...\fc3sock\`, `...\party106\`; supermemory `cLjJUL76bobvfWw9AWxBPF`,
`gpEXomdVhKJWD1TGf5ujJC`, `gX9Fyx5PTBWHhHjBfcGjZn`.

- **Сетевой код самого движка — `storm::echo` (RendezVous), и в нём есть слой LAN + loopback-матчмейкинга.**
  Строки: `storm::echo::lan::BroadcastLanDiscovery2`, `storm::echo::lan::DiscoverSession`.
- LAN-переменные конфигурации регистрируются (большая инициализация `FUN_111f6650` RVA 0x111f6650 через
  `FUN_11ab6ed0(name,ptr,off,0x12)`): `LanMatchmakingReuseAddress` (имя VA 0x11fb7210),
  `LanMatchmakingDiscoveryOnLoopbackEnable` (имя VA 0x11fb72e4; описание «включите, чтобы находить сессии
  только на этой машине»), `LanHostBroadcastPort` (имя VA 0x11f1b2ac), `LanClientBroadcastPort`
  (имя VA 0x11f1b2c4).
- **Запуск сессии из командной строки — штатный**, разбирается в `InitDuniaEngine` @ 0x117a5750
  (RVA 0x17a5750):
  - `-dedicated` (лит. VA 0x11f0e7dc) + переменная `dedicatedConfig` (`FUN_116feea0`; регистрация
    `FUN_11ab6750("dedicatedConfig",0xc,0,3)`) = режим головless-выделенного хоста.
  - лаунчер коопы/быстрого матча `FUN_11a8c440` (RVA 0x1a8c440) + `FUN_11a8c8b0` (RVA 0x1a8c8b0) читают
    через strstr строку команд: `-coop` (VA 0x11fb81fc), `-online` (VA 0x11fb8234), `-ranked` (ставит bool
    в +0x7e конфигурации запуска), `-sessionuid` (VA 0x11fb81e4).
  - режим `-client` ТРЕБУЕТ `-login` И `-ip` — строка ошибки «Missing -login or -ip for -client.». То есть
    движок умеет запускаться **сетевым клиентом прямо на указанный IP хоста**.
  - `-offline` (лит. VA 0x11f37244 RVA 0x1f37244) читает `FUN_10fa07b0` (RVA 0xfa07b0): пропускает
    онлайн-только операцию локализации сессии, а вместе с `-donotloadfrontendworld` — загрузку онлайн
    FRONTEND-мира.
- **Архитектура теперь ясна**: FC3 импортирует весь набор Winsock (43 функции; `WSASocketA` @ 0x10abeb9b,
  `WSASendTo` @ 0x10abed37, `WSARecvFrom` @ 0x10abef04 = сокетный слой неткода). Плоскость данных игры =
  собственный UDP движка; `storm::echo` = LAN/loopback UDP с broadcast-обиском + выделенный хост +
  миграция хоста (`ObjectMigrationMode.SessionHostOnly`); `uplay_r14.dll` (Orbit) = ТОЛЬКО онлайн-
  матчмейкинг / rendezvous / авторизация (именованный канал `connectToNamedPipe`). Партийный слой, который
  FC3 использует для игровой коопы, — это его собственный `CParty*` (Rv), а не Uplay Orbit party API.
- **Синглтоны параметров Rv GameSession** (проверено в `party106/final3.txt` + `party106/strs.txt`,
  FC3_106): геттер-синглтон `CJoinGameSessionParam` = `FUN_10207af0` (возвращает `&DAT_12859564`, флаг
  инициализации `DAT_12859560`), `CCreateGameSessionParam` = `FUN_10208000` (→ `&DAT_12859464`/`DAT_12859460`;
  один из вызывающих — `FUN_11956990`, адрес вызова 119569a3), `CDeleteGameSessionParam` = `FUN_10207b90`
  (вызывающий `FUN_11955f30`). Эти синглтоны возвращают объект-параметр, который передаётся службе Rv
  GameSession. **Тела функций-вызывающих для входа/создания пока НЕ декомпилированы** (все прогоны
  безголового `decompile_session_callers_106.py` упали: неверная папка проекта + PyGhidra в 12.1.4
  не даёт `currentProgram`; файл `callers.txt` не создан). Значит конкретные точки перехвата хоста/входа
  ещё не подтверждены. Следующий проход: Java-скрипт Ghidra под `-noanalysis` (Jython/PyGhidra в 12.1.4
  не связывает `currentProgram`) либо REA MCP по проектам FC3_106 / FC3s105. (Исправление 2026-11-10:
  в черновике здесь фигурировал вызывающий входа `FUN_1188ca20` — этот адрес встречается 0 раз во всех
  реальных артефактах и был ошибочным.)
- **Пересмотренный план офлайн-2-4 (намного легче, чем перезапуск неткода)**: рабочий билд solo262/1.05
  уже загружает FC3 в сессию с правилами коопы офлайн (9 миссий scubrah). Остаток — заставить ВТОРОЙ
  экземпляр найти и подключиться к первому через собственный loopback-LAN-путь движка: выставить
  `LanMatchmakingDiscoveryOnLoopbackEnable=1`, `LanMatchmakingReuseAddress=1`,
  `LanHostBroadcastPort`/`LanClientBroadcastPort`, и либо использовать `-coop` / `-client -ip 127.0.0.1`,
  либо перехватить вызывающих create/join Rv GameSession, чтобы они несли loopback-адрес. Это
  **шим установления сессии** (совпадает с транспортом B в PLAN), а не переписывание протокола.
- **Два открытых блокера** (определяют форму шима):
  1. Проверяет ли вход `storm::echo` сервисный `storm::echo::SessionTicket`
     (`SessionTicketRequestAttachment`, `inEvent::RequestJoinSessionRefId`)? Если плоскость данных принимает
     пира без тикета, шиму нужно подделать только обиск + ростер; если тикет проверяется — шим должен
     подделать или заглушить путь тикета.
  2. Зашифрован/подписан ли полезный груз `WSASendTo`/`WSARecvFrom` (RC4/AES/HMAC/seed)? Сборка Ghidra
     `FC3_105` (`build_105.bat`) генерируется ради прохода строк/ссылок по месту отправки.


### Сессия 24 — декомпилированы тикет storm::echo и LAN-хендшейк входа (проверено, Java-headless FC3_106)

Реальный вывод Java-headless прогона `CoopOfflineV2.java` (делегат `del_mw9rdojr_zz1x`, завершён; артефакты
`H:\FarCryCoop\scratch\ghidra\out\coop_offline_v1\{dumps.txt,dumps2.txt,rvjobs.txt}` и строки
`out\coopnet\*`). Заменяет прежние неподтверждённые утверждения о вызывающем входа и закрывает блокер №1.

- **S5 — поток тикета/входа в сессию это ВНУТРИПРОЦЕССНЫЙ РЕЕСТР СОБЫТИЙ storm::echo, целиком в LAN**
  (каждый обработчик регистрируется через `FUN_1008c600("<имя события>", id)`; 36-байтные функции семейства
  `FUN_1070a910` регистрируют по одному событию):
  `storm::echo::session::inEvent::RequestTicketSessionRefId`, `::AcceptTicketRequest`, `::DistributeTicket`,
  `::RefuseTicketRequest`, `storm::echo::session::internal::inEvent::ReceiveTicketRequest`,
  `::ReceiveAcceptTicketRequest`, `storm::echo::SessionTicketRequestAttachment`, `storm::echo::SessionTicket`,
  `storm::echo::player::inEvent::RequestJoinSessionRefId`, `storm::echo::lan::inEvent::DiscoverSession`,
  `storm::echo::lan::inEvent::internal::BroadcastLanDiscovery2`.
- **Чтение блокера №1 (SessionTicket): СИЛЬНЫЕ свидетельства, что тикет выдаёт ХОСТ, а не сервис.**
  Поток — рукопожатие пир→хост по LAN-каналу событий: `DiscoverSession` → `RequestJoinSessionRefId` →
  `RequestTicket` → на стороне хоста `ReceiveTicketRequest` → `AcceptTicketRequest` → `DistributeTicket`.
  В этом пути нет ни одного символа сервиса/Orbit — корень доверия в storm::echo это хост, поэтому путь
  тикета сам по себе Ubisoft НЕ требует. (Остался один подтверждающий проход: прочитать тела обработчиков
  `DistributeTicket`/`ReceiveTicketRequest`, чтобы доказать, что корень доверия — хост, а не релей, прежде
  чем считать это закрытым.)
- **Протокол — PRUDP (подтверждено)**: насос сокетов `FUN_10ac3340` (размер 865) отправляет через
  `FUN_10abec30`, принимает через `FUN_10abedb0` (оба берут структуру-дескриптор сокета), транспорт помечен
  литералом `prudp:/` (`FUN_10ad7190("prudp:/")`). PRUDP = слой надёжности Ubisoft поверх UDP, т.е. плоскость
  данных это PRUDP-over-UDP, а не сырой самодельный UDP.
- **S4 vtable обработчиков результата**: `createResultHandlerTable @ 0x11f57c14`, `joinResultHandlerTable @
  0x11f56dac` — таблицы колбэков исходов create/join, через которые служба GameSession раздаёт результаты;
  это конкретные поверхности перехвата для сессионного шима (лучше, чем геттеры-синглтоны).
- **Крипто неткода (из того же прогона `crypto_probe.py` по сырым байтам FC3.dll)**: нет сигнатур AES/SHA1/
  MD5/SHA256/Blowfish/CRC32c; только таблицы CRC32 (×10), простых чисел xxhash32 (×27), TEA-delta (×2).
  Согласуется с PRUDP (XOR + контрольная сумма Adler, без массового шифра) → груз НЕ шифруется массово, но
  рукопожатие PRUDP всё равно нужно воспроизвести. Блокер №2 переформулирован: вопрос теперь «встроить/быть
  внутри PRUDP», а не «взломать AES».


### Сессия 25 — модуль LAN-матчмейкинга движка СУЩЕСТВУЕТ и настраивается под loopback, но офлайн-поток его не запускает (решение по пути транспорта)

LanTrace.java по проанализированному FC3_106 (артефакт `H:\FarCryCoop\scratch\ghidra\out\lantrace\report.txt`;
запуск `H:\FarCryCoop\scratch\ghidra\run_lantrace2.bat`). Прочитан рабочий
`scratch/exp_lan_config/engine/settings/defaultnetworkconfig.xml` (тот самый нетконфиг, что парсит движок):

- Конфиг неткода несёт целый блок **LAN-матчмейкинга**: `OnlineEnginePort=9000`, `OnlineServicePort=9001`,
  `FileTransferHostPort=9002/ClientPort=9003`, `LanHostBroadcastPort=9004`, `LanClientBroadcastPort=9005`,
  `ScanPortStart=9000 ScanPortRange=1000`, `EnableNatTraversal=1`, `SecureSocketEnabled=1`,
  `MainSocketEncrypted=1`, `MaximumPeerCount=25`. Плюс строковые ключи `LanMatchmakingReuseAddress`,
  `LanMatchmakingDiscoveryOnLoopbackEnable` (есть в FC3.dll, но нет в XML по умолчанию → читаются как
  отсутствуют→дефолт).
- `FUN_11733e50` = **регистратор настроек сетевого движка**: регистрирует каждый атрибут
  defaultnetworkconfig.xml (`TimeOutEnabled`, `SecureSocketEnabled`=«Enable network socket security (applied
  when network engine is restarted)», `LanHostBroadcastPort`, `MainSocketEncrypted`, …) через
  `FUN_11ab6ed0(name, offset, descriptor, 0x13)`. `FUN_111f6650` = регистратор **соединений / LAN-матчмейкинга**
  storm::echo (`Connection*TimeoutInMs` + ключи `LanMatchmakingReuseAddress` /
  `LanMatchmakingDiscoveryOnLoopbackEnable`). ⇒ эти LAN-ключи настоящие, парсятся и применяются при старте движка.
- В storm::echo есть LAN-подсистема: строки `lanmanager`, `BroadcastLanDiscovery`,
  `storm::echo::lan::inEvent::DiscoverSession`, `...lan::inEvent::internal::BroadcastLanDiscovery2`.

**Решение — жив ли путь через транспорт движка?** ДА в принципе, и работа — НЕ переписывание транспорта:
- Игра уже поставляет первоклассный модуль LAN-матчмейкинга с поддержкой loopback (порты 9004/9005, ключи
  reuse + loopback-discovery, события LAN-обнаружения). Офлайн он достижим *на уровне неткода*.
- Блокер — это **слой сессии/лобби**, а не транспорт: офлайн-подделка solo262 `uplay_r14` бросает игру в
  «соло»-сессию кооператива только для себя и **без браузера сессий** (собственная заметка владельца
  m03754/m03905). Поэтому `lanmanager` есть, но **не вызывается** — игра не зовёт host-LAN / discover, т.к.
  офлайн-поток вообще не попадает в состояние «хостируемая/входимая» сессия кооператива.
- Значит «2 живых человека офлайн» = задача **запуска сессии / UI** (заставить офлайн-сборку открывать
  хостируемую сессию кооператива + путь обнаружения/входа вместо жёстко заданной сессии «только я»), а НЕ
  задача заново реализовать PRUDP. `SecureSocketEnabled=1` означает, что любой вход идёт через слой защиты
  сокета (нюанс блокера №2) — нужно его рукопожатие, но без массового AES.
- Буквальный живой тест (запустить, открыть LAN-браузер,захостить, второй экземпляр заходит через loopback)
  **сейчас заблокирован**: в офлайн-потоке нет LAN-браузера, через который можно хостить/заходить, пока не
  будет получена хостируемая офлайн-сессия кооператива. Одних ключей loopback/reuse для этого мало.


## Сессия 26 (2026-11-10): полный разбор патчей OpenWorldCoop 1.5 (ревизия по coop-revive, шаги 1-2)

Цель (владелец, m04981): рабочий кооп в **основном мире** **онлайн**. OpenWorldCoop 1.5 — единственная
сборка, которая это умела; по скиллу хаба `coop-revive` проводим ревизию по подсистемам. Артефакты:
`H:\FarCryCoop\scratch\ow_diff\owdiff_{d3d9,d3d11}.json`, `patchdiff.json`; скрипт
`local/scratch/ow_diff.py`; распакованные деревья `H:\FarCryCoop\scratch\ow_extract` (3316 файлов) и
`H:\FarCryCoop\scratch\van_extract` (427, эталонный 1.06 patch.dat md5 5a788dd5f7befada6e6919ec1799c172).

**Нативная часть крошечная (184 байта в FC3.dll; 134 в FC3_d3d11.dll; кода НОЛЬ):**
- 2 хука стриминга: штатные 5-NOP площадки 0x8C306B и 0x8C4036 (в файле 0x8C406B/0x8C5036) заменены
  `E8 rel32` CALL на одну и ту же существующую штатную функцию **RVA 0x8C2F09** (d3d11: 0xA1D1E2/0xA1E1AD
  -> 0xA1D080). Идёт Ghidra-анализ FC3_105_OW (фон, `H:\FarCryCoop\scratch\ghidra\owan.log`) — имя
  функции и контексты площадок.
- строка карты: 0x15341D0 `mpdlc1_aegir` -> `fc3_main` (строка H7a уже в моде).
- тюнинг стриминга/дальностей x4: 256->512, 1536->5120, 2048->5120, 1280->5120, 128->512, 1.29e5->5.13e5,
  0.7708->0.6625, 4.75->5.625; u24 0x49BB80->0x4A9C40 @0x1535959.
- 14 однобайтовых переименований ключей конфигов 'F'/'C'->'X' (0x2799DA.., 0x151BBFF.., 0x15D6220..,
  семейство FOVTime) = выключение штатных поведений отсутствующим ключом.
- 6 однобайтовых увеличений (8->9, 6->7, 7->8) @0x2799DA/9FB/27AA27/48 + 0x59237A/9B.

**Data-часть (patch.dat):** 427 -> 3316 записей; +2859 пересобранных `.fcb`-чанков острова (остров
пересобран под стриминг коопа; depload.dat 1.35МБ->2.92МБ), +53 конфигов/скриптов, 7 ИЗМЕНЁННЫХ lua
аутпостов `lib_defend` (волны), 13 `__unknown/scripts/*.lua` = ещё варианты lib_defend (nowave/hard/med/
easy+dog). Ключевые добавленные файлы: `engine/gamemodes/gamemodesconfig.xml` (FCXCoop @строка 325,
Mask=128; список сервисов; строки fc3_main НЕТ -> выбор карты не здесь),
`engine/settings/defaultnetworkconfig.xml` (**MaximumPeerCount=25**, порты 9000-9005, MainSocketEncrypted=1,
SecureSocketEnabled=1, EmulatorEnabled=1, 20 Мбит), `engine/settings/pc/defaultengineconfig.xml`,
`defaultrenderconfig.xml`, `domino/system/worldloadpause.lua` (спойнер синхронизации SP-эффектов в коопе:
шторм/ветер/регenetnavmesh/зенodiac), `domino/system/coop/allplayers/enableinitialspawn.lua`,
`coop/misc/strayplayerzone_v2.lua`, `system/ai/spawnreinforcement_v4.lua`,
`library/coop/zz_devhelpers._playerloop.lua`, `engine/scripts/game/newbrains/*.ai.rml` (мозги животных),
2 gosm-статемашины игрока, `spbarkmanager.xml`, `inputactionmapcommon.xml`, oasisstrings. Удалено: немного
графики лодок, 2 катсцены, fc3coopintro.bik (триггинг размера, не функция). + fc3_main_vistas.dat 3.06ГБ
(129 894 записей).

**Вывод:** мод = (a) два NOP-площадки в вызов существующей штатной функции стриминга, (b) строка карты
коопа -> fc3_main, (c) константы стриминга x4, (d) пересобранный мир острова (.fcb+vistas) + доделанные
под кооп SP-конфиги/скрипты, (e) лимит пиров 25. Больше ничего. Возрождение = воспроизвести/проверить
(a)-(d), затем починить ОНЛАЙН-д_join (состояние серверов 2026 — вопрос, см. веб-разыскания ранее).


### Сессия 26b (2026-11-10, агент) — ГЛАВНАЯ ПРОВЕРКА: движок 1.05 работает на данных 1.06

Тест в `H:\FarCryCoop\TestFC3_105` (правило владельца: все проверки из этой папки — upc запускает
ту папку игры, которая настроена у него). Поставил чистый ванильный 1.05 bin (`FC3.dll` 5ff04533,
`farcry3.exe` 202088) + чистый 1.06 `patch.dat` (5a788dd5), пару OW-вест вынес, запуск напрямую
`bin\farcry3.exe` (офлайн, лоадеры uplay_r14 + solo262 оставлены):
- Игра грузит главное меню; появляется закрываемый диалог «Служба Far Cry 3 недоступна»
  (предупреждение о сервисе, не фатально — за ним работает меню).
- С `FC3.dll` = гибрид (md5 341888251150, scratch\FC3_hybrid.dll) меню грузится полностью
  (видны ИГРА / СОВМЕСТНАЯ ИГРА / КОЛЛЕКТИВНАЯ ИГРА; доступен браузер кооператива).
- Навигация клавишами (стрелки+Enter) -> слот «новая игра» -> «ВНИМАНИЕ: в слоте сохранение,
  загрузить?» -> НЕТ -> **мир острова ЗАГРУЗИЛСЯ и рендерится** (начальная сцена, ночные джунгли,
  ракета). fc3_main.dat 1.06 (fea2e5a1) + движок 1.05 = полностью играбельный старт.
- Вынесенное состояние свопа: `H:\FarCryCoop\scratch\swap_105_datatest\` (patch_solo262.dat/fat,
  fc3_main_vistas). Откат = вернуть на место.

Следствия:
- Полный стек OpenWorldCoop (OW FC3.dll = 1.05 + 184 байта патча, OW patch.dat, OW vistas) может
  работать в этой папке без барьера совместимости движка и данных: совместимость доказана.
- Далее: офлайн-регрессия (гибрид + solo262 patch.dat + vistas -> локальный кооп на острове), затем
  установка OW-стека для попытки ОНЛАЙН-коопа в основном мире через настоящий upc.

> **Поправка (та же сессия, позже).** Тест 26b шёл на патч-архиве **1.05** (192 307 217 Б;
> хеш 5a788dd5 = ванильный 1.05, сверено с `Downloads\OW15\game\data_win32`), а НЕ на 1.06,
> как сначала. Архив мира `worlds\fc3_main\fc3_main.dat` — действительно **1.06** (fea2e5a1,
> 3 496 061 837 Б, сверено с установкой Uplay), пара вест — OW-2020 (cb5da2c2, 3,0 ГБ). То есть
> итог в существенном остаётся: **движок 1.05 + архив мира fc3_main из 1.06 + весты OW = остров
> грузится и рендерит.** (Какой FC3.dll был в `bin` в этом запуске — ванильный 5ff04533 или гибрид
> 341888251150 — не зафиксирован; FC3_d3d11.dll, которую грузит `farcry3_d3d11.exe`, была патченная
> solo262 46bcc097.)

### Сессия 26c (2026-11-10, агент) — OpenWorld-стек только онлайн; матрица живых запусков

Проверенные md5 факты о файлах:
- `data_win32\patch.dat`: ваниль **1.05 = 192 307 217 Б** (5a788dd5), патч мода 262 =
  212 002 032 Б (157f2d76), патч **OpenWorld Patch 1.5 = 90482fbe** (тот же размер, другой
  содержимое), ваниль **1.06 = 202 132 751 Б** (в `_backup_106_before_solo262`).
- `FC3.dll` OpenWorld (927a1a30) отличается от ванили 1.05 (5ff04533) всего **~100 байтами**:
  косметические переименования строк (`FOV`->`XOV`, `CoopNameplates`->`XoopNameplates`), куски
  float-констант и ОДНА содержательная подмена строки: `mpdlc1_aegir` -> `fc3_main` на файловом
  смещении `0x15345d0`. **В бинарном патче OW нет никакого обхода сервисов** — онлайн-сервисы
  Ubisoft (party/Rv) жёстко требуются.

Матрица живых запусков (папка `TestFC3_105`, запуск прямо `bin\farcry3.exe`):
- данные solo262 (157f2d76) + гибрид FC3.dll + fc3_main 1.06 + весты 1.06: меню грузится
  (диалог о сервисе закрывается), в меню кооператива видны три пункта (ИГРА ОНЛАЙН /
  ВМЕСТЕ ВЕ СЕТИ [зелёная подсветка = офлайн-кооп пункт] / ВСТУПИТЕЛЬНЫЙ РОЛИК), но **ни один не
  реагирует на Enter или клик** в этом состоянии данных (FC3.log сессии на C: не найден).
- данные solo262 + ванильный 1.05 FC3.dll 5ff04533 + FC3_d3d11 solo262 46bcc097: меню грузится.
- стек OW (927a1a30/07abaf66 + 90482fbe): **фатальный диалог «Служба Far Cry 3 недоступна.
  Перезапустите игру.»** — и напрямую, и через `uplay://launch/46/0` при только что перезапущенном
  **онлайн** Ubisoft Connect: сервис самой игры (Rv/party) реально мёртв на стороне серверов;
  онлайна upc мало.
- командная строка хоста 1.05 `-host fc3_main -login tester -coop` (прямой запуск, данные solo262):
  **фатальный диалог про сервис** — ветка `-host` тоже требует сервисного провайдера, хотя создаёт
  локальный тип сессии 3; тот же exe без флагов грузит меню нормально.

Сошедшийся вывод (третье независимое подтверждение): **единственное препятствие и для офлайн-коопа,
и для любого онлайна — склейка party/сессий сервиса в orbit-API `uplay_r14`.** Следующий шаг —
внутрипроцессный эмулятор orbit-API (`uplay_r14` грузится в процесс, FC3 привязывает его через
`GetProcAddress("OrbitApi_InterfaceRequest")` — лоадер под нашим контролем): подделать список
party (2-4 слота), `IsPartyLeader=true` и успех создания/входа GameSession локальным типом 3.
Опоры: артефакты сессии 24 `CoopOfflineV2.java` + `local/scratch/multislot_design.md` +
доказательство 100-байтного диффа выше.

Состояние `TestFC3_105` после сессии: данные solo262 (157f2d76) + весты OW cb5da2c2 +
FC3.dll = ваниль 1.05 5ff04533 + FC3_d3d11 = solo262 46bcc097. Гибрид FC3.dll сохранён в
`H:\FarCryCoop\scratch\swap_105_datatest\solo262_state\FC3_hybrid.dll`; стек OW —
`Downloads\OW15\game` (см. `swap_105_datatest\ow_state\README.txt`).


## Сессия 27 (2026-11-10): собран прокси orbit-API uplay_r1_loader + проверена прозрачность проброса; сборка сделана воспроизводимой

Продолжение вывода сессии 26c: единственный блокер — это склейка сервисов пати/сессий Ubisoft в orbit-API
(`uplay_r14`/`uplay_r1_loader`). Первый инженерный шаг: прокси-логгер на пробросе, оборачивающий настоящий
лодер и записывающий каждый вызов orbit, который делает FC3, — чтобы перед подделкой наблюдать поверхность
host/join. Исходники `src/uplay_proxy/{uplay_proxy.cpp,uplay_proxy.def,proxytest.c,build.bat,build_x86.bat}`;
генератор `scripts/gen_uplay_proxy.py` (строит таблицу из 58 thunk-экспортов и `.def`). Артефакты — в `local/scratch/`.

- **Замысел.** `uplay_r1_loader.dll` (x86) экспортирует 58 cdecl-функций `UPLAY_*` как «нагие» thunk-пробрасыватели
  стека (`th_0..th_57`). В `DllMain` он грузит настоящий лодер из `<bindir>\real\uplay_r1_loader.dll`
  (`LOAD_WITH_ALTERED_SEARCH_PATH`), находит его экспорты по именам и для каждого thunk ставит проброс + запись
  в лог (номер, метка времени, 8 стековых аргументов, вызывающий `модуль!+RVA`, возвращаемое значение). FC3
  связан именно с лодером, поэтому DLL — прозрачная наблюдаемая надстройка. Установлен в
  `H:\FarCryCoop\TestFC3_105\bin\uplay_r1_loader.dll`; настоящий лежит в `...\bin\real\uplay_r1_loader.dll` (294400 Б).
- **Прозрачность проброса проверена в игре.** Офлайн-загрузка solo262: `uplay_api.log` показывает `real=<base>
  exports=58 missing=0`, и до меню игра обращается ровно к двум функциям orbit — `UPLAY_Init`
  (`FC3_d3d11.dll+0x420a2d`, ret=1) и `UPLAY_PARTY_Init` (`FC3_d3d11.dll+0x77d52f`, ret=1). Обе вернули
  настоящее значение сквозь прокси ⇒ путь проброса прозрачен в живой игре.
- **Прозрачность проверена отдельно.** `proxytest.c` (x86-консоль) грузит прокси напрямую и вызывает
  `UPLAY_USER_IsConnected / UPLAY_Init / UPLAY_Poll / UPLAY_PARTY_*`; прокси пишет в лог `real=<base> exports=58
  missing=0` и пробрасывает каждый вызов настоящему лодеру. (Настоящий лодер, загруженный *без* прокси,
  порождает рабочие треды orbit/сервиса, которые переживают `main`, поэтому зонд настоящего лодера зависает и
  должен запускаться отязанным.)
- **Сборка сделана воспроизводимой.** `build.bat` / `build_x86.bat` вызывали `vcvars64.bat` (причём
  `build_x86.bat` передавал `-arch_host=x64 -arch=x86`, что `vcvars64` в VS18 игнорирует → окружение не
  выставляется). Оба теперь используют `vcvars32.bat` (правильная 32-битная цепочка для цели
  `/MACHINE:X86 /DWIN32`). Свежий запуск `build.bat` воспроизводит развёрнутый прокси **побайтово**
  (SHA-1 `153e016e…`, `machine 0x14c`, 58 экспортов) — то есть дерево действительно является источником
  рабочего шима.
- **Метки вызывающих.** Логгер размечает известные RE-сайты: RVCreateGameSession (`FC3.dll+0x00cf6790`),
  RVJoinGameSession (`FC3.dll+0x00cf6690`), область party-склейки (диапазон RVA `0x10620400..0x10623500` в
  `FC3.dll`) и `FUN_113409d0` лодера. Они срабатывают только когда игра реально пытается host/join.
- **Прочтение и следующий шаг.** Трассировка загрузки из двух вызовов orbit третьим способом подтверждает блокер
  26c: офлайн-поток никогда не доходит до хостопригодной/вступаемой кооп-сессии, поэтому `UPLAY_PARTY_GetFullMemberList`,
  `UPLAY_PARTY_IsPartyLeader`, `UPLAY_SetGameSession` или RVCreate/RVJoinGameSession так и не появляются. Прокси
  теперь — надёжный наблюдатель; дальше нужно довести игру до пути host/join (двигать кооп-UI или детурнить
  вызовы сессии в FC3) и затем в этом же прокси подделывать список пати из 2–4 слотов,
  `UPLAY_PARTY_IsPartyLeader=true` и успех создания/входа GameSession по локальному типу сессии 3.


## Сессия 28 (2026-11-11): прокси orbit-API получает гейт-фейлы по переменной окружения; починены регрессии генератора

Продолжение сессии 27. Цель: перевести прокси orbit-API с чистого наблюдения к первому безопасному *фейлу*,
чтобы проверить гипотезу 26c (кооп-меню мертво, потому что гейты пати/онлайна читают мёртвый сервис Ubisoft).
Артефакты: `src/uplay_proxy/{uplay_proxy.cpp,uplay_proxy.def}` (перегенерированы), `scripts/probe_orbit_gates.py`,
`scripts/gen_uplay_proxy.py`.

- **Сначала проверка ABI (`probe_orbit_gates.py`).** В настоящем `bin\real\uplay_r1_loader.dll` экспорты-гейты
  (`UPLAY_USER_IsConnected`, `UPLAY_PARTY_IsInParty`, `UPLAY_PARTY_IsPartyLeader`, геттеры списков участников,
  `UPLAY_PARTY_Init`) — все 5-байтовые `jmp`-трюки в двухуровневой таблице-заглушке (сам лодер форвардит
  реализацию orbit/сервиса через именованный канал). Значит bool-гейты — это `int(void)` cdecl, возвращающие
  значение сервиса; с мёртвым сервисом они возвращают FALSE — ровно то, что выключает кооп-меню.
- **Фейл добавлен безопасно по ABI и под флагом.** `gen_uplay_proxy.py` теперь печатает таблицу
  `g_fakeval[NEXP]` по экспортам и флаг `g_fake` из `getenv("FC3COOP_FAKE_PARTY")`. В `apiThunk` фейк-слот
  короткозамыкает (`if (fk) r = fk; else if (real) {проброс}`) и пишет строку лога с суффиксом ` [FAKE]`.
  Принудительно в 1 ставятся только три bool-гейта без аргументов (`IsConnected`, `IsPartyLeader`, `IsInParty`);
  вызовы списков участников / `SetGameSession` остаются **проброшенными** (их фейк требует раскладки структуры
  списка участников — риск падения, отложено). По умолчанию (без env) — побайтово чистый проброс поведения сессии 27.
- **Починены три латентные регрессии генератора (важно).** Закоммиченный `gen_uplay_proxy.py` больше не
  воспроизводил закоммиченный `uplay_proxy.cpp`: он строил три строки формата `fprintf` и четыре строки-тега
  вызывающего через `qh(chr(34)+FMT)[:-1]`, что теряет последний символ формата и выдаёт сломанный `\"...%`
  (без закрывающей кавычки), а путь к `real` печатал как `strcpy(s+1, "real" BSB "uplay_r1_loader.dll")`, где
  `BSB` — переменная `char[]`, а не литерал (не компилируется). Регенерация теперь портила эти строки. Исправлено
  на `chr(34)+FMT+chr(34)` и обратно на `sprintf(s+1,"real%suplay_r1_loader.dll",BSB)`. С выключенными фейками
  перегенерированный cpp снова идентичен HEAD, поэтому fake-сборка заслуживает доверия; `build.bat`/`build_x86.bat`
  используют `vcvars32` (починено в сессии 27), `cl` выходит с кодом 0 (только предупреждения C4996).
- **Собрано и развёрнуто.** Свежий x86-прокси `machine 0x14c`, 58 экспортов, `sha1 2de99a7e…`, установлен в
  `H:\FarCryCoop\TestFC3_105\bin\uplay_r1_loader.dll` (по умолчанию фейл выкл; настоящий лодер остался в
  `bin\real\`). Строка лога `proxy up:` теперь пишет `fake=%d`.
- **Открыто (проверка в рантайме).** Зависит ли от того, вызывает ли офлайн-игра гейт-функции (и оживает ли
  кооп-меню host/join при принуждении их в 1), требует живого прогона с `FC3COOP_FAKE_PARTY=1`. Стенд `proxytest.c`
  не доказывает это сам по себе: загрузка настоящего лодера порождает рабочие треды orbit/сервиса, которые
  переживают `main`, поэтому стенд виснет и должен запускаться отсоединённо с kill-по-таймауту. Живая загрузка
  зовёт только `UPLAY_Init`+`UPLAY_PARTY_Init`; гейты срабатывают при навигации в кооп-меню. Отложено на следующий шаг.
- **Решение по транспорту зафиксировано.** Для FC3 транспорт — это собственный `storm::echo` LAN/loopback игры
  (опция скилла coop-networking «the engine's own netcode»), а НЕ Steam-релей Spacewar (AppID 480): FC3 в рантайме
  не Steam-игра (`нет steam_api.dll`, идёт через лодер Ubisoft Connect), а релей лишь мостит сессию, которую игра
  должна сначала открыть — а это и есть проблема session-glue, слоем ниже. HXCoop-релей остаётся задокументированной
  опцией фазы 2 (через интернет).


### Сессия 28b (тот же день) — дополнение по рантайму: механизм фейла ДОКАЗАН; живая навигация по меню — за владельцем

- **Путь фейла проверен в рантайме** (proxytest, `FC3COOP_FAKE_PARTY=1`): `UPLAY_USER_IsConnected` пишет
  `[FAKE] ret=1 (0x1)` (гейт короткозамкнут), а `UPLAY_Init` проброшен нормально (`ret=0`, без `[FAKE]`).
  То есть `g_fakeval` + `g_fake` + маркер лога `[FAKE]` работают; прежний «завис» proxytest был лишь из-за
  рабочих тредов orbit/сервиса настоящего лодера, переживающих `main` после возврата фейла, а не из-за фейл-пути.
- **Прямой запуск игры с `fake=1` доходит до лодера, но не до меню.** Запуск `bin\farcry3.exe` с переменной:
  стаб пере-исполняется в `farcry3_d3d11.exe`, прокси цепляется `fake=1`, трасса загрузки обычная — только
  `UPLAY_Init` + `UPLAY_PARTY_Init`, — но окно не создаётся (прямой запуск не завершает DRM/Uplay-рукопожатие
  без потока `upc Play` + junction из сессии 13b), поэтому водить нечего, а гейт-функции (срабатывают при
  навигации в кооп-меню) не вызываются. Процесс затем собран; осиротевших процессов не осталось.
- **Что это оставляет владельцу (проверка самой гипотезы).** Запустить рабочий интерактивный boot
  (`upc Play` через junction на `TestFC3_105`) с выставленной для процесса игры переменной `FC3COOP_FAKE_PARTY=1`,
  затем открыть подменю коопа и попробовать host/join. Следить в `bin\uplay_api.log`: гейты теперь должны писать
  `[FAKE] ret=1`, и открытый вопрос — оживут ли ранее мёртвые кооп-пункты (`ВМЕСТЕ ВЕ СЕТИ`). Если да, следующий
  фейл для добавления — список участников + успех `SetGameSession` (нужна раскладка структуры).


### Сессия 28c (тот же день) - потребители orbit-API разобраны: гейт-фейлы валидированы, фейл ростера относится к слою Rv

Статический RE потребителей `uplay_r1_loader.dll` в `FC3_d3d11.dll` (machine 0x14c, база `0x10000000`; пробы
`scripts/probe_memberlist_imports.py` + байтовый скан `call/jmp [IAT]`). FC3 импортирует orbit-API из
`uplay_r1_loader.dll` (блок IAT `0x114aca64..0x114acac8`) и вызывает его через серию трampoline'ов `jmp [IAT]`
в `0x10e5b044..0x10e5b0b6`: `Init` `0x10e5b044`, `IsConnected` `0x10e5b07a`, `SetGameSession` `0x10e5b08c`,
`PARTY_Init` `0x10e5b092`, `GetFullMemberList` `0x10e5b0a4`, `IsPartyLeader` `0x10e5b0b6`.

- **`IsPartyLeader` потребляется как обычный bool** - уже поставленные гейт-фейлы имеют правильную форму.
  Вызывающие: `0x1077ddea` -> `mov byte ptr [esi], al` (сохраняет флаг лидера прямо в байт), и `0x1077e9e7`
  -> `test al,al; je ...; mov byte ptr [ebp-1],1` в UI/state-логику разрешений (далее тест `[edi+0x14] & 2`
  и чтение `[ebx+0x248]`). Значит, принуждение лодера вернуть 1 заставляет FC3 сохранить `leader=true` без
  всяких структур - ABI валидирован у потребителя, а не только предположен.
- **`GetFullMemberList` только проверяется на null, поля не читаются, в FC3.** Его единственный вызывающий
  трampoline `0x1077d6b1` = `test eax,eax; jne <ok>; push 0x11e67ed8 (строка assert); call 0x10e5b080` - трактует
  геттер как «есть ли указатель на список участников» и никогда не итерирует записи участников. Поэтому
  доверенный ростер 2-4, который использует кооп-логика, - это внутренний Rv party controller (Сессия 22:
  `provider+0x38/+0x3c`, `FUN_11273650`), а не Uplay-геттер. **Следствие для плана: фейл «список участников +
  SetGameSession» должен целиться в Rv party controller (S2-детур join-параметров / хук доверенного списка
  участников из PLAN), а не в orbit-лодер.** Фейл `GetFullMemberList` в прокси не подал бы ростер в геймплей.
- Итог: три loader-гейт-фейла (сессии 27-28) имеют правильную форму и являются правильной первой пробой;
  следующая реальная задача (ростер 2-4) - это детур Rv party controller, что совпадает с хук-поинтами сессий 22/24.


### Сессия 28d (тот же день) - зонд Rv party-controller: ростер - это граф объектов сервиса; join-gate - точка детура

Офлайн-дизасм хук-поинтов Rv party/session-контроллера из сессий 22/24 по 1.06 `FC3.dll`
(`H:\Uplay\Far Cry 3\bin\FC3.dll`, md5 `5742de2a`, machine 0x14c, база `0x10000000`, `.text` до `0x11bcac61`;
проба `scripts/probe_rv_party.py`). Это 1.06-адреса (`.text` у 1.05 `FC3.dll` md5 `5ff04533` кончается на
`0x1149d215`, значит `FUN_11273650` есть только в 1.06).

- **`FUN_11273650` (доверенный список участников) обходит граф объектов сервиса, а не плоский массив.** Тело:
  `mov edi,[edx+4]; add edi,0x120; call 0x10070590; cmp eax,edi` (`+0x120` совпадает с заметкой сессии 22
  "хост == session+0x120"), затем цепочка геттеров `[[eax+0x18]+0x20] -> [ecx] -> vtable[+0x2c] -> call eax`,
  дающая объект-участника; далее тест `[ecx+0x64]`, `test byte[edx+0xec],8` и refcount `dec dword[ecx+4]`.
  Вывод: доверенный ростер - это живой граф объектов через геттер `0x10070590` и vtable-слоты, поэтому фейл
  ростера должен populate/детурить этот контроллер, что согласуется с сессией 28c (не лодер).
- **`FUN_11218480` (join-gate) декодируется чисто и является лучшим кандидатом в детур.** Читает `[esi+0x30]`,
  пишет `mov dword[edx],1` (out-параметр истина), строит строковый объект с тегом (vftable `0x11fabf24`) и
  возвращает `al=1` через `ret 0x14`. Это валидатор/акцептор с единственным булевым исходом -> хук,
  возвращающий успех + синтетического участника, и есть конкретная точка join-шим (PLAN S2).
- **`FUN_1006f990` (host test) и `FUN_103660e0` на этом билде по этим адресам не декодируются**
  (`0x1006f990` начинается с одиночного `ret`; `0x103660e0` рассинхрон) -> НЕ доверять этим двум адресам как есть;
  пересчитать их из Ghidra-проекта `FC3_106` (их семантика из сессии 22 может стоять на сдвинутых адресах между
  Ghidra-снимком и md5 `5742de2a`).

Дальше (замысел): строить детур ростера на `FUN_11218480` + геттере объекта-участника `0x10070590`, и сначала
проверить раскладку полей объекта-участника по тому, что потребляет ниже `FUN_11273650`, прежде чем писать фейл.


### Сессия 28e (тот же день) - структура ростера вскрыта: std::map по 64-битному id участника; join-gate виртуальный

Продолжение 28d (`scripts/probe_rv_detour.py`, xref + выровненный дизасм по 1.06 `FC3.dll` md5 `5742de2a`).

- **Доверенный ростер - это `std::map` с 64-битным ключом id участника.** Геттер `0x10070590` идёт по
  красно-чёрному дереву: связи узлов `[node+0x00]`/`[node+0x04]`, младший дабл-word ключа в `[node+0x10]`,
  старший в `[node+0x14]`; при промахе возвращает `edi` (конец карты/`this`). Значит подставить фейковую пати
  2-4 = вставить узлы map по ключу id, а не писать плоский массив. `FUN_11273650` затем читает поля объекта-участника
  через vtable-слот `[+0x2c]`, тестит флаг `byte[+0xec]&8` и `[+0x64]`.
- **Join-gate `FUN_11218480` - виртуальный метод** (0 прямых `call`-xref; кончается `ret 0x14`). Хукать через
  слот vtable, либо через его вызывающих.
- **Блок контроллера роста/входа в кооп - это `~0x11218480..0x112185xx`.** У `FUN_11273650` (trusted list) ровно
  2 вызывающих - `0x11218506` (этот блок) и `0x1127422a` (глубже в контроллере); у `FUN_103660e0` (query участника)
  1 вызывающий - `0x112184dc` (тот же блок). Именно этот блок резолвит пати при host/join.
- **Query участника `FUN_103660e0` привязан к синглтону сервиса** в глобалах `0x12854784` (объект) и `0x1285478c`
  (значение сравнения); вызывает vtable-метод объекта `[+0x4]`, проверяет `[+0x4]==1` и `[+0x8]==0x1285478c`.
  Этот синглтон - сильный якорь детура: заставить/наблюдать его может быть проще, чем патчить map напрямую.
- **`FUN_1006f990` - НЕ host-test в этом билде** - это 1-байтовый `ret`-стаб с 495 вызывающими (тривиальный
  метод по умолчанию). Адрес "host test == session+0x120" из сессии 22 не совпадает с md5 `5742de2a`; реальный
  тест лидера/хоста в другом месте (это `add edi,0x120; call 0x10070590; cmp eax,edi` внутри `FUN_11273650`).
  Пересчитать `FUN_1006f990` перед использованием.

Замысел детура (дальше): либо (a) populate ростер-`std::map` (геттер `0x10070590`, ключ = id участника) +
заставить синглтон `0x12854784` сообщать о членстве, либо (b) детурить блок контроллера `0x11218480..0x112185xx`,
внедряя синтетический ростер 2-4 и форсируя проход join-gate. (b) - меньшая поверхность; обоим нужна раскладка
полей объекта-участника (vtable `+0x2c` / `[+0x64]` / `[+0xec]`) из того, что потребляет ниже `FUN_11273650`.


### Сессия 28f (тот же день) - карта полей party-контроллера: две слот-группы участника + presence-маска; спецификация детура ростера

Продолжение 28e (дизасм хвоста FUN_11273650 и более глубокого вызывающего FUN_1127422a на 1.06 `FC3.dll`).

- **Карта полей party-контроллера (`this` = `ebx`)** (из пути уничтожения в FUN_11273650):
  - две параллельные слот-группы участника: группа A в `+0x30`(ptr) / `+0x34`(byte-флаг, =1) / `+0x38`(контейнер),
    группа B в `+0x54`(ptr) / `+0x58`(byte-флаг) / `+0x5c`(контейнер); каждый контейнер освобождается через
    `0x10116890`; стражи `+0x44`, `+0x68` (не-ноль -> путь освобождения).
  - presence-маска: `[+0x24] & [+0x28]`, сравнение с `-1` (0xFFFFFFFF = «нет участника»).
  - контейнер ростера, который использует предикат пустоты, находится в **`+0x5c`** (вызывающий FUN_1127422a делает
    `cmp ecx,[esi+0x5c]; jb ...`), значит доверенная пати это `+0x5c`, зеркало — `+0x38`.
- **Состояние объекта-участника**: внутренний объект через `[member+0x64]`, флаг состояния `byte[inner+0xec] & 8`
  (булев контроль, который путь входа тестирует перед принятием участника).
- **Спецификация детура ростера (готова к реализации, след. шаг):** populate контейнер `+0x5c` ростера
  (`std::map` по 64-битному id, ключ узла lo/hi `+0x10/+0x14`) 2-4 записями участников, выставить `+0x58`/`+0x54`
  (группа B) и presence-маску `[+0x24]&[+0x28]` в значение не-(-1), и чтобы у каждого участника проходил
  внутренний `byte[+0xec]&8`. Альтернатива с меньшей поверхностью — детур блока контроллера
  `0x11218480..0x112185xx` (join-gate там виртуальный). Синглтон сервиса `0x12854784` (из 28e) — наименее
  инвазивная точка наблюдения.
- Осторожно: все смещения для билда 1.06 md5 `5742de2a`; и ничто из этого не проверяемо без живой игры,
  дошедшей до host/join (интерактивный запуск владельцем `upc Play` с `FC3COOP_FAKE_PARTY=1`), поэтому следующий
  действенный шаг — этот живой прогон, а не новый статический RE.


### Сессия 28g (тот же день) - авторитетный декрип гейта пати; правит 28e/28f (`scripts/ghidra/DecompileParty.java`)

Прогнал настоящий декрипатор Ghidra по проанализированному проекту `FC3_106` (нужно запускать в изолированном
`-scriptPath`: каталог scratch-скриптов содержит устаревшие не-компилирующиеся скрипты, которые отравляют
сборку Java-пакета). Вывод `decomp_party.txt`. Заменяет несколько догадок 28e/28f по capstone на истину.

- **Join-gate `FUN_11218480` (thiscall, this = param_1; тело 0x11218480-0x11218775).** Резолвит менеджер пати
  из **глобального синглтона `DAT_12805180` -> `+4`** (`iVar3`). Гейт проходит только если ВСЁ верно:
  1. `FUN_102000d0(mgr, mgr+0x118, mgr+0x11c) != 0` (проверка онлайна/подключённости менеджера),
  2. `FUN_11216750() == 0` И `FUN_112166f0() == 0` И `FUN_11216690() == 0` (три негативных блока),
  3. `FUN_103660e0() != 0` - и это возвращает объект сервиса пати (значит это **геттер**, а не query).
- **`FUN_103660e0` = геттер сервиса пати** (использует синглтон `0x12854784`; гейт затем читает `+0x74`
  возвращённого менеджера и передаёт его билдеру ростера).
- **Ростер, который ест гейт = vector записей по 0x20 байта**, который строит `FUN_11273650(mgr, &out)`
  (out = {data, end, capacity}); гейт идёт `for p in out шаг 0x20`. Имя/id участника из
  `[mgr + 0x3c + i + 0x14]`; vtable записи - `PTR_FUN_11f57660` и `PTR_FUN_1201fa24`; на запись
  `local_28 = (*[DAT_12805180+4] + 0x274) != 0` - это флаг **локального игрока**. Пустой ростер (`count == 0`)
  уходит в соло-ветку (`FUN_112734a0` + `FUN_112163b0` + `FUN_10366240`).
- **Правки к 28e/28f:** `0x10070590` - НЕ отдельный геттер map - он лежит внутри `FUN_10070470` (рост/realloc
  контейнера). `FUN_1006f990` - НЕ стаб - это RB-tree `lower_bound` по `[this+8]` (внутренний индекс id->участник
  менеджера). Формулировка «заполнять std::map» была неверна на уровне гейта: гейт читает **0x20-байтовый vector
  из `FUN_11273650`**, который строится из `[mgr+0x38]/+0x3c` (таблица участников из неткода), а не из map напрямую.

**Детур-цель переформулирована (авторитетно):** чтобы host/join офлайн показал пати 2-4, выполнить четыре
условия гейта `FUN_11218480` и сделать так, чтобы таблица участников менеджера (`mgr+0x38` счётчик,
`mgr+0x3c + i + 0x14` id) давала 2-4 записи, и тогда `FUN_11273650` выдаст непустой vector. Наименее инвазивная
точка наблюдения - синглтон `DAT_12805180+4` (менеджер). Все адреса 1.06 md5 `5742de2a`. Всё ещё нужна живая игра.


### Сессия 28h (тот же день) - декомпилированы подусловия гейта: два синглтона + машина состояний сессии (`scripts/ghidra/DecompileGate.java`)

Декомпилировал четыре подусловия гейта `FUN_11218480` + соло-хелпер. Закрывает линию статического анализа:
каждое нижележащее условие зависит от рантайм-состояния неткода, поэтому связь фейл-загрузчика↔гейт решаема
только вживую.

- **`FUN_102000d0(mgr, mgr+0x118, mgr+0x11c)` (позитивное условие «подключён»):** требует
  `((mgr+0x118) & (mgr+0x11c)) != 0xffffffff` (валидный id пати присутствует), затем зовёт RB-tree lower_bound
  `FUN_1006f990()`, чтобы найти **узел локального игрока в дереве участников менеджера по `[mgr + 0x120]`**; при
  попадании идёт по vtable `+0x2c` и резолвит участника против **массива лобби `[mgr+0x1ec] / [mgr+0x1f0]`** и
  `+0x98` участника. => Условие выполнимо только когда есть и дерево участников менеджера, и лобби - то есть оно
  кормится неткодом, это и есть реальный офлайн-блокер.
- **Три негативных блока читают синглтон сессии/режима `DAT_12804acc`** (`+0x6c` = байт «есть сессия»,
  `+0x68` = объект сессии):
  - `FUN_112166f0()` возвращает `[session + 0x9b8] == -7`;
  - `FUN_11216690()` возвращает `[session + 0x9b8] == -6`;
  - `FUN_11216750()` - обработчик состояния сессии (ветвится по тому же состоянию `DAT_12804acc`).
  Гейту нужно все три ложными => код статуса сессии не -6 и не -7, и объект сессии в нормальном (не ошибочном)
  состоянии.
- **Два управляющих синглтона:** `DAT_12805180 + 4` (сетевой менеджер/пати: дерево участников `[+0x120]`, таблица
  участников `[+0x38]/[+0x3c]`, лобби `[+0x1ec]/[+0x1f0]`, поля id `[+0x118]/[+0x11c]`) и `DAT_12804acc`
  (контроллер режима/сессии: есть-сессия `[+0x6c]`, сессия `[+0x68]`, статус `[session+0x9b8]`).
- **Вывод (терминус статики):** гейт пати - это рантайм-машина состояний сессии. Фейл Orbit SDK-вызовов на уровне
  загрузчика (гейт-фейлы `uplay_proxy`) поможет только если лодер Ubisoft Connect реально переведёт эти два
  синглтона в валидное состояние пати. Статически это не наблюдать; решающий следующий шаг - живой `upc Play` на
  TestFC3_105 с `FC3COOP_FAKE_PARTY=1` с проверкой, берётся ли ветка кооп-меню в `FUN_11218480` (при сборке
  тест-мода поставить брейкпоинты/лог на `DAT_12805180+4` и `DAT_12804acc+0x6c`). Все адреса 1.06 md5 `5742de2a`.


### Сессия 28i (тот же день) - исправлен небезопасный пере-вызов в прокси (баг ABI) -> tail-call; деплой `sha1 e045f054`

Живая попытка `upc Play` уронила `farcry3_d3d11.exe` с **0xc0000005 (access violation), модуль сбоя
"unknown 0.0.0.0", BEX/StackHash_2beb** сразу после `UPLAY_PARTY_Init`; до гейт-фейлов orbit дело не дошло
(ни одного `IsConnected`/`IsPartyLeader` от игры). При перечитывании `gen_uplay_proxy.py` старый `apiThunk`
**пере-вызывал** реальный экспорт с фиксированным 8-аргументным `__cdecl`-прототипом и без сохранения `ecx` —
неверно для любого не-cdecl / thiscall / указательного возврата, что портит вызывающего. Переписал:

- `apiThunk` -> `log_entry(int slot, void** argp, DWORD retaddr)`: только ЧИТАЕТ 8 стек-аргументов под SEH и
  пишет лог; реальную функцию не вызывает.
- Каждый экспорт (все 58, `cdecl`+`others` объединены) — теперь голый thunk: `pushfd; pushad; lea eax,[esp+40];
  mov edx,[esp+36]; push edx; push eax; push slot; call log_entry; add esp,12; popad; popfd;` затем либо
  `mov eax,1; ret` (3 гейт-фейка), либо `mov eax,[g_rawp_i]; jmp eax` — **tail-call, сохраняющий точный стек,
  адрес возврата и регистры вызывающего (включая ecx)**, поэтому реальный экспорт выполняется с побайточно точным ABI.
- Пересобран x86 чисто (только предупреждения C4996), `machine 0x14c`, 58 экспортов, задеплоен в
  `TestFC3_105\bin\uplay_r1_loader.dll` = `sha1 e045f054...`.
- Оговорка: `proxytest.exe` (мусорные аргументы) всё ещё выходит 0xc0000005 через прокси, тогда как прямой реальный
  прогон зависает на сетевом экспорте — харнесс расходится по причинам, не связанным с пробросом (мусорные аргументы +
  ветка fake=1), поэтому он НЕ является чистым индикатором прокси-против-реала. Правка прокси обоснована анализом кода
  и игровым 0xc0000005; окончательный тест — живая игра, сейчас заблокирована (см. ниже).
- **Текущий блокер больше не в коде:** Ubisoft Connect отказывается запускать игру для вошедшего аккаунта
  («не удалось проверить доступ к этой игре»). Игре нужен DRM-рукопожатие UC, чтобы дойти до окна (прямой запуск
  `farcry3.exe` выходит без окна), поэтому эта проверка прав завязывает любой живой тест. Решать владельцу; см.
  процедуру живого теста в NOTES. Личных идентификаторов здесь не записано.


### Сессия 28j (тот же день) - ИСПРАВЛЕНА модель запуска: upc запускает `TestFC3_105` напрямую; метод junction здесь устарел

Поправка владельца (авторитетно, держать в каждой будущей сессии; подтверждено скриншотом upc «Свойства → Установка»: папка установки `H:/FarCryCoop/TestFC3_105/`, «Ваша игра установлена здесь»): **зарегистрированный путь установки Far Cry 3 в Ubisoft Connect на этом ПК — это сам `H:\FarCryCoop\TestFC3_105`** (владелец ранее направил upc на эту папку). Поэтому кнопка Play в upc запускает `H:\FarCryCoop\TestFC3_105\bin\farcry3.exe` НАПРЯМУЮ. Трюк из сессии 13 с junction (зарегистрировать `H:\Uplay\Far Cry 3` и `mklink` на копию) **на этом ПК устарел и неприменим** — он лишь переименовывает реальную установку без пользы и оставляет её осиротевшей (см. ниже). Это корень путаницы в сессиях 28b/28i: игра всегда стартовала из копии; прогоны `fake=1` были настоящими запусками upc, унаследовавшими окружение HKCU, а прямой запуск из helper — это другой путь без окна.

- Следствие для переменной: раз игру запускает **upc** (не helper), переключатель гейт-фейлов должен лежать в HKCU —
  `setx FC3COOP_FAKE_PARTY 1` + полный перезапуск Ubisoft Connect — иначе он не долетит до процесса. Helper,
  выставляющий переменную только своему дочернему процессу, путь через upc не отражает.
- Осиротевшее состояние файловой системы от брошенного junction (проверено): `H:\Uplay\Far Cry 3` ОТСУТСТВУЕТ, а
  реальная установка лежит переименованная в `H:\Uplay\Far Cry 3.OFFICIAL`. Уборка (владелец, админ): запустить
  `undo_junction.bat` — при отсутствии junction он лишь переименует `Far Cry 3.OFFICIAL` обратно в `Far Cry 3`
  (безопасно, копию не трогает). `use_copy_junction.bat` больше НЕ запускать.
- Исправленная процедура живого теста: (1) `undo_junction.bat` (навести порядок, по желанию но рекомендовано);
  (2) `setx FC3COOP_FAKE_PARTY 1`; (3) полностью закрыть Ubisoft Connect (в т.ч. из трея) и открыть заново;
  (4) Play в FC3 — upc запускает копию напрямую, прокси `sha1 e045f054` + фейки активны; (5) дойти до кооп-меню;
  агент затем читает `H:\FarCryCoop\TestFC3_105\bin\uplay_api.log`.
- Если Ubisoft Connect по-прежнему показывает «не удалось проверить доступ к этой игре» — это вопрос аккаунта/прав
  для текущего вошедшего аккаунта (он должен владеть FC3 и быть онлайн) — на стороне владельца, вне работы с модом.


### Сессия 28k (тот же день) - ЖИВАЯ веха: подключение к коопу достигнуто; блокер — РОДНОЙ «сервис FC3», не orbit

Первый полностью стабильный живой прогон копии через прокси (владелец: `setx FC3COOP_FAKE_PARTY 1` + полный
перезапуск UC + Play). Без краша; игра загрузилась и крутила штатный orbit-пульс. Владелец дошёл: главное меню ->
«ИГРА ОНЛАЙН» (кооп) -> серия диалогов (скриншоты):
1. «Вы не подключены к серверам Ubisoft. Хотите попробовать подключить сейчас?» (OK/Отмена)
2. после OK: «Идет подключение к серверам Far Cry 3. Пожалуйста, подождите.»
3. финал: **«ОШИБКА. Служба Far Cry 3 недоступна. Повторите попытку позже.»**

Находки по логу прокси:
- Навигация в кооп поднимала `UPLAY_USER_IsConnected` пачками, наш `[FAKE] ret=1` срабатывал каждый раз — **но игра
  всё равно сообщала «не подключено»**. Значит понимание игрой «подключён к сервису кооперации» НЕ определяется
  булевым orbit `IsConnected`.
- Во время «Идет подключение» в логе асинхронный паттерн `UPLAY_HasOverlappedOperationCompleted` (+
  `GetOverlappedOperationResult`) крутится — игра запустила асинхронную orbit-операцию и опрашивала её.
- На ошибке «Служба недоступна» в логе **ТОЛЬКО** idle-пульс `UPLAY_Update`/`GetNextEvent` — **ни одного** orbit-экспорта
  ошибку не сопровождает. => Соединение с сервисом кооперации Far Cry 3 выполняет собственный сетевой стек игры
  (storm::echo / PRUDP по UDP напрямую к бэкенду кооперации Ubisoft FC3), а НЕ через `uplay_r1_loader`. Тот бэкенд
  отключён, поэтому соединение падает и кооп не открывается.

Вывод / стратегия: прозрачность orbit + булевы фейки верны и доказаны, но покрывают только поверхность orbit API.
Реальный гейт — это родное соединение с сервисом кооперации (и только после его успеха наполняется Rv-менеджер пати
`DAT_12805180+4` / гейт `FUN_11218480`). Два направления, чтобы получить офлайн-кооп:
- (A) Локальный фейковый кооп-сервер: направить эндпоинт кооп-сервиса игры на локальный хост, говорящий достаточно
  storm::echo/PRUDP, чтобы довести рукопожатие пати до «доступно». Нужен эндпоинт (host:port) + трассировка протокола.
- (B) Прошить в `FC3.dll` машину состояний сервиса/соединения игры, чтобы она пропускала/симулировала проверку
  «сервис доступен» и переходила к слою Rv party, а там наполнить менеджер пати (карта 28g-28h).
Оба большие; следующий offline-шаг, полезный для (A) в любом случае, — найти эндпоинт кооп-сервиса, на который звонит игра.
Это подтверждает тезис проекта от начала до конца: блокер кооперации — мёртвый онлайн-сервис, достигнутый родным
неткодом, а не проверки логина orbit.


### Сессия 28l (тот же день) - стек кооп-онлайна в FC3.dll определён: RendezVous + storm::echo + .svc SOAP; флаг CLI `-coop`

Offline-скан строк `FC3.dll` / `FC3_d3d11.dll` (только чтение) обосновывает развилку стратегии из 28k.

- **«Rv» = RendezVous**, онлайн-бэкенд сессий/матчмейкинга Ubisoft. Пути исходников вбиты в бинарь:
  `..\platforms\win32\OnlineSession\RendezVousBackEndServices_native.cpp` и
  `..\platforms\win32\OnlineSession\RendezVousGuestBackEndServices_native.cpp`. Сообщения сессий RendezVous:
  `GameSessionUnsuccessfulJoinSession`, `GameSessionSearchWithParticipantsResult`, `GameSessionInvitationReceived`.
  Это тот же слой, что гейт 28g `FUN_11218480` и RVA загрузчика `RVCreateGameSession`/`RVJoinGameSession` —
  точки входа «RendezVous Create/Join GameSession».
- **Транспорт — `storm::echo`**: `storm::echo::RoutablePacket`, `storm::echo::session_time::...`,
  `storm::echo::simulation::internal::inEvent::CreateCamera`, `CEchoStartupParams`. Подтверждает план «нативный
  storm::echo»; дата-плейн кооперации едет по storm::echo, плоскость лобби/матчмейкинга — по RendezVous.
- **Онлайн-сервисы — HTTP/SOAP**: `/OnlineConfigService.svc/GetOnlineConfig?onlineConfigID=...` и SOAP-конверты
  `<s:Envelope ...soap-envelope...>` — конфиг-сервис WCF `.svc`. Живое «Служба недоступна» (28k) — это
  недостижимость этого RendezVous/config-бэкенда; эндпоинт получается в рантайме (Uplay + OnlineConfig), поэтому
  простого хоста кооперации в DLL нет.
- **Есть CLI-флаги кооперации**: `-coop`, `-coopchallengesettings`, `-firestorm`, `-fromuplay`, `-sessionuid`,
  `-networktimeslice`. Опция запуска `-coop` может форсить кооп-режим; дёшево проверить, но кооп всё равно требует
  сервис, поэтому в одиночку гейт вряд ли обойдёт.
- Объекты геймплея кооперации: `CFCXCompetitiveCoop*`, `CCoopChallengeService`, `CCoopAISpawnerService`,
  `ActivateCoopGate`, `CDominoNetFunc*Coop*` — контент кооп-сессии, когда сессия уже есть.

Чтение стратегии (рекомендация владельцу): направление (B) — проходимое: прошить `RendezVousBackEndServices_native`
/ путь RV Create/Join в `FC3.dll`, чтобы локальный вход сообщался успешным, и наполнить Rv-менеджер пати
(`DAT_12805180+4`, гейт `FUN_11218480`, геттер `FUN_103660e0`), обходя мёртвый бэкенд RendezVous. Направление (A)
(локальный фейк-сервер RendezVous+storm::echo) трудозатратнее, т.к. бэкенд — конфиг-управляемый SOAP + echo.
Следующая offline-работа: найти нативные функции бэкенда RendezVous и код, поднимающий «service unavailable».


### Сессия 28m (тот же день) - FUN_11218480 это ОДОБРЕНИЕ входа в пати (не создание/подключение); бэкенд RendezVous — виртуальный + конфиг-управляемый (`scripts/probe_rv_backend.py`)

Полный декомпилят гейта входа и зонд бэкенда (`scripts/probe_rv_backend.py`) уточняют направление (B).

- **`FUN_11218480` (thiscall) — это ОДОБРЕНИЕ входящих в пати, не создание/подключение сессии.** Сперва охраняется
  `FUN_102000d0(mgr, mgr+0x118, mgr+0x11c)`; затем строит список кандидатов (`FUN_11273650`), считает вошедших,
  прошедших `FUN_1193b8c0`, и ОТКАЗЫВАЕТ (возврат 0) со строками лога "Rejecting partyId: %u; New joiners count: %d
  because the result teams would have a size difference > 2 ..." и "... more than half the max allowed size for the
  current playlist". Когда охрана «подключён» не проходит — просто `return 1` (пустышка). То есть это балансировка
  входящих в УЖЕ подключённой пати; здесь НЕ рождается «Служба недоступна».
- **RV Create/Join зовутся виртуально** — `RVCreateGameSession 0x10cf6790` / `RVJoinGameSession 0x10cf6690`
  (теги describe() лодера, пространство RVA FC3_d3d11) имеют 0 rel32-вызывающих в FC3.dll; идут через vtable (как
  гейт). **Токены RendezVous из строк — это RTTI/имёна шаблонов** (`qlist<GameSession...>`, `ANetObject.LobbyService`),
  а `RendezVousBackEndServices_native.cpp` / `OnlineConfigService.svc` имеют 0 прямых immediate в `.text` ->
  используются косвенно. Значит граф объектов RV-сервиса достигается виртуальными вызовами, а эндпоинт получается в
  рантайме; офлайн-иксрефом по строкам не раскрывается.
- Следствие: точку подъёма «Служба недоступна» и нативные функции RV Create/Join чисто офлайн не закрепить. Два
  пути для направления (B): (1) ЖИВАЯ инструментировка (Frida) на запущенной игре — брейк на объекте сессии
  RendezVous / синглтоне менеджера пати `DAT_12805180+4` и снять точную последовательность подключения+отказа; или
  (2) найти русскую строку диалога в данных локализации -> её ключ -> код, ссылающийся на ключ (= точка подъёма для
  нейтрализации). Оба — новая фаза; offline-фаза orbit+прокси завершена и доказана.


### Сессия 28n (тот же день) - лог прокси теперь глушит idle-пульс (FC3COOP_LOG_PUMP); локализация в упакованных .dat

- Живой лог `uplay_api.log` раздулся до ~95 МБ, потому что писался каждый idle `UPLAY_Update`/`GetNextEvent`
  (~1 Гц каждый). `log_entry` теперь выходит раньше для этих двух имён, если не задан `FC3COOP_LOG_PUMP`, так что
  реальные кооп/пати-вызовы остаются читаемыми. Пересобран x86 чисто (`BUILD_DONE 0`); деплой в ожидании (запущенная
  игра держит `bin\uplay_r1_loader.dll`; закрой `farcry3_d3d11.exe`, чтобы задеплоить преемника `sha1 e045f054`).
- Текст диалога «Служба недоступна» и все UI-строки лежат в упакованных архивах Ubisoft `data_win32\{common,patch,ige}.dat`
  (+ `.fat`), поэтому трассировка «ключ локализации -> точка подъёма» (пункт 28m вариант 2) сначала требует
  распаковщика `.dat/.fat` — новый подсубинструмент. Вместе с виртуальным/конфиг-бэкендом RendezVous это закрывает
  продуктивные OFFLINE-only пути направления (B). Следующий реальный шаг требует либо инструментировать живую игру
  (Frida), либо распаковать упакованные данные.


### Сессия 28o (тот же день) - эндпоинт кооп-сервиса найден через Frida: lb-rdv-as-prod01.ubisoft.com / UDP 11000-11001 (ДОСТУПЕН, отвечает)

Захват `scripts/frida/fc3_coop_trace.py` на живом подключении кооперации (`local/scratch/frida_coop_*.log`):

- **Хост RendezVous:** `gethostbyname("lb-rdv-as-prod01.ubisoft.com")` резолвится (hostent не null). rdv = RendezVous.
- **Игра обменивается UDP с бэкендом:** `sendto -> 203.132.26.108:11000`, `203.132.26.108:11001`,
  `203.132.26.109:11000`, и `recvfrom` возвращает пакеты (4) — бэкенд ОТВЕЧАЕТ. Значит это НЕ мёртвый хост /
  не стена маршрутизации; UDP-рукопожатие storm::echo / PRUDP происходит и получает ответы.
- **Сокеты игры:** `bind 0.0.0.0:3074` (стандартный NAT/live-порт Ubisoft) и `bind 192.168.1.8:9000` (локальный
  порт данных storm::echo на LAN-IP). Повторяющийся `gethostbyname("IT")` = игра резолвит имя локального ПК
  (COMPUTERNAME `IT`) при перечислении интерфейсов — шум, не сервис.
- **Вывод:** «Служба Far Cry 3 недоступна» — это результат прикладного уровня рукопожатия RendezVous (сервер,
  вероятно, всё ещё принимает сокет, но отвергает/депрекейтит тенант/сессии-операции FC3-rendezvous), а НЕ сбой
  достижимости. Рычаг теперь — СОДЕРЖИМОЕ и исход рукопожатия.
- **След. шаг инструмента:** трейсер теперь дампит первые 64 байта (hex) `sendto`/`recvfrom` на rendezvous-портах.
  Повторить захват один раз, чтобы прочитать реальное рукопожатие и отказ сервера -> побайтовый вид позволит и
  (A) локальный фейк RendezVous (проиграть/сфабриковать рукопожатие), и (B) точно найти игровой вызов для нейтрализации.


### Сессия 28p (тот же день) - итог разведки rendezvous: бэкенд жив и отвечает; блокер — прикладной уровень PRUDP/RendezVous

Повторные свежие живые захваты (`frida_coop_*.log`) стабильно показывают инициализацию онлайна в главном меню:
`gethostbyname("lb-rdv-as-prod01.ubisoft.com")` резолвится, игра биндит `0.0.0.0:3074` + `<lan>:9000`
(storm::echo). Реальный UDP-бёрст подключения кооперации (`sendto -> 203.132.26.108/109:11000/11001` + ответы
`recvfrom`, NOTES 28o) сработал на первом свежем сеансе и прерывист после него (клиент шорт-серкитит к
«сервис недоступен» при последующих попытках). Итог находок, новыми прогонами не изменился:

- Бэкенд RendezVous **доступен и ОТВЕЧАЕТ по UDP** — это не мёртвый-хост / DNS / стена маршрутизации, и не слой
  orbit/Uplay (тот уже подделан прокси-загрузчиком).
- Значит «Служба Far Cry 3 недоступна» — это сбой **прикладного уровня (PRUDP) переговоров RendezVous** для
  тенанта/тайтла FC3 на стороне сервера.
- Единственный способ заставить *сервер* ответить — заново реализовать PRUDP. Это ревил развилка по объёму:
  - **(A) локальный эмулятор PRUDP/RendezVous** (направить `lb-rdv-*` через hosts, говорить по PRUDP+тики) —
    наибольшая точность для «друзья подключаются через нас по интернету», но недели реверса протокола.
  - **(B) обойти RendezVous в FC3.dll и вести кооп-сессию на собственном echo/peer-транспорте игры (сначала LAN,
    ретранслятор позже)** — без PRUDP; нужны места вызова RV session-create/join, они виртуально-диспетчеризуемые и
    разрешимы только живым трассированием объектов RV/echo (оставить frida-трейсер, зацепить нативы RV на пути
    sendto, как только будут названы). Средне-сложно, неопределённо.
  - **(C) задокументировать как известный блокер с найденным эндпоинтом** и сузить объём.

Рекомендация: (B) сначала-LAN (совпадает с playbook coop-networking и обходит PRUDP); следующий техшаг — frida-
трассировка, называющая нативы RV create/join, вызываемые прямо перед диалогом «недоступно».


### Сессия 28q (тот же день) - направление B вскрыло цепочку RV; КРИТИЧЕСКОЕ исправление личности модуля

Захват стеков (лог frida_coop) атрибутировал каждый вызов rendezvous/echo к **FC3_d3d11.dll**
(работающий процесс `farcry3_d3d11.exe`), никогда к `FC3.dll`. Названные цепочки (RVA = addr - 0x10000000):

- **RendezVous bootstrap** (дёргает `gethostbyname("lb-rdv-as-prod01.ubisoft.com")`):
  `FC3_d3d11.dll+0x122f759` <- `+0x122f96f` <- `+0x123311e` <- `+0x1279bc5` <- `+0x127a320` <- `+0x127a3d2`.
- **настройка сокета storm::echo** (`bind <lan>:9000`): обёртка `+0xe5be2c` / `+0xe5be51` <- `+0x41a795` <-
  `+0x92d2bd` <- pump `+0x55171e` <- `+0x550d96` <- `+0x551737` <- `+0x4f907f`; второй путь
  `+0xe82eef` <- `+0xec069c` <- `+0xefafcf` <- `+0xe666a2`.

**КРИТИЧЕСКОЕ исправление (проверено scripts/probe_rv_live.py):** он-диск бинарники копии отличаются от
реальной установки и от прежней цели Ghidra:
  - работающий модуль = `H:\FarCryCoop\TestFC3_105\bin\FC3_d3d11.dll`  md5 **46bcc097**, 30 057 832 Б,
    ImageBase 0x10000000, SizeOfImage 0x23cc000, machine 0x14c (x86), **не упакован / дизассемблируется чисто**;
    `FC3.dll` в копии = md5 5ff04533.
  - прежний проект Ghidra FC3_106 анализировал реальную установку `FC3.dll` md5 **5742de2a** (40,7 МБ, DX9) -
    ДРУГОЙ файл. **Все RVA из сессий 28e-28h (FUN_11218480 гейт вечеринки и т.п.) получены из неверного бинаря
    и НЕ отображаются на работающую игру.** Всё будущее RE RV/echo/гейта должно целиться в md5 46bcc097.

Дизасембл RV-bootstrap по VA 0x1122f700-0x1122f870 (из probe_rv_live.py) - реальный код: вызывает слоты IAT
0x114ac6e4 / 0x114ac690 со строковыми аргументами у 0x116bc50c / 0x116bc594 и локальный вызов 0x11211290, возврат
которого - ровно фрейм 0x1122f759, т.е. эта функция и есть резолвер RV-хоста. Дальше: импортировать md5 46bcc097
в свежий проект Ghidra, автораспаковать и декомпилировать цепочки RV-bootstrap + echo-setup, чтобы спроектировать
обход направления B.


### Сессия 28r (тот же день) - карта RV дешифрована + сетевой движок имеет встроенный режим LAN (направлению B не нужен PRUDP)

Импорт+анализ Ghidra работающей копии `FC3_d3d11.dll` (md5 46bcc097, проект `FC3d3d11_live`, ~48 мин), затем
декомпиляция цепочек 28q (`rv_decompile.txt`). Карты:

- **Цепочка bootstrap RendezVous (сверху->вниз):** игровой вход `FUN_1044123b` -> `FUN_1127a3b0` -> `FUN_1127a300`
  -> **`FUN_11279ba0` (гейт: возвращает 1 только если RV-сетевая операция `FUN_112492a0` успешна, иначе 0)** ->
  при успехе `FUN_1127a1d0` делает пост-RV операцию сессии. Конфиг-сторона: `FUN_1122f870` парсит строку URL
  сервера, `FUN_1122f680` дробит `address=<host>;port=<n>`, резолвер `FUN_11211290` = `inet_addr`, иначе
  `gethostbyname` (IPv4 хранится в obj+4; частный случай "255.255.255.255"). Ленивый геттер флага готовности
  `FUN_11233110` возвращает obj+0x4a.
- **Инициализация сетевого движка `FUN_1092d256` (вызывающий только через vtable в 0x115c0e24):** имеет
  ПЕРВОКЛАССНЫЙ режим подключения: `param_1[0xe]` = 0 -> логирует **"LAN"**, 1 -> **"Online"**, 2 -> **"Offline"**;
  плюс синглтон `(**(*DAT_11e42a90 + 4))()`, возвращающий 1/2/3 -> 3/2/1 (селектор типа сети). Он биндит
  echo-UDP-сокет (`FUN_1041a75a` -> `FUN_10e5bdc0`) и ошибается "Net engine initialization failed.(UDP binding)"
  (код -0xf4229) лишь при сбое бинда. `FUN_105516a8` — пофреймовый помп сессии (состояния 0..4 по списку пиров).

**Вывод направления B (снят риск):** в игре УЖЕ есть LAN-путь неткода; кооп падает лишь потому, что сессия
переводится в режим "Online", а затем RendezVous отвергает тенант FC3. Рычаг — **селектор сетевого режима**, а не
PRUDP. Конкретные след. шаги:
1. Найти всех писателей режима (поля вокруг `obj+0xe`, синглтон `DAT_11e42a90` + его vtable-слот +4) и где кооп-меню
   выставляет Online vs LAN.
2. Frida-эксперимент **в памяти** (без записи на диск): форсить сетевой режим в LAN (и/или форсить `FUN_11279ba0`
   возвращать 1) при подключении кооп и наблюдать, исчезает ли "сервис недоступен" и какие сокеты/пиры использует
   путь LAN. Это безопасный тест go/no-go перед любой правкой на диске.

> **Дополнение 28r (rv2):** гейт FUN_11279ba0 сперва читает глобальный флаг онлайна `FUN_11245090`=`DAT_11f07e48`
> (0 -> немедленный отказ); нетоп FUN_112492a0 читает конфиг **"SandboxUrl"**, статус 2/3 -> отказ, иначе требует
> `FUN_11233110` (адрес разрешён) -> успех; пост-RV FUN_1127a1d0 строит **UbiAuthentication**-сессию
> (RendezVous/Services/UbiAuthentication/.../UbiAuthenticationClient.cpp). Форс гейта по одному упирается в UbiAuth,
> поэтому B должен использовать режим LAN движка (`FUN_1092d256` param+0xe:0), а не фейковый онлайн-успех.
> Синглтон типа сети DAT_11e42a90 читается ~80 раз / пишется один раз (конструктор FUN_100bc087).


### Сессия 28s (тот же день) - диспетчер сессий кооперации вскрыл НЕ-RV путь (рычаг направления B) + живой Frida теперь блокируется анти-инъекцией

Быстрые передекомпиляции проанализированного `FC3d3d11_live` (без перегонки) разрешили решение о режиме:

- **Диспетчер создания сессии кооперации `FUN_10441fb6`** (вызывается через vtable в 0x11526798): разрешает запись
  сессии (`FUN_10431a1b` поверх `FUN_1041dba9`; stride записи 0x90, id в +0x10) и ветвится по байт-флагу `*(rec+5)`:
  - флаг `== 0` -> **`FUN_1044123b` = ПУТЬ ОНЛАЙН** -> RV bootstrap (`FUN_1127a380`/`FUN_1127a3b0`) -> UbiAuth (мёртв).
  - флаг `!= 0` -> **`FUN_10443663` = НЕ-RV ПУТЬ** -> `FUN_11275f40(rec, &id, ..., this+1)` создаёт/входит в сессию
    БЕЗ RendezVous. Оба сообщают о сбоях через диспетчер кодов ошибок `FUN_104532ec`.

Значит в движке уже есть не-RV путь кооп-сессии; направление B = заставить кооп-сессию идти по
`FUN_10443663`/`FUN_11275f40` вместо онлайн `FUN_1044123b`. Открытые вопросы (след. статика): подтвердить, что
`FUN_11275f40` - прямой storm::echo/UDP-пейринг-хост (без Ubisoft), и найти, где ставится LAN-флаг записи +5
(т.е. может ли хост/джойн-UI кооперации создать сессию типа LAN, или жёстко зашит онлайн).

**Живой Frida теперь заблокирован:** x86-инжектор здоров (attach Frida к 32-битному SysWOW64-процессу проходит за
2.1с, тот же путь frida-helper-x86, что и у игры), но attach к `farcry3_d3d11.exe` стабильно уходит в таймаут даже на
свежей игре после вычистки всех frida-helper. => анти-инъекция FC3 теперь последовательно отвергает attach (в 28q
тот же трейсер цеплялся нормально). Интерактивный force-зонд потому ненадёжен; продолжать статикой + тестами on-disk-патча.


### Сессия 28t (тот же день) - ОКОНЧАТЕЛЬНО: кооп-сессия компании жёстко через RendezVous (не-RV пути в движке нет)

Финальные быстрые декомпиляции закрывают жизнеспособность направления B:

- «Другая» ветка кооперации `FUN_10443663 -> FUN_11275f40` ВСЁ РАВНО вызывает RV-гейт `FUN_11279ba0`, затем
  **`FUN_11275d90`**, который обращается к `.../online/RendezVous/RendezVous/Services/SubAccount/src/Client/SubAccountClient.cpp`
  и зовёт `FUN_112536a0(...)` = создать **RendezVous Session**. Значит эта ветка - путь **хоста** RendezVous
  (SubAccount + RVSession). Ветка `+5==0` (`FUN_1127a1d0`) - путь **входа через UbiAuthentication** RendezVous.
- Потому ОБЕ ветки сессии кооперации компании идут через RendezVous (`FUN_11279ba0` обязателен), что требует
  OnlineConfigService/`SandboxUrl` + Ubi auth - всё мертво. LAN/Online/Offline движка (`FUN_1092d256`) - это только
  инициализация транспорта; **не-RV кода установки кооп-сессии нет**, и перенаправлять некуда.

**Пересмотр:** направление B как «принудить LAN / пропустить RendezVous в движке» НЕЖИЗНЕСПОСОБНО - перенаправлять
нечего. Остаются только крупные технические маршруты:
  - **(A) эмулировать стек Ubisoft online**, нужный кооп-пути (SOAP OnlineConfigService -> SandboxUrl, сервер
    RendezVous/PRUDP сессий, UbiAuthentication, SubAccount), чтобы клиент сам завершил своё рукопожатие.
  - **(A') глубокий патч на уровне RendezVous Session**: перехватить обмен адресами пиров RV-сессии (PRUDP), чтобы
    игре передавались LAN-адреса пиров вместо ретрансляторов; всё равно требует понимания семантики RV/PRUDP-сессий.
Переиспользуемые активы: загрузчик-прокси (фейки orbit, ABI-корректный) и полная карта RV-вызовов (28r-28t). Рекомендую
задокументировать блокер вместе с картой + PR, затем решать, финансировать ли спайк (A)/(A').


### Сессия 28u (тот же день) - вердикт A'-спайка: подмена адресов пиров требует полной эмуляции RV-сессии; и A, и A' велики

A'-спайк (статика, без правок) прошёл создание RV host-сессии `FUN_112536a0` (`RendezVous/Core/.../BackEndServices.cpp`):
требуется `FUN_11237670` (RV подключён), сессия строится фабрикой `FUN_112532a0(...)` в `obj+0x74`, запускается вызовом
vtable (`*vtable+4`) и `FUN_112283a0(obj,0)`. Клиент RV Session - это ровно тот компонент, который через PRUDP делает
матчмейкинг и передаёт каждому пиру адрес другого. Потому:

- **A' (патчить слой RV-сессии ради подмены LAN-адресов пиров) НЕ дешевле A** - чтобы сессия сформировалась, игре всё
  равно нужно, чтобы RV-сессия выдала реальные адреса пиров и двинула обмен storm::echo; без RV-сервиса (или
  переписывания его семантики сессии) выдавать нечего, и сессия не формируется.
- **A (эмуляция стека Ubisoft online)** требует как минимум: (1) SOAP `OnlineConfigService`, отдающий конфиг
  `SandboxUrl`/rendezvous, (2) **RendezVous-сервер по PRUDP** (RC4/DH + тикеты + mutex/машина состояний + матчмейкинг
  сессий), (3) логин `UbiAuthentication`, (4) `SubAccount` - всё для тайтла FC3. Масштаб недель.

**Итог (честно):** кооперация кампании FC3 глубоко связана со стеком Ubisoft RendezVous + UbiAuth + SubAccount;
не-LAN пути в движке и дешёвого патча гейта нет. Переиспользуемые поставляемые активы: ABI-корректный загрузчик-прокси
(фейки orbit) и полная статическая карта RV-вызовов (28r-28u). Рекомендация: поставить это в PR и зафиксировать RV-стену;
работа над A - это многопротокольный проект, который надо оценивать отдельной задачей, а не продолжать по частям здесь.
