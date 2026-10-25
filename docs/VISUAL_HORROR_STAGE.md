# Визуальные аномалии — постановочный слой

В игре game/index.html и редакторе game-editor/index.html теперь есть лёгкая система атмосферных эффектов. Источник: studio/source/game-runtime.html (HORROR_VISUALS_BEGIN).

- Система читает story.adventure.rooms[].default_variant, текущие state.variants[room] и флаг Q02_DONE.
- До завершения второй главы эффекты полностью отключены. Обычный вариант комнаты также ничего не меняет.
- Спектральные состояния B_GHOST_MIRROR, H_ANNA_GLASS, J_FALSE_BELOV, F_SUIT_STANDING, K_TOWER_SILHOUETTE, D_LATE_MIRROR, G_MIRROR_DOOR получают сдержанные силуэты; координаты их появления привязаны к 360-градусной панораме.
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
