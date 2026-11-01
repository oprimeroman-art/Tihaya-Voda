#!/usr/bin/env python3
"""Add optional, non-blocking environmental encounters to the existing game.

This does not change canonical quests, mandatory actions, saves or endings.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply_optional_encounters(payload, root=ROOT):
    story = payload["story"]["adventure"]
    additions = json.loads((root / "production/optional-encounters.json").read_text(encoding="utf-8"))
    rooms = {room["id"] for room in story["rooms"]}
    for field in ("actions", "events"):
        existing = {item["id"] for item in story[field]}
        for item in additions[field]:
            if item["room"] not in rooms:
                raise ValueError("Unknown room in optional encounter: " + item["id"])
            if item["id"] not in existing:
                story[field].append(item)
                existing.add(item["id"])
    # Optional evidence deduction board uses the exact same save-state flags as
    # authored encounters; it never blocks the twelve canonical chapters.
    cases = additions.get("evidenceCases", [])
    for case in cases:
        if case["echoRoom"] not in rooms:
            raise ValueError("Unknown evidence echo room: " + case["id"])
        if any(fragment["room"] not in rooms for fragment in case["fragments"]):
            raise ValueError("Unknown evidence fragment room: " + case["id"])
    story["evidenceCases"] = cases
    return payload
