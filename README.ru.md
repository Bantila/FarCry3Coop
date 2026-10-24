# FarCry3Coop — кооператив для Far Cry 3

English version: [README.md](README.md)

Часть проекта FarCryCoop: кооперативные моды для серии Far Cry, по репозиторию на игру.
Другие игры: https://github.com/Bantila/FarCryCoop/blob/main/README.ru.md#другие-игры-серии

Статус: исследование. Заметки и находки: [NOTES.ru.md](NOTES.ru.md).
План: 4 игрока проходят весь сюжет с катсценами, побочными занятиями и коллекционными предметами, вход по приглашению Steam: [PLAN.ru.md](PLAN.ru.md).

## Тестирование / помощь

В репозитории нет файлов игры и файлов чужих модов: нужна своя копия Far Cry 3 (Steam). Инструменты
исследования и тестов лежат в [scripts/](scripts/) (Python 3 и Windows PowerShell). Пока в них пути
владельца (`E:\FarCryCoop\...`, библиотека Steam на `E:`); поправьте пути в начале скрипта под свой ПК.

- `build_testgame.ps1 -Version 1.05|1.06` — тестовая копия игры вне папки Steam (`bin` версии 1.05 берётся из депо Steam 220241, манифест `7362101836779063707`, через DepotDownloader).
- `patch_dll.py <копия FC3.dll / FC3_d3d11.dll>` — текущие правки DLL (`--selftest` их проверяет); установку Steam не трогает.
- `build_patch.ps1`, `switch_variant.ps1` — архив patch и переключение тестовой копии между штатной игрой и модом.
- `launch_105.ps1 -Role host|client` — хост и клиент на одном ПК через ключи быстрого запуска разработчиков.
- `thread_eips.ps1 -ProcessId <pid>` — где выполняются самые загруженные потоки игры.

Текущее состояние и открытые проблемы: последние разделы [NOTES.ru.md](NOTES.ru.md).
