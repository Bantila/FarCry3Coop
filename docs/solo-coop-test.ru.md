# Живой тест соло-офлайн-коопа (patch_solo_offline_coop_vanilla-262)

Пара: этот файл — русский, `solo-coop-test.md` — английский. Правятся вместе.

Это процедура на машине: запустить рабочую копию 1.05 через Ubisoft Connect и зайти в соло-кооп-сессию с набором лоадеров `patch_solo_offline_coop_vanilla-262` (nexus 262). Всё только на рабочей копии (`H:\FarCryCoop\TestFC3_105`); до настоящей установки есть доступ лишь через NTFS junction, и она не изменяется. Все скрипты в `H:\FarCryCoop\scratch\`.

## Текущее состояние
- `TestFC3_105` = мод 1.05: `bin\FC3.dll` (5ff045331557), `bin\FC3_d3d11.dll` (46bcc0975905), `bin\uplay_r1_loader.dll` (dacd14c07775), `bin\ubiorbitapi_r2_loader.dll` (ba6015e566c9), `bin\uplay_r14.dll` (6c75cb01cef6), `data_win32\patch.dat` (212 002 032 Б, md5 157f2d7682a5), `data_win32\patch.fat` (850412635760).
- Бэкап 1.06 до мода: `TestFC3_105\_backup_106_before_solo262\` (FC3 5742de2aaa76, FC3_d3d11 916c6d4b876d, patch.dat 5a788dd5f7be, patch.fat c829e677c352).
- NTFS junction `H:\Uplay\Far Cry 3` -> `H:\FarCryCoop\TestFC3_105` (создан `use_copy_junction.bat`; настоящая папка сохранена как `Far Cry 3.OFFICIAL`).
- Ещё НЕ сделано: `uplay_r14.dll` в папку лаунчера (нужны права администратора).

## Шаг 1 — положить uplay_r14.dll туда, где его видит лаунчер (администратор)
Запустить `install_uplay_r14_launcher.bat` от имени администратора. Он копирует `uplay_r14.dll` (6c75cb01cef6) в `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\` (аддитивно — такого файла там нет; откат = просто удалить этот файл).

## Шаг 2 — запуск через Ubisoft Connect
1. Полностью выйти из Ubisoft Connect (иконка в трее -> Выход), затем запустить снова, чтобы он перечитал файлы игры.
2. Нажать **Играть** у Far Cry 3 (junction заставляет upc запустить копию 1.05).
3. Когда появится главное меню, цепочка лоадеров: `farcry3.exe` -> `bin\uplay_r1_loader.dll` -> `uplay_r14.dll` (фейковая платформа Uplay/orbit).

## Шаг 3 — проверить, что эмулятор реально загрузился (опционально, только чтение)
С игрой в меню, из обычной консоли:
```
python -I H:\FarCryCoop\scratch\fc3_probe_modules.py
```
Он перечислит модули работающего `farcry3.exe` и сообщит, загружены ли `uplay_r14.dll` и `uplay_r1_loader.dll`. Если `uplay_r14.dll` нет — шим не достигается; вернуть агенту `H:\FarCryCoop\scratch\fc3_mods.txt` и хвост `C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\logs\launcher_log.txt`.

## Шаг 4 — заход в соло-кооп-сессию
В главном меню: **ИГРАТЬ -> КООПЕРАТИВ -> Приватная сессия -> Играть одному -> Начать**. Мод отсчитывает ~10 с и загружает кооп-мир офлайн. Успех = вы управляемы в кооп-точке появления. Записать, какая глава/область загрузилась.

## Откат
- Откатить только мод: запустить `uninstall_solo262.bat` от имени администратора (удаляет `uplay_r14.dll` на C: + 3 DLL-зависимости в bin, восстанавливает 1.06 `FC3.dll`/`FC3_d3d11.dll`/`patch.dat`/`patch.fat` из `_backup_106_before_solo262\`).
- Откатить junction: запустить `undo_junction.bat` от имени администратора (убирает junction, возвращает настоящую папку `H:\Uplay\Far Cry 3`).
