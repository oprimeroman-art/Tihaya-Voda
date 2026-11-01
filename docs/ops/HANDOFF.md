---
title: Agent handoff
summary: Current authored horror scenes, playable corridor false threshold and immediate follow-up.
code_paths: ["studio/source/game-runtime.html", "studio/source/adventure-ui.js", "studio/verification/false-threshold.test.cjs", "site-assets/horror-actors/**"]
---
# Handoff — 2026-11-01

- Active project: `oprimeroman-art/Tihaya-Voda`, existing browser game (no rewrite).
- Latest change: a **chapter-six false threshold** in corridor C, triggered once when attempting an otherwise valid exit. The engine remains in C; the actual `C_HIDDEN_DOOR` authored panorama replaces the normal room with a brief blackout cut, directional metal/knock/step cues, and a real projected clickable door handle. Finding the handle, trying the exit again, or waiting produces three different permanent journal entries. The canonical exit works immediately on retry; no chapter, ending, item or door requirements are modified.
- Implementation: optional `beforeTravel` hook in `GagarinAdventure.UI.enterRoom()`, state and visual direction in the `CORRIDOR_FALSE_THRESHOLD` section of `studio/source/game-runtime.html`. The scene and button reset on a new game or load and are cleared by leaving C.
- Local targeted check: `node studio/verification/false-threshold.test.cjs` passed for examined, fled, expired outcomes, same-room behavior and original panorama recovery. Both modified JavaScript files passed `node --check` (player script extracted for its inline JavaScript).
- The existing 16 spatial S01–S16 cues and previously authored encounter art remain intact. Earlier directed encounters use original SVGs under `site-assets/horror-actors/`, now with spatial sound.
- Project's larger Work production assignment: [issue #39](https://github.com/oprimeroman-art/Tihaya-Voda/issues/39). Opening an issue does NOT launch Work.
- Do not claim any new public build or editor sync until the corresponding workflow succeeds; direct browser playthrough and all four endings remain unverified.
- Next concrete scene: radio-room speaking-before-the-player anomaly, followed by actual playtesting and restoring any failed CI checks. Focus on diegetic cues and actions, not additional journals or menus.


## Panorama pixel-layer iteration

- Source: studio/source/game-runtime.html (PANORAMA_DETAIL_TILES).
- Room A: slippers action is direct; a PNG equirect UV floor patch renders only after the slippers flag. The later A_SHOES_SHIFTED event hides it. No new giant modal.
- Manifest: production/panorama-detail-tiles.json, approved pixel art: site-assets/panorama-patches/A-slippers-aligned.png.
- Same assets delivered externally for Pages and inline for offline file:// output with codex-scripts/panorama_detail.py.
- Targeted test: node studio/verification/panorama-detail-tiles.test.cjs.
- The approved background is still 1774x887: pixel reassembly does NOT improve it without independently better source tiles.

## Actual Forge source integrated

- Original uploaded Forge core: codex-scripts/panorama_forge_engine.py.
- Build bridge: codex-scripts/forge_pipeline.py.
- Scalable UV tile renderer: studio/source/game-runtime.html, 24 visible tiles
  selected from camera viewport, texture cache limit 30, separate layer draw.
- panorama_detail.py must preserve variant gating in web and standalone packs.
- Synthetic spherical upscale and exact tile roundtrip passed; browser and
  real Vulkan AI still need checking.

## Gameplay iteration: early radio echo (2026-11-01)

- studio/source/game-runtime.html: EARLY_RADIO_ECHO triggers in D after TEA_DONE but before SIGNED_SHIFT, plays original recorded Belov DLG_003 over the radio, changes D_FALSE_MONITOR panorama and projects a physical switch. Cutting, listening and walking away have distinct persistent journal outcomes, and the later canon report echoes the same words. No quest, exit or ending requirements altered.
- codex-scripts/panorama_detail.py: slippers, wash_cup, paper_tray are immediate actions instead of empty full-screen confirmation modals.
- studio/verification/radio-echo.test.cjs covers the three endings, audio, panorama, original restoration and recognition; adventure rooms regression also passed.
- Real full browser playthrough not yet confirmed. Next: in-world appearance changes for more props, reduce unnecessary persistent HUD and build scene-driven rather than document-driven horror.
