# Финальная художественная интеграция · 30 октября 2026

Разработка поверх `aaebef24bd3304762d50cbec4d56c2ecc8bfb99d`, без новой архитектуры и без изменения авторских аудио/видео. По указанию автора новые игровые прогоны и тестовые серии в этой смене не запускались. Это отчёт о реализованной разработке, не сертификат нового плейтеста.

## Сделано

- 10 технических макетов E/G/I/J/K/L/M/N/O/P заменены полноценными панорамами в стиле существующих комнат. Утверждённые A/B/C/D/F/H сохранены.
- 32 новых выбранных изображения: основные помещения, поздние A/B, две койки медпункта, безопасный шлюз, фигура у мачты и её исчезновение, галерея с приближением/отступлением и тремя временами, два кадра монитора, аномалии лаборатории, дизельной и коридора.
- Закрыты 11 прежних незаполненных панорамных состояний. Для L_THREE_WINDOWS используется новая ночная галерея; для N_NORMAL — пустой коридор. Готовые подходящие изображения используются повторно.
- H_1978 теперь показывает нарисованный архив 1978, а не чужое состояние после VHS. H_V01B больше не подставляет изображение Анны в обычную комнату.
- E095 даёт короткий панорамный шаг приближения на 1,8 с существующим механизмом временных сцен. После решения створок запоздалый эффект не возвращает угрозу. E097 оставляет отпечатки, E102/E103 меняют отдельные окна, E105 меняет только сценическое состояние монитора.
- Точки взаимодействия перенесены на предметы и рабочие поверхности; отдельная разметка H_1978 учитывает смену обстановки.
- Все наблюдения получают контекстную иллюстрацию текущего помещения; технические карточки отсутствующего изображения убраны. Название и титры приведены к реальной игре. Расшифровки медиа остаются доступны без съёмочного листа в игровом интерфейсе.

## Исходники и сборка

`production/final-scene-art.json` содержит выбранные изображения, промпты, размеры и происхождение. Генерация выполнена встроенным ImageGen; новые WebP хранятся рядом с существующими ассетами, старые файлы не перезаписаны. `production/interaction-anchors.json` — координаты взаимодействий. `codex-scripts/sync_final_scene_art.py` встраивает одну и ту же художественную версию в проект, автономную игру, редактор и публикацию. Он вызывается после старых волн иллюстраций, чтобы те не возвращали технические макеты и прежние координаты.

В существующий Synchronize adventure runtime добавлен явный режим `assemble_only`: сборка и сохранение HTML без тестовых серий. Обычный режим автоматизации оставлен прежним.

## Файлы изображений

- `I_NORMAL` — `game-project/assets/final-rooms/authored_I_NORMAL.webp`
- `M_NORMAL` — `game-project/assets/final-rooms/authored_M_NORMAL.webp`
- `L_NORMAL` — `game-project/assets/final-rooms/authored_L_NORMAL.webp`
- `J_NORMAL` — `game-project/assets/final-rooms/authored_J_NORMAL.webp`
- `K_NORMAL` — `game-project/assets/final-rooms/authored_K_NORMAL.webp`
- `N_NORMAL` — `game-project/assets/final-rooms/authored_N_NORMAL.webp`
- `E_NORMAL` — `game-project/assets/final-rooms/authored_E_NORMAL.webp`
- `G_NORMAL` — `game-project/assets/final-rooms/authored_G_NORMAL.webp`
- `P_NORMAL` — `game-project/assets/final-rooms/authored_P_NORMAL.webp`
- `O_NORMAL` — `game-project/assets/final-rooms/authored_O_NORMAL.webp`
- `A_LATE` — `game-project/assets/final-rooms/authored_A_LATE.webp`
- `B_LATE` — `game-project/assets/final-rooms/authored_B_LATE.webp`
- `I_COVERED_BODY` — `game-project/assets/final-rooms/authored_I_COVERED_BODY.webp`
- `I_EMPTY_BED` — `game-project/assets/final-rooms/authored_I_EMPTY_BED.webp`
- `J_SAFE` — `game-project/assets/final-rooms/authored_J_SAFE.webp`
- `K_TOWER_EMPTY` — `game-project/assets/final-rooms/authored_K_TOWER_EMPTY.webp`
- `L_SHUTTER_DANGER` — `game-project/assets/final-rooms/authored_L_SHUTTER_DANGER.webp`
- `M_DELAY_MONITOR` — `game-project/assets/final-rooms/authored_M_DELAY_MONITOR.webp`
- `J_FALSE_BELOV` — `game-project/assets/final-rooms/authored_J_FALSE_BELOV.webp`
- `M_FINAL` — `game-project/assets/final-rooms/authored_M_FINAL.webp`
- `L_WINDOW_1978` — `game-project/assets/final-rooms/authored_L_WINDOW_1978.webp`
- `K_TOWER_SILHOUETTE` — `game-project/assets/final-rooms/authored_K_TOWER_SILHOUETTE.webp`
- `L_WINDOW_FUTURE` — `game-project/assets/final-rooms/authored_L_WINDOW_FUTURE.webp`
- `L_COUNTER_NEAR` — `game-project/assets/final-rooms/authored_L_COUNTER_NEAR.webp`
- `L_COUNTER_RETREATED` — `game-project/assets/final-rooms/authored_L_COUNTER_RETREATED.webp`
- `E_FALSE_DIGITAL` — `game-project/assets/final-rooms/authored_E_FALSE_DIGITAL.webp`
- `G_P17` — `game-project/assets/final-rooms/authored_G_P17.webp`
- `G_MIRROR_DOOR` — `game-project/assets/final-rooms/authored_G_MIRROR_DOOR.webp`
- `N_SIGN` — `game-project/assets/final-rooms/authored_N_SIGN.webp`
- `N_HANDWRITING` — `game-project/assets/final-rooms/authored_N_HANDWRITING.webp`
- `N_LATE_EXIT` — `game-project/assets/final-rooms/authored_N_LATE_EXIT.webp`
- `N_CLOCK` — `game-project/assets/final-rooms/authored_N_CLOCK.webp`
