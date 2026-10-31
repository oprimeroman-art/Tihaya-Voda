#!/usr/bin/env python3
"""Bind player-facing objectives and existing inspection art; never alter plot or media."""
import base64
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def apply_player_guidance(game, root=ROOT):
    story = game['story']['adventure']
    guidance = json.loads((root/'production/player-guidance.json').read_text())
    actions = {a['id']: a for a in story['actions']}
    documents = {d['id'] for d in story['documents']}
    quest_ids = {q['id'] for q in story['quests']}
    if set(guidance['quests']) != quest_ids:
        raise ValueError('Player guidance must cover the existing quests exactly')
    for entry in [*guidance['quests'].values(), *guidance.get('branches', [])]:
        for step in entry['steps']:
            if step['action'] not in actions:
                raise ValueError('Unknown guidance action: '+step['action'])
            if not set(step.get('references', [])) <= documents:
                raise ValueError('Unknown guidance document')
    story['playerGuidance'] = copy.deepcopy(guidance)
    props = story.setdefault('illustratedProps', {})
    images = props.setdefault('image', {})
    bindings = props.setdefault('action', {})
    inspections = props.setdefault('inspections', {})
    manifest = json.loads((root/'production/inspection-art.json').read_text())
    for entry in manifest['assets'].values():
        blob = (root/'game-project'/entry['file']).read_bytes()
        if hashlib.sha256(blob).hexdigest() != entry['sha256']:
            raise ValueError('Inspection art checksum mismatch: '+entry['file'])
        images[entry['id']] = 'data:image/webp;base64,'+base64.b64encode(blob).decode('ascii')
        for action in entry['actions']:
            if action not in actions:
                raise ValueError('Unknown inspection action: '+action)
            bindings[action] = entry['id']
            inspections[action] = {'image': entry['id'], 'alt': entry['alt']}
    return game
