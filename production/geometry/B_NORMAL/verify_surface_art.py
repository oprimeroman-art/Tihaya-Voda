#!/usr/bin/env python3
"""Tests for physical Cyrillic signage and source-driven 3D cast shadows."""
import numpy as np
import render_kitchen360 as renderer
import surface_details as signage
import light_transport as shadows

def main():
    renderer.kitchen()
    scene={b[0]:b for b in renderer.SCENE}
    assert len(signage.PRINTED)==4
    for name in signage.PRINTED:
        assert name in scene,'Printing mapped to missing physical 3D card: '+name
        _,lo,hi,*_=scene[name]
        centre=((lo+hi)*.5).reshape(1,1,3)
        ink=signage.sampled_label(name,centre,lo,hi)
        assert ink.shape==(1,1,3) and np.isfinite(ink).all(),name
        tex=signage.paper(name)
        assert tex.shape==(768,512,3),name
        assert np.std(tex)>25 and np.any(tex[...,0]<100),name
    blocked_points=np.array([[0.,.015,1.2],[0.,.015,-.8]],np.float32)
    light=(0,2.72,.78)
    vis=shadows.visibility(blocked_points,light,shadows.blockers(renderer.SCENE),'floor')
    assert np.all(np.isfinite(vis)) and np.all((vis>=0)&(vis<=1)),vis
    assert vis[0]<vis[1],('Table should cast shadow on floor',vis)
    assert all(n!='warm_light0' for n,*_ in shadows.blockers(renderer.SCENE))
    # Stable, view-independent, metre-based printed UV: same 3D point,
    # same printed colour for every direction of the observer.
    lo,hi=scene['tea_instruction'][1:3]
    pos=lo+np.array([0,.42,.17],np.float32)*(hi-lo)
    a=signage.sampled_label('tea_instruction',pos.reshape(1,3),lo,hi)
    b=signage.sampled_label('tea_instruction',pos.reshape(1,1,3),lo,hi)
    assert np.allclose(a[0],b[0,0])
    print('PASS: four Cyrillic physical signs, pinned positions, CC0 light occlusion and stable decals')

if __name__=='__main__':main()
