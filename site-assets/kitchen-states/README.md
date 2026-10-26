# Kitchen scene states — chapter 4

- `B_SECOND_PLATE.webp`: E018, after `cooked`. The kitchen table has a second warm plate, but the mirror is still empty. The spoon shadow stays physically plausible.
- `B_GHOST_MIRROR.webp`: E019, after `inspect_sink_after_cooked`. Anna appears only in the mirror; the plate has a faint impossible face-like reflection and the spoon shadow no longer lines up.

Both are deterministic 2048×1024 offline WebP scene states. They are mapped to existing canonical variants; no actions, flags, events, endings, or story text were added or rewritten. `codex-scripts/generate_kitchen_ghost_art.py` can regenerate the mirror state and derive the precursor by repainting only the mirror glass, plate centre, and spoon shadow. The integration validates the original E018/E019 triggers, WebP signatures, and SHA-256 checksums before embedding both assets.
