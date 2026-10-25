"""Analytic sphere and capped-cylinder primitives for the B_NORMAL offline renderer.

All intersections use world coordinates and true ray geometry; no projected
stickers or per-viewport distortions.  Vectorised over rays for reproducibility.
"""
import numpy as np


def ellipsoid(name, center, radii, color, kind='enamel'):
    return (name,'ellipsoid',np.asarray(center,dtype=np.float32),
            np.asarray(radii,dtype=np.float32),np.asarray(color,dtype=np.float32),kind)

def cylinder(name, center, radius, y_min, y_max, color, kind='enamel'):
    return (name,'cylinder',np.asarray(center,dtype=np.float32),
            np.asarray((radius,y_min,y_max),dtype=np.float32),
            np.asarray(color,dtype=np.float32),kind)

def intersect(primitive, origin, direction):
    """Return t and normal for every ray; t=inf where no intersection.

    origin is (3,) or (...,3), direction (...,3). Uses the nearest
    positive hit and also correctly handles camera-inside primitives.
    """
    _,kind,centre,params,*_=primitive
    origin=np.asarray(origin,dtype=np.float32)
    direction=np.asarray(direction,dtype=np.float32)
    shape=direction.shape[:-1]
    if kind=='ellipsoid':
        relative=(origin-centre)/params
        velocity=direction/params
        a=np.sum(velocity*velocity,axis=-1)
        b=2*np.sum(relative*velocity,axis=-1)
        c=np.sum(relative*relative,axis=-1)-1
        delta=b*b-4*a*c
        radical=np.sqrt(np.maximum(delta,0))
        t1=(-b-radical)/(2*a)
        t2=(-b+radical)/(2*a)
        dist=np.where(t1>.001,t1,np.where(t2>.001,t2,np.inf))
        dist=np.where(delta>=0,dist,np.inf)
        location=origin+direction*np.where(np.isfinite(dist),dist,0)[...,None]
        normal=(location-centre)/(params*params)
    else:
        radius,yl,yh=params
        dx=direction[...,0];dz=direction[...,2]
        ox=origin[...,0]-centre[0];oz=origin[...,2]-centre[2]
        a=dx*dx+dz*dz
        b=2*(ox*dx+oz*dz)
        c=ox*ox+oz*oz-radius*radius
        delta=b*b-4*a*c
        radical=np.sqrt(np.maximum(delta,0))
        safe_a=np.where(a>1e-9,a,1)
        t1=(-b-radical)/(2*safe_a)
        t2=(-b+radical)/(2*safe_a)
        y1=origin[...,1]+direction[...,1]*t1
        y2=origin[...,1]+direction[...,1]*t2
        ok=(delta>=0)&(a>1e-9)
        side1=np.where(ok&(t1>.001)&(y1>=yl)&(y1<=yh),t1,np.inf)
        side2=np.where(ok&(t2>.001)&(y2>=yl)&(y2<=yh),t2,np.inf)
        side=np.minimum(side1,side2)
        safe_y=np.where(np.abs(direction[...,1])>1e-9,direction[...,1],1)
        low=(yl-origin[...,1])/safe_y
        high=(yh-origin[...,1])/safe_y
        cap_lx=origin[...,0]+direction[...,0]*low-centre[0]
        cap_lz=origin[...,2]+direction[...,2]*low-centre[2]
        cap_hx=origin[...,0]+direction[...,0]*high-centre[0]
        cap_hz=origin[...,2]+direction[...,2]*high-centre[2]
        has_vertical=np.abs(direction[...,1])>1e-9
        low=np.where(has_vertical&(low>.001)&(cap_lx**2+cap_lz**2<=radius**2),low,np.inf)
        high=np.where(has_vertical&(high>.001)&(cap_hx**2+cap_hz**2<=radius**2),high,np.inf)
        dist=np.minimum(side,np.minimum(low,high))
        location=origin+direction*np.where(np.isfinite(dist),dist,0)[...,None]
        cap=np.isfinite(dist)&((dist==low)|(dist==high))
        normal=np.stack(np.broadcast_arrays(location[...,0]-centre[0],
                   np.zeros(shape,dtype=np.float32),location[...,2]-centre[2]),axis=-1)
        normal[...,1]=np.where(cap,np.where(dist==low,-1,1),0)
        normal[...,0]=np.where(cap,0,normal[...,0])
        normal[...,2]=np.where(cap,0,normal[...,2])
    normal=np.where(np.isfinite(dist)[...,None],normal,0)
    norm=np.linalg.norm(normal,axis=-1,keepdims=True)
    normal=normal/np.maximum(norm,1e-12)
    return dist,normal
