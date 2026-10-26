#!/usr/bin/env python3
"""Validate every generated found-footage clip and its offline game integration."""
import base64,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
project=json.loads((ROOT/'game-project/project.json').read_text(encoding='utf-8'))
adventure=json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text(encoding='utf-8'))
html=(ROOT/'game/index.html').read_text(encoding='utf-8')
marker='window.BUILT_GAME='
assert html.count(marker)==1
pos=html.index(marker)+len(marker);pos+=len(html[pos:])-len(html[pos:].lstrip());game,_=json.JSONDecoder().raw_decode(html[pos:])
ids=['V01','V01B']+[f'V{i:02d}' for i in range(2,13)]
assert len([m for m in adventure['media'] if m.get('kind')=='video' and m['id'] in ids])==13
for aid in ids:
 path=ROOT/'game-project/video/found_footage'/(aid.lower()+'.mp4')
 raw=path.read_bytes();assert b'ftyp' in raw[:32] and len(raw)>10000,aid
 assert any(x.get('id')==aid and x.get('mime')=='video/mp4' and x.get('file')==f'video/found_footage/{aid.lower()}.mp4' for x in project['videos'])
 assert aid in game.get('video',{}) and b'ftyp' in base64.b64decode(game['video'][aid]['data'])[:32]
 slot=next(m for m in game['story']['adventure']['media'] if m['id']==aid)
 assert slot.get('assetId')==aid and slot.get('kind')=='video'
 probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height','-show_entries','format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
 meta=json.loads(probe.stdout);stream=meta['streams'][0];duration=float(meta['format']['duration'])
 assert stream['codec_name']=='h264' and stream['width']==320 and stream['height']==180,(aid,stream)
 expected=float(slot['duration']);assert abs(duration-expected)<=.3,(aid,duration,expected)
print('PASS: 13 full-duration H.264 found-footage clips, project references and offline game payload verified')
assert game.get('audio') and all(f'S{i:02d}' in game['audio'] for i in range(1,17)), 'video pass must preserve the 16 spatial sound cues'
assert game.get('panoramas',{}).get('B',{}).get('mime')=='image/png', 'normal gameplay panorama must remain unchanged'
print('PASS: sound pack and normal production room preserved')
