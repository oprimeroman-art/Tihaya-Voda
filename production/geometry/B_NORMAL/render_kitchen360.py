#!/usr/bin/env python3
"""Render a reproducible true equirectangular 360 x 180 kitchen geometry prototype.

Uses deterministic analytic ray–AABB intersections (not panorama stretching).
Output is an ART CANDIDATE. Run: python render_kitchen360.py --width 2048
"""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

SCENE=[]
def box(name, lo, hi, rgb, kind='plain'):
    SCENE.append((name,np.array(lo,dtype=np.float32),np.array(hi,dtype=np.float32),np.array(rgb,dtype=np.float32),kind))
def kitchen():
    SCENE.clear()  # Repeated preview/test renders must not duplicate room geometry.
    # Station module 6m wide x 5m long; camera at human eye height.
    box('floor',(-3,-.06,-2.5),(3,0,2.5),(98,99,89),'floor')
    box('ceiling',(-3,2.82,-2.5),(3,2.9,2.5),(131,132,123),'panels')
    for name,a,b in [('back',(-3,0,-2.58),(3,2.82,-2.5)),('front',(-3,0,2.5),(3,2.82,2.58)),('left',(-3.08,0,-2.58),(-3,2.82,2.58)),('right',(3,0,-2.58),(3.08,2.82,2.58))]:
        box(name,a,b,(137,142,133),'panels')
    # Floor wear and plumbing at the galley counter.
    box('counter_base',(-2.72,.07,-2.45),(2.03,.85,-1.66),(77,91,89),'paint')
    box('counter_top',(-2.85,.86,-2.47),(2.11,.96,-1.48),(129,124,111),'wood')
    box('counter_front_toe',(-2.72,.07,-1.67),(2.03,.17,-1.6),(40,47,46))
    for x in [-2.2,-.91,.33,1.5]:
        box('drawer_gap',(x,.27,-1.61),(x+.025,.77,-1.58),(33,42,42))
        box('drawer_pull',(x+.25,.57,-1.605),(x+.6,.61,-1.55),(181,177,159),'steel')
    # Cabinet hanging units.
    for i,x in enumerate([-2.60,-1.42,0.78,1.72]):
        box('cabinet_'+str(i),(x,1.74,-2.40),(x+.82,2.46,-1.88),(113,120,103),'paint')
        box('cabinet_door_'+str(i),(x+.07,1.84,-1.885),(x+.74,2.40,-1.84),(122,127,106),'paint')
        box('cabinet_knob_'+str(i),(x+.63,2.08,-1.835),(x+.67,2.2,-1.79),(208,194,161),'steel')
    # Mirror and sink beneath it, a functional horror-story anchor.
    box('mirror_frame',(-1.75,1.23,-2.49),(-.58,1.76,-2.42),(60,70,69),'steel')
    box('mirror_glass',(-1.67,1.29,-2.425),(-.66,1.69,-2.390),(63,94,101),'glass')
    box('sink_rim',(-1.78,.963,-2.34),(-.59,.983,-1.72),(185,182,169),'steel')
    box('sink_water',(-1.68,.984,-2.29),(-.68,.99,-1.80),(47,68,75),'glass')
    box('faucet_stem',(-1.19,1,-2.37),(-1.13,1.29,-2.31),(170,175,173),'steel')
    box('faucet_arm',(-1.17,1.23,-2.39),(-.89,1.30,-2.31),(182,184,179),'steel')
    box('faucet_spout',(-.95,1.12,-2.39),(-.88,1.24,-2.33),(178,183,179),'steel')
    # Compact ceramic cooker.
    box('cooker_trim',(.15,.97,-2.37),(1.52,1.005,-1.60),(40,43,46),'steel')
    for x,z in [(.42,-2.17),(.94,-2.17),(.42,-1.83),(.94,-1.83)]:
        box('burner',(x,1.006,z),(x+.26,1.023,z+.25),(19,22,25),'steel')
    # White kettle beside the burners; honest low-poly proxy for final model.
    box('kettle_body',(1.62,.975,-2.26),(1.91,1.32,-1.97),(186,194,187),'enamel')
    box('kettle_lid',(1.66,1.32,-2.23),(1.87,1.36,-2.00),(58,64,66),'steel')
    box('kettle_handle',(1.67,1.39,-2.19),(1.85,1.44,-2.04),(48,49,48),'steel')
    # Fridge, shelves, papers. Keep the operating station lived-in, not abandoned.
    box('fridge',(2.18,.05,-2.31),(2.79,2.02,-1.30),(177,178,159),'enamel')
    box('fridge_seam',(2.17,.92,-2.32),(2.81,.955,-1.29),(84,91,86))
    box('fridge_handle',(2.13,1.16,-2.02),(2.17,1.70,-1.89),(66,68,65),'steel')
    for y in [1.73,2.14]:
        box('right_shelf',(2.78,y,-.85),(2.96,y+.06,.7),(92,84,71),'wood')
    for z in [-.63,-.25,.20]:
        box('shelf_tin',(2.72,1.80,z),(2.86,2.10,z+.14),(130,146,129),'enamel')
    # Mirror-side noticeboard and dry towels.
    box('notice',(-2.98,1.26,.48),(-2.90,2.08,1.65),(101,85,59),'wood')
    box('note_page',(-2.89,1.42,.73),(-2.86,1.86,1.1),(202,194,159),'paper')
    box('tea_instruction',(-2.88,1.47,1.18),(-2.85,1.83,1.45),(214,203,168),'paper')
    box('small_window',(-2.955,1.2,-1.62),(-2.92,2.18,-.63),(39,75,94),'window')
    # Table and chairs near the opposite side of the camera.
    box('table_top',(-1.06,.74,.57),(1.0,.80,1.75),(118,92,64),'wood')
    for x in [-.92,.83]:
        for z in [.70,1.54]:
            box('table_leg',(x,.06,z),(x+.12,.75,z+.12),(89,71,54),'wood')
    for x in [-1.4,1.30]:
        box('chair_seat',(x,.43,1.15),(x+.43,.50,1.65),(71,89,81),'paint')
        box('chair_back',(x,.52,1.56),(x+.43,1.29,1.63),(77,96,88),'paint')
    box('plate',(-.37,.81,1.04),(.06,.835,1.39),(216,215,194),'enamel')
    box('mug',(.32,.81,1.03),(.51,.97,1.20),(208,210,199),'enamel')
    # Door to corridor: on east wall.
    box('door_trim',(2.91,0,.62),(2.99,2.31,1.66),(72,81,82),'steel')
    box('door_leaf',(2.89,.10,.70),(2.96,2.20,1.57),(110,120,120),'paint')
    box('door_window',(2.875,1.28,.96),(2.89,1.70,1.31),(35,67,81),'window')
    box('door_handle',(2.86,.94,1.41),(2.89,1.04,1.50),(178,178,160),'steel')
    # Small utilitarian fittings are generated as actual 3-D volumes, not decals.
    for i, zz in enumerate([-2.14, -1.55, -.9, -.2, .55, 1.28]):
        box('ceiling_conduit_'+str(i),(-2.98,2.63,zz), (2.90,2.675,zz+.035),(52,61,58),'steel')
    for i, xx in enumerate([-2.65,-1.9,.13,1.1,2.5]):
        box('hanger_rail_'+str(i),(xx,2.50,-2.48),(xx+.05,2.54,-1.90),(64,66,61),'steel')
    for i, xx in enumerate([-2.28,-1.71,-.16,.73]):
        box('panel_rivet_'+str(i),(xx,1.31,-1.584),(xx+.035,1.355,-1.555),(162,152,135),'steel')
    for i, xx in enumerate([-2.16,-1.75,-1.34]):
        box('spice_jar_'+str(i),(xx,1.42,-2.27),(xx+.16,1.70,-2.07),
            (137+12*i,102+12*i,73+17*i),'enamel')
    # Radio notice and a drying rag distinguish an inhabited operational station.
    box('work_notice',(2.968,1.24,-.28),(2.981,1.91,.28),(211,203,178),'paper')
    box('work_notice_clip',(2.954,1.89,-.08),(2.983,1.94,.08),(75,82,82),'steel')
    box('dry_towel',(-2.39,1.06,-1.625),(-2.01,1.51,-1.591),(126,139,125),'cloth')
    box('towel_rail',(-2.50,1.53,-1.631),(-1.92,1.56,-1.576),(173,176,166),'steel')
    # Warm circular ceiling lights approximated by laminated squares.
    for i,z in enumerate([-1.4,.78]):
        box('light_halo'+str(i),(-.52,2.74,z-.33),(.52,2.77,z+.33),(132,116,88),'steel')
        box('warm_light'+str(i),(-.4,2.735,z-.23),(.4,2.74,z+.23),(249,218,149),'lamp')

def render(width=2048):
    height=width//2
    # World x east, y up, z south. At u=.5 camera faces north (-z).
    u=(np.arange(width,dtype=np.float32)+.5)/width
    camera=np.array([0,1.65,0],dtype=np.float32)
    result=np.empty((height,width,3),dtype=np.uint8)
    for y0 in range(0,height,36):
        yy=np.arange(y0,min(y0+36,height),dtype=np.float32)
        lat=((.5-(yy+.5)/height)*np.pi)[:,None]
        phi=((u-.5)*2*np.pi)[None,:]
        cs=np.cos(lat)
        direction=np.stack(np.broadcast_arrays(cs*np.sin(phi),np.sin(lat),-cs*np.cos(phi)),axis=-1)
        shape=direction.shape[:2]
        best=np.full(shape,1e6,np.float32)
        base=np.zeros((*shape,3),np.float32)
        for name,lo,hi,color,kind in SCENE:
            safe=np.where(abs(direction)<1e-7,np.where(direction<0,-1e-7,1e-7),direction)
            t0=(lo-camera)/safe;t1=(hi-camera)/safe
            near=np.minimum(t0,t1);far=np.maximum(t0,t1)
            entry=np.max(near,axis=2);exit=np.min(far,axis=2)
            hit=(exit>=np.maximum(entry,0))&(entry>=0)&(entry<best)
            if not np.any(hit):continue
            axis=np.argmax(near,axis=2)
            pt=camera+direction*entry[...,None]
            norm=np.zeros_like(direction)
            for ax in range(3):norm[...,ax]=np.where(axis==ax,-np.sign(direction[...,ax]),0)
            # Light at two ceiling fixtures, warm local illumination and cold window bounce.
            ambient=np.float32(.35)
            illum=np.full(shape,ambient,np.float32)
            for lx,ly,lz,power in [(0,2.72,-1.4,4.4),(0,2.72,.78,3.0),(-2.9,1.8,-1.1,1.1)]:
                vec=np.array([lx,ly,lz],np.float32)-pt
                dd=np.sum(vec*vec,axis=2)+.26
                dot=np.maximum(0,np.sum(norm*vec,axis=2)/np.sqrt(dd))
                illum+=power*dot/(dd+2)
            illum=np.clip(illum,.30,1.55)
            x,z=pt[...,0],pt[...,2]
            # Surface detail is evaluated in world space: it stays aligned when
            # the player rotates 360 degrees, unlike a screen-space filter.
            x,z=pt[...,0],pt[...,2]
            q=pt[...,1]
            micro=np.sin(x*53.6+z*31.4+q*17.7)*np.sin(z*47.1-q*33.4)*.031
            medium=np.sin(x*7.4+z*13.9-q*5.1)*np.cos(z*4.7+x*11.3+q*2.7)*.082
            coarse=np.sin(x*1.9+z*2.5+q*4.1)*np.cos(z*3.2-x*3.0+q*1.8)*.075
            grit=.45*micro+.34*medium+.21*coarse
            factor=1+grit
            tint=np.ones((*shape,3),np.float32)
            if kind=='wood':
                fibers=np.sin(x*47+z*7.8+.5*np.sin(z*2.5))*np.cos(x*4.5+z*1.4)
                age=np.sin(x*11.2+z*25.8)*np.cos(x*8.8-z*4.1)
                factor+=.10*fibers+.09*age+.025*np.sin(x*119)
                tint[...,0]*=1.09
                tint[...,2]*=.83
            elif kind=='panels':
                # Fine riveted enamel wall panels and age at modular seams.
                if name in ('left','right'):
                    hori=z
                else:
                    hori=x
                seam_x=np.abs(((hori+.015)/1.02+.5)%1-.5)
                seam_y=np.abs(((q+.03)/.94+.5)%1-.5)
                seam=np.minimum(seam_x,seam_y)
                factor-=np.where(seam<.012,.22,0)
                near_seam=np.exp(-((seam/.055)**2))
                corrosion=np.maximum(0,medium+.6*coarse+.015)
                factor-=.23*near_seam*corrosion
                tint[...,0]+=near_seam*corrosion*.14
                tint[...,1]-=near_seam*corrosion*.10
                tint[...,2]-=near_seam*corrosion*.18
            elif kind=='paint':
                brush=np.sin(x*75+z*20+q*8)*.025
                factory=np.sin(x*2+z*3+q*4)*.026
                factor+=brush+factory
                boundary=np.minimum.reduce([np.abs(pt[...,i]-lo[i]) for i in range(3)]+
                                           [np.abs(hi[i]-pt[...,i]) for i in range(3)])
                chips=(boundary<.012)&(medium>.02)
                factor-=np.where(chips,.24,0)
                tint[...,0]+=chips*.10
            elif kind=='floor':
                tilex=np.abs(((x+.02)/.60+.5)%1-.5)
                tilez=np.abs(((z+.04)/.72+.5)%1-.5)
                grout=(tilex<.012)|(tilez<.012)
                factor-=np.where(grout,.27,0)
                # Old washed tile: patchy wear, a few reflective worn patches.
                factor+=.10*np.sin(5*x+9*z)+.05*np.cos(17*x-11*z)
                factor-=.12*np.maximum(0,-medium-.005)
                gloss=.08*np.maximum(0,np.sin(x*9.3+z*12.9)+np.cos(x*6.7-z*4.3))
                factor+=gloss
                # Contact darkening beneath counters and dining table.
                table_shadow=np.exp(-((x/.94)**4+((z-1.2)/.55)**4))
                counter_shadow=np.exp(-((z+2.0)/.42)**4)
                factor-=.25*table_shadow+.20*counter_shadow
            elif kind=='steel':
                brushed=np.sin(q*119+x*75+z*68)*.030
                factor+=brushed+.045*np.cos(x*7+z*13)
                tint[...,2]*=1.05
            elif kind=='glass':
                # Cold hard tint: this is a placeholder for actual reflection
                # capture, not a physically convincing ghost mirror yet.
                factor+=.12*np.sin(q*17+x*14)+.04*np.cos(x*29)
                tint[...,0]*=.67
                tint[...,2]*=1.35
            elif kind=='window':
                tint[...,0]*=.55
                tint[...,2]*=1.50
            elif kind=='enamel':
                factor+=.015*np.cos(44*x)+.021*np.sin(63*z+13*q)
            elif kind=='paper':
                factor-=.025*np.cos(24*x+6*z)
                smudges=np.maximum(0,np.sin(x*13+q*35)*np.cos(z*15))
                factor-=.065*smudges
            elif kind=='cloth':
                factor+=.042*np.sin(x*120+q*70)+.06*np.cos(q*13)
            # Keep warm overhead light against cold Arctic-window fill.
            if kind=='lamp':
                illum=np.full(shape,1.4,np.float32)
                tint[...,0]*=1.13
                tint[...,2]*=.78
            lum=np.clip(illum*factor,.08,1.65)
            rgb=np.minimum(255,color[None,None,:]*lum[...,None]*tint)
            if kind!='lamp':
                rgb[...,0]*=1.14
                rgb[...,1]*=.995
                rgb[...,2]*=.81
            # Mild photographic toe; preserve detail without raising blacks.
            rgb=np.where(rgb<33,rgb*.85,rgb)
            best=np.where(hit,entry,best)
            base=np.where(hit[...,None],rgb,base)
        # Deliberately wrap the longitude seam by computing last ray from the first column.
        result[y0:y0+len(yy)]=np.uint8(np.clip(base,0,255))
    # Seam borders must represent the same azimuth.
    result[:,-1]=result[:,0]
    return Image.fromarray(result,'RGB')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--width',type=int,default=2048)
    p.add_argument('--out',type=Path,default=Path('art/candidates/B_B_NORMAL_360_geometry.webp'))
    args=p.parse_args()
    if args.width<512 or args.width%2:raise SystemExit('--width must be an even integer >=512')
    kitchen()
    image=render(args.width)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    image.save(args.out,'WEBP',quality=88,method=5)
    print('Rendered',args.out,'size',image.size,'objects',len(SCENE),'bytes',args.out.stat().st_size)
if __name__=='__main__':main()
