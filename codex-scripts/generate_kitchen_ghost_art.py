#!/usr/bin/env python3
"""Deterministically paint the chapter-4 kitchen ghost-mirror panorama.

The artwork is a 2:1, offline WebP scene variant for the existing B_GHOST_MIRROR
story state. It introduces no gameplay objects or narrative changes.
"""
from pathlib import Path
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site-assets/kitchen-states/B_GHOST_MIRROR.webp'
W,H=2048,1024
rng=np.random.default_rng(197804)
y,x=np.mgrid[0:H,0:W]
# Cold painted base: weakly lit tile wall and darker floor, with the fluorescent
# pool concentrated over the sink/mirror and a dead zone in the corners.
wall=np.array([43,58,63.],dtype=float); floor=np.array([24,32,35.],dtype=float)
t=(y/H)[...,None]
base=wall[None,None,:]*(1-np.clip((y-610)/240,0,1)[...,None])+floor[None,None,:]*np.clip((y-610)/240,0,1)[...,None]
light=np.exp(-(((x-1050)/560)**2+((y-285)/320)**2)*1.4)*34
vignette=np.clip(1-.42*((x-W/2)/(W*.72))**2-.38*((y-H/2)/(H*.8))**2,.35,1)
noise=rng.normal(0,3.0,(H,W,1))
arr=np.clip((base+light[...,None]+noise)*vignette[...,None],0,255).astype('uint8')
im=Image.fromarray(arr,'RGB').convert('RGBA')
# Separate blurred practical-light pool; no flat, sterile gradients.
lightlayer=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lightlayer)
ld.ellipse((650,80,1460,570),fill=(177,204,195,36)); lightlayer=lightlayer.filter(ImageFilter.GaussianBlur(90)); im=Image.alpha_composite(im,lightlayer)
d=ImageDraw.Draw(im,'RGBA')
# Ceiling: sagging panels, fluorescent fixture and cable run.
d.polygon([(0,0),(W,0),(W,128),(1530,168),(540,150),(0,190)],fill=(18,27,31,235))
for xx in range(0,W,310):
 d.line((xx,0,xx+35,150),fill=(110,130,130,70),width=3)
d.polygon([(720,85),(1325,94),(1290,130),(740,123)],fill=(160,178,169,100))
d.rounded_rectangle((770,83,1280,113),radius=8,fill=(207,221,194,225),outline=(221,227,206,180),width=3)
d.line((780,94,1268,102),fill=(255,240,196,130),width=5)
# Old tiled wall, uneven joints and water staining.
d.polygon([(0,170),(W,145),(W,660),(0,655)],fill=(53,70,73,125))
for yy in [235,310,385,460,535,610]:
 d.line((0,yy,W,yy-18),fill=(133,150,145,44),width=2)
for xx in range(60,W,155):
 d.line((xx,170,xx-10,655),fill=(126,142,139,38),width=2)
# Pipes and electrical conduit along the back wall.
d.line([(120,150),(120,585),(250,585),(250,650)],fill=(13,22,25,255),width=18)
d.line([(120,150),(120,585),(250,585),(250,650)],fill=(91,105,101,180),width=6)
d.line([(1760,145),(1760,520),(1660,550),(1660,650)],fill=(14,21,24,255),width=21)
d.line([(1760,145),(1760,520),(1660,550),(1660,650)],fill=(105,117,108,180),width=5)
# Left service counter, battered steel doors, sink and enamel cup.
d.polygon([(0,425),(610,394),(680,440),(0,490)],fill=(17,27,30,255))
d.polygon([(0,490),(680,440),(680,595),(0,636)],fill=(62,75,76,255))
d.polygon([(0,478),(672,431),(676,451),(0,504)],fill=(143,157,148,180))
for xx in [145,310,480]:
 d.line((xx,486-(xx/18),xx,610-(xx/18)),fill=(21,31,33,240),width=6)
 d.ellipse((xx-10,545-(xx/30),xx+3,558-(xx/30)),fill=(171,177,157,180))
# Sink basin, tap and a dirty mug.
d.polygon([(350,410),(535,397),(585,425),(388,443)],fill=(21,31,33,255),outline=(147,161,152,180))
d.line([(444,405),(444,372),(460,356),(486,356),(486,402)],fill=(131,147,143,230),width=9)
d.line((459,356,480,356),fill=(182,193,176,210),width=5)
d.ellipse((520,386,548,410),fill=(183,187,164,235),outline=(27,39,40,255),width=4)
# Right stove and warming pipes.
d.polygon([(1480,415),(1915,395),(2048,433),(2048,630),(1470,595)],fill=(18,27,30,255))
d.polygon([(1500,420),(1900,402),(2010,430),(1510,454)],fill=(116,128,120,225))
d.polygon([(1510,454),(2010,430),(2010,595),(1510,575)],fill=(51,63,64,255))
for xx in [1580,1700,1820,1940]:
 d.ellipse((xx,447,xx+40,467),fill=(18,27,29,255),outline=(176,181,159,190),width=4)
 d.ellipse((xx+12,452,xx+28,462),fill=(125,137,124,220))
d.line((1530,505,1980,489),fill=(146,153,139,120),width=3)
# Wall mirror: a heavy oxidized frame, cloudy glass, wrong depth.
# Draw reflection glass to its own layer so the silhouette appears behind the
# actual room, not as a person standing in the kitchen.
mx0,my0,mx1,my1=760,185,1320,470
d.rounded_rectangle((mx0-23,my0-21,mx1+24,my1+25),radius=10,fill=(13,21,24,255),outline=(116,128,116,230),width=9)
d.rounded_rectangle((mx0,my0,mx1,my1),radius=6,fill=(67,89,91,255),outline=(27,39,42,255),width=5)
# Reflective mottled haze.
mirror=Image.new('RGBA',(560,285),(0,0,0,0)); md=ImageDraw.Draw(mirror,'RGBA')
md.rectangle((0,0,560,285),fill=(90,119,121,145))
for i in range(18):
 xx=int(rng.integers(0,560)); yy=int(rng.integers(0,285)); rr=int(rng.integers(16,70))
 md.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(165,185,174,int(rng.integers(5,20))))
md.line((20,225,540,190),fill=(207,215,193,36),width=4)
md.line((60,42,420,18),fill=(211,221,205,30),width=3)
# Ghostly Anna: hair/shoulders/head and a hand lifted toward an absent plate.
# Her body dissolves into the reflection's vertical water stains.
md.ellipse((240,66,326,164),fill=(22,32,35,220))
md.ellipse((251,77,314,145),fill=(174,177,157,210))
md.pieslice((235,58,331,170),180,360,fill=(18,27,31,240))
md.polygon([(218,160),(252,137),(313,139),(350,178),(372,285),(186,285)],fill=(30,42,44,225))
md.polygon([(270,148),(290,148),(300,204),(284,222),(264,200)],fill=(185,183,157,105))
md.line((213,188,173,225,214,238),fill=(166,178,160,200),width=12)
md.ellipse((203,232,229,246),fill=(190,189,163,185))
md.line((304,188,340,215,360,205),fill=(157,172,155,190),width=10)
# Face has only two dark, uncertain marks; no gore or explicit monster features.
md.ellipse((265,111,272,119),fill=(18,27,30,235)); md.ellipse((296,109,303,117),fill=(18,27,30,235))
md.line((276,134,294,132),fill=(89,94,83,180),width=3)
mirror=mirror.filter(ImageFilter.GaussianBlur(1.4)); im.alpha_composite(mirror,(mx0,my0))
d=ImageDraw.Draw(im,'RGBA')
# Finger marks and a narrow crack in the glass.
d.line((1275,210,1248,266,1264,301,1239,358),fill=(206,218,199,80),width=3)
d.line((786,446,850,440),fill=(197,204,184,100),width=3)
# Foreground steel table, perspective legs and two enamel plates.
d.polygon([(330,610),(1640,582),(1900,680),(180,713)],fill=(11,18,20,235))
d.polygon([(180,713),(1900,680),(1870,750),(225,785)],fill=(57,69,68,255))
d.line((225,785,1870,750),fill=(145,151,134,130),width=4)
d.polygon([(360,715),(420,713),(398,970),(340,970)],fill=(19,27,29,255))
d.polygon([(1600,756),(1660,754),(1740,974),(1684,974)],fill=(19,27,29,255))
# Plate A: ordinary, scratched enamel. Plate B: empty but wet; reflected face
# appears in a faint, impossible shadow rather than a second physical person.
def plate(cx,cy,rx,ry,ghost=False):
 d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(12,20,22,230))
 d.ellipse((cx-rx+9,cy-ry+5,cx+rx-9,cy+ry-5),fill=(184,189,170,245),outline=(223,222,198,190),width=4)
 d.ellipse((cx-rx+23,cy-ry+13,cx+rx-23,cy+ry-13),fill=(69,82,80,245),outline=(112,127,119,180),width=3)
 if ghost:
  d.ellipse((cx-24,cy-19,cx+24,cy+19),fill=(177,194,179,36))
  d.ellipse((cx-12,cy-10,cx-7,cy-5),fill=(17,27,30,175));d.ellipse((cx+7,cy-10,cx+12,cy-5),fill=(17,27,30,175))
  d.arc((cx-19,cy-2,cx+19,cy+18),10,170,fill=(17,27,30,145),width=2)
  d.arc((cx-rx+27,cy-ry+17,cx+rx-27,cy+ry-17),195,335,fill=(207,219,195,140),width=3)
 else:
  d.arc((cx-rx+24,cy-ry+13,cx+rx-24,cy+ry-13),190,330,fill=(220,215,188,110),width=3)
plate(720,680,115,43,False)
plate(1240,670,112,41,True)
# A spoon suspended just above the empty plate, with a shadow that doesn't match.
d.line((1304,628,1360,654),fill=(191,196,177,235),width=9);d.ellipse((1350,645,1382,662),fill=(186,193,175,220))
d.line((1290,675,1368,704),fill=(9,16,19,160),width=8)
# Cold vapor at table level; soft, low opacity wisps.
fog=Image.new('RGBA',(W,H),(0,0,0,0));fd=ImageDraw.Draw(fog,'RGBA')
for i in range(20):
 yy=int(rng.integers(590,760)); xx=int(rng.integers(500,1580)); ww=int(rng.integers(90,280))
 fd.ellipse((xx,yy,xx+ww,yy+int(rng.integers(12,40))),fill=(176,196,187,int(rng.integers(3,11))))
fog=fog.filter(ImageFilter.GaussianBlur(22));im=Image.alpha_composite(im,fog)
# Subtle surface scratches, edge bloom and film grain tie the vector geometry
# back to a painted horror-game matte.
rgb=np.asarray(im.convert('RGB')).astype(np.int16)
grain=rng.normal(0,3.2,(H,W,1))
rgb=np.clip(rgb+grain,0,255).astype('uint8')
out=Image.fromarray(rgb,'RGB').filter(ImageFilter.GaussianBlur(.28))
OUT.parent.mkdir(parents=True,exist_ok=True)
out.save(OUT,'WEBP',quality=91,method=6)
raw=OUT.read_bytes()
print('WROTE',OUT,'size',len(raw),'sha256',hashlib.sha256(raw).hexdigest(),'dimensions',out.size)
