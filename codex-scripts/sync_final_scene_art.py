#!/usr/bin/env python3
"""Assemble the finished room/state art; no media generation or gameplay tests."""
import base64,copy,json,re
from pathlib import Path
from sync_player_guidance import apply_player_guidance
ROOT=Path(__file__).resolve().parents[1]
BASES={r:r+'_NORMAL' for r in 'EGIJKLMNOP'}
ALIASES={'O_1978':'O_NORMAL','P_FINAL_PANEL':'P_NORMAL','L_THREE_WINDOWS':'L_NORMAL','H_1978':'O_NORMAL'}
SCENES={'E028':'G_P17','E030':'G_MIRROR_DOOR','E046':'K_TOWER_SILHOUETTE','E048':'K_TOWER_EMPTY','E049':'J_FALSE_BELOV','E052':'J_SAFE','E066':'O_NORMAL','E067':'O_NORMAL','E068':'O_NORMAL','E078':'N_CLOCK','E079':'N_SIGN','E080':'N_HANDWRITING','E081':'N_LATE_EXIT','E083':'B_LATE','E084':'E_FALSE_DIGITAL','E087':'I_COVERED_BODY','E088':'I_EMPTY_BED','E090':'A_LATE','E094':'L_SHUTTER_DANGER','E095':'L_COUNTER_NEAR','E097':'L_COUNTER_RETREATED','E101':'L_NORMAL','E102':'L_WINDOW_1978','E103':'L_WINDOW_FUTURE','E104':'M_DELAY_MONITOR','E105':'M_FINAL','E106':'P_NORMAL'}

def apply_final_art(game,root=ROOT):
    manifest=json.loads((root/'production/final-scene-art.json').read_text());entries=manifest['assets']
    anchors=json.loads((root/'production/interaction-anchors.json').read_text())
    story=game['story']['adventure'];story['panoramaStaging']=json.loads((root/'production/panorama-staging.json').read_text());rooms={r['id']:r for r in story['rooms']}
    # Physical installations consume only their actual components; keys and recordings stay.
    used={'install_fuse3':['FUSE_3'],'VHS_ASSEMBLE':['VHS_FRAGMENT_A','VHS_FRAGMENT_B'],'PIN_INSERT':['SHUTTER_PIN']}
    for action in story['actions']:
        for item in used.get(action['id'],[]):
            fx={'removeItem':item}
            if fx not in action.setdefault('effects',[]):action['effects'].append(fx)
    source=isinstance(game['assets'],list);assets={a['id']:a for a in game['assets']}if source else game['assets']
    for key,entry in entries.items():
        aid=entry['assetId'];blob=(root/'game-project'/entry['file']).read_bytes()
        assets[aid]={'id':aid,'name':key,'mime':'image/webp','file':entry['file']}if source else {'mime':'image/webp','data':base64.b64encode(blob).decode('ascii')}
        rid=key[0];meta=rooms[rid]
        if key in meta['variants']:meta.setdefault('variantAssets',{})[key]=aid
    for variant,key in ALIASES.items():rooms[variant[0]].setdefault('variantAssets',{})[variant]=entries[key]['assetId']
    for rid,key in BASES.items():
        meta=rooms[rid];meta['approvedBaseArt']=True;meta.setdefault('variantAssets',{})[meta['default_variant']]=entries[key]['assetId']
        room=next(r for r in game['rooms']if r['id']==rid)
        if rid in {'I','M','N','P'}:
            room.setdefault('view',{}).update(yaw={'I':.95,'M':1.05,'N':-2.14,'P':1.9}[rid],pitch=0,fov=72)
        if source:room.update(file=entries[key]['file'],mime='image/webp',width=entries[key]['width'],height=entries[key]['height'])
        else:game['panoramas'][rid]=copy.deepcopy(assets[entries[key]['assetId']])
    # The old H_1978/V01B aliases showed unrelated ghost/after-VHS pictures.
    rooms['H']['variantAssets']['H_V01B']='illustrated_H_NORMAL'
    for variant in ['L_COUNTER_NEAR','L_COUNTER_RETREATED','L_WINDOW_1978','L_WINDOW_FUTURE']:
        if variant not in rooms['L']['variants']:rooms['L']['variants'].append(variant)
        rooms['L']['variantAssets'][variant]=entries[variant]['assetId']
    for rid,variant,point in [('G','G_MIRROR_DOOR',[.51,.44]),('J','J_FALSE_BELOV',[.82,.51]),('K','K_TOWER_SILHOUETTE',[.48,.20]),('N','N_LATE_EXIT',[.77,.53])]:
        profile=rooms[rid].setdefault('visualProfiles',{}).setdefault(variant,{})
        profile.update(figure=False,gazePoint={'u':point[0],'v':point[1]})
    for rid,variant in [('I','I_COVERED_BODY'),('L','L_SHUTTER_DANGER'),('L','L_COUNTER_NEAR'),('L','L_COUNTER_RETREATED'),('L','L_THREE_WINDOWS'),('L','L_WINDOW_1978'),('L','L_WINDOW_FUTURE'),('M','M_DELAY_MONITOR'),('M','M_FINAL')]:
        rooms[rid].setdefault('visualProfiles',{}).setdefault(variant,{}).update(figure=False,strength=.16)
    rooms['L']['visualProfiles']['L_COUNTER_RETREATED']['disabled']=True
    rooms['J'].setdefault('visualProfiles',{})['J_SAFE']={'disabled':True}
    rooms['K'].setdefault('visualProfiles',{})['K_TOWER_EMPTY']={'disabled':True}
    rooms['N'].setdefault('visualProfiles',{})['N_NORMAL']={'disabled':True}
    for event in story['events']:
        if event['id']in SCENES:event['sceneArt']=entries[SCENES[event['id']]]['assetId']
        change={'E097':{'L':'L_COUNTER_RETREATED'},'E102':{'L':'L_WINDOW_1978'},'E103':{'L':'L_WINDOW_FUTURE'},'E105':{'M':'M_FINAL'}}.get(event['id'])
        if change:
            fx={'variant':change}
            if fx not in event['effects']:event['effects'].append(fx)
        if event['id']=='E095':
            event['visualCue']={'mode':'panorama','panoramaVariant':'L_COUNTER_NEAR','duration':1.8}
            guard={'not':'SHUTTERS_SAFE'}
            if guard not in event['when'].setdefault('all',[]):event['when']['all'].append(guard)
    hooks=[{'room':'A','when':{'min':11},'effects':[{'variant':{'A':'A_LATE'}}]},
           {'room':'B','when':{'min':10,'max':10},'effects':[{'variant':{'B':'B_LATE'}}]}]
    for hook in hooks:
        if hook not in story.setdefault('onEnter',[]):story['onEnter'].append(hook)
    for room in game['rooms']:
        lookup=anchors['rooms'].get(room['id'],{})
        for obj in room.get('objects',[]):
            aid=obj.get('tourKey','')[3:];point=lookup.get(aid)
            if point:
                u,v=point;obj['corners']=[{'u':(u+x)%1,'v':v+y}for x,y in [(-.009,-.012),(.009,-.012),(.009,.012),(-.009,.012)]]
    story['interactionAnchors']=anchors.get('variants',{})
    game['name']='Протокол «Тихая вода»'
    game.setdefault('release',{})['subtitle']='Арктическая станция «Маяк-9». Психологический хоррор.'
    story['credits']='Протокол «Тихая вода»\nАвторский сценарий, редакция 2.0.\nРазработка и художественная интеграция: byGagarin.\nПанорамы и иллюстрации: ImageGen.\nОзвучка альфы: предоставленные автором записи.\nДвижок: Gagarin Panorama Studio.'
    allentries={**entries,**{v:entries[k]for v,k in ALIASES.items()}}
    for key in ['L_COUNTER_NEAR','L_COUNTER_RETREATED','L_WINDOW_1978','L_WINDOW_FUTURE']:
        if not any(x.get('id')==key and x.get('kind')=='panorama' for x in story.setdefault('assetSlots',[])):
            story['assetSlots'].append({'kind':'panorama','id':key,'usage':'room_state','suggested_relative_path':entries[key]['file'],'availability':'provided; authored panorama'})
    for slot in story.get('assetSlots',[]):
        if slot.get('kind')=='panorama'and slot['id']in allentries:
            slot.update(suggested_relative_path=allentries[slot['id']]['file'],availability='provided; authored panorama')
    if source:game['assets']=list(assets.values())
    return apply_player_guidance(game,root)

def main():
    project_path=ROOT/'game-project/project.json';project=apply_final_art(json.loads(project_path.read_text()))
    story=project['story']['adventure']
    for rel,data in [('game-project/project.json',project),('studio/content/TIHAYA_VODA/adventure.json',story),('reports/adventure.json',story)]:
        (ROOT/rel).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for rel in ['game/index.html','game-editor/index.html']:
        path=ROOT/rel;text=path.read_text();mark='window.BUILT_GAME=';pos=text.index(mark)+len(mark);game,n=json.JSONDecoder().raw_decode(text[pos:]);apply_final_art(game)
        # Canonical bindings (including all existing documents, voices and endings) are preserved.
        game['story']['adventure']=copy.deepcopy(story)
        text=text[:pos]+json.dumps(game,ensure_ascii=False,separators=(',',':'))+text[pos+n:]
        text=re.sub(r'<title>.*?</title>','<title>Протокол «Тихая вода»</title>',text,count=1)
        path.write_text(text)
    slots={s['id']:s for s in story.get('assetSlots',[])if s.get('kind')=='panorama'}
    for rel in ['studio/content/PRODUCTION/09_ASSET_SLOTS.tsv','reports/MISSING_ASSETS.tsv']:
        path=ROOT/rel;rows=[]
        for line in path.read_text().splitlines():
            cols=line.split('\t')
            if len(cols)==5 and cols[0]=='panorama'and cols[1]in slots:
                slot=slots[cols[1]];cols[3]=slot.get('suggested_relative_path',cols[3]);cols[4]=slot.get('availability',cols[4])
            rows.append('\t'.join(cols))
        present={line.split('\t')[1]for line in rows if line.startswith('panorama\t')}
        for key in ['L_COUNTER_NEAR','L_COUNTER_RETREATED','L_WINDOW_1978','L_WINDOW_FUTURE']:
            if key not in present:rows.append('\t'.join(['panorama',key,'room_state',slots[key]['suggested_relative_path'],'provided; authored panorama']))
        path.write_text('\n'.join(rows)+'\n')
    print('Assembled final authored rooms, state transitions, scene art and interaction anchors. Original audio/video retained.')
if __name__=='__main__':main()
