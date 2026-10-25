#!/usr/bin/env python3
"""Check candidate action target exposure using the actual 3-D renderer collision math.

One centre ray per target is a pre-screen only: multi-point browser QA is still
needed for occlusion, usability, and mirrored/conditional hotspots.
"""
import json
from pathlib import Path
import numpy as np
import render_kitchen360 as r
import curved_geometry as curved
import generate_hotspots as h

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/qa/B_NORMAL_visibility_v1.json'
CAM=np.array((0,1.65,0),dtype=np.float32)
GROUPS={'plate':'plate','kettle_body':'kettle',
        'cooker_trim':'burner','sink_water':'sink',
        'mirror_glass':'mirror','intercom_A05_face':'intercom_A05'}

def first_hit(point):
    dir=point-CAM
    length=np.linalg.norm(dir)
    direction=dir/length
    near=float('inf'); winner=None
    safe=np.where(np.abs(direction)>1e-9,direction,np.where(direction<0,-1e-9,1e-9))
    for name,lo,hi,_,kind in r.SCENE:
        if name in r.REPLACED_BOXES:continue
        t0=(lo-CAM)/safe
        t1=(hi-CAM)/safe
        a=float(np.max(np.minimum(t0,t1)))
        b=float(np.min(np.maximum(t0,t1)))
        if b>=max(a,0) and 0<a<near:
            near=a;winner=name
    for primitive in r.CURVED:
        dist,_=curved.intersect(primitive,CAM,direction[None,:])
        t=float(dist[0])
        if np.isfinite(t) and t<near:
            near=t;winner=primitive[0]
    return winner,near,length

def audit(project):
    r.kitchen()
    mapping={}
    for x in r.SCENE:mapping.setdefault(x[0],[]).append(x)
    items=[]
    for obj in next(z for z in project['rooms'] if z['id']=='B')['objects']:
        aid=obj.get('tourKey','').removeprefix('ga:')
        if aid not in h.MAPPING:
            items.append({'action':aid,'status':'missing_model'})
            continue
        name,idx=h.MAPPING[aid]
        _,lo,hi,*_=mapping[name][idx or 0]
        target=(lo+hi)*.5
        nearest,depth,total=first_hit(target)
        prefix=GROUPS.get(name,name)
        visible=bool(nearest and (nearest.startswith(prefix) or name.startswith(nearest)))
        items.append({'action':aid,'source':name,'nearest_geometry':nearest,
            'visible_centre_ray':visible,'distance_m':round(depth,3),
            'target_depth_m':round(float(total),3)})
    return {'schema':1,'room':'B','status':'preliminary_3d_ray_visibility',
        'not_final_player_validation':True,'items':items}

def main():
    project=json.loads((ROOT/'game-project/project.json').read_text(encoding='utf-8'))
    report=audit(project)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for x in report['items']:print(x['action'],x.get('source'),x.get('nearest_geometry'),x.get('visible_centre_ray'))
    print('VISIBLE',sum(x.get('visible_centre_ray',False) for x in report['items']),'/',len(report['items']))
if __name__=='__main__':main()
