#!/usr/bin/env python3
"""Promote existing approved room art into the actual project and offline builds.

ABC corners come from the approved manifest. D/F/H placements remain provisional;
this is recorded as an art QA limitation, never a native spherical capture claim.
"""
from pathlib import Path
import base64,copy,json
from build_pages_demo import bundle
from alpha_wave2 import apply_wave2
from alpha_wave3 import apply_wave3
ROOT=Path(__file__).resolve().parents[1]

def main():
    cp=ROOT/'studio/content/TIHAYA_VODA/adventure.json';pp=ROOT/'game-project/project.json'
    story=json.loads(cp.read_text());project=json.loads(pp.read_text());assert story==project['story']['adventure']
    payload={'rooms':copy.deepcopy(project['rooms']),'story':{'adventure':copy.deepcopy(story)},'assets':{},'panoramas':{}}
    members,manifest=bundle()
    for rid in 'ABC':
        room=next(r for r in payload['rooms'] if r['id']==rid)
        authored=manifest['rooms'][rid]['objects'];assert set(authored)=={o['id'] for o in room['objects']}
        for o in room['objects']:o['corners']=authored[o['id']]['corners']
        payload['panoramas'][rid]={'mime':'image/webp','data':base64.b64encode(members[rid+'.webp']).decode('ascii')}
    apply_wave2(payload,ROOT);apply_wave3(payload,ROOT)
    affected=set(payload['panoramas']);byid={r['id']:r for r in payload['rooms']}
    for r in project['rooms']:
        if r['id'] in affected:
            r['objects']=byid[r['id']]['objects'];r['file']=f"rooms/{r['id']}/approved_illustrated.webp";r['mime']='image/webp'
            (ROOT/'game-project'/r['file']).write_bytes(base64.b64decode(payload['panoramas'][r['id']]['data']))
    assets={a['id']:a for a in project['assets']}
    for aid,asset in payload['assets'].items():
        filename=f'assets/approved-rooms/{aid}.webp';dest=ROOT/'game-project'/filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(base64.b64decode(asset['data']))
        assets[aid]={'id':aid,'name':aid,'mime':'image/webp','file':filename}
    project['assets']=list(assets.values())
    story=payload['story']['adventure']
    for meta in story['rooms']:
        if meta['id'] in affected:meta['approvedBaseArt']=True
    project['story']['adventure']=story
    for path,data in ((cp,story),(pp,project)):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    marker='window.BUILT_GAME='
    for rel in ('game/index.html','game-editor/index.html'):
        path=ROOT/rel;html=path.read_text();pos=html.index(marker)+len(marker);built,end=json.JSONDecoder().raw_decode(html[pos:])
        built['story']['adventure']=copy.deepcopy(story)
        for r in built['rooms']:
            if r['id'] in affected:r['objects']=copy.deepcopy(byid[r['id']]['objects'])
        built['assets'].update(payload['assets']);built['panoramas'].update(payload['panoramas'])
        path.write_text(html[:pos]+json.dumps(built,ensure_ascii=False,separators=(',',':'))+html[pos+end:])
    print('Existing approved room art integrated:',','.join(sorted(affected)))
if __name__=='__main__':main()
