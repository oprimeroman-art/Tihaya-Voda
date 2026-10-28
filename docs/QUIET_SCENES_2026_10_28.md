# Тихие состояния — 28 октября 2026

Продолжение от main `76d5ed19e93a5a4ae8270cb625844ad227746c89`. Сюжетные реплики, головоломки и медиа сохранены.

- `game-project/assets/variants/authored_A_SECOND_PILLOW.webp`: две физические вмятины на той же подушке. Привязано к исходным E027 и E044; состояние сохраняется при выходе, повторном посещении и загрузке.
- `game-project/assets/variants/authored_C_DAYLIGHT.webp`: дневное освещение существующего коридора. E100 ждёт входа в C после выбора ответа по радио. Три секунды считаются после готовности текстуры и закрытия карточки. Меню и документ приостанавливают время; новые сюжетные карточки ждут окончания короткой постановки. Выход, сброс и загрузка отменяют временный вариант; восстанавливается актуальное сюжетное состояние, а не всегда C_NORMAL. В сохранение временный вариант не записывается.

У E100 восстановлена комната C из исходной `06_DIRECTOR_EVENT_MATRIX.tsv`: прежний сборщик явно обнулял её. Телепортации нет. Исходные строки и условия выбора не изменены.

Изображения получены встроенным **ImageGen** редактированием утверждённых панорам A/C. Геометрия, проекция, положение дверей/окон и координаты игровых объектов оставлены прежними. Формат WebP, 1774×887, конвертация без изменения пропорций. Нормальные панорамы не перезаписаны. Полные контрольные суммы — `production/quiet-scene-art.json`.

## Промпты финальных изображений

**A_SECOND_PILLOW — precise-object-edit.** Edit target: approved 2:1 living-module panorama; second reference is a close-up locator only. Flatten the existing pillow and press TWO adjacent deep oval head-sized concave hollows into its cloth, separated by a raised central ridge of stuffing, dark in the centers with radial compression wrinkles. Clearly readable from a full-room view. Not two pillows, no printed face/body. Keep the pillow footprint and every room coordinate; preserve doors, window, desk, floor, lights, texture, lettering and realistic illustrated style. No person, ghost, caption, close-up output or montage. Output one complete original-composition panorama.

**C_DAYLIGHT — lighting-weather.** Edit the approved 2:1 corridor panorama. Change only illumination and exterior sky: cold pale polar midday spills through existing small windows and round door glazing, catches wet floor and worn metal, briefly overpowers unchanged warm lamps. Bright overcast snow outside, no sun disc or storm flash. Preserve exact camera/projection and every door, window, pipe, poster, extinguisher, object, signage and gritty texture. No new geometry, characters, objects, text or graphics; no bleaching detail or montage. Output one full panorama edge-to-edge.

## Проверка

`quiet-staging.test.cjs` проверяет готовность текстуры, три активные секунды, паузу, модальные окна, возврат исходного состояния, выход и запоздалые callback. `quiet-scene-art.test.py` сверяет файлы, исходные панорамы, канон и три игровых экспорта.

Полный `campaign-browser.test.cjs` включает получение состояния подушки обычным возвращением в A, повторное посещение, а также E100 на четырёх маршрутах: настоящая панорама, меню, сохранение во время света, естественное окончание и загрузка без сохранённой вспышки. После публикации тот же маршрутный тест выполняется по публичному URL. Время ожиданий ускоряется часами браузера, сюжетные флаги не устанавливаются тестом.

Оставшиеся несопоставленные варианты и технические sign-объекты фиксируются в обновлённом `reports/CAMPAIGN_RELEASE_GAPS.json`. Этот блок не объявляет художественный релиз завершённым.

## Согласование остальных состояний коридора

Три прежних composite_C-состояния использовали старую процедурную комнату. Новые `authored_C_MIRROR_LIGHT.webp`, `authored_C_HIDDEN_DOOR.webp`, `authored_C_REVERSED_SNOW.webp` — локальные редактирования той же утверждённой C-панорамы. Старые файлы сохранены; активные привязки переведены на новые. После штатного старого композитора синхронизатор повторно закрепляет утверждённые изображения, чтобы автоматическая сборка не возвращала старую геометрию. Дневной вариант сделан на основе новых снежных следов и сохраняет их при смене света.

Дополнительные промпты встроенного ImageGen (precise-object-edit):

- C_MIRROR_LIGHT: только стекло двери в конце левого прохода, около u=.29/v=.51, показывает круглый тёплый луч фонарика, которого нет в самой комнате; эффект ограничен существующим стеклом, остальные объекты/свет/геометрия не меняются.
- C_HIDDEN_DOOR: только дальняя дверь правого прохода, около u=.83/v=.50, становится приоткрытой тяжёлой тёмной дверью в неосвещённый проход с табличкой «ТИХАЯ»; вся остальная комната остаётся на прежних местах, никого за дверью нет.
- C_REVERSED_SNOW: реалистичные тающие снежные отпечатки сапог от стороны спальни к дальнему шлюзу правого прохода, с правильным перспективным уменьшением; не белые иконки обуви, без человека и изменений окружения.
- Финальный C_DAYLIGHT: первый референс — коридор со следами, второй — дневной свет. Менять только освещение и небо; сохранить каждый отпечаток, его место, форму и направление.

Для всех: полный 2:1 кадр без монтажа/подписей, исходные камера, дверные/оконные проёмы, оборудование, фактура и кинематографический рисованный стиль сохранены.
