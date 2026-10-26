#!/usr/bin/env python3
"""Build distinct, ray-traced 360-degree room art and embed it in the offline game/editor.
Only visual assets are touched. Audio/video assets and their story wiring are left unchanged.
"""
import argparse,base64,hashlib,json,math,re,sys
from pathlib import Path
from collections import defaultdict
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'production/geometry/B_NORMAL';sys.path.insert(0,str(B))
import render_kitchen360 as R
NAMES={'A':'ЖИЛОЙ МОДУЛЬ','B':'КУХНЯ','C':'КОРИДОР','D':'РАДИОРУБКА','E':'ДИЗЕЛЬНАЯ','F':'СКЛАД','G':'ЛАБОРАТОРИЯ','H':'АРХИВ','I':'МЕДПУНКТ','J':'ШЛЮЗ','K':'НАРУЖНЫЙ ДВОР','L':'ГАЛЕРЕЯ','M':'СКВАЖИННЫЙ БЛОК','N':'ДЛИННЫЙ КОРИДОР','O':'АРХИВ · 1978','P':'НИЖНЯЯ КАМЕРА'}
PALETTE={'A':((102,109,91),(74,77,65),(143,136,110),(174,151,91)),'C':((87,104,99),(54,61,55),(122,132,116),(67,131,127)),'D':((64,78,72),(43,49,44),(105,113,96),(67,151,114)),'E':((77,80,67),(51,51,43),(112,104,79),(183,105,43)),'F':((93,86,68),(57,53,44),(122,109,82),(159,119,62)),'G':((87,105,93),(53,61,54),(118,133,113),(91,159,134)),'H':((89,78,59),(54,48,39),(116,99,72),(176,128,66)),'I':((112,121,101),(75,80,66),(152,155,127),(142,168,135)),'J':((68,78,75),(39,44,42),(98,109,99),(177,54,43)),'K':((102,119,116),(164,176,168),(126,145,143),(100,174,190)),'L':((88,105,101),(53,61,58),(120,131,119),(80,135,157)),'M':((74,82,71),(47,50,43),(103,105,85),(173,102,48)),'N':((82,94,89),(49,54,49),(114,121,104),(177,59,49)),'O':((104,86,62),(67,54,40),(135,111,78),(185,133,65)),'P':((61,72,67),(36,41,39),(91,103,90),(177,48,43))}
def box(*a):R.box(*a)
def shell(r):
 wall,floor,ceil,trim=PALETTE[r]
 box('floor',(-3,-.06,-2.5),(3,0,2.5),floor,'floor')
 if r=='K':
  box('snow_field',(-20,-.07,-20),(20,-.005,20),(171,182,176),'floor')
  box('distant_fence',(-20,0,-18),(20,4.5,-17.9),(91,111,106),'steel')
  box('left_snowbank',(-18,0,-18),(-17.9,3,18),(119,137,130),'steel')
  box('right_snowbank',(17.9,0,-18),(18,3,18),(119,137,130),'steel')
  return
 box('ceiling',(-3,2.82,-2.5),(3,2.9,2.5),ceil,'panels')
 for name,lo,hi in [('back',(-3,0,-2.58),(3,2.82,-2.5)),('front',(-3,0,2.5),(3,2.82,2.58)),('left',(-3.08,0,-2.58),(-3,2.82,2.58)),('right',(3,0,-2.58),(3.08,2.82,2.58))]:box(name,lo,hi,wall,'panels')
 for i,x in enumerate(([-2.35,-1.2,0,1.2,2.35] if r in ('C','L','N') else [-2.25,0,2.25])):
  box(f'rib_back_{i}',(x-.025,.08,-2.53),(x+.025,2.68,-2.49),trim,'steel')
  box(f'rib_front_{i}',(x-.025,.08,2.49),(x+.025,2.68,2.53),trim,'steel')
 for i,z in enumerate([-1.65,0,1.65]):
  box(f'side_rib_left_{i}',(-3.05,.08,z-.025),(-3.01,2.68,z+.025),trim,'steel')
  box(f'side_rib_right_{i}',(3.01,.08,z-.025),(3.05,2.68,z+.025),trim,'steel')
 # Physical printed room identity; part of the 3D scene, not a screen overlay.
 title='room_title_'+r;R.signage.PRINTED[title]=(NAMES[r],'СТАНЦИЯ МАЯК-9',[f'СЕКТОР {r}','ДОПУСК ПО СПИСКУ'],'red' if r in 'JMP' else 'blue')
 box(title,(-1.0,2.28,-2.47),(1.0,2.72,-2.40),(191,184,151),'paper')
 accent=PALETTE[r][3]
 for i,z in enumerate([-1.65,.75]):box('lamp_'+str(i),(-.48,2.72,z-.12),(.48,2.79,z+.12),accent if r in 'DEGJKMP' else (202,204,177),'lamp')
 box('base_back',(-3,.08,-2.43),(3,.16,-2.36),trim,'steel')

def door(axis,side,pos,name,w=.9,h=2.18):
 if axis=='z':
  z=side*2.43;x=pos;box(name+'_frame',(x-w/2-.07,.05,z-.08),(x+w/2+.07,h+.06,z+.08),(126,132,112),'steel');box(name+'_leaf',(x-w/2,.1,z-.035),(x+w/2,h,z+.035),(52,65,62),'paint');box(name+'_seam',(x-.012,.15,z-.045),(x+.012,h-.12,z+.045),(19,27,25),'steel');box(name+'_handle',(x+w*.32,.95,z-.055),(x+w*.37,1.18,z+.055),(176,164,123),'steel')
 else:
  x=side*2.9;box(name+'_frame',(x-.08,.05,pos-w/2-.07),(x+.08,h+.06,pos+w/2+.07),(126,132,112),'steel');box(name+'_leaf',(x-.035,.1,pos-w/2),(x+.035,h,pos+w/2),(52,65,62),'paint');box(name+'_handle',(x-.055,.95,pos+w*.32-.025),(x+.055,1.18,pos+w*.32+.025),(176,164,123),'steel')
def shelf(x,z,name,w=1.0,h=1.9,d=.4,rows=4):
 box(name+'_back',(x-w/2,.1,z-d/2),(x+w/2,h,z-d/2+.04),(62,69,55),'wood')
 for xx in (x-w/2,x+w/2-.05):box(name+'_side'+str(xx),(xx,.1,z-d/2),(xx+.05,h,z+d/2),(72,76,59),'wood')
 for i in range(rows+1):
  y=.15+(h-.2)*i/rows;box(name+'_shelf'+str(i),(x-w/2,y,z-d/2),(x+w/2,y+.05,z+d/2),(103,91,65),'wood')
 for i in range(rows):
  for j in range(3):
   xx=x-w*.42+j*w*.29;y=.23+(h-.3)*i/rows;box(name+'_crate'+str(i)+'_'+str(j),(xx,y,z-d*.3),(xx+w*.19,y+.16,z+d*.3),(107+i*3,91+j*4,66),'wood')
def table(x,z,name,w=1.2,d=.7,y=.78):
 box(name+'_top',(x-w/2,y,z-d/2),(x+w/2,y+.08,z+d/2),(92,76,51),'wood')
 for xx in (x-w*.42,x+w*.42):
  for zz in (z-d*.35,z+d*.35):box(name+'_leg'+str(xx)+str(zz),(xx-.04,.08,zz-.04),(xx+.04,y,zz+.04),(55,59,48),'steel')
def console(x,z,name,w=1.2,h=1.05,d=.5):
 y=.72;box(name+'_body',(x-w/2,y,z-d/2),(x+w/2,y+h,z+d/2),(43,54,51),'steel');box(name+'_screen',(x-w*.34,y+.4,z-d/2-.025),(x+w*.34,y+h-.12,z-d/2+.025),(9,23,26),'glass')
 for j in range(3):box(name+'_scan'+str(j),(x-w*.27,y+.48+j*.09,z-d/2-.035),(x+w*.25,y+.495+j*.09,z-d/2+.035),(64,135,113),'glass')
 for i,c in enumerate(((177,49,39),(174,150,89),(64,132,112))):box(name+'_button'+str(i),(x-w*.3+i*w*.25,y+.13,z-d/2-.04),(x-w*.3+i*w*.25+.09,y+.22,z-d/2+.035),c,'lamp' if i==0 else 'steel')
def landmarks(r):
 if r=='A':
  for x in [-1.7,1.7]:
   box('bunk_frame'+str(x),(x-.45,.22,-.1),(x+.45,.34,1.8),(54,63,56),'steel');box('bunk_mattress'+str(x),(x-.4,.34,0),(x+.4,.5,1.72),(145,145,121),'cloth');box('bunk_pillow'+str(x),(x-.32,.5,0),(x+.32,.6,.34),(183,178,146),'cloth')
  shelf(-2.2,-1.4,'personal_locker',.65,1.9,.45,3);door('z',1,-1.8,'dorm_exit')
 elif r=='C':
  for x in [-1.6,1.6]:door('z',-1,x,'corridor_door_'+str(x));door('x',-1,x*.45,'side_door_'+str(x),.8)
  box('mirror_frame',(-2.97,1,-.4),(-2.88,2.2,.55),(128,135,117),'steel');box('mirror_glass',(-2.86,1.08,-.32),(-2.83,2.12,.47),(61,98,105),'glass')
 elif r=='D':
  console(0,-1.3,'radio_console',2.0,1.25,.7);table(0,-.1,'radio_desk',1.8,.8,.8);shelf(-2.2,-1.3,'reel_shelf',.65,1.8,.4,4)
  for x in [-.45,.45]:R.CURVED.append(R.curved.ellipsoid('radio_reel'+str(x),(x,1.55,-1.75),(.22,.22,.06),(140,128,89),'enamel'))
  door('z',1,1.8,'radio_exit')
 elif r=='E':
  box('diesel_base',(-1.15,.1,-1.3),(1.15,.48,.1),(48,54,48),'steel');box('diesel_engine',(-.95,.48,-1.15),(.95,1.85,-.18),(112,75,40),'steel')
  for x in [-.72,-.36,0,.36,.72]:box('engine_rib'+str(x),(x-.035,.58,-.16),(x+.035,1.68,-.10),(210,166,69),'steel')
  console(0,-2.0,'diesel_controls',1.1,.8,.4);door('z',1,1.8,'diesel_exit')
 elif r=='F':
  shelf(-2.1,-1.25,'rack_left',.95,2.2,.45,5);shelf(2.1,-1.25,'rack_right',.95,2.2,.45,5);shelf(-2.1,1.0,'rack_back',.9,1.9,.4,4);table(0,.25,'sorting_table',1.4,.8,.78);door('z',1,1.8,'store_exit')
 elif r=='G':
  table(-1.2,-.55,'lab_bench',1.4,.8,.82);table(1.2,-.55,'sample_bench',1.4,.8,.82);console(0,-2.1,'lab_monitor',1.2,.9,.45);shelf(2.2,.9,'sample_rack',.6,1.6,.35,4)
  for x,c in [(-.55,(68,129,115)),(0,(97,156,132)),(.55,(67,111,103))]:R.CURVED.append(R.curved.ellipsoid('sample_flask'+str(x),(x,1.1,-.5),(.13,.2,.13),c,'glass'))
  door('z',1,1.8,'lab_exit')
 elif r=='H':
  shelf(-2.15,-1.25,'film_rack_left',.9,2.2,.42,5);shelf(2.15,-1.25,'film_rack_right',.9,2.2,.42,5);table(0,-.25,'film_table',1.4,.75,.78);console(0,-2.1,'film_deck',1.15,.85,.5)
  for x in [-.38,.38]:R.CURVED.append(R.curved.ellipsoid('film_reel'+str(x),(x,1.52,-1.2),(.23,.23,.06),(136,112,72),'enamel'))
  door('z',1,1.8,'archive_exit')
 elif r=='I':
  for x in [-1.4,1.4]:
   box('medical_bed'+str(x),(x-.45,.22,-1.2),(x+.45,.38,.6),(53,63,58),'steel');box('medical_mattress'+str(x),(x-.4,.38,-1.15),(x+.4,.52,.55),(157,158,135),'cloth')
  console(-2.2,-1.4,'patient_monitor',.55,.9,.4);shelf(2.2,.9,'medicine_cabinet',.6,1.8,.4,4)
  box('cross_back',(-2.45,1.8,-2.39),(-1.3,2.45,-2.31),(178,179,154),'steel');box('cross_v',(-1.96,1.93,-2.29),(-1.79,2.32,-2.26),(168,49,43),'lamp');box('cross_h',(-2.22,2.08,-2.29),(-1.52,2.21,-2.26),(168,49,43),'lamp');door('z',1,1.8,'medical_exit')
 elif r=='J':
  door('z',-1,0,'outer_airlock',1.3);door('z',1,0,'inner_airlock',1.3);console(-2.2,-1.6,'pressure_controls',.6,.9,.4);console(2.2,-1.6,'intercom',.6,.9,.4)
  box('warning_band',(-1.4,.38,-2.36),(1.4,.51,-2.3),(176,47,39),'steel')
  for x in [-.9,-.3,.3,.9]:box('warning_mark'+str(x),(x-.06,.39,-2.29),(x+.06,.5,-2.27),(210,172,78),'steel')
 elif r=='K':
  box('snow_ground',(-20,-.09,-20),(20,0,20),(171,182,176),'floor');box('distant_fence',(-20,0,-18),(20,5,-17.9),(91,111,106),'steel')
  for x in [-.45,.45]:box('antenna_leg'+str(x),(x-.05,.1,-5.8),(x+.05,7.4,-5.0),(119,137,130),'steel')
  for y in [1,2,3,4,5,6,7]:box('antenna_cross'+str(y),(-.5,y,-5.4),(.5,y+.045,-5.4),(143,154,145),'steel')
  box('service_hut',(1.4,0,-3.8),(2.8,2.5,-2.5),(69,80,77),'steel');door('x',1,-3.1,'yard_service_door',.7,2.1)
  R.signage.PRINTED['antenna_sign']=('АНТЕННА К-9','НАРУЖНЫЙ ДВОР',['МАЯК-9 / ЛИНИЯ СВЯЗИ'],'red');box('antenna_sign',(1.5,1.7,-3.84),(2.65,2.35,-3.77),(186,183,159),'paper')
 elif r=='L':
  for i,x in enumerate([-1.8,0,1.8]):
   box('gallery_window_frame'+str(i),(x-.5,1.25,-2.56),(x+.5,2.25,-2.48),(124,135,122),'steel');box('gallery_window'+str(i),(x-.43,1.32,-2.47),(x+.43,2.18,-2.43),(112,177,192),'window')
  door('z',1,-1.7,'gallery_exit');console(2.2,-1.5,'gallery_shutter',.55,.9,.4)
 elif r=='M':
  box('drill_base',(-1.1,.15,-2.1),(1.1,.48,-.75),(54,61,53),'steel');R.CURVED.append(R.curved.ellipsoid('drill_head',(0,1.2,-1.3),(.56,.56,.3),(94,105,88),'steel'));R.CURVED.append(R.curved.cylinder('drill_spindle',(0,1.18,-1.2),.14,.2,2.05,(130,125,92),'steel'));console(1.8,-1.7,'drill_monitor',.8,1,.4);door('z',1,1.8,'bore_exit')
 elif r=='N':
  for x in [-1.6,1.6]:door('z',-1,x,'north_door'+str(x));door('z',1,0,'north_exit');console(-2.2,-1.7,'north_panel',.55,.9,.4)
  R.CURVED.append(R.curved.ellipsoid('north_clock',(2.7,2.0,-.2),(.05,.28,.28),(173,169,132),'enamel'))
 elif r=='O':
  shelf(-2.15,-1.3,'old_rack_left',.9,2.2,.45,5);shelf(2.15,-1.3,'old_rack_right',.9,2.2,.45,5);table(0,-.25,'1978_desk',1.5,.8,.78);console(0,-2.1,'reel_projector',1,.75,.45)
  for x in [-.3,.3]:R.CURVED.append(R.curved.ellipsoid('old_reel'+str(x),(x,1.48,-1.2),(.21,.21,.05),(156,118,67),'enamel'))
  door('z',1,1.8,'old_archive_exit')
 elif r=='P':
  console(0,-1.25,'final_console',2.35,1.5,.8);table(0,.45,'final_table',1.8,.85,.78);door('z',1,2.0,'final_exit')
  for i,x in enumerate([-1.25,-.42,.42,1.25]):
   c=[(171,47,39),(175,151,89),(65,128,112),(93,110,98)][i];box('final_button'+str(i),(x-.16,1.15,-2.36),(x+.16,1.5,-2.28),c,'lamp' if i==0 else 'steel')

def add_hotspot_props(r,room):
 groups=defaultdict(list)
 for o in room.get('objects',[]):
  cs=o.get('corners') or []
  if cs:groups[(round(sum(float(c['u']) for c in cs)/len(cs),3),round(sum(float(c['v']) for c in cs)/len(cs),3))].append(o)
 count=0
 for i,((u,v),obs) in enumerate(sorted(groups.items())):
  phi=(u-.5)*2*math.pi;dx=math.sin(phi);dz=-math.cos(phi);tx=2.91/max(abs(dx),1e-4);tz=2.42/max(abs(dz),1e-4);t=min(tx,tz);x=dx*t;z=dz*t;y=max(.38,min(2.38,1.65+t*math.tan((.5-v)*math.pi)))
  names=' '.join(str(o.get('name',''))+' '+str(o.get('id','')) for o in obs).lower();kind='paper' if any(k in names for k in ('journal','document','letter','note','запис','журнал','документ','письм','протокол','лист','акт','карточ','рапорт','досье')) else 'glass' if any(k in names for k in ('mirror','зеркал','отраж')) else 'steel'
  title='hotspot_'+r+'_'+str(i);R.signage.PRINTED[title]=(str(obs[0].get('name') or obs[0].get('id') or 'ОБЪЕКТ')[:22].upper(),NAMES[r],[f'ОБЪЕКТ {i+1}','СЛУЖЕБНАЯ МАРКИРОВКА'],'red' if i%4==0 else 'blue')
  if tx<tz:
   xx=(1 if x>0 else -1)*2.88;box(title,(xx-.035,y-.19,z-.29),(xx+.035,y+.19,z+.29),(191,184,151) if kind=='paper' else (48,60,58),kind)
   if kind!='paper':box(title+'_screen',(xx-.045,y-.12,z-.22),(xx+.045,y+.12,z+.22),(14,31,32),'glass')
  else:
   zz=(1 if z>0 else -1)*2.39;box(title,(x-.29,y-.19,zz-.035),(x+.29,y+.19,zz+.035),(191,184,151) if kind=='paper' else (48,60,58),kind)
   if kind!='paper':box(title+'_screen',(x-.22,y-.12,zz-.045),(x+.22,y+.12,zz+.045),(14,31,32),'glass')
  count+=1
 return count

def parse_payload(html):
 marker='window.BUILT_GAME=';assert html.count(marker)==1;pos=html.index(marker)+len(marker);pos+=len(html[pos:])-len(html[pos:].lstrip());obj,end=json.JSONDecoder().raw_decode(html[pos:]);return obj,pos,end
def patch(html,obj):
 _,pos,end=parse_payload(html);return html[:pos]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+html[pos+end:]
def render_one(rid,room,width):
 R.SCENE.clear();R.CURVED.clear();R.signage.PRINTED.clear()
 if rid=='B':
  src=ROOT/'art/candidates/B_B_NORMAL_360_geometry.webp';im=Image.open(src).convert('RGB')
  if im.size!=(width,width//2):im=im.resize((width,width//2),Image.Resampling.LANCZOS)
  anchors=0
 else:
  shell(rid);landmarks(rid);anchors=add_hotspot_props(rid,room);im=R.render(width)
 out=ROOT/'game-project/rooms'/rid/'panorama_v2.webp';out.parent.mkdir(parents=True,exist_ok=True);im.save(out,'WEBP',quality=88,method=5);raw=out.read_bytes()
 if raw[8:12]!=b'WEBP' or Image.open(out).size!=(width,width//2):raise ValueError('bad render '+rid)
 return {'room':rid,'file':f'rooms/{rid}/panorama_v2.webp','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'hotspot_props':anchors,'width':width,'height':width//2}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--width',type=int,default=1024);args=ap.parse_args();assert args.width>=512 and args.width%2==0
 R.load_materials();project_path=ROOT/'game-project/project.json';project=json.loads(project_path.read_text(encoding='utf-8'));rooms={x['id']:x for x in project['rooms']};html_path=ROOT/'game/index.html';editor_path=ROOT/'game-editor/index.html';html=html_path.read_text(encoding='utf-8');game,_,_=parse_payload(html);qa=[]
 for rid in 'ABCDEFGHIJKLMNOP':
  q=render_one(rid,rooms[rid],args.width);qa.append(q);room=rooms[rid];room['file']=q['file'];room['mime']='image/webp';room['width']=q['width'];room['height']=q['height'];built=next(x for x in game['rooms'] if x['id']==rid);built.update({'file':q['file'],'mime':'image/webp','width':q['width'],'height':q['height']});raw=(ROOT/'game-project'/q['file']).read_bytes();game.setdefault('panoramas',{})[rid]={'mime':'image/webp','data':base64.b64encode(raw).decode('ascii')};print('RENDERED',rid,q['bytes'],'hotspots',q['hotspot_props'],flush=True)
 project_path.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8');html_path.write_text(patch(html,game),encoding='utf-8')
 if editor_path.exists():
  eh=editor_path.read_text(encoding='utf-8')
  if 'window.BUILT_GAME=' in eh:
   eg,_,_=parse_payload(eh);eg['rooms']=game['rooms'];eg['panoramas']=game['panoramas'];editor_path.write_text(patch(eh,eg),encoding='utf-8')
 qa_path.write_text(json.dumps({'schema':'campaign-panorama-pack-v1','projection':'equirectangular-360x180','room_count':16,'hotspot_uvs_changed':False,'rooms':qa},ensure_ascii=False,indent=2),encoding='utf-8')
 hashes={q['sha256'] for q in qa};assert len(hashes)>=15;print('PASS visual-only panorama pack',len(qa),'unique',len(hashes),'bytes',sum(q['bytes'] for q in qa))
if __name__=='__main__':main()
