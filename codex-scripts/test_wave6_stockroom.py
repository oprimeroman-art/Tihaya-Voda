#!/usr/bin/env python3
"""Assert published offline game shows the original D19/D20 stockroom documents."""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
payload, _ = json.JSONDecoder().raw_decode(html.split(marker, 1)[1])
adv = payload["story"]["adventure"]
original = json.loads((ROOT / "game-project/project.json").read_text(encoding="utf-8"))["story"]["adventure"]
assert len(adv["events"]) == len(original["events"]) == 112
assert len(adv["rooms"]) == len(original["rooms"]) == 16
assert [x["id"] for x in adv["events"]] == [x["id"] for x in original["events"]]
assert [x["id"] for x in adv["rooms"]] == [x["id"] for x in original["rooms"]]
assert {x["id"]: x["text"] for x in adv["documents"]} == {x["id"]: x["text"] for x in original["documents"]}
from alpha_wave6_stockroom import STOCKROOM

for doc_id, (action_id, art_id, filename, sha, chapter) in STOCKROOM.items():
    assert adv["illustratedProps"]["action"][action_id] == art_id
    assert adv["illustratedProps"]["document"][doc_id] == art_id
    uri = adv["illustratedProps"]["image"][art_id]
    assert uri.startswith("data:image/svg+xml;base64,")
    raw = base64.b64decode(uri.split(",", 1)[1], validate=True)
    assert hashlib.sha256(raw).hexdigest() == sha
    assert raw == (ROOT / "site-assets/stockroom-props" / filename).read_bytes()
    svg = ET.fromstring(raw)
    assert svg.tag.endswith("svg")
    assert not any(n.tag.endswith("script") for n in svg.iter())
    assert any(x["id"] == action_id and x.get("room") == "F" and
               x.get("document") == doc_id and x.get("when", {}).get("min") == chapter
               for x in adv["actions"])
    assert any(x["id"] == doc_id and x["title"].startswith("СКЛАД /") for x in adv["documents"])
    if doc_id == "D19":
        assert "2 — 4 — 1 — 3".encode() in raw
    if doc_id == "D20":
        assert b"2028" in raw
assert "const art=this.artData()?.action?.[id]" in html
assert "documentView(parent,doc)" in html and "this.documentView(box,d)" in html
print("PASS: D19/D20 art integrated into original 16-room, 112-event story")
