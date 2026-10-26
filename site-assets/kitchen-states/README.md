# Kitchen state art — B_GHOST_MIRROR

`B_GHOST_MIRROR.webp` is a deterministic 2048×1024 painted-style panorama for the existing chapter-4 kitchen state. It visualizes the canonical E019 beat: Anna appears only in the sink mirror while the table holds the empty plate and a spoon with a mismatched shadow.

The asset is loaded locally as `illustrated_B_GHOST_MIRROR` and mapped to the existing `B_GHOST_MIRROR` variant. It adds no new action, flag, event, ending, external request, or story text. The generator is `codex-scripts/generate_kitchen_ghost_art.py`; run it from a repository checkout with Pillow and NumPy installed. The integration script validates the canonical E019 trigger, WebP format, and SHA-256 before embedding the asset.
