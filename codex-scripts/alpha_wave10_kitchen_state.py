#!/usr/bin/env python3
"""Attach the painted kitchen ghost-mirror state to canonical chapter 4."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "B_SECOND_PLATE": ("illustrated_B_SECOND_PLATE", "f0640b11eb5af34e4659320750b89984655d73b0051476674d16abf8a7fba4a9"),
    "B_GHOST_MIRROR": ("illustrated_B_GHOST_MIRROR", "0c330039a320dbb04391b5d418f9bd5aceb5f15ad905ed71430fb0fd1f02ad75"),
}
def apply_wave10(payload, root=ROOT):
    game = payload
    story = game["story"]["adventure"]
    if len(game["rooms"]) < 16 or len(story["events"]) != 112 or len(story["documents"]) != 30:
        raise ValueError("Canonical game/story counts changed")
    room = next(r for r in game["rooms"] if r["id"] == "B")
    meta = next(r for r in story["rooms"] if r["id"] == "B")
    for state, trigger, event_id in (("B_SECOND_PLATE", "cooked", "E018"), ("B_GHOST_MIRROR", "inspect_sink_after_cooked", "E019")):
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
        if existing is not None and existing != value:
            raise ValueError("Conflicting kitchen art asset: " + asset_id)
        existing_variant = meta.setdefault("variantAssets", {}).get(state)
        if existing_variant is not None and existing_variant != asset_id:
            raise ValueError("Conflicting kitchen variant mapping: " + state)
        game["assets"][asset_id] = value
        meta["variantAssets"][state] = asset_id
    return {"kitchen_states": {state: {"asset": ASSETS[state][0], "sha256": ASSETS[state][1]} for state in ASSETS}}
if __name__ == "__main__":
    raise SystemExit("Import apply_wave10 from build_pages_demo.py or sync_standalone_document_art.py")
