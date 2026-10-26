#!/usr/bin/env python3
"""Verify puzzle illustrations are embedded in the original playable story."""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "_site/index.html").read_text(encoding="utf8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
payload, _ = json.JSONDecoder().raw_decode(html.split(marker, 1)[1])
adventure = payload["story"]["adventure"]
original = json.loads((ROOT / "game-project/project.json").read_text(encoding="utf8"))["story"]["adventure"]
for key, expected in [("rooms", 16), ("events", 112)]:
    assert len(adventure[key]) == len(original[key]) == expected
    assert [item["id"] for item in adventure[key]] == [item["id"] for item in original[key]]
assert {x["id"]: x["text"] for x in adventure["documents"]} == {
    x["id"]: x["text"] for x in original["documents"]}
assert [x["id"] for x in adventure["actions"]] == [x["id"] for x in original["actions"]]
from alpha_wave7_puzzle_docs import PUZZLE_DOCS
for doc_id, (action_id, room, chapter, prefix, art_id, filename, sha) in PUZZLE_DOCS.items():
    art = adventure["illustratedProps"]
    assert art["action"][action_id] == art_id
    assert art["document"][doc_id] == art_id
    uri = art["image"][art_id]
    assert uri.startswith("data:image/svg+xml;base64,")
    raw = base64.b64decode(uri.split(",", 1)[1], validate=True)
    assert raw == (ROOT / "site-assets/airlock-archive-props" / filename).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha
    svg = ET.fromstring(raw)
    assert svg.tag.endswith("svg")
    assert not any(n.tag.endswith("script") for n in svg.iter())
    assert any(x["id"] == action_id and x["room"] == room
               and x["document"] == doc_id and x.get("when", {}).get("min") == chapter
               for x in adventure["actions"])
    assert any(x["id"] == doc_id and x["title"].startswith(prefix)
               for x in adventure["documents"])
    labels = ("ВХОД", "ПЕРЕХОД", "ВЫХОД", "КОНТРОЛЬ", "ПО РАДИО") if doc_id == "D22" else (
        "ПИЩЕБЛОК", "ГАЛЕРЕЯ", "РАДИО", "ИГНОРИРОВАТЬ")
    for label in labels:
        assert label.encode("utf8") in raw, (doc_id, label)
assert "const art=this.artData()?.action?.[id]" in html
assert "documentView(parent,doc)" in html and "this.documentView(box,d)" in html
print("PASS: D22/D23 canonical hints and art in original 16-room, 112-event game")
