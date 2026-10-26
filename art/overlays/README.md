# Existing-room variant overlays

These are transparent 2048×1024 WebP layers, not replacement panoramas. They intentionally change only the visual beat listed below while preserving the room's underlying geometry and hotspot layout.

- `C_C_MIRROR_LIGHT.webp` — E013 / `C_MIRROR_LIGHT`: a cold flashlight flare appears in the central mirror reflection.
- `F_F_ARCHIVE12.webp` — E009 / `F_ARCHIVE12`: the existing stockroom sign is replaced by the stamped `АРХИВ-12` plate.
- `H_H_AFTER_V01.webp` — E012 / `H_AFTER_V01`: the archive cabinet is ajar and exposes the note `МЫ УЖЕ ЗНАКОМЫ`.

The overlays are generated deterministically by `codex-scripts/generate_existing_room_overlays.py` against the source room geometry in `game-project/rooms/{C,F,H}/original.png`. The manifest already names these exact paths. `codex-scripts/test_existing_room_overlays.py` checks dimensions, alpha transparency, checksums, and canonical event mappings.

These overlays complete the three missing state layers only. They do **not** complete the production art contract: the eight full 360° panorama targets and 95 hotspot-corner calibrations remain outstanding in the art-readiness audit.
