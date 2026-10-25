#!/usr/bin/env python3
"""Verify actual built offline game preserves canon and displays medical props."""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BUILT = ROOT / "_site/index.html"
html = BUILT.read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
payload, _ = json.JSONDecoder().raw_decode(html.split(marker, 1)[1])
adv = payload["story"]["adventure"]
assert len(adv["events"]) == 112
assert len(adv["rooms"]) == 16
from alpha_wave5_medical import MEDICAL

for doc_id, (action_id, art_id, filename, expected_sha) in MEDICAL.items():
    assert adv["illustratedProps"]["action"][action_id] == art_id
    assert adv["illustratedProps"]["document"][doc_id] == art_id
    uri = adv["illustratedProps"]["image"][art_id]
    assert uri.startswith("data:image/svg+xml;base64,")
    raw = base64.b64decode(uri.split(",", 1)[1], validate=True)
    assert hashlib.sha256(raw).hexdigest() == expected_sha
    assert raw == (ROOT / "site-assets/medical-props" / filename).read_bytes()
    assert ET.fromstring(raw).tag.endswith("svg")
    assert any(x["id"] == action_id and x.get("document") == doc_id and x.get("room") == "I" for x in adv["actions"])
    assert any(x["id"] == doc_id and x["title"].startswith("МЕДПУНКТ /") for x in adv["documents"])
assert "const art=this.artData()?.action?.[id]" in html
assert "const a=this.artData()?.document?.[d.id]" in html
print("PASS: D17 and D18 canonical medical props in playable offline build")
