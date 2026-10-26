#!/usr/bin/env python3
"""Whole-campaign integrity: flags, signals, rooms, media, and shipped payload."""
import base64, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "studio/content/TIHAYA_VODA/adventure.json").read_text(encoding="utf-8"))
project = json.loads((ROOT / "game-project/project.json").read_text(encoding="utf-8"))
html = (ROOT / "game/index.html").read_text(encoding="utf-8")
marker = "window.BUILT_GAME="
assert html.count(marker) == 1
pos = html.index(marker) + len(marker)
pos += len(html[pos:]) - len(html[pos:].lstrip())
game, _ = json.JSONDecoder().raw_decode(html[pos:])

rooms = {r["id"] for r in data["rooms"]}
assert len(data["quests"]) == 12 and [q["chapter"] for q in data["quests"]] == list(range(1, 13))
assert len(data["events"]) == 112 and len({e["id"] for e in data["events"]}) == 112
assert len(data["actions"]) == 128
assert all(e.get("trigger") == e.get("signal") for e in data["events"])
assert all(not e.get("room") or e["room"] in rooms for e in data["events"])
assert all(a.get("room") in rooms for a in data["actions"] if a.get("room"))
assert all(l["from"] in rooms and l["to"] in rooms for l in data["links"])

flag_refs, flag_setters = set(), set(data.get("initial", {}))
def condition(c, parent=None):
    if isinstance(c, str):
        if parent not in ("item", "variant"):
            flag_refs.add(c)
    elif isinstance(c, list):
        for x in c:
            condition(x, parent)
    elif isinstance(c, dict):
        if isinstance(c.get("eq"), dict): flag_refs.update(c["eq"].keys())
        if isinstance(c.get("in"), dict): flag_refs.update(c["in"].keys())
        for k, v in c.items():
            if k not in ("eq", "in", "min", "max"):
                condition(v, k)

def effects(items):
    for fx in items or []:
        if isinstance(fx.get("set"), dict): flag_setters.update(fx["set"].keys())
        if fx.get("document"): flag_setters.add("FOUND_" + fx["document"])
        if fx.get("ending"): flag_setters.update(("ENDING", "Q12_DONE"))

signal_consumers, signal_producers = set(), {"game_start", "ending_done"}
for room in rooms: signal_producers.add("enter:" + room)
for n in range(1, 13): signal_producers.add("chapter:" + str(n))
for q in data["quests"]:
    signal_producers.add(q["id"].lower() + "_done")
    flag_setters.add(q["id"] + "_DONE")
for key in ("CHAPTER", "WORLD_PHASE", "DEATHS", "ENDING", "Q12_DONE"):
    flag_setters.add(key)

for e in data["events"]:
    condition(e.get("when")); effects(e.get("effects"))
    signal_consumers.update(e["signal"] if isinstance(e["signal"], list) else [e["signal"]])
    signal_producers.add("event:" + e["id"])
    if e.get("timelineId"): pass
    for s in e.get("effects", []):
        if s.get("signal"): signal_producers.add(s["signal"])
for a in data["actions"]:
    condition(a.get("when"))
    for key in ("signal", "startSignal"):
        v = a.get(key)
        if isinstance(v, list): signal_producers.update(v)
        elif v: signal_producers.add(v)
    for k in ("effects", "failureEffects", "deathEffects"):
        effects(a.get(k))
        for fx in a.get(k, []):
            if fx.get("signal"): signal_producers.add(fx["signal"])
    for opt in a.get("options", []):
        condition(opt.get("when")); effects(opt.get("effects"))
        for fx in opt.get("effects", []):
            if fx.get("signal"): signal_producers.add(fx["signal"])
for q in data["quests"]: condition(q.get("complete"))
for link in data["links"]: condition(link.get("when"))
for hook in data.get("onEnter", []):
    condition(hook.get("when")); effects(hook.get("effects"))
    for fx in hook.get("effects", []):
        if fx.get("signal"): signal_producers.add(fx["signal"])

unknown_flags = sorted(flag_refs - flag_setters)
unproduced_signals = sorted(s for s in signal_consumers if s and s not in signal_producers)
assert not unknown_flags, "Flags referenced but never set: " + ", ".join(unknown_flags)
assert not unproduced_signals, "Event signals with no producer: " + ", ".join(unproduced_signals)

video_ids = ["V01", "V01B"] + [f"V{i:02d}" for i in range(2, 13)]
audio_ids = [f"S{i:02d}" for i in range(1, 17)]
assert len([m for m in data["media"] if m.get("kind") == "video" and m["id"] in video_ids]) == 13
assert len([e for e in data["events"] if e.get("timelineId")]) == 16
assert all(e.get("horror") is True for e in data["events"] if e.get("timelineId"))
for aid in video_ids:
    path = ROOT / "game-project/video/found_footage" / (aid.lower() + ".mp4")
    assert path.exists() and b"ftyp" in path.read_bytes()[:32], "Missing video: " + aid
    assert aid in game.get("video", {})
    assert base64.b64decode(game["video"][aid]["data"])[4:8] == b"ftyp"
    media = next(m for m in game["story"]["adventure"]["media"] if m["id"] == aid)
    assert media.get("assetId") == aid
for aid in audio_ids:
    path = ROOT / "game-project/audio/spatial" / (aid.lower() + ".ogg")
    assert path.exists() and path.read_bytes().startswith(b"OggS"), "Missing sound: " + aid
    assert aid in game.get("audio", {})
    assert base64.b64decode(game["audio"][aid]["data"]).startswith(b"OggS")
    assert any(s.get("id") == aid for s in game.get("spatialSounds", []))
assert game.get("panoramas", {}).get("B", {}).get("mime") == "image/png"
assert len(game["story"]["adventure"]["events"]) == 112
print("PASS: 12 chapters, 112 events, 128 actions; every flag has a setter and every event signal a producer.")
print("PASS: all 13 MP4s and 16 OGG cues are present, linked, and embedded in the standalone game.")
