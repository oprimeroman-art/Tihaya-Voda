#!/usr/bin/env python3
"""Guard that kitchen anomalies preserve the original panoramic geometry."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
STATES=['B_SECOND_PLATE','B_GHOST_MIRROR','B_TWO_GHOSTS']
arrays={}
for state in STATES:
    f=ROOT/'site-assets/kitchen-states'/f'{state}.webp'
    with Image.open(f) as im:
        assert im.size==(1774,887),f'{state}: expected canonical approved B panorama geometry'
        assert im.format=='WEBP',state
        arrays[state]=np.asarray(im.convert('RGB'),dtype=np.int16)
h,w=arrays['B_SECOND_PLATE'].shape[:2]
mask=np.zeros((h,w),dtype=bool)
mask[round(.35*h):round(.55*h),round(.35*w):round(.45*w)]=True
for state in STATES[1:]:
    difference=np.abs(arrays[state]-arrays['B_SECOND_PLATE']).mean(axis=2)
    within=float(difference[mask].mean())
    beyond=float(difference[~mask].mean())
    assert within>1.3,(state,'missing apparition in the mirror',within)
    assert beyond<1.5,(state,'unrelated room geometry changed',beyond)
    print(f'PASS {state}: mirror delta={within:.3f}; outside delta={beyond:.3f}')
print('PASS kitchen state geometry and authored scene continuity')
