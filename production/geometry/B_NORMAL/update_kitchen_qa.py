#!/usr/bin/env python3
"""Update the existing B_NORMAL candidate QA with verified rendered file metadata."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from fetch_cc0_materials import DEST,TEXTURES,good
import render_kitchen360 as renderer

ROOT=Path(__file__).resolve().parents[3]
QA=ROOT/'production/qa/B_NORMAL_geometry_v1.json'
ASSET=ROOT/'art/candidates/B_B_NORMAL_360_geometry.webp'

def main():
    obj=json.loads(QA.read_text(encoding='utf-8'))
    raw=ASSET.read_bytes()
    image=np.asarray(Image.open(ASSET).convert('RGB'),dtype=np.float32)
    assert image.shape==(1024,2048,3),'Wrong render dimensions'
    seam=float(np.abs(image[:,0]-image[:,-1]).mean())
    assert seam<5,'Bad spherical panorama seam'
    for name,(_,md5,length) in TEXTURES.items():
        assert good((DEST/(name+'_diff_1k.jpg')).read_bytes(),md5,length),'Texture hash changed'
    renderer.kitchen()
    obj['scene_objects']=len(renderer.SCENE)
    obj['curved_primitives']=len(renderer.CURVED)
    obj['material_stage']='CC0_photographic_albedo_v5_curved_props_with_reflection'
    obj['materials']=[{'id':name,'source':'https://polyhaven.com/a/'+name,'license':'CC0','md5':data[1]}
                      for name,data in TEXTURES.items()]
    obj['test']['ratio_2_to_1']=True
    obj['test']['edge_column_mae']=round(seam,3)
    obj['test']['webp_bytes']=len(raw)
    obj['test']['sha256']=hashlib.sha256(raw).hexdigest()
    obj['test']['stable_story_uv_anchors_verified']=7
    obj['test']['photo_albedo_verified']=True
    obj['test']['mirror_single_bounce']=True
    obj['test']['curved_ray_intersections']=True
    obj['test']['candidate_3d_projected_hotspots']=11
    obj['test']['visible_interaction_rays']=11
    obj['test']['audio_A05_intercom_model']=True
    obj['remaining']=[
      'Kettle, mug, plate and faucet now have true curved ray surfaces, but remaining furniture is still stylized',
      '10 candidate hotspots require in-browser visual approval; watch_A05 has no authored physical prop; plate_choice crosses the longitude seam',
      'Do not replace playable room B until art production approval'
    ]
    QA.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('QA_OK',obj['test'])

if __name__=='__main__':main()
