#!/usr/bin/env python3
"""Attach the painted kitchen ghost-mirror state to canonical chapter 4."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSET = "illustrated_B_GHOST_MIRROR"
EXPECTED_SHA256 = "0c330039a320dbb04391b5d418f9bd5aceb5f15ad905ed71430fb0fd1f02ad75"
def apply_wave10(payload, root=ROOT):
    game = payload
    story = game["story"]["adventure"]
    if len(game["rooms"]) < 16 or len(story["events"]) != 112 or len(story["documents"]) != 30:
        raise ValueError("Canonical game/story counts changed")
    room = next(r for r in game["rooms"] if r["id"] == "B")
    meta = next(r for r in story["rooms"] if r["id"] == "B")
    if "B_GHOST_MIRROR" not in meta["variants"]:
        raise ValueError("Canonical kitchen variant B_GHOST_MIRROR is missing")
    event = next((e for e in story["events"] if e.get("event_id") == "E019"), None)
    if not event or event.get("room") != "B" or event.get("trigger") != "inspect_sink_after_cooked":
        raise ValueError("Canonical E019 kitchen trigger changed")
    if not any(eff.get("variant", {}).get("B") == "B_GHOST_MIRROR" for eff in event.get("effects", [])):
        raise ValueError("E019 no longer activates the kitchen ghost-mirror state")
    raw = (root / "site-assets/kitchen-states/B_GHOST_MIRROR.webp").read_bytes()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP" or hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Kitchen ghost-mirror artwork failed format/checksum validation")
    encoded = base64.b64encode(raw).decode("ascii")
    value = {"mime": "image/webp", "data": encoded}
    existing = game["assets"].get(ASSET)
    if existing is not None and existing != value:
        raise ValueError("Conflicting existing kitchen art asset")
    existing_variant = meta.setdefault("variantAssets", {}).get("B_GHOST_MIRROR")
    if existing_variant is not None and existing_variant != ASSET:
        raise ValueError("Conflicting kitchen variant mapping")
    game["assets"][ASSET] = value
    meta["variantAssets"]["B_GHOST_MIRROR"] = ASSET
    return {"kitchen_ghost_mirror": {"variant": "B_GHOST_MIRROR", "bytes": len(raw), "sha256": EXPECTED_SHA256}}
if __name__ == "__main__":
    raise SystemExit("Import apply_wave10 from build_pages_demo.py or sync_standalone_document_art.py")
