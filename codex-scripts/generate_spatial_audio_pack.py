#!/usr/bin/env python3
"""Generate and wire the 16 authored spatial micro-cues into the offline game."""
from __future__ import annotations
import base64, json, re
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'game-project/project.json'
ADVENTURE = ROOT / 'studio/content/TIHAYA_VODA/adventure.json'
GAME_HTML = ROOT / 'game/index.html'
AUDIO_DIR = ROOT / 'game-project/audio/spatial'
SR = 22050

# Each cue is tied to an existing canonical event after the quiet opening.
CUES = [
 {'id':'S01','name':'Шаги за коридорной дверью','desc':'Два шага; ранний третий отзвук нарушает последовательность.','event':'E024','room':'C','u':.18,'kind':'steps','duration':5.8,'volume':.43},
 {'id':'S02','name':'Ложка в металлической мойке','desc':'Лёгкие удары ложки и короткий резонанс нержавеющей чаши.','event':'E023','room':'B','u':.88,'kind':'spoon','duration':4.2,'volume':.42},
 {'id':'S03','name':'Вентилятор и запоздалый хлопок','desc':'Короткая работа вентилятора; металлический хлопок через 12 секунд тишины.','event':'E034','room':'C','u':.68,'kind':'fan_slam','duration':16.2,'volume':.47},
 {'id':'S04','name':'Дыхание за зеркалом','desc':'Тихое близкое дыхание, приглушённое стеклом и стеной.','event':'E020','room':'B','u':.43,'kind':'mirror_breath','duration':7.2,'volume':.29},
 {'id':'S05','name':'Семейная запись за кухонной стеной','desc':'Далёкая неразборчивая бытовая речь с кассетным шумом; не заменяет актёрскую запись.','event':'E061','room':'B','u':.96,'kind':'muffled_talk','duration':8.4,'volume':.24},
 {'id':'S06','name':'Три удара в шлюз','desc':'Три тяжёлых удара по полой металлической двери.','event':'E049','room':'J','u':.62,'kind':'airlock_knocks','duration':4.4,'volume':.55},
 {'id':'S07','name':'Перемотка без мотора','desc':'Неровное шуршание ленты, flutter и статический хвост без слышимого двигателя.','event':'E058','room':'H','u':.31,'kind':'tape_rewind','duration':5.5,'volume':.34},
 {'id':'S08','name':'Падение четвёртого стула','desc':'Сухое трение ножек по полу, затем тяжёлый удар и короткий металлический дребезг.','event':'E068','room':'H','u':.76,'kind':'chair_fall','duration':4.8,'volume':.52},
 {'id':'S09','name':'Вдох под покрывалом','desc':'Шорох ткани и два приглушённых вдоха рядом с медицинским шкафом.','event':'E087','room':'I','u':.55,'kind':'blanket_breath','duration':5.2,'volume':.31},
 {'id':'S10','name':'Чайник за бетонной стеной','desc':'Приглушённое кипение и слабый металлический свист, будто звук идёт из стены.','event':'E104','room':'M','u':.83,'kind':'wall_kettle','duration':7.2,'volume':.31},
 {'id':'S11','name':'Куртка за окном галереи','desc':'Короткое трение плотной ткани на фоне холодного ветра снаружи.','event':'E101','room':'L','u':.14,'kind':'jacket_wind','duration':5.2,'volume':.33},
 {'id':'S12','name':'Детский голос с кассеты','desc':'Узкополосная радиотекстура под канонической репликой; это не актёрская озвучка.','event':'E060','room':'H','u':.39,'kind':'child_radio','duration':6.4,'volume':.30,'subtitle':'«Папа, а у вас там ночь?»'},
 {'id':'S13','name':'Шаги за стеной жилого модуля','desc':'Несколько удалённых шагов через толстую стену, без приближения к игроку.','event':'E090','room':'A','u':.91,'kind':'wall_steps','duration':5.5,'volume':.32},
 {'id':'S14','name':'Ветер в закрытом радиоканале','desc':'Один короткий порыв ветра, прошедший через шум радиоприёмника.','event':'E039','room':'D','u':.73,'kind':'radio_wind','duration':3.0,'volume':.37},
 {'id':'S15','name':'Два касания одной ручки','desc':'Два почти одновременных контакта металла с небольшим различием тембра.','event':'E051','room':'J','u':.53,'kind':'double_handle','duration':3.6,'volume':.39},
 {'id':'S16','name':'Еда в пустой кухне','desc':'Несколько тихих влажных щелчков и движение посуды в почти тихой комнате.','event':'E019','room':'B','u':.46,'kind':'empty_meal','duration':4.2,'volume':.25},
]


def filtered_noise(n, rng, low=None, high=None):
    if n <= 0: return np.zeros(0, dtype=np.float32)
    x = rng.standard_normal(n)
    f = np.fft.rfftfreq(n, 1/SR)
    mask = np.ones_like(f)
    if low is not None: mask *= 1.0 / np.sqrt(1.0 + (np.maximum(f,1e-9)/low)**8)
    if high is not None: mask *= 1.0 / np.sqrt(1.0 + (high/np.maximum(f,1e-9))**8)
    y = np.fft.irfft(np.fft.rfft(x) * mask, n=n)
    y /= max(float(np.std(y)), 1e-6)
    return y.astype(np.float32)


def add_noise(buf, t, dur, amp, rng, low=None, high=None, shape='flat'):
    i=max(0,int(t*SR)); n=min(len(buf)-i,int(dur*SR))
    if n<=0:return
    x=filtered_noise(n,rng,low,high)
    u=np.linspace(0,1,n,endpoint=False)
    if shape=='fade': env=np.minimum(1,u*14)*np.minimum(1,(1-u)*8)
    elif shape=='breath': env=(np.sin(np.pi*u)**1.7)
    elif shape=='rustle': env=np.maximum(0,np.sin(np.pi*u))**.55
    elif shape=='pulse': env=np.sin(np.pi*u)**2
    else: env=np.ones(n)
    buf[i:i+n]+=x*env.astype(np.float32)*amp


def add_tone(buf,t,dur,freq,amp,decay=3.0,phase=0.0):
    i=max(0,int(t*SR)); n=min(len(buf)-i,int(dur*SR))
    if n<=0:return
    u=np.arange(n,dtype=np.float32)/SR
    env=np.exp(-decay*u)
    buf[i:i+n]+=np.sin(2*np.pi*freq*u+phase)*env*amp


def impact(buf,t,amp=.3,base=160,decay=4.5,noise=.16,rng=None):
    add_tone(buf,t,.95,base,amp,decay)
    add_tone(buf,t,.65,base*2.37,amp*.48,decay*1.25,.4)
    add_tone(buf,t,.45,base*4.11,amp*.19,decay*1.8,1.2)
    add_noise(buf,t,.22,noise,rng,low=1800,high=110,shape='fade')


def breath(buf,t,dur,amp,rng,muffled=False):
    add_noise(buf,t,dur,amp,rng,low=900 if muffled else 2600,high=90,shape='breath')
    add_noise(buf,t+dur*.22,dur*.22,amp*.22,rng,low=700,high=180,shape='fade')


def voice_texture(buf,t,dur,amp,rng,child=False):
    # Deliberately nonverbal: a formant-like synthetic texture under canonical subtitles,
    # not a fabricated claim that an actor has recorded the line.
    n=int(dur*SR); i=max(0,int(t*SR)); n=min(n,len(buf)-i)
    if n<=0:return
    u=np.arange(n,dtype=np.float32)/SR
    f0=(205 if child else 118)+10*np.sin(2*np.pi*.8*u)
    phase=np.cumsum(2*np.pi*f0/SR)
    carrier=(np.sin(phase)+.43*np.sin(2*phase+.3)+.18*np.sin(3*phase+1.1))
    syll=np.maximum(0,np.sin(2*np.pi*(2.1 if child else 3.0)*u+0.7))**1.8
    noise=filtered_noise(n,rng,low=2800,high=260)
    radio=filtered_noise(n,rng,low=5200,high=1600)
    x=(carrier*.56+noise*.22)*syll + radio*.13
    x*=np.minimum(1,u*10)*np.minimum(1,(dur-u)*3)
    buf[i:i+n]+=x.astype(np.float32)*amp


def render(c):
    rng=np.random.default_rng(sum((i+1)*ord(ch) for i,ch in enumerate(c['id'])))
    n=int(c['duration']*SR); b=np.zeros(n,dtype=np.float32); k=c['kind']; d=c['duration']
    if k=='steps':
        # An impossible pre-echo arrives before the two ordinary steps.
        impact(b,.24,.10,105,7,.08,rng); impact(b,1.18,.25,78,5,.12,rng); impact(b,2.02,.22,82,5,.10,rng)
        add_noise(b,.05,3.0,.035,rng,low=550,high=60)
    elif k=='spoon':
        for t,f,a in [(.55,980,.25),(1.72,1330,.18),(2.05,720,.10)]:
            impact(b,t,a,f,5,.06,rng); add_tone(b,t,.8,f*2.9,a*.15,2.2,.2)
    elif k=='fan_slam':
        t=np.arange(min(int(3.1*SR),n),dtype=np.float32)/SR
        b[:len(t)]+=(.06*np.sin(2*np.pi*54*t)+.024*np.sin(2*np.pi*108*t))*np.minimum(1,(3.1-t)*2)
        add_noise(b,0,3.1,.08,rng,low=850,high=35,shape='fade')
        impact(b,15.0,.55,64,2.4,.27,rng); add_tone(b,15.02,.9,37,.24,3)
    elif k=='mirror_breath':
        breath(b,.8,1.35,.09,rng,True); breath(b,3.0,1.55,.075,rng,True); add_noise(b,0,d,.012,rng,low=260,high=55)
    elif k=='muffled_talk':
        voice_texture(b,.45,3.2,.045,rng); voice_texture(b,3.2,3.7,.037,rng); add_noise(b,0,d,.012,rng,low=1200,high=350)
    elif k=='airlock_knocks':
        for t in [.42,1.15,1.94]: impact(b,t,.43,72,3.4,.22,rng)
        add_noise(b,0,d,.012,rng,low=600,high=80)
    elif k=='tape_rewind':
        for j in range(11):
            t=.18+j*.39; dur=.19+rng.random()*.12
            add_noise(b,t,dur,.075+rng.random()*.04,rng,low=5200,high=900,shape='rustle')
        for t,f in [(.7,780),(1.9,610),(3.4,860)]: add_tone(b,t,.28,f,.035,8,rng.random())
        add_noise(b,0,d,.018,rng,low=6500,high=2500)
    elif k=='chair_fall':
        add_noise(b,.35,1.55,.13,rng,low=1700,high=180,shape='rustle')
        for t,f,a in [(1.8,180,.26),(2.06,94,.46),(2.28,430,.17)]: impact(b,t,a,f,4,.17,rng)
    elif k=='blanket_breath':
        add_noise(b,.22,.9,.12,rng,low=1100,high=180,shape='rustle'); breath(b,1.1,1.2,.10,rng,True); breath(b,3.0,1.0,.09,rng,True)
    elif k=='wall_kettle':
        add_noise(b,.1,d,.055,rng,low=1800,high=380)
        for t,f,a in [(1.2,440,.045),(2.4,520,.035),(4.1,690,.028)]: add_tone(b,t,1.1,f,a,1.0)
        add_noise(b,2.0,3.5,.045,rng,low=950,high=1800,shape='fade')
    elif k=='jacket_wind':
        add_noise(b,0,d,.055,rng,low=800,high=65,shape='fade')
        for t,dur,a in [(.7,.65,.10),(2.2,.9,.13),(3.9,.55,.08)]: add_noise(b,t,dur,a,rng,low=3000,high=550,shape='rustle')
    elif k=='child_radio':
        add_noise(b,0,d,.022,rng,low=5000,high=1400)
        voice_texture(b,.55,4.7,.11,rng,True)
        add_noise(b,4.8,1.1,.07,rng,low=4000,high=700,shape='fade')
        for t,f in [(.25,960),(2.9,1120),(4.4,780)]: add_tone(b,t,.18,f,.035,9)
    elif k=='wall_steps':
        add_noise(b,0,d,.025,rng,low=420,high=80)
        for t in [.55,1.38,2.22,3.05]: impact(b,t,.12,68,6,.055,rng)
    elif k=='radio_wind':
        add_noise(b,.15,.95,.15,rng,low=5200,high=1200,shape='fade')
        add_noise(b,.05,2.5,.035,rng,low=2200,high=3000)
        add_tone(b,.45,.42,1450,.04,7)
    elif k=='double_handle':
        impact(b,.55,.20,390,7,.07,rng); impact(b,.59,.17,540,8,.055,rng)
        add_noise(b,.5,.75,.04,rng,low=1800,high=450,shape='fade')
    elif k=='empty_meal':
        add_noise(b,.35,.22,.07,rng,low=4200,high=1700,shape='pulse')
        for t,f,a in [(1.05,850,.08),(1.42,620,.055),(2.45,1030,.06),(2.82,720,.04)]:
            add_tone(b,t,.12,f,a,14); add_noise(b,t,.10,.025,rng,low=5000,high=2200,shape='pulse')
        impact(b,3.3,.06,280,9,.025,rng)
    # Fade edges, keep dynamics quiet and avoid digital clipping.
    fade=min(int(.045*SR),n//4); b[:fade]*=np.linspace(0,1,fade); b[-fade:]*=np.linspace(1,0,fade)
    peak=float(np.max(np.abs(b))) if n else 0
    if peak>0: b*=min(.86,.86/peak)
    return b


def patch_event_data(data):
    events={e['id']:e for e in data['events']}
    for c in CUES:
        e=events.get(c['event'])
        if not e or e.get('room')!=c['room'] or not e.get('horror'):
            raise ValueError(f"Cue {c['id']} must map to a post-warmup horror event in {c['room']}: {c['event']}")
        e['timelineId']=e['id']
    for slot in data.get('assetSlots',[]):
        if slot.get('kind')=='audio' and slot.get('id') in {c['id'] for c in CUES}:
            slot['availability']='generated provisional synthetic design audio; not actor-recorded'
    return data


def update_list(existing, updates, key='id'):
    keep=[x for x in (existing or []) if x.get(key) not in {u.get(key) for u in updates}]
    return keep+updates


def patch_html(html, game):
    marker='window.BUILT_GAME='
    if html.count(marker)!=1: raise ValueError('Expected exactly one window.BUILT_GAME payload')
    pos=html.index(marker)+len(marker); lead=len(html[pos:])-len(html[pos:].lstrip())
    start=pos+lead; decoded, end=json.JSONDecoder().raw_decode(html[start:])
    payload=json.dumps(game,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return html[:start]+payload+html[start+end:]


def main():
    project=json.loads(PROJECT.read_text(encoding='utf-8'))
    adventure=json.loads(ADVENTURE.read_text(encoding='utf-8'))
    if len(adventure.get('events',[]))!=112 or len(adventure.get('quests',[]))!=12: raise ValueError('Canonical campaign structure changed')
    adventure=patch_event_data(adventure)
    AUDIO_DIR.mkdir(parents=True,exist_ok=True)
    project_audio=[]; built_audio={}; spatial=[]; timeline_by_id={t['id']:t for t in project.get('timelines',[])}
    for c in CUES:
        raw=render(c); path=AUDIO_DIR/(c['id'].lower()+'.ogg')
        sf.write(path,raw,SR,format='OGG',subtype='VORBIS')
        payload=path.read_bytes()
        if not payload.startswith(b'OggS') or len(payload)<1200: raise ValueError('Invalid audio output '+c['id'])
        rel='audio/spatial/'+path.name
        project_audio.append({'id':c['id'],'name':c['name'],'mime':'audio/ogg','file':rel})
        built_audio[c['id']]={'mime':'audio/ogg','data':base64.b64encode(payload).decode('ascii')}
        spatial.append({'id':c['id'],'name':c['name'],'roomId':c['room'],'audioId':c['id'],'u':c['u'],'volume':c['volume'],'loop':False,'autoplay':False})
        tl=timeline_by_id.get(c['event'])
        if not tl:
            tl={'id':c['event'],'name':c['event']+' · '+c['name'],'roomId':c['room'],'steps':[]}; project.setdefault('timelines',[]).append(tl); timeline_by_id[tl['id']]=tl
        tl['roomId']=c['room']; tl['steps']=[{'at':0,'type':'sound','value':c['id']}]
        if c.get('subtitle'): tl['steps'].append({'at':0,'type':'subtitle','value':c['subtitle']})
    project['audio']=update_list(project.get('audio',[]),project_audio)
    project['spatialSounds']=update_list(project.get('spatialSounds',[]),spatial)
    project['story']['adventure']=adventure
    PROJECT.write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ADVENTURE.write_text(json.dumps(adventure,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Update the actual shipped standalone runtime, not just the editable project.
    html=GAME_HTML.read_text(encoding='utf-8')
    marker='window.BUILT_GAME='
    pos=html.index(marker)+len(marker); lead=len(html[pos:])-len(html[pos:].lstrip()); start=pos+lead
    game,end=json.JSONDecoder().raw_decode(html[start:])
    game['audio']=dict(game.get('audio') or {}); game['audio'].update(built_audio)
    game['spatialSounds']=update_list(game.get('spatialSounds',[]),spatial)
    game['timelines']=update_list(game.get('timelines',[]),[timeline_by_id[c['event']] for c in CUES])
    game_adventure=game.setdefault('story',{}).setdefault('adventure',adventure)
    game_events={e['id']:e for e in game_adventure.get('events',[])}
    for c in CUES:
        if c['event'] not in game_events: raise ValueError('Shipped game missing event '+c['event'])
        game_events[c['event']]['timelineId']=c['event']
    GAME_HTML.write_text(patch_html(html,game),encoding='utf-8')
    # Mark the inventory honestly: generated sound design is useful and playable, but not actor-recorded final audio.
    for manifest in [ROOT/'reports/MISSING_ASSETS.tsv',ROOT/'studio/content/PRODUCTION/09_ASSET_SLOTS.tsv']:
        if not manifest.exists(): continue
        lines=manifest.read_text(encoding='utf-8').splitlines(); out=[lines[0]]
        for line in lines[1:]:
            cols=line.split('\t')
            if len(cols)>=5 and cols[0]=='audio' and cols[1] in {c['id'] for c in CUES}:
                cols[4]='generated provisional synthetic design audio; not actor-recorded'
                line='\t'.join(cols)
            out.append(line)
        manifest.write_text('\n'.join(out)+'\n',encoding='utf-8')
    print(f'Generated {len(CUES)} OGG cues ({sum((AUDIO_DIR/(c["id"].lower()+".ogg")).stat().st_size for c in CUES)} bytes); wired to 16 canonical story events and embedded in offline game.')

if __name__=='__main__': main()
