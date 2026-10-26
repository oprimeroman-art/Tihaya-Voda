#!/usr/bin/env python3
"""Regression test for late-game illustrated documents in the built demo."""
from __future__ import annotations
import base64, hashlib, json
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "D24": ("read_D24", "A", 11, "D24_personal_page", "73e3270565a720c81a1f5a7382eac6783739eeee6bc828fe42da1acecd7d3953"),
    "D25": ("read_D25", "H", 8, "D25_outgoing_receipt", "f2af4ca4b39063c9760755a232110e74db8ff0e6af2d759eb910c098b34fa920"),
    "D26": ("read_D26", "L", 12, "D26_irina_door_note", "a176877f4596e1a34f4fd22eb223948abd77e477ad3781c397009dcd4acc4273"),
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
    assert root.attrib.get("width") == "720" and root.attrib.get("height") == "960"
    assert not any(node.tag.endswith("script") for node in root.iter())
    if doc_id == "D25":
        assert "КОПИЯ 02" not in raw.decode("utf-8")
assert "ga-art-figure" in html and "Сюжетная иллюстрация" in html
print("PASS D24/D25/D26 artwork attached to canonical actions and journal; 16 rooms, 112 events, 30 documents preserved")
