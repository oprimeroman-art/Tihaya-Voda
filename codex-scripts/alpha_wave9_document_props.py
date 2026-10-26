#!/usr/bin/env python3
"""Attach canonical D27-D29 document artwork to the existing playable story."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "D27": ("read_D27", "D", 6, "РАДИОРУБКА / РАДИОГРАММА ИЗ 2028", "D27_radio_transmission", "D27_radio_transmission.svg", "726764aec794f7fd5c80e134644c46fe879f8efba900790490f6f2476727d58e", ("У нас четыре сотрудника в смене", "голос может принадлежать человеку")),
    "D28": ("read_D28", "E", 2, "ДИЗЕЛЬНАЯ / ПОДСКАЗКА НА ПАНЕЛИ", "D28_generator_bus_panel", "D28_generator_bus_panel.svg", "aecfed87b642bf3e89f1f74d33f47787ba6e80469e8b5704b17097dcc0d5cc55", ("ШИНА А — ПРЕДЕЛ 5", "ШИНА Б — ПРЕДЕЛ 5")),
    "D29": ("read_D29", "H", 8, "АРХИВ / ПИСЬМО АННЫ, ЧЕРНОВИК", "D29_anna_draft", "D29_anna_draft.svg", "1546b17aff50504175e82a074da67902a980d0436a984cb05f792e56eb78951e", ("Я вижу мужчину, которого не помню", "не оставил следов в снегу")),
}
def apply_wave9(payload, root=ROOT):
    adventure = payload["story"]["adventure"]
    if len(adventure["rooms"]) != 16 or len(adventure["events"]) != 112 or len(adventure["documents"]) != 30:
        raise ValueError("Canonical room/event/document counts changed")
    actions = {a["id"]: a for a in adventure["actions"]}
    docs = {d["id"]: d for d in adventure["documents"]}
    art = adventure.setdefault("illustratedProps", {})
    for key in ("image", "action", "document"):
        art.setdefault(key, {})
    for doc_id, (action_id, room, chapter, title, art_id, filename, expected_sha, fragments) in DOCS.items():
        action = actions[action_id]
        if action.get("room") != room or action.get("document") != doc_id or action.get("when", {}).get("min") != chapter:
            raise ValueError("Canonical action mapping changed: " + action_id)
        if not docs[doc_id]["title"].startswith(title):
            raise ValueError("Canonical document title changed: " + doc_id)
        if any(fragment not in docs[doc_id]["text"] for fragment in fragments):
            raise ValueError("Canonical document text check failed: " + doc_id)
        raw = (root / "site-assets/late-docs" / filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("Document art checksum mismatch: " + filename)
        svg = ET.fromstring(raw)
        if svg.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Invalid SVG root: " + filename)
        for node in svg.iter():
            if node.tag.endswith("script") or any(k.lower().endswith(("href", "onload", "onclick", "onerror")) for k in node.attrib):
                raise ValueError("External or executable SVG content prohibited: " + filename)
        uri = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        existing = (art["image"].get(art_id), art["action"].get(action_id), art["document"].get(doc_id))
        expected = (uri, art_id, art_id)
        if any(value is not None for value in existing):
            if existing == expected:
                continue
            raise ValueError("Conflicting existing illustration mapping: " + doc_id)
        art["image"][art_id] = uri
        art["action"][action_id] = art_id
        art["document"][doc_id] = art_id
    return {"late_document_art_wave9": len(DOCS)}
if __name__ == "__main__":
    raise SystemExit("Import apply_wave9 from build_pages_demo.py; this module does not rewrite canonical source files.")
