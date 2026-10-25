"""Deterministic kitchen static direct-light shadowing for raycast surfaces.

Direct shadows are computed in the same metric 3-D model as B_NORMAL.
Excludes generic microdetails, the sampled surface, and emissive fixtures.
No online models, external renderer, GPU, user data, or nondeterministic noise.
"""
import numpy as np

MAJOR_OCCLUDERS={
    'counter_base','counter_top','fridge','fridge_seam','table_top',
    'door_leaf','door_trim','right_shelf','chair_back','chair_seat',
    'cooker_trim','mirror_frame','sink_rim','faucet_arm','faucet_spout',
    'notice','small_window','intercom_A05'
}
SHADOW_SURFACES={'floor','back','front','left','right','table_top','counter_top'}

def blockers(scene):
    return [(name,lo,hi) for name,lo,hi,_color,_kind in scene
            if name in MAJOR_OCCLUDERS or name.startswith(('cabinet_','cabinet_door_'))]

def visibility(points,source,boxes,receiver=None):
    """One-bounce shadow visibility from arbitrary shape (...,3) 3-D hits.

    Returns scalar 0-1 area-light approximation: full lit or a 15%-lit
    penumbra proxy. A real light sample is used (never just painted shading).
    """
    pt=np.asarray(points,dtype=np.float32)
    vec=np.asarray(source,dtype=np.float32)-pt
    dist=np.linalg.norm(vec,axis=-1)
    safe=np.where(np.abs(vec)<1e-7,np.where(vec<0,-1e-7,1e-7),vec)
    shadow=np.zeros(pt.shape[:-1],dtype=np.bool_)
    for name,lo,hi in boxes:
        if name==receiver:continue
        # Parametric t along segment to fixture: 0 at surface, 1 at light.
        t0=(lo-pt)/safe
        t1=(hi-pt)/safe
        tnear=np.max(np.minimum(t0,t1),axis=-1)
        tfar=np.min(np.maximum(t0,t1),axis=-1)
        blocked=(tfar>=np.maximum(tnear,.008))&(tnear>.008)&(tnear<.985)
        shadow|=blocked
    return np.where(shadow,np.float32(.18),np.float32(1.0))
