# Campaign 360-degree room art

`production/geometry/CAMPAIGN/render_campaign360.py` generates distinct equirectangular 360×180 scenes for rooms A–P using the shared ray-traced geometry and pinned CC0 materials. The existing high-detail kitchen candidate is reused for B; other rooms have dedicated furniture and landmarks matching their settings: dormitory, corridor/mirror, radio room, diesel generator, stockroom, lab, film archive, medical bay, airlock, snowy antenna yard, gallery, drill block, long corridor, 1978 archive, and lower chamber.

Existing object UV interaction corners are not changed. Physical props are staged near those anchors. Original PNGs remain as backups; the editable project and standalone HTML use `rooms/<ID>/panorama_v2.webp`.

This build is visual-only. It does not generate, replace, or rewrite user-supplied audio/video files. The workflow validates the existing 13 video clips, 16 spatial audio cues, authored story-state panoramas, and gameplay code before committing generated images.
