"""Panorama Forge-style independent pixel regions for Tihaya Voda.

Tile data is authored, not inferred at runtime. The main panorama stays
unchanged; images are delivered as separate tiles, with web URLs or embedded
data URLs for standalone file:// play. No artificial resolution claims.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path
import shutil

MANIFEST = "production/panorama-detail-tiles.json"

def apply_panorama_details(payload: dict, root: Path, *, web_dir: Path | None = None) -> None:
    spec = json.loads((root / MANIFEST).read_text(encoding="utf8"))
    if spec.get("schema") != 1:
        raise ValueError("Unsupported panorama tile manifest version")
    result = []
    for row in spec["tiles"]:
        rect = row["rect"]
        if (len(rect) != 4 or not all(isinstance(v,(int,float)) and 0 <= v <= 1 for v in rect)
                or not rect[0] < rect[2] or not rect[1] < rect[3]):
            raise ValueError("Invalid UV tile: " + row["id"])
        path = Path(row["path"])
        if path.is_absolute() or ".." in path.parts or path.parts[:2] != ("site-assets", "panorama-patches"):
            raise ValueError("Tile source must be in site-assets/panorama-patches")
        file = root / path
        data = file.read_bytes()
        mime = row.get("mime", "image/png")
        if mime == "image/png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Invalid PNG tile: " + row["id"])
        if web_dir is None:
            src = "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")
        else:
            target = Path(web_dir) / "panorama-detail" / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
            src = "panorama-detail/" + path.name
        result.append({k:row[k] for k in ("id","room","rect","when","priority") if k in row} | {"src":src})
    payload["panoramaDetailTiles"] = result
    # Canonical game action becomes a direct physical interaction, not a modal
    # confirmation. Keep the existing story flag and allow E015 to unset the
    # visual state on later visits, so the player can align them again.
    for action in payload.get("story",{}).get("adventure",{}).get("actions",[]):
        if action.get("id") == "slippers":
            action["instant"] = True
            action["instantFeedback"] = "Тапочки стоят ровно."
            effects = action.setdefault("effects",[])
            if not any(x.get("set",{}).get("A_SHOES_SHIFTED") is False for x in effects):
                effects.append({"set":{"A_SHOES_SHIFTED":False}})
