#!/usr/bin/env python3
"""Regression guard for the chapter-4 kitchen ghost-mirror panorama."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED="0c330039a320dbb04391b5d418f9bd5aceb5f15ad905ed71430fb0fd1f02ad75"
def verify(path):
 html=path.read_text(encoding="utf-8")
 assert html.count("window.BUILT_GAME=")==1,path
 game,_=json.JSONDecoder().raw_decode(html[html.index("window.BUILT_GAME=")+len("window.BUILT_GAME="):])
 story=game["story"]["adventure"]
 assert len(game["rooms"])>=16 and len(story["events"])==112 and len(story["documents"])==30
 room=next(r for r in story["rooms"] if r["id"]=="B")
 assert "B_GHOST_MIRROR" in room["variants"]
 assert room["variantAssets"]["B_GHOST_MIRROR"]=="illustrated_B_GHOST_MIRROR"
 event=next(e for e in story["events"] if e.get("event_id")=="E019")
 assert event["trigger"]=="inspect_sink_after_cooked" and any(x.get("variant",{}).get("B")=="B_GHOST_MIRROR" for x in event["effects"])
 art=game["assets"]["illustrated_B_GHOST_MIRROR"]
 assert art["mime"]=="image/webp"
 raw=base64.b64decode(art["data"],validate=True)
 assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP" and hashlib.sha256(raw).hexdigest()==EXPECTED
 assert "function adventureApplyVariant" in html and "B_GHOST_MIRROR" in html and "illustrated_B_GHOST_MIRROR" in html
 print("PASS",path.relative_to(ROOT),"kitchen ghost-mirror state embedded",len(raw),"bytes")
verify(ROOT/"game/index.html")
verify(ROOT/"game-editor/index.html")
if (ROOT/"_site/index.html").exists():
 verify(ROOT/"_site/index.html")
print("PASS B_GHOST_MIRROR: E019 and canonical counts unchanged")
