#!/usr/bin/env python3
"""Add illustrations to two existing puzzle documents, without changing story logic."""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "site-assets/airlock-archive-props"
PUZZLE_DOCS = {
    "D22": ("read_D22", "J", 7, "ШЛЮЗ /", "D22_airlock_algorithm", "D22_airlock_algorithm.svg", "8026d194928c0810394d7e1eb3dff546d5472598f5fd3b2c8adb6e3d64eb5bd3"),
    "D23": ("read_D23", "H", 8, "АРХИВ /", "D23_vhs_sync", "D23_vhs_sync.svg", "8e30b46400a42ffa821d49c5fb7fe27d9299af34b8f0148deceaac6cc808b956"),
}

def apply_puzzle_docs(payload, root=ROOT):
    adventure = payload["story"]["adventure"]
    if len(adventure["rooms"]) != 16 or len(adventure["events"]) != 112:
        raise ValueError("Canonical room/event count changed")
    actions = {action["id"]: action for action in adventure["actions"]}
    documents = {doc["id"]: doc for doc in adventure["documents"]}
    art = adventure["illustratedProps"]
    for doc_id, (action_id, room, chapter, prefix, art_id, filename, expected_sha) in PUZZLE_DOCS.items():
        action = actions[action_id]
        if (action.get("room") != room or action.get("document") != doc_id
                or action.get("when", {}).get("min") != chapter
                or not any(effect.get("document") == doc_id for effect in action.get("effects", []))):
            raise ValueError("Canonical action trigger changed: " + action_id)
        if not documents[doc_id]["title"].startswith(prefix):
            raise ValueError("Canonical document title changed: " + doc_id)
        raw = (root / "site-assets/airlock-archive-props" / filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("Illustration checksum mismatch: " + filename)
        svg = ET.fromstring(raw)
        if svg.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Invalid SVG: " + filename)
        for node in svg.iter():
            if node.tag.endswith("script") or any(
                    key.lower().endswith(("href", "onload", "onclick"))
                    for key in node.attrib):
                raise ValueError("External or executable SVG content prohibited: " + filename)
        if (art_id in art["image"] or action_id in art["action"] or doc_id in art["document"]):
            raise ValueError("Refusing to replace existing canonical illustration: " + doc_id)
        art["image"][art_id] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        art["action"][action_id] = art_id
        art["document"][doc_id] = art_id
    return {"canonical_puzzle_documents": len(PUZZLE_DOCS)}
