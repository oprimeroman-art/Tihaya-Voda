#!/usr/bin/env python3
"""Regression tests for curved kitchen props and 360-seam-safe candidate hotspots."""
import json
from pathlib import Path
import numpy as np
import curved_geometry as curve
import render_kitchen360 as model
import generate_hotspots as spots

def main():
    # Ellipsoid: front pole hit distance is geometrically exact.
    e=curve.ellipsoid('test',(0,0,0),(1,2,1),(180,180,180))
    d,n=curve.intersect(e,np.array((0,0,3),np.float32),
                        np.array([[0,0,-1],[1,0,0]],np.float32))
    assert np.isclose(d[0],2,atol=1e-5),(d,n)
    assert np.allclose(n[0],[0,0,1],atol=1e-4)
    assert np.isinf(d[1]),'missed ellipsoid must not appear'
    c=curve.cylinder('test',(0,0,0),1,-1,1,(180,180,180))
    d,n=curve.intersect(c,np.array((0,0,3),np.float32),
                        np.array([[0,0,-1]],np.float32))
    assert np.isclose(d[0],2,atol=1e-5)
    cap,n=curve.intersect(c,np.array((0,0,0),np.float32),
                          np.array([[0,1,0]],np.float32))
    assert np.isclose(cap[0],1,atol=1e-5),'cylinder cap intersection'
    assert np.allclose(n[0],[0,1,0],atol=1e-4)
    model.kitchen()
    assert len(model.CURVED)==5, 'expected five physically curved props'
    assert {'kettle_body','kettle_lid','mug','plate','faucet_stem'}==model.REPLACED_BOXES
    names={x[0] for x in model.CURVED}
    assert 'kettle_curved' in names and 'plate_curved' in names
    j=json.loads(spots.PROJECT.read_text(encoding='utf-8'))
    output=spots.generate(j)
    entries=output['objects']
    assert len(entries)==11,'all current kitchen actions must be covered'
    assert len({x['action_id'] for x in entries})==11
    assert len([x for x in entries if x['status']=='requires_authored_3d_prop'])==1
    assert next(x for x in entries if x['action_id']=='watch_A05')['status']=='requires_authored_3d_prop'
    plate=next(x for x in entries if x['action_id']=='plate_choice')
    assert plate['seam_split'] and len(plate['candidate_quads'])==2,        'a physical plate spans the 0/1 meridian; do not emit broken bounding rectangle'
    for x in entries:
        for quad in x.get('candidate_quads',[]):
            assert len(quad)==4
            assert all(0<=p['u']<=1 and 0<=p['v']<=1 for p in quad)
            assert quad[0]['u']<quad[1]['u']
            assert quad[0]['v']<quad[2]['v']
    assert output['not_in_shipped_game']
    print('PASS: curved sphere/cylinder rays, kettle/mug/plate, 11 actions, split seam and 1 unplaced prop')

if __name__=='__main__':main()
