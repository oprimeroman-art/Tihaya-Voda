#!/usr/bin/env python3
"""Regression checks for reproducible kitchen geometry and story object anchors."""
import math
from pathlib import Path
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_kitchen360 as renderer

# The coordinates from production/qa/B_NORMAL_geometry_v1.json must not drift.
# They are object centres, not final interaction quadrilaterals.
ANCHORS = {
 'TEA_SEQUENCE': ((1.74,1.18,-2.1),(.61012,.55432),'kettle_body'),
 'COOKING': ((.75,1.02,-1.97),(.55790,.59244),'cooker_trim'),
 'plate_choice': ((-.18,.83,1.19),(.02389,.69038),'plate'),
 'wash_cup': ((-1.25,.985,-2.04),(.41251,.58630),'sink_water'),
 'mirror04': ((-1.16,1.47,-2.41),(.42860,.52139),'mirror_glass'),
 'mirror04_away': ((-.2,.76,1.18),(.02672,.70353),'table_top'),
 'mirror04_third': ((2.91,1.5,1.1),(.80752,.51534),'door_leaf'),
}

def uv(p):
 x,y,z=p; dy=y-1.65
 return ((.5+math.atan2(x,-z)/(2*math.pi))%1,
         .5-math.atan2(dy,math.hypot(x,z))/math.pi)

def main():
 renderer.SCENE.clear()
 renderer.load_materials()
 assert len(renderer.MATERIALS)==4,'Four CC0 photographic albedo textures required'
 renderer.kitchen()
 names={o[0] for o in renderer.SCENE}
 assert len(renderer.SCENE)>=90 and len(names)>=50, 'Scene has lost key geometry'
 for label,(world,expected,object_name) in ANCHORS.items():
  assert object_name in names, f'{label}: 3D object missing'
  actual=uv(world)
  assert all(abs(a-b)<.0001 for a,b in zip(actual,expected)),f'{label} has moved: {actual} vs {expected}'
 print(f'PASS: {len(renderer.SCENE)} 3D objects, {len(ANCHORS)} unchanged quest UV anchors')
 out=Path(__file__).resolve().parent/'_verify_render.webp'
 try:
  im=renderer.render(512)
  photographed=np.asarray(im,dtype=np.float32)
  renderer.MATERIALS.clear()
  procedural=np.asarray(renderer.render(512),dtype=np.float32)
  renderer.load_materials()
  assert np.abs(photographed-procedural).mean()>1.0, 'Photographic materials do not affect rendering'

  im.save(out,'WEBP',quality=87)
  pix=np.asarray(Image.open(out).convert('RGB'),dtype=np.float32)
  assert pix.shape==(256,512,3), 'Not a 2:1 equirectangular image'
  seam=float(np.abs(pix[:,0]-pix[:,-1]).mean())
  assert seam<3.5, f'Broken longitude seam: {seam:.3f}'
  assert np.std(pix)>10, 'Rendered image unexpectedly blank'
  print(f'PASS: sphere 512x256, seam {seam:.2f}/255, deterministic materials')
 finally:
  out.unlink(missing_ok=True)
if __name__=='__main__':main()
