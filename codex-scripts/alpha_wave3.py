#!/usr/bin/env python3
"""Склад F: существующие сюжетные события + три рисунка из раскадровки."""
from __future__ import annotations
import base64, hashlib, io, json, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "site-assets/alpha-wave3"
ARCHIVE_SHA256 = "f345d7320c5c83b6144aa446a5c41afc40946e3677cc51377e7ef883cac25c87"
PARTS = 15
STATES = ("F_NORMAL", "F_ARCHIVE12", "F_SUIT_STANDING")
# Preliminary clickable centres on the original F illustration;
# user can precisely correct all 4 corners later in Panorama Studio.
ACTION_CENTRES = {
    "take_FUSE_3": (.15, .45),
    "PLUMB_SEQ": (.57, .62),
    "count_cans": (.39, .47),
    "read_D05": (.30, .44),
    "read_D19": (.61, .51),
    "read_D20": (.81, .48),
}

def load():
    files = sorted(CHUNK_DIR.glob("part_*.b64"))
    if len(files) != PARTS: raise ValueError(f"F warehouse art: missing parts ({len(files)}/{PARTS})")
    if any(p.name != f"part_{i:03}.b64" for i,p in enumerate(files)):
        raise ValueError("Warehouse art chunks out of order")
    raw = base64.b64decode("".join(p.read_text("ascii").strip() for p in files), validate=True)
    if hashlib.sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Warehouse art checksum mismatch")
    with tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz") as archive:
        data = {entry.name: archive.extractfile(entry).read() for entry in archive if entry.isfile()}
    if set(data) != {x + ".webp" for x in STATES} | {"manifest.json"}:
        raise ValueError("Warehouse image state filenames mismatch")
    manifest = json.loads(data["manifest.json"].decode("utf-8"))
    if manifest["room"] != "F" or set(manifest["variant_names"]) != set(STATES):
        raise ValueError("Wrong illustrated room manifest")
    for state in STATES:
        blob = data[state + ".webp"]
        if blob[:4] != b"RIFF" or blob[8:12] != b"WEBP":
            raise ValueError("Warehouse is not a WebP illustration: "+state)
        if hashlib.sha256(blob).hexdigest() != manifest["sha256"][state]:
            raise ValueError("Warehouse illustration corrupt: "+state)
    return data

def corners(u,v,w=.125,h=.12):
    u0=max(0,round(u-w/2,5));u1=min(1,round(u+w/2,5))
    v0=max(0,round(v-h/2,5));v1=min(1,round(v+h/2,5))
    return [{"u":u0,"v":v0},{"u":u1,"v":v0},{"u":u1,"v":v1},{"u":u0,"v":v1}]

def apply_wave3(game,root=ROOT):
    bundle = load()
    room = next(r for r in game["rooms"] if r["id"]=="F")
    variant_room = next(r for r in game["story"]["adventure"]["rooms"] if r["id"]=="F")
    if set(variant_room["variants"]) != set(STATES):
        raise ValueError("The original warehouse story variants have changed")
    actions = {o["tourKey"][3:] for o in room["objects"] if o.get("tourKey","").startswith("ga:")}
    if actions != set(ACTION_CENTRES):
        raise ValueError("The original warehouse story interactions have changed: "+repr(actions ^ set(ACTION_CENTRES)))
    for o in room["objects"]:
        action = o.get("tourKey","")[3:]
        if action in ACTION_CENTRES:
            o["corners"] = corners(*ACTION_CENTRES[action])
    for state in STATES:
        key="illustrated_"+state
        game["assets"][key]={"mime":"image/webp","data":base64.b64encode(bundle[state+".webp"]).decode("ascii")}
        variant_room["variantAssets"][state] = key
    game["panoramas"]["F"] = game["assets"]["illustrated_F_NORMAL"]
    return {"F":{"actions":len(ACTION_CENTRES),"variants":len(STATES)}}
