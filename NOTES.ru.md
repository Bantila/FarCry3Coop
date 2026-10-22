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

- Штатный кооп: отдельная кампания из 6 миссий, до 4 игроков онлайн https://co-optimus.com/article/8473/far-cry-3-follow-up-questions-plus-new-co-op-campaign-trailer-and-images.html . Мод: Open World Co-op (scubrah), без сюжетных миссий, альфа https://www.nexusmods.com/farcry3/mods/220 (каталог coop-anything).
