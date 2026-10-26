#!/usr/bin/env python3
"""Regression checks for the authored first-act and lab room-state composites."""
import base64, importlib.util, json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
script = ROOT / "codex-scripts/apply_panorama_state_overlays.py"
spec = importlib.util.spec_from_file_location("state_overlay_builder", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.generate_first_act_state_overlays()
expected = {
    "D_D_FALSE_MONITOR.webp": (567, 409, 621, 451),
    "D_D_LATE_MIRROR.webp": (1132, 409, 1202, 451),
    "B_B_TWO_GHOSTS.webp": (567, 522, 621, 564),
    "D_D_DOUBLE_ACTS.webp": (1714, 522, 1768, 564),
    "H_H_ANNA_GLASS.webp": (567, 409, 621, 451),
    "G_G_P17.webp": (567, 409, 621, 451),
    "G_G_MIRROR_DOOR.webp": (1132, 409, 1202, 451),
    "C_C_HIDDEN_DOOR.webp": (796, 362, 966, 622),
}
for filename, bounds in expected.items():
    path = ROOT / "art/overlays" / filename
    assert path.is_file(), f"missing generated overlay: {filename}"
    image = Image.open(path).convert("RGBA")
    assert image.size == (2048, 1024), f"wrong overlay size: {filename} {image.size}"
    assert image.getchannel("A").getbbox() == bounds, f"overlay escaped calibrated monitor UVs: {filename}"

project = json.loads((ROOT / "game-project/project.json").read_text(encoding="utf-8"))
adventure = json.loads((ROOT / "studio/content/TIHAYA_VODA/adventure.json").read_text(encoding="utf-8"))
html = (ROOT / "game/index.html").read_text(encoding="utf-8")
editor_html = (ROOT / "game-editor/index.html").read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1, "expected one standalone game payload"
pos = html.index(marker) + len(marker)
game, _ = json.JSONDecoder().raw_decode(html[pos:].lstrip())
assert editor_html.count(marker) == 1, "expected one editor payload"
epos = editor_html.index(marker) + len(marker)
editor_game, _ = json.JSONDecoder().raw_decode(editor_html[epos:].lstrip())
for state, room_id, asset_id in (("D_FALSE_MONITOR", "D", "composite_d_false_monitor"), ("D_LATE_MIRROR", "D", "composite_d_late_mirror"), ("B_TWO_GHOSTS", "B", "composite_b_two_ghosts"), ("D_DOUBLE_ACTS", "D", "composite_d_double_acts"), ("H_ANNA_GLASS", "H", "composite_h_anna_glass"), ("G_P17", "G", "composite_g_p17"), ("G_MIRROR_DOOR", "G", "composite_g_mirror_door"), ("C_HIDDEN_DOOR", "C", "composite_c_hidden_door")):
    composite = ROOT / "game-project/assets/variants" / f"{asset_id}.webp"
    assert composite.is_file(), f"missing playable composite: {composite.name}"
    image = Image.open(composite)
    assert image.size == (2048, 1024), f"wrong composite dimensions: {state}"
    raw = composite.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    assert game.get("assets", {}).get(asset_id, {}).get("data") == encoded, f"standalone payload mismatch: {state}"
    assert editor_game.get("assets", {}).get(asset_id, {}).get("data") == encoded, f"editor payload mismatch: {state}"
    for room_list in (adventure["rooms"], project["story"]["adventure"]["rooms"], game["story"]["adventure"]["rooms"], editor_game["story"]["adventure"]["rooms"]):
        room = next(r for r in room_list if r["id"] == room_id)
        assert room.get("variantAssets", {}).get(state) == asset_id, f"variant not wired in {room_id}: {state}"
    assert any(a.get("id") == asset_id and a.get("file") == f"assets/variants/{asset_id}.webp" for a in project["assets"]), f"editable asset missing: {state}"
print("PASS: B_TWO_GHOSTS, D_FALSE_MONITOR, D_DOUBLE_ACTS, D_LATE_MIRROR, H_ANNA_GLASS, G_P17, G_MIRROR_DOOR and C_HIDDEN_DOOR are calibrated, embedded, and mapped in the editor, story data, and standalone game.")
