#!/usr/bin/env python3
"""Regression tests for the three existing multi-room state-art integrations."""
import base64, json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
project = json.loads((ROOT/"game-project/project.json").read_text(encoding="utf-8"))
adventure = json.loads((ROOT/"studio/content/TIHAYA_VODA/adventure.json").read_text(encoding="utf-8"))
html = (ROOT/"game/index.html").read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
pos = html.index(marker) + len(marker); pos += len(html[pos:]) - len(html[pos:].lstrip())
game, _ = json.JSONDecoder().raw_decode(html[pos:])
expected = [("B","B_SECOND_PLATE"),("B","B_GHOST_MIRROR"),("C","C_MIRROR_LIGHT"),("F","F_ARCHIVE12"),("H","H_AFTER_V01")]
for room, state in expected:
    aid = next(r for r in adventure["rooms"] if r["id"]==room)["variantAssets"][state]
    entry = next(a for a in project["assets"] if a["id"]==aid)
    path = ROOT/"game-project"/entry["file"]
    assert path.exists() and path.read_bytes()[8:12] == b"WEBP"
    im = Image.open(path)
    assert im.size == ((1774,887) if aid.startswith("authored_C_") else (2048,1024)) and im.mode in ("RGB","RGBA")
    assert any(a.get("id")==aid and a.get("file")=="assets/variants/"+path.name for a in project["assets"])
    assert game["assets"][aid]["mime"] == "image/webp"
    assert base64.b64decode(game["assets"][aid]["data"])[8:12] == b"WEBP"
    for collection in (adventure["rooms"], project["story"]["adventure"]["rooms"], game["story"]["adventure"]["rooms"]):
        meta = next(r for r in collection if r["id"]==room)
        assert meta["variantAssets"][state] == aid
    assert state in next(r for r in game["story"]["adventure"]["rooms"] if r["id"]==room)["variants"]
assert game["panoramas"]["B"]["mime"] in ("image/png", "image/webp")
print("PASS: story-variant panoramas are embedded and mapped; default room panoramas remain intact.")
