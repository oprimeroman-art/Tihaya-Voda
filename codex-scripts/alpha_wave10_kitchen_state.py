#!/usr/bin/env python3
"""Attach the painted kitchen ghost-mirror state to canonical chapter 4."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "B_SECOND_PLATE": ("illustrated_B_SECOND_PLATE", "6f4cc9c45b813ca1f0a6d5455c61e5d0ff3a231ee498b6fc794d2fdf67c90368"),
    "B_GHOST_MIRROR": ("illustrated_B_GHOST_MIRROR", "168d08a767f2e7727f92d3d8f3c00e2da007904c74f84a6bb196e30e80043c0b"),
    "B_TWO_GHOSTS": ("illustrated_B_TWO_GHOSTS", "641007fec25de4740079cdb1420055d6c1d6d0a7e211a255688c69668fd915d2"),
}
def apply_wave10(payload, root=ROOT):
    game = payload
    story = game["story"]["adventure"]
    if len(game["rooms"]) < 16 or len(story["events"]) != 112 or len(story["documents"]) != 30:
        raise ValueError("Canonical game/story counts changed")
    room = next(r for r in game["rooms"] if r["id"] == "B")
    meta = next(r for r in story["rooms"] if r["id"] == "B")
    for state, trigger, event_id in (("B_SECOND_PLATE", "cooked", "E018"), ("B_GHOST_MIRROR", "inspect_sink_after_cooked", "E019"), ("B_TWO_GHOSTS", "first_visit_ch11", "E085")):
        if state not in meta["variants"]:
            raise ValueError("Canonical kitchen variant is missing: " + state)
        event = next((e for e in story["events"] if e.get("event_id") == event_id), None)
        if not event or event.get("room") != "B" or event.get("trigger") != trigger:
            raise ValueError("Canonical kitchen trigger changed: " + event_id)
        if not any(eff.get("variant", {}).get("B") == state for eff in event.get("effects", [])):
            raise ValueError(event_id + " no longer activates " + state)
        asset_id, expected_sha = ASSETS[state]
        raw = (root / "site-assets/kitchen-states" / (state + ".webp")).read_bytes()
        if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP" or hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("Kitchen artwork failed format/checksum validation: " + state)
        value = {"mime": "image/webp", "data": base64.b64encode(raw).decode("ascii")}
        existing = game["assets"].get(asset_id)
        # This release deliberately replaces the previous provisional illustration.
        # Bytes above are checksum-verified before overriding the same stable asset ID.
        existing_variant = meta.setdefault("variantAssets", {}).get(state)
        if existing_variant is not None and existing_variant != asset_id and not (state == "B_TWO_GHOSTS" and existing_variant == "composite_b_two_ghosts"):
            raise ValueError("Conflicting kitchen variant mapping: " + state)
        game["assets"][asset_id] = value
        meta["variantAssets"][state] = asset_id
    return {"kitchen_states": {state: {"asset": ASSETS[state][0], "sha256": ASSETS[state][1]} for state in ASSETS}}
if __name__ == "__main__":
    raise SystemExit("Import apply_wave10 from build_pages_demo.py or sync_standalone_document_art.py")
