# Визуальные аномалии — постановочный слой

В игре game/index.html и редакторе game-editor/index.html теперь есть лёгкая система атмосферных эффектов. Источник: studio/source/game-runtime.html (HORROR_VISUALS_BEGIN).

- Система читает story.adventure.rooms[].default_variant, текущие state.variants[room] и флаг Q02_DONE.
- До завершения второй главы эффекты полностью отключены. Обычный вариант комнаты также ничего не меняет.
- Для авторских состояний B_GHOST_MIRROR, H_ANNA_GLASS, F_SUIT_STANDING, D_LATE_MIRROR и G_MIRROR_DOOR CSS-силуэты отключены, чтобы не дублировать фигуру поверх арта. Для B/H/D/G gaze-точка привязана к самой панорамной аномалии: при намеренном взгляде состояние возвращается к normal и сохраняется как увиденное. J_FALSE_BELOV и K_TOWER_SILHOUETTE теперь используют авторскую графику; все семь состояний с призраками отключают дублирующие CSS-силуэты. CSS-fallback остаётся только для старых состояний без арта.
- Временные состояния, включая H_1978, получают полосы и холодный цвет.
- Опасные состояния, например L_SHUTTER_DANGER, получают выраженную виньетку.
- Пауза, спокойные состояния и возврат к обычной комнате убирают эффекты.
- Эффекты работают без сети, поверх WebGL и CPU-рендера; prefers-reduced-motion отключает анимацию.

Для любой комнаты можно дополнительно задать карту visualProfiles с ключом варианта. Пример:

    "visualProfiles": {
      "B_GHOST_MIRROR": {"signal":"spectral", "strength":0.25, "figure":{"u":0.44,"v":0.48,"scale":1}}
    }

figure:false отключает силуэт; disabled:true отключает весь эффект. u,v — координаты equirectangular-панорамы в диапазоне 0–1. С появлением авторских художественных ассетов временные фигуры можно убрать, сохранив цветовой профиль.

ОГРАНИЧЕНИЕ: силуэты и помехи являются процедурными визуальными эффектами, а не отснятыми видеозаписями. 13 сцен found-footage и художественные панорамы всё ещё требуют отдельного производства.

Проверка:
  python3 codex-scripts/sync_embedded_engine.py --check
  node studio/verification/horror-visuals.test.cjs
  python3 studio/verification/standalone-html.test.py

GitHub Actions обновляет существующие HTML после изменения источника.


## Режиссёрские импульсы событий (этап 2)

Теперь краткая постановка включается **после того, как игрок закрыл описание события** (кнопкой «Продолжить» либо Esc). Это важно: эффект не проигрывается позади модального окна. Управляет этим `GagarinAdventure.UI.scene()` через необязательный `hooks.cue`, без изменения формата сейвов.

Без специальных настроек система использует уже утверждённую сценарную категорию события: `mirror`, `ghost`, `human`, `body` — призрачное свечение (`apparition`); `spatial`, `future` — временный сбой (`temporal`); `threat` — краткая темнота (`blackout`); `outdoor` — краткое мерцание (`flicker`). Для `trace`, `quiet`, `sound` и обычных записей эффекты по умолчанию **отсутствуют**, потому что не каждый шум должен вызывать скример. Начальная расслабленная фаза блокирует всю режиссуру до `Q02_DONE`.

**Авторская настройка:** у события в `story.adventure.events` допускается необязательный объект:

```json
"visualCue": {
  "mode": "apparition",
  "duration": 2.4,
  "strength": 0.43
}
```

`mode`: `apparition`, `temporal`, `blackout`, `flicker`; `duration` в секундах — 0.4–5, `strength` — 0.05–0.85; `disabled: true` отключает импульс. Это универсальное свойство сценарного события; художественный контент не зашит в JS. После открытия новых глав его можно настроить вручную в сценарном редакторе и затем экспортировать игру.

Импульс непостоянный: игровая пауза останавливает время анимации, переход в другую комнату его прекращает, а сброс и загрузка сохранения **не повторяют** событие. Никаких случайных скримеров, новых сетевых зависимостей или больших текстур. Временные CSS-фигуры остаются заглушками и не заменяют финальную графику призраков, зеркал и панорам.

Проверка: `node studio/verification/horror-cues.test.cjs`; регрессия включена в `.github/workflows/sync-adventure-runtime.yml`.


## Реакция зеркальных призраков на взгляд (этап 3)

Для `B_GHOST_MIRROR`, `H_ANNA_GLASS`, `D_LATE_MIRROR`, `G_MIRROR_DOOR` и `J_FALSE_BELOV` фигура закреплена в конкретном направлении 360° и исчезает, если игрок удерживает её около центра взгляда примерно 0.9–1.3 с. Поворот камеры в сторону сбрасывает отсчёт. Во время паузы или модального окна сцены время не накапливается.

После исчезновения записывается ключ `progress.seenApparitions["<room>:<variant>"]=true` в существующий сериализуемый объект adventure save v1. Поэтому призрак не возрождается при загрузке сейва и не влияет на другие варианты комнаты. Отдельных файлов или новых форматов сохранений нет.

В `rooms[].visualProfiles[variant]` можно указать `gaze: <seconds>` в диапазоне 0.25–4 либо `gaze: false` для запрета исчезновения. Другие призраки без gaze-профиля остаются частью обстановки до сценарного изменения состояния.

Для производственных ассетов понадобится привязать эти `u/v` к реальным зеркалам и силуэтам. Текущие CSS-фигуры — заглушки, не замена художественных панорам.

Проверка: `node studio/verification/horror-gaze.test.cjs` (подключена к GitHub Actions).


## First-act monitor reflections

The visual-only panorama build now wires twenty-one room-state composites plus the two existing kitchen-state composites; eighteen state inserts are generated deterministically at 2048×1024 from the existing D-room hotspot UVs: `D_FALSE_MONITOR` shows a second corridor inside the dead CRT; `D_LATE_MIRROR` shows a delayed human reflection that does not fit the room; `B_TWO_GHOSTS` adds two distinct silhouettes to the kitchen sink mirror; `D_DOUBLE_ACTS` duplicates the incident paperwork; `H_ANNA_GLASS` places Anna’s face and hand inside the cabinet glass; `G_P17` shows the wet sample in the freezing box; `G_MIRROR_DOOR` places an impossible corridor door inside the microscope reflection; `C_HIDDEN_DOOR` reveals a full-height door in the previously continuous corridor wall; `C_REVERSED_SNOW` adds floor-level tracks leading toward the airlock; `E_FALSE_DIGITAL` replaces numeric digits with human silhouettes; `F_SUIT_STANDING` shows an empty pressure suit standing upright; `D_INDOOR_TOWER` shows the antenna mast on a monitor inside the building; `N_CLOCK`, `N_SIGN`, and `N_HANDWRITING` preserve the three corridor clues; `N_LATE_EXIT` places Late at the end of the corridor and can be dismissed into `N_NORMAL`. The physical monitor bezel remains visible. All twenty-one room-state composites and both kitchen-state composites are wired through `variantAssets` into the editable project, editor payload, and standalone `game/index.html`. Art-backed apparition states suppress duplicate CSS figures and return to a normal/empty panorama after a deliberate stare; the disappearance persists in saves. J_FALSE_BELOV and K_TOWER_SILHOUETTE use authored art too. The long-corridor N_LATE_EXIT apparition now also dissolves into a new empty N_NORMAL panorama after a deliberate stare; the indoor-tower monitor uses authored art without a second CSS figure. Seven apparitions are gaze-dismissable; the empty pressure suit remains a static authored state. The CSS fallback remains only for legacy profiles without art. These are presentation-only changes: no audio or video is generated or modified.

Regression: `python3 studio/verification/monitor-variant-art.test.py`.
