---
title: Project state — Tihaya Voda
summary: Actual horror engine, current assets and build constraints verified on 2026-11-01.
code_paths: ["studio/**", "game-project/**", "game/**", "game-editor/**", "site-assets/horror-actors/**"]
---
# Tihaya Voda — current state

- Existing browser horror/adventure set at the Arctic station, built with Gagarin Panorama Studio; repo `oprimeroman-art/Tihaya-Voda`.
- `studio/source/game-runtime.html` holds projection, in-room hotspots, original WebGL/CPU panorama engine, visual/audio director and inventory-gated flashlight.
- `studio/source/adventure-ui.js` holds gameplay UI and tasks; canonical story in `studio/content/TIHAYA_VODA/adventure.json`; additional optional investigations in `production/optional-encounters.json`.
- The game has twelve canonical chapters and four logical endings. An uninterrupted UI playthrough of every route is NOT confirmed.
- 16 authored spatial audio cues S01–S16 were produced earlier in `game-project/audio/spatial/`. The 2026-11-01 source added context-sensitive stereo events (footsteps, knocks, breaths, metal) mixed into station ambience. No claim of professional voice acting.
- Three small original SVG illustrations in `site-assets/horror-actors/` were embedded inside the runtime for offline apparitions. They are stylized fallback art, NOT finished photographic scene panoramas.
- Current user priority: horror direction, original images and sounds, escalating character/room transformations and consequences, no pointless HUD or unrelated menus. Full assignment: [GitHub issue #39](https://github.com/oprimeroman-art/Tihaya-Voda/issues/39).
- Published URL: https://oprimeroman-art.github.io/Tihaya-Voda/ ; deployed content and release QA must be checked against GitHub Actions before any success claims.
- New multi-agent guidance exists in `AGENTS.md`, `.ai/` and `docs/ops/HANDOFF.md`; there is no always-running agent wired to GitHub issues.
