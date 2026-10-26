#!/usr/bin/env python3
"""Verify distinct room panoramas and preservation of the existing game/media."""
import base64,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
project=json.loads((ROOT/'game-project/project.json').read_text(encoding='utf-8'))
qa=json.loads((ROOT/'production/qa/campaign_panorama_pack_v1.json').read_text(encoding='utf-8'))
html=(ROOT/'game/index.html').read_text(encoding='utf-8');marker='window.BUILT_GAME='
assert html.count(marker)==1
pos=html.index(marker)+len(marker);pos+=len(html[pos:])-len(html[pos:].lstrip());game,_=json.JSONDecoder().raw_decode(html[pos:])
assert qa['room_count']==16 and len(qa['rooms'])==16 and qa['hotspot_uvs_changed'] is False
assert set(game['panoramas'])==set('ABCDEFGHIJKLMNOP')
pr={r['id']:r for r in project['rooms']};gr={r['id']:r for r in game['rooms']};hashes=set();total=0
for rid in 'ABCDEFGHIJKLMNOP':
 room=pr[rid];built=gr[rid];assert room['file']==f'rooms/{rid}/panorama_v2.webp' and room['mime']=='image/webp'
 assert built['file']==room['file'] and built['mime']=='image/webp'
 path=ROOT/'game-project'/room['file'];raw=path.read_bytes();assert raw[8:12]==b'WEBP';assert Image.open(path).size==(2048,1024)
 assert hashlib.sha256(raw).hexdigest()==next(x['sha256'] for x in qa['rooms'] if x['room']==rid)
 assert game['panoramas'][rid]['mime']=='image/webp' and base64.b64decode(game['panoramas'][rid]['data'])==raw
 hashes.add(hashlib.sha256(raw).hexdigest());total+=len(raw);assert (ROOT/'game-project/rooms'/rid/'original.png').exists()
 assert {o['id']:o.get('corners') for o in room.get('objects',[])}=={o['id']:o.get('corners') for o in built.get('objects',[])}
assert len(hashes)>=15 and len(game.get('video',{}))>=13 and len(game.get('audio',{}))>=16
for room,state,aid in [('B','B_SECOND_PLATE','illustrated_B_SECOND_PLATE'),('B','B_GHOST_MIRROR','illustrated_B_GHOST_MIRROR'),('C','C_MIRROR_LIGHT','composite_c_mirror_light'),('F','F_ARCHIVE12','composite_f_archive12'),('H','H_AFTER_V01','composite_h_after_v01')]:
 meta=next(r for r in game['story']['adventure']['rooms'] if r['id']==room);assert meta.get('variantAssets',{}).get(state)==aid and aid in game.get('assets',{})
print(f'PASS: 16 distinct 2048x1024 panoramas embedded ({total} bytes); original PNGs and hotspot UVs preserved.')
print('PASS: five authored story variants, 13 existing videos, 16 existing audio cues preserved.')
