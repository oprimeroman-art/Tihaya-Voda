#!/usr/bin/env python3
"""Regression guard for the chapter-4 kitchen ghost-mirror panorama."""
import base64,hashlib,json
from pathlib import Path
from web_assets import hydrate_payload
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
 "B_SECOND_PLATE": ("illustrated_B_SECOND_PLATE", "6f4cc9c45b813ca1f0a6d5455c61e5d0ff3a231ee498b6fc794d2fdf67c90368", "E018", "cooked"),
 "B_GHOST_MIRROR": ("illustrated_B_GHOST_MIRROR", "168d08a767f2e7727f92d3d8f3c00e2da007904c74f84a6bb196e30e80043c0b", "E019", "inspect_sink_after_cooked"),
 "B_TWO_GHOSTS": ("illustrated_B_TWO_GHOSTS", "641007fec25de4740079cdb1420055d6c1d6d0a7e211a255688c69668fd915d2", "E085", "first_visit_ch11"),
}
def verify(path):
 html=path.read_text(encoding="utf-8")
 assert html.count("window.BUILT_GAME=")==1,path
 game,_=json.JSONDecoder().raw_decode(html[html.index("window.BUILT_GAME=")+len("window.BUILT_GAME="):])
 game=hydrate_payload(game,path.parent)
 story=game["story"]["adventure"]
 assert len(game["rooms"])>=16 and len(story["events"])==112 and len(story["documents"])==30
 room=next(r for r in story["rooms"] if r["id"]=="B")
 for state,(asset_id,sha,event_id,trigger) in EXPECTED.items():
  assert state in room["variants"] and room["variantAssets"][state]==asset_id
  event=next(e for e in story["events"] if e.get("event_id")==event_id)
  assert event["trigger"]==trigger and any(x.get("variant",{}).get("B")==state for x in event["effects"])
  art=game["assets"][asset_id]
  assert art["mime"]=="image/webp"
  raw=base64.b64decode(art["data"],validate=True)
  assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP" and hashlib.sha256(raw).hexdigest()==sha
 assert "function adventureApplyVariant" in html and "B_GHOST_MIRROR" in html and "illustrated_B_GHOST_MIRROR" in html
 print("PASS",path.relative_to(ROOT),"both kitchen scene states embedded")
verify(ROOT/"game/index.html")
verify(ROOT/"game-editor/index.html")
if (ROOT/"_site/index.html").exists():
 verify(ROOT/"_site/index.html")
print("PASS E018→B_SECOND_PLATE and E019→B_GHOST_MIRROR; canonical counts unchanged")
