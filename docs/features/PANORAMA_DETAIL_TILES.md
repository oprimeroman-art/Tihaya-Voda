# Panorama Detail Tiles — встроенная послойная 360-сцена

Рабочая интеграция раздельных пиксельных областей в игру, не самостоятельный движок.

## Сцена

Жилой модуль A: «Ровно поставить тапочки» теперь мгновенное действие прямо в панораме, без большого окна. RGBA-заплатка с переставленной обувью заменяет участок изображения пола, но не всю комнату. После сюжетного события A_SHOES_SHIFTED первоначальное положение возвращается. Повторное нажатие опять ставит тапочки ровно.

## Контракт

- production/panorama-detail-tiles.json — положение области в equirectangular UV [left,top,right,bottom], room, id, path, when: flag/notFlag/done.
- site-assets/panorama-patches/ — прозрачные плитки PNG.
- studio/source/game-runtime.html — четыре независимых WebGL-текстуры, отображаемые в прямых UV-координатах поверх низкодетального фона. У каждого фрагмента собственное разрешение. Есть CPU fallback.
- codex-scripts/panorama_detail.py — один упаковщик для веба (отдельные файлы) и автономной HTML-игры (data-URL).
- codex-scripts/build_pages_demo.py берёт актуальный runtime, не ждёт синхронизации другого workflow.

## Ограничения

Дробление пикселей не создаёт недостающие детали: исходник комнаты A — 1774×887. Текущий фрагмент демонстрирует изменяемое изображение, а не апскейл. Для улучшения разрешения нужны отдельно детализированные фрагменты, положенные в тот же UV прямоугольник. Поддерживается четыре активных фрагмента на WebGL-кадр, до 16 в кэше, без плиток движок показывает исходную панораму. Плитки не пересекают шов 0/1.

Архив PanoramaForge_0.1_Windows.zip найден в библиотеке, но байтовое содержимое недоступно для материализации; его код не исследован. Нынешняя реализация сделана на реальных исходниках игры.

Быстрый тест: node studio/verification/panorama-detail-tiles.test.cjs

## 2026-11-01: Original Panorama Forge 0.1 core integrated

The exact uploaded engine.py is now codex-scripts/panorama_forge_engine.py.
It implements spherical wrap/pole padding, precision Lanczos x2/x4, optional
Real-ESRGAN-ncnn-vulkan and seam matching. The game tool
codex-scripts/forge_pipeline.py runs restoration, feeds the output into the
lossless pixel tile slicer, and optionally registers tiles in the game manifest.
Example:

    python codex-scripts/forge_pipeline.py input_360.png --room A --variant A_NORMAL --mode precision --scale 2 --tile-size 1024 --register

Use transparent detail tiles for mutable props. Whole-room tiles are composited
above normal runtime room sprites and may hide dynamic overlays; do not
automatically register them for every variant. An explicit --register is
required to modify the live manifest.

WebGL now displays the background plus up to 24 visible UV tiles in separate
alpha-blended draw passes using only two texture units. It unloads distant
textures via a 30-entry cache. The 4-tile ceiling is removed, not performance
limits. The CPU fallback is preserved. Game art must actually contain
high-resolution details for visible quality to improve.

Synthetic precision x2 + spherical seam correction + lossless tile production
was tested locally. Real GPU AI and complete 8K browser gameplay were NOT tested.
