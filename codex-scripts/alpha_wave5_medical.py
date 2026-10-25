#!/usr/bin/env python3
"""Illustrate the two canonical chapter-10 medical documents in the existing UI.

Adds only offline SVG data to the pre-existing illustratedProps mapping.
Does not add events, change rooms, rewrite text or touch the game engine.
"""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "site-assets/medical-props"
MEDICAL = {
    "D17": ("read_D17", "D17_patient_record", "D17_patient_record.svg",
            "e899a6e150574585dd30fc912137a70d2441328ad7b7d8d8e8871cb3e37a1bda"),
    "D18": ("read_D18", "D18_rhythm_chart", "D18_rhythm_chart.svg",
            "0cd9ef55d6fd36ec9d9e85fefd29b893f6d88df6b75f69bd975d7ac23fe7ed58"),
}


def apply_medical_props(payload, root=ROOT):
    adventure = payload["story"]["adventure"]
    actions = {item["id"]: item for item in adventure["actions"]}
    docs = {item["id"]: item for item in adventure["documents"]}
    art = adventure["illustratedProps"]
    for doc_id, (action_id, art_id, filename, expected_sha) in MEDICAL.items():
        action = actions[action_id]
        if action.get("room") != "I" or action.get("document") != doc_id:
            raise ValueError("Canonical medpoint trigger changed: " + action_id)
        if not docs[doc_id]["title"].startswith("МЕДПУНКТ /"):
            raise ValueError("Canonical medical document changed: " + doc_id)
        raw = (root / "site-assets/medical-props" / filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("Medical art checksum mismatch: " + filename)
        svg = ET.fromstring(raw)
        if svg.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Not an SVG document: " + filename)
        if any(node.tag.endswith("script") for node in svg.iter()):
            raise ValueError("SVG script is not allowed: " + filename)
        if any(art_id in section for section in (art["image"], art["action"], art["document"])):
            raise ValueError("Medical artwork already mapped: " + art_id)
        if action_id in art["action"] or doc_id in art["document"]:
            raise ValueError("Existing story artwork would be replaced: " + doc_id)
        art["image"][art_id] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        art["action"][action_id] = art_id
        art["document"][doc_id] = art_id
    return {"medical_documents": len(MEDICAL)}
