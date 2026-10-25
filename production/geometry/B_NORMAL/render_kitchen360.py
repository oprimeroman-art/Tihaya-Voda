#!/usr/bin/env python3
"""Render a reproducible true equirectangular 360 x 180 kitchen geometry prototype.

Uses deterministic analytic ray–AABB intersections (not panorama stretching).
Output is an ART CANDIDATE. Run: python render_kitchen360.py --width 2048
"""
import argparse
from pathlib import Path
import numpy as np
import curved_geometry as curved
from PIL import Image

SCENE=[]
CURVED=[]
REPLACED_BOXES={'kettle_body','kettle_lid','mug','plate','faucet_stem'}
# Photoscanned albedo maps. This intentionally preserves the established mesh
# and scenario UV anchors; only the colour of intersected surfaces changes.
MATERIALS={}
MATERIAL_NAMES={
    'wood':'wood_table',
    'floor':'concrete_floor',
    'paint':'rusty_painted_metal',
    'panels':'concrete_floor',
    'steel':'metal_plate',
    'enamel':'concrete_floor',
    'cloth':'wood_table'
}
REPO_ROOT=Path(__file__).resolve().parents[3]
TEXTURE_DIR=REPO_ROOT/'art/materials/cc0'

def load_materials(directory=TEXTURE_DIR):
    """Load pinned CC0 photo albedo maps; never silently fake a photomaterial."""
    MATERIALS.clear()
    for name in sorted(set(MATERIAL_NAMES.values())):
        filename=Path(directory)/(name+'_diff_1k.jpg')
        if not filename.is_file():
            raise FileNotFoundError(f'CC0 photo material missing: {filename}. '
                'Run python production/geometry/B_NORMAL/fetch_cc0_materials.py')
        with Image.open(filename) as im:
            rgb=np.asarray(im.convert('RGB'),dtype=np.float32)
        if min(rgb.shape[:2])<512:
            raise ValueError('Material has insufficient detail: '+str(filename))
        mean=np.maximum(rgb.mean(axis=(0,1)),15)
        MATERIALS[name]=(rgb,mean)
    return MATERIALS

def sample_photo(kind,point,normal):
    """Planar box-face UV mapping (physical metres, not camera longitude).

    The projection uses the dominant wall normal to choose the two consistent
    in-plane world axes; photo grain therefore stays glued to surfaces.
    """
    texture_name=MATERIAL_NAMES.get(kind)
    if not texture_name or texture_name not in MATERIALS:return None
    rgb,mean=MATERIALS[texture_name]
    dims=rgb.shape
    normal_index=np.argmax(np.abs(normal),axis=-1)
    pu=np.where(normal_index==0,point[...,2],point[...,0])
    pv=np.where(normal_index==1,point[...,2],point[...,1])
    if kind=='wood':pu=np.where(normal_index==1,point[...,0],pu)
    repeat={'wood':.68,'floor':1.02,'paint':.73,'panels':.42,
            'steel':1.7,'enamel':.81,'cloth':1.15}.get(kind,1.0)
    ix=np.mod(np.floor(pu*repeat*dims[1]).astype(np.int32),dims[1])
    iy=np.mod(np.floor(pv*repeat*dims[0]).astype(np.int32),dims[0])
    sample=rgb[iy,ix]
    # Rescale the photographed colour to the original art-direction palette:
    # preserve working-station greys rather than making every wall rusty red.
    normalized=np.clip(sample/mean[None,None,:],.34,1.72)
    strength={'wood':.79,'floor':.58,'paint':.38,'panels':.35,
              'steel':.62,'enamel':.18,'cloth':.24}.get(kind,.25)
    return (1-strength)+strength*normalized
def box(name, lo, hi, rgb, kind='plain'):
    SCENE.append((name,np.array(lo,dtype=np.float32),np.array(hi,dtype=np.float32),np.array(rgb,dtype=np.float32),kind))
def kitchen():
    SCENE.clear()  # Repeated preview/test renders must not duplicate room geometry.
    CURVED.clear()
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
    add_detail_geometry()
    # True curved silhouettes in the same world positions as the original
    # scripted AABB prop anchors; these replace only rasterized proxy boxes.
    CURVED.extend([
        curved.ellipsoid('kettle_curved',(1.765,1.155,-2.115),(.148,.183,.146),
                         (190,198,194),'enamel'),
        curved.cylinder('kettle_lid_curved',(1.765,0,-2.115),.114,1.335,1.367,
                        (99,104,101),'steel'),
        curved.cylinder('mug_curved',(.415,0,1.115),.098,.808,.981,
                        (208,207,194),'enamel'),
        curved.cylinder('plate_curved',(-.155,0,1.215),.220,.805,.839,
                        (224,224,204),'enamel'),
        curved.cylinder('faucet_stem_curved',(-1.16,0,-2.34),.033,1.0,1.286,
                        (168,179,177),'steel')
    ])

def add_circular_trim(name,cx,y,cz,r,segments,thickness,color,material='steel'):
    """Concentric physical details modelled in world space as many short cuboids."""
    for i in range(segments):
        angle=2*np.pi*i/segments
        x=cx+r*np.cos(angle);z=cz+r*np.sin(angle)
        box(f'{name}_{i:02d}',(x-thickness,y,z-thickness),
            (x+thickness,y+thickness*.65,z+thickness),color,material)


def add_detail_geometry():
    """Enhance prop silhouettes without moving any approved scripted object centres."""
    # Stove: each of the four burners has metallic trim, ceramic control dots.
    for i,(x,z) in enumerate([(.42,-2.17),(.94,-2.17),(.42,-1.83),(.94,-1.83)]):
        add_circular_trim(f'burner_ring_{i}',x+.13,1.028,z+.125,.107,12,.015,
                          (84,89,88))
        box(f'burner_center_{i}',(x+.106,1.031,z+.104),
            (x+.154,1.036,z+.145),(43,45,48),'steel')
    for i,x in enumerate([.28,.55,.83,1.11]):
        box(f'stove_switch_{i}',(x,.98,-1.55),(x+.058,1.04,-1.515),
            (170,169,157),'steel')
    # Sink: separate edge trim and a visible drain instead of a flat blue plate.
    for key,lo,hi in [
        ('sink_front',(-1.78,.995,-1.73),(-.59,1.02,-1.705)),
        ('sink_left',(-1.79,.99,-2.34),(-1.765,1.02,-1.72)),
        ('sink_right',(-.615,.99,-2.34),(-.59,1.02,-1.72)),
        ('sink_back',(-1.78,.99,-2.355),(-.59,1.02,-2.33))]:
        box(key,lo,hi,(171,179,179),'steel')
    add_circular_trim('sink_drain',-1.18,.999,-2.015,.048,12,.006,(42,54,59))
    box('faucet_valve',(-1.23,1.065,-2.42),(-1.08,1.09,-2.35),
        (151,159,158),'steel')
    for i in range(4):
        box(f'faucet_handle_ridge_{i}',(-1.15+i*.024,1.285,-2.35),
            (-1.144+i*.024,1.3,-2.31),(201,205,194),'steel')
    # Kettle remains centred on its original interactive anchor.
    add_circular_trim('kettle_lid_rim',1.77,1.365,-2.115,.103,16,.014,
                      (64,68,66))
    box('kettle_lid_knob',(1.746,1.371,-2.137),(1.794,1.42,-2.095),
        (41,44,45),'steel')
    for j in range(4):
        yy=1.02+j*.069
        add_circular_trim(f'kettle_shell_{j}',1.765,yy,-2.113,
                          .143-.009*max(j-1,0),16,.016,
                          (174+j*2,183+j*2,177+j*2),'enamel')
    # Handle sits visibly above the kettle, with steam outlet on one side.
    box('kettle_handle_left',(1.68,1.375,-2.173),(1.709,1.485,-2.145),
        (43,44,43),'steel')
    box('kettle_handle_right',(1.823,1.375,-2.173),(1.849,1.485,-2.145),
        (43,44,43),'steel')
    box('kettle_handle_grip',(1.68,1.477,-2.174),(1.85,1.505,-2.143),
        (44,46,46),'steel')
    box('kettle_power_indicator',(1.733,1.027,-1.964),(1.775,1.051,-1.957),
        (138,39,29),'enamel')
    # Mirror: multiple independent real surfaces, rivets and metal wear.
    for side,x in [('left',-1.757),('right',-.583)]:
        box('mirror_trim_'+side,(x,1.224,-2.451),(x+.016,1.763,-2.405),
            (164,170,165),'steel')
    box('mirror_upper_lip',(-1.76,1.757,-2.45),(-.565,1.771,-2.404),
        (166,173,172),'steel')
    box('mirror_lower_lip',(-1.76,1.22,-2.455),(-.565,1.239,-2.403),
        (143,150,148),'steel')
    for xx in [-1.715,-.614]:
        for yy in [1.264,1.728]:
            box('mirror_screw',(xx,yy,-2.405),(xx+.014,yy+.014,-2.398),
                (62,68,69),'steel')
    # Fridge equipment: drip tray, door gasket, ventilation grille.
    for i,y in enumerate([.29,.32,.35,.38,.41]):
        box(f'fridge_grille_{i}',(2.145,y,-2.22),(2.158,y+.010,-1.53),
            (79,86,84),'steel')
    box('fridge_badge',(2.145,1.768,-1.970),(2.163,1.851,-1.711),
        (190,190,174),'enamel')
    # Cabinets: physical hinge joints and two pulls for the main doors.
    for x in [-2.58,-1.40,.80,1.74]:
        for yy in [1.94,2.30]:
            box('cabinet_hinge',(x+.021,yy,-1.838),(x+.049,yy+.07,-1.804),
                (159,163,156),'steel')
    # Table hardware and chair legs for a practical working canteen.
    for xx in [-1.38,1.34]:
        for zz in [1.18,1.55]:
            box('chair_leg',(xx,.055,zz),(xx+.038,.44,zz+.037),
                (51,54,51),'steel')
    for i,z in enumerate([.62,1.63]):
        box(f'table_edge_detail_{i}',(-1.055,.746,z),(1.00,.774,z+.025),
            (83,64,49),'wood')
    for i,x in enumerate([-.98,.92]):
        box(f'table_edge_end_{i}',(x,.744,.60),(x+.026,.774,1.75),
            (79,62,48),'wood')


def curved_shading(position, normal, colour, kind):
    """World-space lighting for rounded surfaces, using the same CC0 albedo."""
    illum=np.full(position.shape[:-1],.25,np.float32)
    for lx,ly,lz,power in [(0,2.72,-1.4,4.4),(0,2.72,.78,3.0),(-2.9,1.8,-1.1,1.1)]:
        vec=np.asarray((lx,ly,lz),np.float32)-position
        dd=np.sum(vec*vec,axis=-1)+.26
        dot=np.maximum(0,np.sum(normal*vec,axis=-1)/np.sqrt(dd))
        illum+=power*dot/(dd+2)
    sampled=sample_photo(kind,position,normal)
    base=np.asarray(colour,np.float32)*np.clip(illum[...,None],.2,1.42)
    if sampled is not None:base*=sampled
    return np.minimum(255,base)


def mirror_rays(hit_points, incoming, mask):
    """One real planar reflection bounce. Reflect room surfaces, never the mirror itself."""
    rows,cols=np.nonzero(mask)
    if len(rows)==0:return rows,cols,np.zeros((0,3),np.float32)
    origin=hit_points[rows,cols].copy()
    rays=incoming[rows,cols].copy()
    rays[:,2]*=-1  # Mirror plane faces inward towards positive Z.
    origin[:,2]+=.0008
    best=np.full(len(rows),np.inf,np.float32)
    colours=np.tile(np.array([17,27,35],dtype=np.float32),(len(rows),1))
    safe=np.where(np.abs(rays)<1e-7,np.where(rays<0,-1e-7,1e-7),rays)
    for obj,lo,hi,col,kind in SCENE:
        if obj.startswith('mirror_') or obj in REPLACED_BOXES:continue
        t0=(lo-origin)/safe
        t1=(hi-origin)/safe
        near=np.minimum(t0,t1)
        far=np.maximum(t0,t1)
        entry=np.max(near,axis=1)
        exit=np.min(far,axis=1)
        valid=(exit>=np.maximum(entry,.001))&(entry>.001)&(entry<best)
        if not np.any(valid):continue
        axis=np.argmax(near,axis=1)
        normals=np.zeros_like(rays)
        for j in range(3):normals[:,j]=np.where(axis==j,-np.sign(rays[:,j]),0)
        position=origin+entry[:,None]*rays
        light=np.array([0,2.73,-1.4],np.float32)-position
        ll=np.maximum(.00001,np.linalg.norm(light,axis=1))
        lambert=np.maximum(0,np.einsum('ij,ij->i',normals,light)/ll)
        fade=np.clip(.27+.73*lambert/(.7+.09*ll*ll),.24,.91)
        shade=np.minimum(255,np.asarray(col,np.float32)[None,:]*fade[:,None])
        shade[:,2]*=1.06
        colours[valid]=shade[valid]
        best=np.where(valid,entry,best)
    # Curved props must also be visible in the mirror. Reflection is one bounce.
    for primitive in CURVED:
        distance,normal=curved.intersect(primitive,origin,rays)
        visible=np.isfinite(distance)&(distance<best)
        if not np.any(visible):continue
        position=origin+rays*np.where(visible,distance,0)[...,None]
        shade=curved_shading(position,normal,primitive[4],primitive[5])
        colours[visible]=shade[visible]
        best=np.where(visible,distance,best)
    return rows,cols,colours


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
            if name in REPLACED_BOXES:continue
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
            photographed=sample_photo(kind,pt,norm)
            if photographed is not None:
                tint*=photographed
            rgb=np.minimum(255,color[None,None,:]*lum[...,None]*tint)
            if kind!='lamp':
                rgb[...,0]*=1.14
                rgb[...,1]*=.995
                rgb[...,2]*=.81
            # Mild photographic toe; preserve detail without raising blacks.
            rgb=np.where(rgb<33,rgb*.85,rgb)
            if name=='mirror_glass':
                py,px,reflected=mirror_rays(pt,direction,hit)
                if len(py):
                    rgb[py,px]=.12*rgb[py,px]+.88*reflected
            best=np.where(hit,entry,best)
            base=np.where(hit[...,None],rgb,base)
        # Replace proxy boxes with actual curved props; depth-test against walls,
        # stove and furniture, so hidden parts never float through foreground.
        for primitive in CURVED:
            distance,normal=curved.intersect(primitive,camera,direction)
            visible=np.isfinite(distance)&(distance<best)
            if not np.any(visible):continue
            position=camera+direction*np.where(visible,distance,0)[...,None]
            shaded=curved_shading(position,normal,primitive[4],primitive[5])
            base=np.where(visible[...,None],shaded,base)
            best=np.where(visible,distance,best)
        # Deliberately wrap the longitude seam by computing last ray from the first column.
        result[y0:y0+len(yy)]=np.uint8(np.clip(base,0,255))
    # Seam borders must represent the same azimuth.
    result[:,-1]=result[:,0]
    return Image.fromarray(result,'RGB')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--width',type=int,default=2048)
    p.add_argument('--out',type=Path,default=Path('art/candidates/B_B_NORMAL_360_geometry.webp'))
    p.add_argument('--materials',choices=['photoscan','procedural'],default='photoscan',
                   help='photoscan is default; procedural is explicit offline fallback')
    args=p.parse_args()
    if args.width<512 or args.width%2:raise SystemExit('--width must be an even integer >=512')
    if args.materials=='photoscan':load_materials()
    else:MATERIALS.clear()
    kitchen()
    image=render(args.width)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    image.save(args.out,'WEBP',quality=88,method=5)
    print('Rendered',args.out,'size',image.size,'objects',len(SCENE),'bytes',args.out.stat().st_size)
if __name__=='__main__':main()
