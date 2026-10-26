#!/usr/bin/env python3
"""Composite existing authored transparent art into playable full-room variant panoramas."""
import base64, json, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "game-project/project.json"
ADVENTURE = ROOT / "studio/content/TIHAYA_VODA/adventure.json"
REPORT = ROOT / "reports/adventure.json"
GAME_HTML = ROOT / "game/index.html"
EDITOR_HTML = ROOT / "game-editor/index.html"
OUT = ROOT / "game-project/assets/variants"
OVERLAYS = [
    ("C", "C_MIRROR_LIGHT", "C_C_MIRROR_LIGHT.webp", "Отражение фонаря в зеркале"),
    ("F", "F_ARCHIVE12", "F_F_ARCHIVE12.webp", "Табличка АРХИВ-12"),
    ("H", "H_AFTER_V01", "H_H_AFTER_V01.webp", "Приоткрытый шкаф и записка после V01"),
]

def update_list(existing, item):
    return [x for x in (existing or []) if x.get("id") != item["id"]] + [item]

def payload(html):
    marker = "window.BUILT_GAME="
    if html.count(marker) != 1:
        raise ValueError("Expected one window.BUILT_GAME payload")
    pos = html.index(marker) + len(marker)
    pos += len(html[pos:]) - len(html[pos:].lstrip())
    game, end = json.JSONDecoder().raw_decode(html[pos:])
    return game, pos, end

def patch_html(html, game):
    marker = "window.BUILT_GAME="
    _, pos, end = payload(html)
    encoded = json.dumps(game, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return html[:pos] + encoded + html[pos + end:]

def main():
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    adventure = json.loads(ADVENTURE.read_text(encoding="utf-8"))
    html = GAME_HTML.read_text(encoding="utf-8")
    game, _, _ = payload(html)
    OUT.mkdir(parents=True, exist_ok=True)
    generated = []
    for room, state, filename, name in OVERLAYS:
        base_path = ROOT / "game-project/rooms" / room / "original.png"
        overlay_path = ROOT / "art/overlays" / filename
        if not base_path.exists() or not overlay_path.exists():
            raise FileNotFoundError(f"Missing source art for {room}/{state}")
        base = Image.open(base_path).convert("RGBA")
        overlay = Image.open(overlay_path).convert("RGBA")
        if base.size != (2048, 1024) or overlay.size != base.size:
            raise ValueError(f"Panorama dimensions mismatch for {state}: {base.size}, {overlay.size}")
        if overlay.getchannel("A").getbbox() is None:
            raise ValueError(f"Overlay is fully transparent: {state}")
        composite = Image.alpha_composite(base, overlay).convert("RGB")
        asset_id = "composite_" + state.lower()
        out_path = OUT / (asset_id + ".webp")
        composite.save(out_path, "WEBP", lossless=True, method=6)
        raw = out_path.read_bytes()
        if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
            raise ValueError(f"Invalid composite panorama: {state}")
        value = {"mime": "image/webp", "data": base64.b64encode(raw).decode("ascii")}
        existing = game.setdefault("assets", {}).get(asset_id)
        if existing is not None and existing != value:
            raise ValueError(f"Conflicting built asset {asset_id}")
        game["assets"][asset_id] = value
        project_asset = {"id": asset_id, "name": name, "mime": "image/webp", "file": "assets/variants/" + out_path.name}
        project["assets"] = update_list(project.get("assets", []), project_asset)
        for collection in (adventure["rooms"], project["story"]["adventure"]["rooms"], game["story"]["adventure"]["rooms"]):
            meta = next((r for r in collection if r["id"] == room), None)
            if meta is None: raise ValueError(f"Missing room metadata {room}")
            if state not in meta.get("variants", []):
                raise ValueError(f"Missing canonical variant {state}")
            meta.setdefault("variantAssets", {})[state] = asset_id
        generated.append((state, asset_id, len(raw)))
    PROJECT.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ADVENTURE.write_text(json.dumps(adventure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if REPORT.parent.exists():
        REPORT.write_text(json.dumps(adventure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    GAME_HTML.write_text(patch_html(html, game), encoding="utf-8")
    if EDITOR_HTML.exists():
        editor_html = EDITOR_HTML.read_text(encoding="utf-8")
        if "window.BUILT_GAME=" in editor_html:
            editor_game, _, _ = payload(editor_html)
            for state, asset_id, _ in generated:
                value = game["assets"][asset_id]
                editor_game.setdefault("assets", {})[asset_id] = value
            for room, state, filename, name in OVERLAYS:
                meta = next(r for r in editor_game["story"]["adventure"]["rooms"] if r["id"] == room)
                meta.setdefault("variantAssets", {})[state] = "composite_" + state.lower()
            EDITOR_HTML.write_text(patch_html(editor_html, editor_game), encoding="utf-8")
    print("PASS composed and embedded", len(generated), "room-state panoramas:", ", ".join(f"{s}={n}B" for s,_,n in generated))

if __name__ == "__main__":
    main()
