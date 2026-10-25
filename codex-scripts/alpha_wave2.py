#!/usr/bin/env python3
"""D (radio room) + H (archive): approved storyboard art, original story engine.

Six artwork samples follow the user's approved five-room storyboard. Upsampled
samples serve alpha staging, not verified native-spherical 360 captures.
"""
from __future__ import annotations
import base64,hashlib,io,json,tarfile
from pathlib import Path

EXPECTED="608a42c0a96050ddbda0d2a8ef2d090fc1ad8f5279da192f0e3ce029f8d7ec6e"
COUNT=13
MAPPING={
 "D":{"D_NORMAL":"D_NORMAL","D_FALSE_MONITOR":"D_FALSE_MONITOR",
      "D_DOUBLE_ACTS":"D_FALSE_MONITOR","D_LATE_MIRROR":"D_LATE_MIRROR",
      "D_INDOOR_TOWER":"D_LATE_MIRROR"},
 "H":{"H_NORMAL":"H_NORMAL","H_AFTER_V01":"H_AFTER_V01",
      "H_1978":"H_AFTER_V01","H_ANNA_GLASS":"H_ANNA_GLASS",
      "H_V01B":"H_ANNA_GLASS"},
}
# Provisional placements, not changes to established story actions.
# The built-in editor is the final authority on per-image four corners.
ZONES={
 "D":{
  "sign_shift":(.72,.43), "RADIO_TUNE":(.25,.58),
  "send_report":(.56,.65),"WAVE_PHASE":(.25,.58),
  "watch_A01":(.31,.55),"watch_A02":(.31,.55),
  "flip_acts":(.59,.63),"TIMELINE_SYNC":(.38,.51),
  "watch_V04":(.38,.51),"name_reply":(.22,.59),
  "read_D02":(.65,.62),"read_D07":(.56,.64),
  "read_D11":(.67,.46),"read_D14":(.73,.46),
  "read_D15":(.59,.63),"read_D27":(.23,.55),
  "watch_V08":(.4,.5),"watch_V10":(.38,.5),
  "paper_tray":(.57,.65),"mirror06":(.4,.5),
  "mirror06_again":(.4,.5),"late10":(.4,.5),
 },
 "H":{
  "watch_V01":(.48,.61),"cabinet_message":(.83,.46),
  "take_VHS_FRAGMENT_A":(.83,.46),"take_VHS_FRAGMENT_B":(.17,.45),
  "VHS_ASSEMBLE":(.49,.64),"watch_V02":(.49,.62),
  "take_VHS_V03":(.2,.46),"watch_V03":(.48,.62),
  "take_PUNCHCARD_RU":(.53,.64),"take_PUNCHCARD_DE":(.55,.64),
  "PUNCHCARD_OVERLAY":(.49,.64),"enter_1978":(.83,.46),
  "calibration_plate":(.5,.6),"exit_1978":(.83,.46),
  "reenter_1978":(.83,.46),"NODE_MEMORY":(.48,.58),
  "petr_letter":(.58,.55),"read_D04":(.49,.63),
  "read_D08":(.5,.66),"read_D09":(.5,.66),
  "read_D12":(.47,.66),"read_D13":(.5,.65),
  "read_D21":(.46,.64),"read_D23":(.47,.63),
  "read_D25":(.48,.62),"read_D29":(.49,.67),
  "watch_V01B":(.48,.61),"watch_V05":(.48,.61),
  "watch_V06":(.48,.61),"watch_V07":(.48,.61),
  "watch_V09":(.52,.54),"watch_V11":(.48,.61),
  "watch_A03":(.5,.6),
 },
}
def read_bundle(root: Path):
    directory=root/'site-assets/alpha-wave2'
    paths=sorted(directory.glob('part_*.b64'))
    if len(paths)!=COUNT:raise ValueError(f'Missing second-wave image pieces: {len(paths)}')
    for i,p in enumerate(paths):
        if p.name!=f'part_{i:03}.b64':raise ValueError('Unordered art part: '+p.name)
    raw=base64.b64decode(''.join(p.read_text('ascii').strip() for p in paths),validate=True)
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('Radio/archive art checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tf:
        files={member.name:tf.extractfile(member).read() for member in tf.getmembers() if member.isfile()}
    expected={state+'.webp' for scenes in MAPPING.values() for state in scenes.values()}|{'manifest.json'}
    if set(files)!=expected:raise ValueError('Unexpected art files: '+repr(set(files)^expected))
    manifest=json.loads(files['manifest.json'])
    for state,digest in manifest['sha256'].items():
        if hashlib.sha256(files[state+'.webp']).hexdigest()!=digest:raise ValueError('Image corrupt: '+state)
    return files

def quad(u,v,w=.12,h=.12):
    u1=max(0,round(u-w/2,5));u2=min(1,round(u+w/2,5))
    v1=max(0,round(v-h/2,5));v2=min(1,round(v+h/2,5))
    return [{'u':u1,'v':v1},{'u':u2,'v':v1},{'u':u2,'v':v2},{'u':u1,'v':v2}]

def apply_wave2(payload,root: Path):
    files=read_bundle(root)
    story=payload['story']['adventure']
    allvariants={room['id']:room for room in story['rooms']}
    placed={}
    for room_id,mapping in MAPPING.items():
        game_room=next(r for r in payload['rooms'] if r['id']==room_id)
        hotspot=ZONES[room_id]
        observed={o['tourKey'][3:] for o in game_room['objects'] if o.get('tourKey','').startswith('ga:')}
        if observed!=set(hotspot):
            raise ValueError(f'{room_id} action list changed; update art anchors: {observed^set(hotspot)}')
        for obj in game_room['objects']:
            action=obj.get('tourKey','')[3:]
            if action in hotspot:obj['corners']=quad(*hotspot[action])
        for variant,state in mapping.items():
            name='illustrated_'+state
            data={'mime':'image/webp','data':base64.b64encode(files[state+'.webp']).decode('ascii')}
            payload['assets'][name]=data
            allvariants[room_id]['variantAssets'][variant]=name
        payload['panoramas'][room_id]=payload['assets']['illustrated_'+room_id+'_NORMAL']
        placed[room_id]={'actions':len(hotspot),'variants':len(mapping)}
    return placed
