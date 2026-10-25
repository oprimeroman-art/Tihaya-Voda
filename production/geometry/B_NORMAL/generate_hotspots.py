#!/usr/bin/env python3
"""Derive *candidate* clickable quads from real 3-D bounds (never edit game).

Wraparound 360-degree objects emit two rectangles, not a broken spanning box.
Author must approve these in the in-browser panorama QA viewer.
"""
import json,math
from pathlib import Path
import render_kitchen360 as model

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'game-project/project.json'
OUTPUT=ROOT/'production/qa/B_NORMAL_hotspots_candidate.json'

# Explicit authoritative authored feature-to-3D-object mapping.
# No fictional 3D object has been invented for watch_A05.
MAPPING={
 'TEA_SEQUENCE':('kettle_body',None),
 'COOKING':('cooker_trim',None),
 'plate_choice':('plate',None),
 'read_D01':('tea_instruction',None),
 'read_D16':('note_page',None),
 'wash_cup':('sink_water',None),
 'mirror04':('mirror_glass',None),
 'mirror04_away':('chair_back',1),
 'mirror04_again':('mirror_glass',None),
 'mirror04_third':('door_leaf',None),
}

def longitude(x,z):return (.5+math.atan2(x,-z)/(2*math.pi))%1
def uv(p):
 x,y,z=p
 return (longitude(x,z), .5-math.atan2(y-1.65,math.hypot(x,z))/math.pi)
def corners(bounds):
 _,lo,hi,*_=bounds
 return [uv((x,y,z)) for x in (lo[0],hi[0])
         for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
def rectangles(bounds):
 projected=corners(bounds)
 us=sorted(a for a,b in projected)
 # Find shortest longitude arc using the largest empty angular gap.
 gaps=[((us[(i+1)%len(us)]+(1 if i==len(us)-1 else 0))-us[i],i)
       for i in range(len(us))]
 _,gap=max(gaps)
 begin=us[(gap+1)%len(us)]
 end=us[gap]+(1 if gap < (gap+1)%len(us) else 0)
 if end<begin:end+=1
 a=begin-.008;b=end+.008
 vs=[v for u,v in projected]
 top=max(0,min(vs)-.012);bottom=min(1,max(vs)+.012)
 centre=(a+b)/2
 if b-a<.027:a=centre-.0135;b=centre+.0135
 if bottom-top<.035:c=(top+bottom)/2;top=max(0,c-.0175);bottom=min(1,c+.0175)
 intervals=[]
 if a<0:intervals=[(0,b),(a+1,1)]
 elif b>1:intervals=[(a,1),(0,b-1)]
 else:intervals=[(a,b)]
 result=[]
 for low,high in intervals:
  if high-low<.002:continue
  u1,u2=round(low,5),round(high,5)
  v1,v2=round(top,5),round(bottom,5)
  result.append([{'u':u1,'v':v1},{'u':u2,'v':v1},
                 {'u':u2,'v':v2},{'u':u1,'v':v2}])
 return result

def generate(project):
 room=next(r for r in project['rooms'] if r['id']=='B')
 model.kitchen()
 boxes={}
 for entry in model.SCENE:boxes.setdefault(entry[0],[]).append(entry)
 output=[]
 for obj in room['objects']:
  action=obj.get('tourKey','').removeprefix('ga:')
  if action not in MAPPING:
   output.append({'id':obj['id'],'action_id':action,'status':'requires_authored_3d_prop',
                  'reason':'No corresponding physical object is present; do not bind to empty wall'})
   continue
  name,index=MAPPING[action]
  selected=boxes[name][index or 0]
  quads=rectangles(selected)
  output.append({'id':obj['id'],'action_id':action,'source_3d_object':name,
                'status':'needs_manual_in_game_approval',
                'seam_split':len(quads)>1,'candidate_quads':quads})
 return {'schema':1,'room':'B','variant':'B_NORMAL','stage':'art_candidate_only',
   'projection':'equirectangular_360x180','camera_m':[0,1.65,0],
   'source':'world-space AABB projected to panorama UV',
   'objects':output,
   'not_in_shipped_game':True,
   'warning':'Do not directly write these rectangles to game-project before checking visibility, occlusion, seam handling and chapter Q01/Q04 interactions.'}

def main():
 project=json.loads(PROJECT.read_text(encoding='utf-8'))
 result=generate(project)
 OUTPUT.parent.mkdir(parents=True,exist_ok=True)
 OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('UV_CANDIDATES',len(result['objects']),'splits',sum(o.get('seam_split',False) for o in result['objects']),
       'blocked',sum(o['status']!='needs_manual_in_game_approval' for o in result['objects']))
if __name__=='__main__':main()
