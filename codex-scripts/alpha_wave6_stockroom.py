#!/usr/bin/env python3
"""Illustrate existing stockroom F documents D19/D20, without changing canon."""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STOCKROOM = {
    "D19": ("read_D19", "D19_archive_crate", "D19_archive_crate.svg",
            "1f18ac0b6b31731591c5b5342d0d35b0c1b89fb60f2f89af0b9548ccc51c58c9", 3),
    "D20": ("read_D20", "D20_food_inventory", "D20_food_inventory.svg",
            "0db8de2eb9d69cac219e3da0846b18510f589c803056aca9a17c286116b8e0f2", 4),
}


def apply_stockroom_props(payload, root=ROOT):
    adventure = payload["story"]["adventure"]
    actions = {a["id"]: a for a in adventure["actions"]}
    documents = {d["id"]: d for d in adventure["documents"]}
    art = adventure["illustratedProps"]
    if len(adventure["rooms"]) != 16 or len(adventure["events"]) != 112:
        raise ValueError("Unexpected canonical room/event count")
    for doc_id, (action_id, art_id, filename, sha, chapter) in STOCKROOM.items():
        action = actions[action_id]
        if (action.get("room") != "F" or action.get("document") != doc_id
                or action.get("when", {}).get("min") != chapter
                or not any(e.get("document") == doc_id for e in action.get("effects", []))):
            raise ValueError("Canonical stockroom trigger changed: " + action_id)
        if not documents[doc_id]["title"].startswith("СКЛАД /"):
            raise ValueError("Canonical stockroom document changed: " + doc_id)
        raw = (root / "site-assets/stockroom-props" / filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError("Stockroom art checksum mismatch: " + filename)
        svg = ET.fromstring(raw)
        if svg.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Not a valid SVG: " + filename)
        for node in svg.iter():
            if node.tag.endswith("script") or any(
                    k.lower().endswith(("href", "onload", "onclick")) for k in node.attrib):
                raise ValueError("External/script SVG content prohibited: " + filename)
        if art_id in art["image"] or action_id in art["action"] or doc_id in art["document"]:
            raise ValueError("Refusing to overwrite existing illustration: " + doc_id)
        art["image"][art_id] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        art["action"][action_id] = art_id
        art["document"][doc_id] = art_id
    return {"stockroom_documents": len(STOCKROOM)}
