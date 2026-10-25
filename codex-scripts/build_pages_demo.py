#!/usr/bin/env python3
"""Publish the approved illustrated Tihaya Voda scene from existing live engine.

Reconstruct A/B/C approved painted images and manually authored hotspot corners
from the verified 37-part source bundle. No Blender, no new game logic, no
external browser dependencies, no edits to original game/index.html.
"""
from __future__ import annotations
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import argparse

ROOT=Path(__file__).resolve().parents[1]
CHUNKS=ROOT/"site-assets/illustrated"
SOURCE=ROOT/"game/index.html"
EXPECTED_SHA256="c674daf1114456c9d502c4e847d467992a0386c37cf20169ae13e47a5ef941e7"
EXPECTED_COUNT=37
QA_RE=re.compile(
    r'<script>\s*/\* KITCHEN_QA_PREVIEW_BEGIN \*/.*?'
    r'/\* KITCHEN_QA_PREVIEW_END \*/\s*</script>\s*',re.S)

def bundle():
    paths=sorted(CHUNKS.glob("part_*.b64"))
    assert len(paths)==EXPECTED_COUNT, f"Illustrated bundle incomplete: {len(paths)} != {EXPECTED_COUNT}"
    for i,p in enumerate(paths):
        assert p.name==f"part_{i:03}.b64",f"Unexpected split asset chunk: {p.name}"
    b64="".join(x.read_text(encoding="ascii").strip() for x in paths)
    archive=base64.b64decode(b64,validate=True)
    assert hashlib.sha256(archive).hexdigest()==EXPECTED_SHA256,"Illustrated asset archive checksum mismatch"
    with tarfile.open(fileobj=io.BytesIO(archive),mode="r:gz") as t:
        members={x.name:t.extractfile(x).read() for x in t.getmembers() if x.isfile()}
    assert set(members)=={"A.webp","B.webp","C.webp","manifest.json"}
    manifest=json.loads(members["manifest.json"].decode("utf-8"))
    assert manifest["schema"]==1
    assert manifest["required"]==["A","B","C"]
    for k in "ABC":
        blob=members[k+".webp"]
        assert blob[:4]==b"RIFF" and blob[8:12]==b"WEBP"
    return members,manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,default=ROOT/"_site")
    args=ap.parse_args()
    members,manifest=bundle()
    html=SOURCE.read_text(encoding="utf-8")
    assert html.count("window.BUILT_GAME=")==1
    marker="window.BUILT_GAME="
    start=html.index(marker)+len(marker)
    payload,end=json.JSONDecoder().raw_decode(html[start:])
    assert len(payload["rooms"])>=16,"Never replace original story rooms"
    assert len(payload.get("story",{}).get("adventure",{}).get("events",[]))>=100
    applied={}
    for roomid in "ABC":
        room=next(x for x in payload["rooms"] if x["id"]==roomid)
        existing={o["id"]:o for o in room["objects"]}
        authored=manifest["rooms"][roomid]["objects"]
        if set(existing)!=set(authored):
            raise ValueError(f"Interaction IDs changed in {roomid}; recheck art anchors")
        for oid,desc in authored.items():
            points=desc["corners"]
            assert len(points)==4 and all(0<=p["u"]<=1 and 0<=p["v"]<=1 for p in points)
            existing[oid]["corners"]=points
        art=members[roomid+".webp"]
        payload["panoramas"][roomid]={"mime":"image/webp","data":base64.b64encode(art).decode("ascii")}
        applied[roomid]=len(authored)
    # Illustrate the next original story locations; no new quest text or events.
    from alpha_wave2 import apply_wave2
    applied.update(apply_wave2(payload,ROOT))
    # Production demo uses original story but approved images.
    # No procedural kitchen override or different QA SAVE_KEY.
    html,count=QA_RE.subn("",html)
    if "KITCHEN_QA_PREVIEW_BEGIN" in html:
        raise ValueError("Leftover temporary 3D art preview injection")
    html=html[:start]+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+html[start+end:]
    html=html.replace("</head>",'<meta name="robots" content="noindex,nofollow,noarchive"></head>',1)
    html=html.replace("<title>ПОЛЯРНАЯ СМЕНА</title>",
                      "<title>Протокол «Тихая вода» — демо</title>",1)
    assert html.count('window.BUILT_GAME=')==1
    assert all(payload["panoramas"][id]["mime"]=="image/webp" for id in "ABCDH")
    dest=args.output
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"index.html").write_text(html,encoding="utf-8")
    (dest/"robots.txt").write_text("User-agent: *
Disallow: /
",encoding="ascii")
    # Source only from the game, not the whole private repository.
    print("PUBLISHED",dest/"index.html","bytes",len(html.encode("utf-8")),
          "approved_rooms",applied,"panoramas",len(payload["panoramas"]))
if __name__=="__main__":
    main()
