import json,re,base64,zipfile,io,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont
from paths import *
data=json.loads((ROOT/'TIHAYA_VODA/adventure.json').read_text(encoding='utf-8'))
def font(n):return ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',n)
def png(im):
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def pano(r):
    im=Image.new('RGB',(2048,1024),'#283840');d=ImageDraw.Draw(im)
    d.rectangle((0,650,2048,1024),fill='#202b30');d.rectangle((0,0,2048,290),fill='#33464e')
    for x in range(0,2049,256):
        d.line((x,0,x,1024),fill='#45565e',width=3);d.line((1024+(x-1024)*.4,650,x,1024),fill='#3d4a4e',width=2)
    for y in [680,740,830,950]:d.line((0,y,2048,y),fill='#3d4a4e',width=2)
    for x in [250,850,1450]:
        d.rounded_rectangle((x,310,x+330,620),radius=10,fill='#1b2a33',outline='#768d97',width=3)
        d.rectangle((x+20,330,x+310,430),fill='#53646a');d.line((x+30,570,x+300,570),fill='#a7bac0',width=4)
    for x in [90,760,1430]:
        d.text((x,155),'СТАНЦИЯ МАЯК-9',fill='#cedbdf',font=font(25));d.text((x,198),r['name'].upper(),fill='#f0e7cf',font=font(29))
        d.text((x,248),'ОТСУТСТВУЕТ АССЕТ: '+r['default_variant'],fill='#dfc28a',font=font(18))
    return png(im)
def card(label):
    im=Image.new('RGBA',(500,150),(17,30,37,238));d=ImageDraw.Draw(im);d.rounded_rectangle((2,2,498,148),radius=12,outline='#bfd0d8',width=3)
    words=label.split();lines=[''];
    for w in words:
        if len(lines[-1])+len(w)>30:lines.append('')
        lines[-1]+=(' ' if lines[-1] else '')+w
    for i,l in enumerate(lines[:3]):d.text((18,12+i*39),l,fill='#e4ebec',font=font(24))
    return png(im)
assets={};manifest={'schema':'panorama-studio-v2','name':'ПОЛЯРНАЯ СМЕНА','release':{'subtitle':'Симулятор обслуживания автономной научной станции. Техническая сборка с явно обозначенными медиаслотами.','startRoom':'A','startTorch':False},'activeRoom':'A','editorView':'360','previewMax':2048,'globals':[],'story':{'sequences':[],'quests':[],'adventure':data},'rooms':[],'assets':[],'audio':[],'videos':[],'spatialSounds':[],'timelines':[]}
flags={**{k:False for k in json.loads(read('DATA/07_PROJECT_CONTENT_CONTRACT.json'))['flags_registry']},**data['initial']}
for k,v in flags.items():manifest['globals'].append(dict(key=k,type='bool' if type(v)==bool else 'number' if type(v)==int else 'string',value=v))
for e in data['events']:
    # Editable staging timelines retain all named events. Core queue manages trigger/once/modal semantics.
    manifest['timelines'].append(dict(id=e['id'],name=e['id']+' · '+e['presentation'],roomId=e['room'] or 'C',steps=[dict(at=0,type='subtitle',value='ОТСУТСТВУЕТ АССЕТ: '+e['id']+' · '+e['presentation'])]))
for line in data['dialogues']:manifest['story']['sequences'].append(dict(id=line['id'],name=line['speaker']+' · '+line['id'],steps=[dict(type='dialogue',speaker=line['speaker'],text=line['text'])]))
manifest['story']['quests']=[dict(id=q['id'],name=q['title']) for q in data['quests']]
files={};built=dict(name=manifest['name'],release=manifest['release'],current='A',globals=manifest['globals'],story=manifest['story'],rooms=[],assets={},video={},audio={},panoramas={},retouch={},spatialSounds=[],timelines=manifest['timelines'])
for r in data['rooms']:
    rid=r['id'];path=f'rooms/{rid}/original.png';raw=pano(r);files[path]=raw;built['panoramas'][rid]={'mime':'image/png','data':base64.b64encode(raw).decode()}
    objects=[]
    for i,a in enumerate(x for x in data['actions'] if x['room']==rid):
        aid='sign_'+a['id'];raw=card(a['label']);apath='assets/'+aid+'.png';files[apath]=raw;manifest['assets'].append(dict(id=aid,name=a['label'],mime='image/png',file=apath));built['assets'][aid]={'mime':'image/png','data':base64.b64encode(raw).decode()}
        u=.15+(i%6)*.14;v=.42+(i//6%3)*.11;w=.10;h=.075
        objects.append(dict(id='obj_'+a['id'],name=a['label'],tourKey='ga:'+a['id'],corners=[dict(u=u-w/2,v=v-h/2),dict(u=u+w/2,v=v-h/2),dict(u=u+w/2,v=v+h/2),dict(u=u-w/2,v=v+h/2)],states=[aid],state=0,visible=rid=='A',media={'kind':'none'},trigger='click',delay=1.5,once=False,elapsed=0))
    room=dict(id=rid,name=r['name'],mime='image/png',file=path,width=2048,height=1024,view={'yaw':0,'pitch':0,'fov':78},objects=objects,vars=[],rules=[],exits=[{'to':l['to']} for l in data['links'] if l['from']==rid])
    manifest['rooms'].append(room);built['rooms'].append({k:v for k,v in room.items() if k not in ['file','width','height','mime']})
files['project.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
files['README.txt']='Редактируемый проект Studio 2.8 с расширением adventure. Откройте PROJECT.zip в обновлённом редакторе. Вкладка 7 — сценарий. Сохранение и повторная сборка сохраняют все данные.'.encode('utf-8')
def archive(path,entries):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for k,v in entries.items():z.writestr(k,v)
archive(OUT/'PROJECT.zip',files)
(ROOT/'TIHAYA_VODA/project.json').write_bytes(files['project.json'])
runtime=(STUDIO/'source/game-runtime.html').read_text(encoding='utf-8')
story='\n'.join((STUDIO/'source'/s).read_text(encoding='utf-8-sig') for s in ['story-core.js','adventure-core.js','adventure-ui.js'])
runtime=runtime.replace('__GAME_DATA__',json.dumps(built,ensure_ascii=False).replace('<','\\u003c')).replace('__TITLE__','ПОЛЯРНАЯ СМЕНА').replace('__ENGINE_CORE__',(STUDIO/'source/rules-core.js').read_text(encoding='utf-8-sig')).replace('__STORY_CORE__',story)
# Include the existing 2.8 localization layer exactly as the editor exporter does.
i18n=(STUDIO/'source/i18n.js').read_text(encoding='utf-8-sig')
runtime=runtime.replace('</body>', '<script>'+i18n+'</script></body>')
gameDir=OUT/'GAME';gameDir.mkdir(exist_ok=True)
(gameDir/'index.html').write_text(runtime,encoding='utf-8');shutil.copyfile(OUT/'PROJECT.zip',gameDir/'source-project.zip')
readme='ПОЛЯРНАЯ СМЕНА — техническая сборка.\nРаспакуйте GAME.zip целиком. Откройте index.html в Chrome/Edge, без сервера.\nОтсутствующие ассеты явно подписаны. PLAY запускает раскадровку; следующий фрагмент позволяет прочитать её без ожидания.\nСейв: меню / Esc, переносимый SAVE.json. После финала сохраняется точка перед подписью.\nРедактирование: откройте GAME.zip или source-project.zip в обновлённой Studio.\n'
(gameDir/'README.txt').write_text(readme,encoding='utf-8');archive(OUT/'GAME.zip',{'index.html':runtime.encode('utf-8'),'source-project.zip':(OUT/'PROJECT.zip').read_bytes(),'README.txt':readme.encode('utf-8')})
archive(OUT/'STUDIO_SOURCE.zip',{str(p.relative_to(STUDIO)).replace('\\','/'):p.read_bytes() for p in STUDIO.rglob('*') if p.is_file() and p.suffix!='.zip'})
(OUT/'adventure.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({p.name:p.stat().st_size for p in [OUT/'PROJECT.zip',OUT/'GAME.zip',OUT/'STUDIO_SOURCE.zip']}))
