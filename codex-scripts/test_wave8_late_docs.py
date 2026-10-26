#!/usr/bin/env python3
"""Regression test for late-game illustrated documents in the built demo."""
from __future__ import annotations
import base64, hashlib, json
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "D24": ("read_D24", "A", 11, "D24_personal_page", "03f77edc820d6265f83cef79fb60a5d94dc50ab038dcf3a735ead104504ae4b9"),
    "D25": ("read_D25", "H", 8, "D25_outgoing_receipt", "4558001b117633ca8f575296125022727131655947441b307b3c4df58013183c"),
    "D26": ("read_D26", "L", 12, "D26_irina_door_note", "4c37a8e8c9d44ebcf4f91a06c27a19f6b9bfd66cba33f64485ee6b15a1aff6e0"),
}
html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
payload, _ = json.JSONDecoder().raw_decode(html[html.index(marker) + len(marker):])
adv = payload["story"]["adventure"]
assert len(payload["rooms"]) == 16 and len(adv["events"]) == 112 and len(adv["documents"]) == 30
art = adv["illustratedProps"]
for doc_id, (action_id, room, chapter, art_id, sha) in EXPECTED.items():
    action = next(a for a in adv["actions"] if a["id"] == action_id)
    assert action["room"] == room and action["document"] == doc_id
    assert action["when"]["min"] == chapter
    assert any(e.get("document") == doc_id for e in action["effects"])
    assert art["action"][action_id] == art_id and art["document"][doc_id] == art_id
    uri = art["image"][art_id]
    prefix = "data:image/svg+xml;base64,"
    assert uri.startswith(prefix)
    raw = base64.b64decode(uri[len(prefix):], validate=True)
    assert hashlib.sha256(raw).hexdigest() == sha
    root = ET.fromstring(raw)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert not any(node.tag.endswith("script") for node in root.iter())
assert "ga-art-figure" in html and "Сюжетная иллюстрация" in html
print("PASS D24/D25/D26 artwork attached to canonical actions and journal; 16 rooms, 112 events, 30 documents preserved")
