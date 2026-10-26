#!/usr/bin/env python3
"""Regression tests for generated spatial cues and the shipped offline payload."""
import base64, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
project=json.loads((ROOT/'game-project/project.json').read_text(encoding='utf-8'))
adventure=json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text(encoding='utf-8'))
html=(ROOT/'game/index.html').read_text(encoding='utf-8')
marker='window.BUILT_GAME='
assert html.count(marker)==1, 'standalone game must have one built payload'
pos=html.index(marker)+len(marker); pos+=len(html[pos:])-len(html[pos:].lstrip())
game,_=json.JSONDecoder().raw_decode(html[pos:])
ids=[f'S{i:02d}' for i in range(1,17)]
assert len(adventure['quests'])==12 and len(adventure['events'])==112
for cue in ids:
 path=ROOT/'game-project/audio/spatial'/(cue.lower()+'.ogg')
 assert path.exists() and path.read_bytes().startswith(b'OggS'), f'missing OGG: {cue}'
 assert path.stat().st_size>1200, f'audio file suspiciously small: {cue}'
 assert any(x.get('id')==cue and x.get('file')==f'audio/spatial/{cue.lower()}.ogg' for x in project['audio'])
 assert cue in game.get('audio',{}) and base64.b64decode(game['audio'][cue]['data']).startswith(b'OggS')
 assert any(x.get('id')==cue and x.get('audioId')==cue for x in project['spatialSounds'])
 assert any(x.get('id')==cue and x.get('audioId')==cue for x in game['spatialSounds'])
for e in adventure['events']:
 if e.get('timelineId'):
  tl=next(x for x in project['timelines'] if x['id']==e['timelineId'])
  assert any(s['type']=='sound' and s['value'] in ids for s in tl['steps'])
  assert e.get('horror') is True, f'audio cue must not break quiet opening: {e["id"]}'
  assert e.get('room')==tl.get('roomId')
  assert any(x['id']==e['id'] and x.get('timelineId')==e['id'] for x in game['story']['adventure']['events'])
assert sum(1 for e in adventure['events'] if e.get('timelineId'))==16
assert len([x for x in game['spatialSounds'] if x['id'] in ids])==16
assert next(r for r in project['rooms'] if r['id']=='B')['file']=='rooms/B/original.png', 'normal production room source path must remain untouched'
assert game.get('panoramas',{}).get('B',{}).get('mime')=='image/png', 'normal B panorama must remain active in the default game'
print('PASS: 16 playable OGG cues, canonical trigger/timeline wiring, offline embedded audio, quiet opening preserved, 12 chapters/112 events intact')
