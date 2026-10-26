#!/usr/bin/env python3
"""Render the 13 missing authored found-footage slots as real silent MP4 clips."""
from __future__ import annotations
import base64, json, math, re, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'game-project/project.json'
ADVENTURE=ROOT/'studio/content/TIHAYA_VODA/adventure.json'
GAME_HTML=ROOT/'game/index.html'
OUT=ROOT/'game-project/video/found_footage'
W,H,FPS=320,180,6
VIDEO_IDS={'V01','V01B','V02','V03','V04','V05','V06','V07','V08','V09','V10','V11','V12'}
FONT_PATH='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD_PATH='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def font(size,bold=False):
    try:return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH,size)
    except OSError:return ImageFont.load_default()


def fit_lines(text,limit=48,max_lines=2):
    words=re.sub(r'\s+',' ',str(text or '')).split(); lines=[]; cur=''
    for word in words:
        if len(cur)+len(word)+1>limit and cur:
            lines.append(cur);cur=word
        else:cur=(cur+' '+word).strip()
    if cur:lines.append(cur)
    if len(lines)>max_lines:lines=lines[:max_lines];lines[-1]=lines[-1][:max(0,limit-1)]+'…'
    return lines


def shot_texts(media):
    frames=media.get('frames') or []
    out=[dict(start=float(f.get('start',0)),end=float(f.get('end',media.get('duration',10))),text=f.get('text','')) for f in frames]
    # V01B has a single authored timing card but a multi-beat alternate take.
    if len(out)==1 and float(media.get('duration',0))>20:
        production=str(media.get('production',''))
        sentences=[x.strip(' .\n\t') for x in re.split(r'(?<=[.!?])\s+|\n+',production) if len(x.strip())>24]
        source=[out[0]['text']]+sentences
        chosen=[]
        for x in source:
            if x and x not in chosen:chosen.append(x)
        chosen=chosen[:4] or [out[0]['text']]
        dur=float(media['duration'])/len(chosen)
        out=[dict(start=i*dur,end=(i+1)*dur,text=x) for i,x in enumerate(chosen)]
    if not out:out=[dict(start=0,end=float(media.get('duration',10)),text=media.get('production',''))]
    # Clamp and fill gaps so every second has a corresponding visual beat.
    duration=float(media.get('duration',max(x['end'] for x in out)))
    out[0]['start']=0
    for i,x in enumerate(out):
        x['start']=max(0,min(duration,x['start']))
        x['end']=max(x['start']+.2,min(duration,x['end']))
        if i and x['start']<out[i-1]['end']*.55:x['start']=out[i-1]['end']
    out[-1]['end']=duration
    for i in range(1,len(out)):
        if out[i]['start']>=out[i]['end'] or out[i]['start']>out[i-1]['end']+.5:
            out[i]['start']=out[i-1]['end']
    return out


def scene_type(mid,text,index):
    s=(mid+' '+text).lower()
    if mid in ('V01','V01B','V03','V12') and any(k in s for k in ['кух','чайник','круж','чаш','еда','холодиль']):return 'kitchen'
    if mid in ('V01','V01B','V07') and any(k in s for k in ['корид','двер','проход','оператор']):return 'corridor'
    if mid=='V02' or any(k in s for k in ['вентилятор','болт','ремонт','предохран']):return 'repair'
    if mid=='V03' or any(k in s for k in ['семейн','дочь','кассет','плён','плен','запис']):return 'tape'
    if mid=='V04' or any(k in s for k in ['створк','рычаг','шлюз','давлен','авари']):return 'airlock'
    if mid=='V05' or any(k in s for k in ['комисс','протокол','совещан','акт']):return 'commission'
    if mid=='V06' or any(k in s for k in ['озеров','архив','стул','зеркал','калибр']):return 'archive'
    if mid=='V08' or any(k in s for k in ['личн','персонал','карточ','список']):return 'personnel'
    if mid=='V09' or any(k in s for k in ['лаборатор','микроскоп','керн','зеркал']):return 'lab'
    if mid=='V10' or any(k in s for k in ['белов','монитор','радиоруб','экран']):return 'office'
    if mid=='V11' or any(k in s for k in ['ирина','мед','койк','пациент']):return 'medical'
    if any(k in s for k in ['антенн','снег','ветер','улиц','вышк','мачт']):return 'snow'
    if mid=='V12':return 'letter'
    return ['corridor','office','archive','lab'][index%4]


def gradient():
    y=np.linspace(0,1,H)[:,None,None]
    top=np.array([43,54,55],dtype=np.float32)[None,None,:]
    bottom=np.array([12,19,22],dtype=np.float32)[None,None,:]
    arr=np.broadcast_to(top*(1-y)+bottom*y,(H,W,3)).copy()
    x=np.linspace(-1,1,W)[None,:,None]
    vignette=np.clip(1-.23*(x*x)-.18*((y-.5)**2),.5,1.0)
    arr*=vignette
    return Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB')


def human(d,x,y,scale=1.0,coat=(26,31,31),lean=0):
    head=int(10*scale); shoulder=int(21*scale); body=int(47*scale)
    d.ellipse((x-head,y-int(44*scale),x+head,y-int(24*scale)),fill=(17,21,22),outline=(87,96,91),width=max(1,int(scale*1.3)))
    d.polygon([(x-shoulder,y-int(23*scale)),(x+shoulder,y-int(23*scale)),(x+int(16*scale)+lean,y+body),(x-int(18*scale)+lean,y+body)],fill=coat,outline=(77,83,76))
    d.line((x-shoulder+3,y-int(15*scale),x-int(29*scale)+lean,y+int(18*scale)),fill=(29,34,33),width=max(2,int(6*scale)))
    d.line((x+shoulder-3,y-int(15*scale),x+int(29*scale)+lean,y+int(18*scale)),fill=(29,34,33),width=max(2,int(6*scale)))
    d.line((x-int(8*scale)+lean,y+body,x-int(11*scale)+lean,y+body+int(28*scale)),fill=(16,20,21),width=max(2,int(7*scale)))
    d.line((x+int(8*scale)+lean,y+body,x+int(11*scale)+lean,y+body+int(28*scale)),fill=(16,20,21),width=max(2,int(7*scale)))


def draw_machine(d,x,y,w,h,kind='panel'):
    d.rounded_rectangle((x+2,y+3,x+w+2,y+h+3),radius=4,fill=(2,5,6),outline=(3,5,6),width=2)
    d.rounded_rectangle((x,y,x+w,y+h),radius=4,fill=(37,48,48),outline=(118,128,116),width=2)
    d.rectangle((x+5,y+5,x+w-5,y+int(h*.17)),fill=(21,29,30),outline=(76,88,83),width=1)
    if kind=='fan':
        cx=x+w//2;cy=y+h//2
        d.ellipse((cx-int(h*.28),cy-int(h*.28),cx+int(h*.28),cy+int(h*.28)),fill=(15,22,23),outline=(129,140,125),width=3)
        for ang in [0,90,180,270]:
            a=math.radians(ang); d.polygon([(cx,cy),(cx+math.cos(a)*h*.25,cy+math.sin(a)*h*.25),(cx+math.cos(a+1.2)*h*.17,cy+math.sin(a+1.2)*h*.17)],fill=(96,108,100))
        d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=(170,174,143))
    elif kind=='monitor':
        d.rectangle((x+9,y+10,x+w-9,y+int(h*.65)),fill=(8,18,21),outline=(102,119,112),width=2)
        d.line((x+16,y+int(h*.32),x+w-14,y+int(h*.32)),fill=(72,130,123),width=1)
        d.line((x+16,y+int(h*.46),x+w-26,y+int(h*.46)),fill=(54,103,98),width=1)
        d.rectangle((x+w*.4,y+h*.69,x+w*.6,y+h*.8),fill=(70,79,73))
    else:
        for i in range(3):
            xx=x+12+i*(w-24)/3; d.ellipse((xx,y+h*.36,xx+9,y+h*.36+9),fill=(196,157,88) if i==0 else (65,118,112))
        d.line((x+10,y+h*.65,x+w-10,y+h*.65),fill=(101,112,101),width=2)


def render_still(media,text,index,total):
    W0,H0=360,220
    global W,H
    ow,oh=W,H; W,H=W0,H0
    im=gradient(); d=ImageDraw.Draw(im,'RGBA'); mid=media['id']; typ=scene_type(mid,text,index)
    # Old Soviet polar station: steel wall, low ceiling, fluorescent lamps and hard perspective.
    d.rectangle((0,0,W,H*.19),fill=(22,30,31,255))
    d.polygon([(0,38),(W,38),(W,145),(0,145)],fill=(45,56,54,255))
    d.polygon([(0,145),(W,145),(W,H),(0,H)],fill=(18,26,28,255))
    for x in range(-60,W+80,58):
        d.line((x,42,x,143),fill=(92,102,91,90),width=1)
        d.line((W/2+(x-W/2)*.42,145,x,H),fill=(67,76,70,115),width=1)
    for y in [151,164,182,205]:d.line((0,y,W,y),fill=(58,68,62,80),width=1)
    # A ceiling fluorescent strip and occasional cold window.
    d.polygon([(W*.36,12),(W*.65,12),(W*.69,25),(W*.32,25)],fill=(184,187,157,170),outline=(222,224,196,200))
    d.line((W*.37,14,W*.63,14),fill=(235,238,204,210),width=2)
    if typ=='corridor':
        for side in [0,1]:
            x=14 if side==0 else W-62
            d.rectangle((x,58,x+48,143),fill=(26,36,36),outline=(111,121,104),width=2)
            d.rectangle((x+5,64,x+43,137),fill=(18,26,28),outline=(60,70,65),width=1)
            d.ellipse((x+35,100,x+39,104),fill=(163,156,119))
        d.rectangle((W*.39,47,W*.61,144),fill=(24,33,33),outline=(123,129,109),width=2)
        d.rectangle((W*.42,52,W*.58,140),fill=(10,16,18),outline=(63,75,70),width=1)
        d.line((W*.5,55,W*.5,138),fill=(66,78,72),width=2)
        if mid in ('V01','V01B','V07') and (index==total-1 or 'оператор' in text.lower() or 'фигур' in text.lower()): human(d,int(W*.5),int(H*.76),.56,(27,32,31))
    elif typ=='kitchen':
        d.rectangle((18,83,W-18,145),fill=(53,60,52),outline=(119,127,106),width=2)
        d.rectangle((25,89,W-25,101),fill=(109,102,76),outline=(163,148,107),width=1)
        d.rectangle((30,104,W-30,142),fill=(34,43,40),outline=(78,88,74),width=1)
        for x in [50,105,160,215,270,315]:d.line((x,105,x,141),fill=(64,74,65),width=1)
        d.ellipse((W*.2,52,W*.37,84),fill=(19,28,29),outline=(131,141,120),width=2)
        d.arc((W*.22,54,W*.35,82),0,180,fill=(164,165,135),width=2)
        d.rectangle((W*.65,57,W*.9,84),fill=(29,38,37),outline=(102,113,94),width=2)
        d.line((W*.67,65,W*.88,65),fill=(136,143,111),width=1)
        if 'чайник' in text.lower() or index%3==0:
            d.ellipse((W*.43,72,W*.56,85),fill=(22,30,30),outline=(160,155,123),width=2)
            d.arc((W*.53,75,W*.59,83),270,90,fill=(152,150,123),width=2)
        if mid in ('V03','V12') and ('пётр' in text.lower() or 'анна' in text.lower() or index==total-1):human(d,int(W*.78),int(H*.78),.55,(31,37,35))
    elif typ=='repair':
        draw_machine(d,80,50,190,110,'fan')
        d.line((40,160,320,160),fill=(120,127,102),width=2)
        for x,y in [(103,58),(245,58),(103,152),(245,152)]:d.ellipse((x-4,y-4,x+4,y+4),fill=(169,169,139),outline=(36,42,38),width=1)
        d.rectangle((22,56,58,143),fill=(31,41,40),outline=(101,112,97),width=2)
        d.line((30,65,49,134),fill=(132,136,112),width=2)
        if index in (1,total-1):human(d,292,151,.48,(32,37,34),-3)
    elif typ=='tape':
        d.rectangle((28,62,W-28,151),fill=(39,49,45),outline=(105,117,96),width=2)
        # Cassette/reel deck, two spools, tape window and a paper label.
        d.rounded_rectangle((W*.22,72,W*.78,134),radius=4,fill=(17,25,25),outline=(130,133,104),width=2)
        for cx in [W*.37,W*.63]:
            d.ellipse((cx-17,83,cx+17,117),fill=(28,36,34),outline=(161,155,119),width=2)
            d.ellipse((cx-5,95,cx+5,105),fill=(151,145,109),outline=(52,60,52),width=1)
        d.polygon([(W*.4,88),(W*.6,88),(W*.58,112),(W*.42,112)],fill=(62,72,63),outline=(123,130,103))
        d.rectangle((W*.42,55,W*.58,66),fill=(183,172,139),outline=(73,73,61),width=1)
        d.text((W*.43,57),'VHS',font=font(7,True),fill=(43,47,40))
        if index==total-1:human(d,int(W*.78),155,.52,(29,34,32))
    elif typ=='airlock':
        d.rectangle((70,39,290,174),fill=(20,28,30),outline=(126,134,114),width=3)
        d.rectangle((82,49,278,166),fill=(32,41,41),outline=(72,84,77),width=2)
        d.rectangle((102,63,258,111),fill=(8,16,18),outline=(88,100,91),width=2)
        d.line((180,66,180,109),fill=(66,81,75),width=2)
        draw_machine(d,25,78,45,65,'panel'); draw_machine(d,290,78,45,65,'panel')
        d.ellipse((W*.47,117,W*.53,145),fill=(149,148,115),outline=(24,30,28),width=2)
        if 'человек' in text.lower() or 'белов' in text.lower() or index==total-1:human(d,180,164,.48,(25,31,30))
    elif typ=='commission':
        d.rectangle((25,105,W-25,135),fill=(53,48,38),outline=(116,109,85),width=2)
        for i,x in enumerate([55,111,178,246,305]):
            human(d,x,116,.48,(25+i*2,30+i,30+i),(-5 if i%2 else 3))
        for x in [65,135,205,275]:d.rectangle((x,119,x+22,126),fill=(179,171,139),outline=(89,86,70),width=1)
        d.rectangle((145,45,215,81),fill=(24,34,34),outline=(101,115,100),width=2)
        d.text((152,54),'КОМИССИЯ',font=font(8,True),fill=(178,185,153))
    elif typ=='archive':
        for x in [22,105,188,271]:
            d.rectangle((x,48,x+62,155),fill=(34,43,39),outline=(105,114,92),width=2)
            for j in range(4):
                y=57+j*23; d.line((x+5,y+17,x+56,y+17),fill=(101,104,82),width=2)
                d.rectangle((x+8,y,x+24,y+14),fill=(139+j*4,127+j*3,94),outline=(65,65,53),width=1)
                d.rectangle((x+28,y+2,x+51,y+14),fill=(75,86,75),outline=(34,41,37),width=1)
        d.ellipse((W*.37,65,W*.63,119),fill=(12,19,20,120),outline=(160,167,144,190),width=3)
        d.line((W*.5,66,W*.5,118),fill=(167,174,147,150),width=2)
        if index==total-1: d.line((W*.4,130,W*.62,152),fill=(178,160,121),width=4)
    elif typ=='personnel':
        for row in range(2):
            for col in range(5):
                x=22+col*66;y=47+row*57
                d.rectangle((x,y,x+52,y+47),fill=(39,49,44),outline=(111,121,99),width=1)
                d.rectangle((x+5,y+5,x+20,y+22),fill=(80,88,75),outline=(137,138,111),width=1)
                d.ellipse((x+9,y+7,x+16,y+14),fill=(17,23,23))
                d.polygon([(x+7,y+22),(x+18,y+22),(x+21,y+33),(x+4,y+33)],fill=(22,28,28))
                d.line((x+26,y+12,x+47,y+12),fill=(173,165,132),width=1)
                d.line((x+26,y+20,x+43,y+20),fill=(93,103,85),width=1)
                d.line((x+6,y+39,x+45,y+39),fill=(94,100,81),width=1)
    elif typ=='lab':
        d.rectangle((20,112,W-20,150),fill=(45,54,48),outline=(116,123,99),width=2)
        draw_machine(d,36,61,54,64,'panel'); draw_machine(d,125,55,90,75,'monitor')
        d.polygon([(242,62),(300,62),(311,111),(231,111)],fill=(44,59,56),outline=(128,143,119))
        for x in [249,267,285]:d.line((x,70,x+4,104),fill=(119,153,142),width=2)
        if index%2:human(d,295,151,.45,(26,32,30))
    elif typ=='office':
        d.rectangle((25,112,W-25,139),fill=(51,48,39),outline=(119,109,83),width=2)
        draw_machine(d,95,47,130,91,'monitor')
        d.rectangle((37,61,79,98),fill=(24,33,34),outline=(103,111,92),width=2)
        d.line((45,72,70,72),fill=(87,132,119),width=1)
        d.rectangle((250,58,321,102),fill=(30,40,39),outline=(101,113,92),width=2)
        d.arc((263,67,306,94),190,350,fill=(150,160,131),width=2)
        if index%2==1 or 'отраж' in text.lower():human(d,179,133,.49,(20,25,26))
    elif typ=='medical':
        d.rectangle((24,94,W-24,134),fill=(58,65,54),outline=(123,130,104),width=2)
        d.rectangle((37,61,W-37,96),fill=(91,98,82),outline=(153,154,123),width=2)
        d.rectangle((42,66,W-42,90),fill=(147,149,127),outline=(181,178,148),width=1)
        d.polygon([(83,65),(252,65),(267,87),(73,87)],fill=(185,184,157,220))
        d.ellipse((W*.43,57,W*.57,76),fill=(115,119,103),outline=(175,174,143),width=1)
        d.rectangle((260,50,326,89),fill=(19,29,31),outline=(114,123,99),width=2)
        d.line((267,70,277,70),fill=(92,155,141),width=2);d.line((277,70,285,60,296,79,305,66,318,66),fill=(92,155,141),width=1)
    elif typ=='snow':
        d.rectangle((0,80,W,145),fill=(95,111,109))
        d.polygon([(0,150),(W,140),(W,H),(0,H)],fill=(158,169,159))
        d.polygon([(W*.2,40),(W*.8,40),(W*.76,145),(W*.24,145)],fill=(22,33,35),outline=(118,133,126))
        for x in [W*.3,W*.7]:d.line((x,45,x,145),fill=(148,161,151),width=2)
        for y in [65,88,111]:d.line((W*.28,y,W*.72,y),fill=(140,154,146),width=1)
        for i in range(20):
            x=(i*47+index*13)%W;y=(i*29+index*17)%H;d.ellipse((x,y,x+1,y+2),fill=(223,229,215,170))
        if index%2:human(d,int(W*.68),150,.48,(24,30,31))
    elif typ=='letter':
        d.rectangle((0,130,W,H),fill=(21,27,26))
        d.ellipse((W*.55,25,W*.85,100),fill=(170,135,78,35))
        d.rectangle((45,48,270,154),fill=(187,179,145),outline=(95,93,72),width=2)
        for i in range(6):
            yy=61+i*14; d.line((57,yy,248-(i%3)*18,yy),fill=(66,70,58,190),width=1)
        d.text((58,54),'ОЛЕ',font=font(9,True),fill=(43,46,38))
        d.polygon([(270,48),(305,65),(300,155),(270,154)],fill=(41,48,43),outline=(104,110,91))
        d.ellipse((W*.72,56,W*.82,98),fill=(18,24,25),outline=(120,126,104),width=2)
    # The footage is deliberately imperfect, but readable at the actual game viewport size.
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((0,0,W,14),fill=(0,0,0,70));d.rectangle((0,H-24,W,H),fill=(0,0,0,175))
    d.ellipse((7,5,13,11),fill=(170,37,33,235));d.text((17,3),'REC',font=font(8,True),fill=(212,204,178,230))
    d.text((W-58,3),f'{2023+int(mid[1:3])%6:04d}',font=font(8),fill=(204,201,173,205))
    for i,line in enumerate(fit_lines(text,54,2)):
        d.text((7,H-22+i*9),line,font=font(8),fill=(224,220,194,245),stroke_width=1,stroke_fill=(0,0,0,220))
    # Restore global dimensions for caller.
    W,H=ow,oh
    return im


def camera_frame(still, t, shot_t, shot_d, frame_no, rng):
    # A slow handheld crop, small gate weave, intermittent dust and scan lines.
    sw,sh=still.size; zoom=1.02+.055*min(1,shot_t/max(.1,shot_d))
    cw=max(W,int(sw/zoom));ch=max(H,int(sh/zoom))
    maxx=max(0,sw-cw);maxy=max(0,sh-ch)
    x=int(maxx*(.5+.38*math.sin(shot_t*.27+frame_no*.01)))
    y=int(maxy*(.5+.34*math.sin(shot_t*.19+frame_no*.014)))
    frame=still.crop((x,y,x+cw,y+ch)).resize((W,H),Image.Resampling.BICUBIC).convert('RGB')
    d=ImageDraw.Draw(frame,'RGBA')
    # VHS tracking lines and a mild horizontal wobble.
    if frame_no%3==0:
        yy=int((frame_no*17)%H);d.rectangle((0,yy,W,yy+1),fill=(202,210,191,28))
    if frame_no%29==0:
        yy=int((frame_no*7)%H);d.rectangle((0,yy,W,min(H,yy+2)),fill=(219,226,204,42))
    for j in range(2):
        px=int(rng.integers(0,W));py=int(rng.integers(0,H));d.ellipse((px,py,px+1,py+1),fill=(235,231,210,80))
    # Low contrast, cool archival tint; never black out the image.
    arr=np.asarray(frame,dtype=np.float32); arr[:,:,0]*=.91;arr[:,:,1]*=.96;arr[:,:,2]*=1.02
    return Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB')


def render_clip(media,path,ffmpeg):
    duration=float(media.get('duration',10)); shots=shot_texts(media); stills=[]
    for i,shot in enumerate(shots): stills.append((shot,render_still(media,shot['text'],i,len(shots))))
    total=max(1,int(math.ceil(duration*FPS))); rng=np.random.default_rng(sum(ord(x) for x in media['id']))
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s:v',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','30','-pix_fmt','yuv420p','-movflags','+faststart','-t',str(duration),'-metadata',f'title={media["id"]} · {media["title"]}',str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        si=0
        for n in range(total):
            t=n/FPS
            while si<len(stills)-1 and t>=stills[si][0]['end']-.01:si+=1
            sh,still=stills[si]; shot_t=max(0,t-sh['start']); shot_d=max(.2,sh['end']-sh['start'])
            frame=camera_frame(still,t,shot_t,shot_d,n,rng)
            proc.stdin.write(np.asarray(frame,dtype=np.uint8).tobytes())
        proc.stdin.close(); err=proc.stderr.read().decode('utf-8','replace'); code=proc.wait(timeout=240)
        if code: raise RuntimeError(f'ffmpeg failed for {media["id"]}: {err[-1200:]}')
    except Exception:
        try:proc.kill()
        except Exception:pass
        raise
    raw=path.read_bytes()
    if b'ftyp' not in raw[:32] or len(raw)<10000:raise ValueError(f'Invalid MP4 {path}: {len(raw)} bytes')
    return len(raw)


def update(existing,updates):
    ids={x['id'] for x in updates};return [x for x in (existing or []) if x.get('id') not in ids]+updates


def patch_html(html,game):
    marker='window.BUILT_GAME='
    if html.count(marker)!=1:raise ValueError('Expected one standalone game payload')
    pos=html.index(marker)+len(marker); pos+=len(html[pos:])-len(html[pos:].lstrip()); start=pos
    _,end=json.JSONDecoder().raw_decode(html[start:])
    encoded=json.dumps(game,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return html[:start]+encoded+html[start+end:]


def main():
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:raise SystemExit('ffmpeg is required to render found footage')
    project=json.loads(PROJECT.read_text(encoding='utf-8')); adventure=json.loads(ADVENTURE.read_text(encoding='utf-8'))
    media=[m for m in adventure['media'] if m.get('kind')=='video' and m.get('id') in VIDEO_IDS]
    if {m['id'] for m in media}!=VIDEO_IDS:raise ValueError('Expected all 13 authored V01–V12/V01B slots')
    OUT.mkdir(parents=True,exist_ok=True); project_videos=[]; built_videos={}; media_by_id={m['id']:m for m in adventure['media']}
    for m in media:
        aid=m['id']; path=OUT/(aid.lower()+'.mp4'); size=render_clip(m,path,ffmpeg); raw=path.read_bytes()
        project_videos.append({'id':aid,'name':m['title'],'mime':'video/mp4','file':'video/found_footage/'+path.name})
        built_videos[aid]={'mime':'video/mp4','data':base64.b64encode(raw).decode('ascii')}
        m['assetId']=aid
        for slot in adventure.get('assetSlots',[]):
            if slot.get('kind')=='video' and slot.get('id')==aid:slot['availability']='generated procedural found-footage clip; silent; not live-action'
        print(aid,'seconds',m['duration'],'frames',int(math.ceil(float(m['duration'])*FPS)),'bytes',size)
    project['videos']=update(project.get('videos',[]),project_videos)
    project['story']['adventure']=adventure
    PROJECT.write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    ADVENTURE.write_text(json.dumps(adventure,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=ROOT/'reports/adventure.json'
    if report.parent.exists(): report.write_text(json.dumps(adventure,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    html=GAME_HTML.read_text(encoding='utf-8'); marker='window.BUILT_GAME='; pos=html.index(marker)+len(marker); pos+=len(html[pos:])-len(html[pos:].lstrip()); game,_=json.JSONDecoder().raw_decode(html[pos:])
    game['video']=dict(game.get('video') or {});game['video'].update(built_videos)
    game_media={m['id']:m for m in game.get('story',{}).get('adventure',{}).get('media',[])}
    for aid in VIDEO_IDS:
        if aid not in game_media:raise ValueError('Shipped game missing media slot '+aid)
        game_media[aid]['assetId']=aid
    GAME_HTML.write_text(patch_html(html,game),encoding='utf-8')
    for manifest in [ROOT/'reports/MISSING_ASSETS.tsv',ROOT/'studio/content/PRODUCTION/09_ASSET_SLOTS.tsv']:
        if manifest.exists():
            lines=manifest.read_text(encoding='utf-8').splitlines();out=[lines[0]]
            for line in lines[1:]:
                cols=line.split('\t')
                if len(cols)>=5 and cols[0]=='video' and cols[1] in VIDEO_IDS:
                    cols[3]='video/found_footage/'+cols[1].lower()+'.mp4';cols[4]='generated procedural found-footage clip; silent; not live-action';line='\t'.join(cols)
                out.append(line)
            manifest.write_text('\n'.join(out)+'\n',encoding='utf-8')
    print('PASS generated',len(VIDEO_IDS),'found-footage clips; embedded bytes',sum(len(base64.b64decode(x['data'])) for x in built_videos.values()))

if __name__=='__main__':main()
