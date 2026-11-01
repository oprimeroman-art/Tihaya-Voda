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
    return payload
