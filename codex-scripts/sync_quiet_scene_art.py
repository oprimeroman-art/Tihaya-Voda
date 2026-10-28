#!/usr/bin/env python3
"""Attach approved-room edits to their original quiet/temporal events."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'production/quiet-scene-art.json').read_text())
    path=ROOT/'game-project/project.json';project=json.loads(path.read_text());story=project['story']['adventure']
    assets={a['id']:a for a in project['assets']};embedded={}
    for variant,entry in manifest['variants'].items():
        blob=(ROOT/'game-project'/entry['file']).read_bytes()
        assert len(blob)>1000 and blob[:4]==b'RIFF' and blob[8:12]==b'WEBP'
        assert hashlib.sha256(blob).hexdigest()==entry['sha256']
        room=next(r for r in story['rooms'] if variant in r['variants'])
        room.setdefault('variantAssets',{})[variant]=entry['assetId']
        assets[entry['assetId']]={'id':entry['assetId'],'name':variant,'mime':'image/webp','file':entry['file']}
        embedded[entry['assetId']]={'mime':'image/webp','data':base64.b64encode(blob).decode()}
    for slot in story.get('assetSlots',[]):
        entry=manifest['variants'].get(slot['id']) if slot.get('kind')=='panorama' else None
        if entry:slot.update(suggested_relative_path=entry['file'],availability='provided; authored approved-room edit')
    for relative in ['studio/content/PRODUCTION/09_ASSET_SLOTS.tsv','reports/MISSING_ASSETS.tsv']:
        target=ROOT/relative;rows=[]
        for line in target.read_text().splitlines():
            fields=line.split('\t')
            if len(fields)==5 and fields[0]=='panorama' and fields[1] in manifest['variants']:
                fields[3]=manifest['variants'][fields[1]]['file'];fields[4]='provided; authored approved-room edit'
            rows.append('\t'.join(fields))
        target.write_text('\n'.join(rows)+'\n')
    for id in ['E027','E044']:
        event=next(e for e in story['events'] if e['id']==id)
        effect={'variant':{'A':'A_SECOND_PILLOW'}}
        if effect not in event['effects']:event['effects'].append(effect)
        event['sceneArt']='authored_A_SECOND_PILLOW'
    for id,variant in {'E013':'C_MIRROR_LIGHT','E031':'C_HIDDEN_DOOR','E053':'C_REVERSED_SNOW'}.items():
        next(e for e in story['events'] if e['id']==id)['sceneArt']=manifest['variants'][variant]['assetId']
    event=next(e for e in story['events'] if e['id']=='E100')
    # Its canonical director matrix targets the corridor. Queue it there; never teleport.
    event['room']='C';event['sceneArt']='authored_C_DAYLIGHT'
    event['visualCue']={'mode':'panorama','panoramaVariant':'C_DAYLIGHT','duration':3}
    project['assets']=list(assets.values())
    for target,value in [(path,project),(ROOT/'studio/content/TIHAYA_VODA/adventure.json',story),(ROOT/'reports/adventure.json',story)]:target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    for relative in ['game/index.html','game-editor/index.html']:
        target=ROOT/relative;html=target.read_text();marker='window.BUILT_GAME=';start=html.index(marker)+len(marker)
        built,n=json.JSONDecoder().raw_decode(html[start:]);built['assets'].update(embedded);built['story']['adventure']=story
        target.write_text(html[:start]+json.dumps(built,ensure_ascii=False,separators=(',',':'))+html[start+n:])
    print('Integrated pillow and four corridor states; original media untouched')

if __name__=='__main__':main()
