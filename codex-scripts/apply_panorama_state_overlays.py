#!/usr/bin/env python3
"""Composite existing authored transparent art into playable full-room variant panoramas."""
import base64, json, re, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "game-project/project.json"
ADVENTURE = ROOT / "studio/content/TIHAYA_VODA/adventure.json"
REPORT = ROOT / "reports/adventure.json"
GAME_HTML = ROOT / "game/index.html"
EDITOR_HTML = ROOT / "game-editor/index.html"
OUT = ROOT / "game-project/assets/variants"
OVERLAYS = [
    ("C", "C_MIRROR_LIGHT", "C_C_MIRROR_LIGHT.webp", "ÐÑÑÐ°Ð¶ÐµÐ½Ð¸Ðµ ÑÐ¾Ð½Ð°ÑÑ Ð² Ð·ÐµÑÐºÐ°Ð»Ðµ"),
    ("F", "F_ARCHIVE12", "F_F_ARCHIVE12.webp", "Ð¢Ð°Ð±Ð»Ð¸ÑÐºÐ° ÐÐ Ð¥ÐÐ-12"),
    ("H", "H_AFTER_V01", "H_H_AFTER_V01.webp", "ÐÑÐ¸Ð¾ÑÐºÑÑÑÑÐ¹ ÑÐºÐ°Ñ Ð¸ Ð·Ð°Ð¿Ð¸ÑÐºÐ° Ð¿Ð¾ÑÐ»Ðµ V01"),
    ("D", "D_FALSE_MONITOR", "D_D_FALSE_MONITOR.webp", "Ложное изображение в мониторе"),
    ("D", "D_LATE_MIRROR", "D_D_LATE_MIRROR.webp", "Позднее отражение в экране"),
    ("B", "B_TWO_GHOSTS", "B_B_TWO_GHOSTS.webp", "Два отражения в зеркале"),
    ("D", "D_DOUBLE_ACTS", "D_D_DOUBLE_ACTS.webp", "Дублирующиеся акты инцидента"),
    ("H", "H_ANNA_GLASS", "H_H_ANNA_GLASS.webp", "Отражение Анны в стекле"),
    ("G", "G_P17", "G_G_P17.webp", "Образец P-17 в незамерзающей воде"),
    ("G", "G_MIRROR_DOOR", "G_G_MIRROR_DOOR.webp", "Дверь в отражении линзы"),
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

def generate_first_act_state_overlays():
    """Create deterministic transparent inserts aligned to existing first-act mirror/monitor UVs."""
    overlay_dir = ROOT / "art/overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    width, height = 2048, 1024
    # Width follows the actual rendered wall panel: side-wall monitor is narrower than the rear-wall screen.
    states = {
        "D_D_FALSE_MONITOR.webp": (0.29, 0.42, 54, 42, "false"),
        "D_D_LATE_MIRROR.webp": (0.57, 0.42, 70, 42, "mirror"),
        "B_B_TWO_GHOSTS.webp": (0.29, 0.53, 54, 42, "twins"),
        "D_D_DOUBLE_ACTS.webp": (0.85, 0.53, 54, 42, "acts"),
        "H_H_ANNA_GLASS.webp": (0.29, 0.42, 54, 42, "anna"),
        "G_G_P17.webp": (0.29, 0.42, 54, 42, "p17"),
        "G_G_MIRROR_DOOR.webp": (0.57, 0.42, 70, 42, "door"),
    }
    for filename, (u, v, panel_width, panel_height, mode) in states.items():
        w, h = panel_width, panel_height
        x0, y0 = round(u * width - w / 2), round(v * height - h / 2)
        panel = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        pixels = panel.load()
        for y in range(h):
            for x in range(w):
                nx = abs(x / max(1, w - 1) - 0.5) * 2
                ny = abs(y / max(1, h - 1) - 0.5) * 2
                glow = max(0, 1 - nx * 0.78 - ny * 0.42)
                if mode == "false":
                    pixels[x, y] = (int(7 + 8 * glow), int(16 + 26 * glow), int(19 + 31 * glow), 255)
                elif mode == "twins":
                    pixels[x, y] = (int(21 + 15 * glow), int(28 + 18 * glow), int(27 + 17 * glow), 255)
                elif mode == "acts":
                    pixels[x, y] = (int(174 + 18 * glow), int(165 + 19 * glow), int(137 + 15 * glow), 255)
                elif mode == "anna":
                    pixels[x, y] = (int(23 + 10 * glow), int(35 + 15 * glow), int(34 + 14 * glow), 255)
                elif mode == "p17":
                    pixels[x, y] = (int(23 + 22 * glow), int(37 + 27 * glow), int(40 + 30 * glow), 255)
                elif mode == "door":
                    pixels[x, y] = (int(6 + 6 * glow), int(13 + 13 * glow), int(15 + 15 * glow), 255)
                else:
                    pixels[x, y] = (int(5 + 7 * glow), int(13 + 15 * glow), int(17 + 18 * glow), 255)
        draw = ImageDraw.Draw(panel, "RGBA")
        if mode == "false":
            # A second impossible corridor inside the dead screen, with a distant figure.
            left, top, right, bottom = int(w*.38), int(h*.10), int(w*.66), int(h*.91)
            draw.rectangle((left, top, right, bottom), fill=(18,31,32,255), outline=(88,121,115,220), width=2)
            draw.rectangle((left+7, top+5, right-7, bottom-5), fill=(6,14,17,255))
            draw.line((w*.51,h*.15,w*.51,h*.88), fill=(167,187,165,150), width=2)
            draw.ellipse((w*.485,h*.28,w*.535,h*.44), fill=(2,5,7,255))
            draw.polygon([(w*.44,h*.87),(w*.46,h*.54),(w*.48,h*.45),(w*.53,h*.45),(w*.56,h*.57),(w*.59,h*.87)], fill=(1,4,6,255))
            draw.line((w*.06,h*.22,w*.30,h*.22), fill=(110,155,145,100), width=1)
            draw.line((w*.72,h*.73,w*.94,h*.73), fill=(110,155,145,75), width=1)
        elif mode == "mirror":
            # A reflection too close to fit the physical room; a second offset frame ghosts it.
            cx = w * .52
            ghost = Image.new("RGBA", panel.size, (0,0,0,0)); gd = ImageDraw.Draw(ghost, "RGBA")
            gd.ellipse((cx-w*.10,h*.04,cx+w*.09,h*.39), fill=(124,155,145,88), outline=(181,204,188,105), width=2)
            gd.polygon([(cx-w*.22,h*.95),(cx-w*.18,h*.56),(cx-w*.10,h*.39),(cx+w*.10,h*.39),(cx+w*.20,h*.57),(cx+w*.25,h*.95)], fill=(111,143,135,82))
            gd.line((cx-w*.11,h*.16,cx+w*.06,h*.16), fill=(202,219,199,80), width=1)
            panel = Image.alpha_composite(panel, ghost.filter(ImageFilter.GaussianBlur(1.2)))
            draw = ImageDraw.Draw(panel, "RGBA")
            draw.ellipse((cx+w*.06,h*.08,cx+w*.20,h*.36), fill=(106,138,132,50))
            draw.polygon([(cx-w*.06,h*.95),(cx-w*.02,h*.58),(cx+w*.07,h*.42),(cx+w*.18,h*.48),(cx+w*.23,h*.95)], fill=(112,143,137,35))
        elif mode == "twins":
            # Two distinct silhouettes in one mirror; the second is offset like an impossible reflection.
            for cx, alpha, scale in ((w*.34, 115, .72), (w*.68, 80, .88)):
                head_w = w*.12*scale; head_h = h*.27*scale
                draw.ellipse((cx-head_w/2,h*.12,cx+head_w/2,h*.12+head_h), fill=(5,9,10,alpha), outline=(172,190,174,70), width=1)
                shoulder_y = h*.12+head_h
                draw.polygon([(cx-w*.15*scale,h*.96),(cx-w*.13*scale,shoulder_y+h*.08),(cx-w*.07*scale,shoulder_y),(cx+w*.07*scale,shoulder_y),(cx+w*.14*scale,shoulder_y+h*.09),(cx+w*.16*scale,h*.96)], fill=(4,8,9,alpha))
            draw.line((w*.5,h*.06,w*.5,h*.93), fill=(188,202,188,40), width=1)
        elif mode == "acts":
            # Two nearly identical paper records overlap; duplicated red seals are the anomaly.
            draw.rectangle((2,2,w-3,h-3), fill=(188,179,150,255), outline=(71,65,53,230), width=1)
            draw.rectangle((5,4,w-7,h-5), outline=(104,94,75,150), width=1)
            for row in range(5):
                yy=7+row*6
                draw.line((7,yy,w-7,yy), fill=(66,67,58,145 if row<4 else 90), width=1)
            draw.ellipse((w*.12,h*.12,w*.42,h*.50), outline=(142,37,32,210), width=2)
            draw.ellipse((w*.54,h*.16,w*.84,h*.54), outline=(142,37,32,170), width=2)
            draw.line((w*.15,h*.28,w*.37,h*.28), fill=(142,37,32,200), width=1)
            draw.line((w*.57,h*.32,w*.79,h*.32), fill=(142,37,32,160), width=1)
        elif mode == "anna":
            # A pale face and a hand appear only in the cabinet glass, without a jump-scare flash.
            draw.rectangle((2,2,w-3,h-3), outline=(125,158,146,110), width=1)
            cx=w*.52
            draw.ellipse((cx-w*.13,h*.09,cx+w*.12,h*.50), fill=(139,162,145,95), outline=(194,208,186,120), width=1)
            draw.polygon([(cx-w*.24,h*.98),(cx-w*.21,h*.63),(cx-w*.12,h*.47),(cx+w*.12,h*.47),(cx+w*.22,h*.65),(cx+w*.25,h*.98)], fill=(91,122,111,100))
            draw.ellipse((w*.73,h*.38,w*.86,h*.67), fill=(162,183,161,70), outline=(205,218,196,95), width=1)
            draw.line((cx-w*.07,h*.28,cx+w*.07,h*.28), fill=(29,42,39,180), width=1)
        elif mode == "p17":
            # The cold-storage tray contains liquid water and a specimen that does not frost over.
            draw.rectangle((2,4,w-3,h-4), fill=(26,43,46,255), outline=(123,154,153,210), width=1)
            draw.rectangle((5,7,w-6,h-7), fill=(42,64,67,255), outline=(95,129,130,180), width=1)
            draw.ellipse((w*.16,h*.26,w*.84,h*.73), fill=(112,139,136,255), outline=(198,219,208,220), width=1)
            draw.line((w*.22,h*.44,w*.78,h*.42), fill=(221,241,225,240), width=2)
            draw.line((w*.28,h*.55,w*.68,h*.57), fill=(26,74,77,230), width=1)
            for dx,dy in ((.20,.19),(.76,.23),(.72,.78),(.27,.76)):
                draw.ellipse((w*dx-1,h*dy-1,w*dx+2,h*dy+2), fill=(213,238,235,230))
        elif mode == "door":
            # The microscope/lens reflection contains a corridor door that is not behind the player.
            draw.rectangle((2,2,w-3,h-3), fill=(8,15,17,255), outline=(101,129,120,160), width=1)
            left,top,right,bottom=int(w*.31),int(h*.08),int(w*.70),int(h*.94)
            draw.rectangle((left,top,right,bottom), fill=(28,43,40,255), outline=(168,188,161,235), width=2)
            draw.rectangle((left+5,top+4,right-5,bottom-4), fill=(7,15,16,255))
            draw.rectangle((left+9,top+7,right-9,bottom-7), fill=(117,135,105,95))
            draw.line((w*.51,h*.16,w*.51,h*.86), fill=(204,214,181,180), width=1)
            draw.ellipse((w*.61,h*.49,w*.64,h*.54), fill=(218,202,139,230))
        if mode in ("false", "mirror", "twins"):
            for y in range(2, h, 4):
                draw.line((0,y,w,y), fill=(143,180,166,18 if mode == "mirror" else 12), width=1)
        if mode == "false":
            bloom = Image.new("RGBA", panel.size, (0,0,0,0)); bd = ImageDraw.Draw(bloom, "RGBA")
            bd.ellipse((w*.25,h*.05,w*.78,h*.98), fill=(95,145,130,24))
            panel = Image.alpha_composite(panel, bloom.filter(ImageFilter.GaussianBlur(7)))
        canvas = Image.new("RGBA", (width,height), (0,0,0,0))
        canvas.alpha_composite(panel, (x0,y0))
        canvas.save(overlay_dir / filename, "WEBP", lossless=True, method=6)


def main():
    project = json.loads(PROJECT.read_text(encoding="utf-8"))
    adventure = json.loads(ADVENTURE.read_text(encoding="utf-8"))
    html = GAME_HTML.read_text(encoding="utf-8")
    game, _, _ = payload(html)
    OUT.mkdir(parents=True, exist_ok=True)
    generated = []
    generate_first_act_state_overlays()
    # Keep the two existing kitchen states in the editable project too; previously they were only embedded by the standalone build step.
    for state, asset_id in (("B_SECOND_PLATE", "illustrated_B_SECOND_PLATE"), ("B_GHOST_MIRROR", "illustrated_B_GHOST_MIRROR")):
        source = ROOT / "site-assets/kitchen-states" / (state + ".webp")
        out_path = OUT / (asset_id + ".webp")
        if not source.exists(): raise FileNotFoundError("Missing kitchen state art: " + state)
        shutil.copyfile(source, out_path)
        raw = out_path.read_bytes()
        if raw[:4] != b"RIFF" or raw[8:12] != b"WEBP": raise ValueError("Invalid kitchen state asset: " + state)
        value = {"mime": "image/webp", "data": base64.b64encode(raw).decode("ascii")}
        if game.setdefault("assets", {}).get(asset_id) not in (None, value): raise ValueError("Conflicting kitchen asset: " + asset_id)
        game["assets"][asset_id] = value
        project_asset = {"id": asset_id, "name": state, "mime": "image/webp", "file": "assets/variants/" + out_path.name}
        project["assets"] = update_list(project.get("assets", []), project_asset)
        for collection in (adventure["rooms"], project["story"]["adventure"]["rooms"], game["story"]["adventure"]["rooms"]):
            meta = next((r for r in collection if r["id"] == "B"), None)
            if meta is None or state not in meta.get("variants", []): raise ValueError("Missing canonical kitchen variant " + state)
            meta.setdefault("variantAssets", {})[state] = asset_id
        generated.append((state, asset_id, len(raw)))
    for room, state, filename, name in OVERLAYS:
        base_path = ROOT / "game-project/rooms" / room / "panorama_v2.webp"
        if not base_path.exists(): base_path = ROOT / "game-project/rooms" / room / "original.png"
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
        # Composite state panoramas depend on the current base room art. Replace the
        # previous embedded composite when a base panorama is regenerated.
        game.setdefault("assets", {})[asset_id] = value
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
            for room, state, aid in [("B","B_SECOND_PLATE","illustrated_B_SECOND_PLATE"),("B","B_GHOST_MIRROR","illustrated_B_GHOST_MIRROR")] + [(room,state,"composite_"+state.lower()) for room,state,filename,name in OVERLAYS]:
                meta = next(r for r in editor_game["story"]["adventure"]["rooms"] if r["id"] == room)
                meta.setdefault("variantAssets", {})[state] = aid
            EDITOR_HTML.write_text(patch_html(editor_html, editor_game), encoding="utf-8")
    print("PASS composed and embedded", len(generated), "room-state panoramas:", ", ".join(f"{s}={n}B" for s,_,n in generated))

if __name__ == "__main__":
    main()
