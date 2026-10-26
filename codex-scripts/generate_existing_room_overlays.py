#!/usr/bin/env python3
"""Generate the three missing transparent overlays for existing C/F/H rooms.

All canvases are 2048x1024 and alpha-only outside the authored changes. The
base panorama remains authoritative; no room geometry or story logic is changed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, hashlib
ROOT=Path(__file__).resolve().parents[1]
SIZE=(2048,1024)
OUT=ROOT/'art/overlays'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(path,size):
 try:return ImageFont.truetype(path,size)
 except OSError:return ImageFont.load_default()
def save(name,im):
 OUT.mkdir(parents=True,exist_ok=True); p=OUT/name
 im.save(p,'WEBP',lossless=True,method=6)
 raw=p.read_bytes(); print(name,'bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest(),'size',im.size,'alpha',im.getchannel('A').getextrema())
 return p
def source(room):
 p=ROOT/f'game-project/rooms/{room}/original.png'
 im=Image.open(p).convert('RGBA')
 if im.size!=SIZE: raise ValueError(f'{p} must be {SIZE}, got {im.size}')
 return im

def mirror_light():
 im=Image.new('RGBA',SIZE,(0,0,0,0))
 # Soft reflected flashlight bloom contained within the center mirror/panel.
 yy,xx=np.mgrid[0:SIZE[1],0:SIZE[0]]
 cx,cy=1100,445
 radial=np.exp(-(((xx-cx)/165)**2+((yy-cy)/125)**2)*2.0)
 beam=np.zeros((SIZE[1],SIZE[0]),dtype=float)
 # Narrow cone from the torch reflection toward the lower-right of the glass.
 x0,y0,x1,y1=1030,415,1270,575
 vx,vy=x1-x0,y1-y0; t=np.clip(((xx-x0)*vx+(yy-y0)*vy)/(vx*vx+vy*vy),0,1)
 px=x0+t*vx; py=y0+t*vy; dist=np.sqrt((xx-px)**2+(yy-py)**2)
 cone=np.exp(-(dist/(12+26*t))**2*1.8)*np.clip(1-t,0,1)
 # Restrict all glow to the center framed glass, leaving the rest transparent.
 mask=((xx>=850)&(xx<=1370)&(yy>=265)&(yy<=640)).astype(float)
 alpha=np.clip((radial*92+cone*72)*mask,0,120).astype('uint8')
 glow=np.zeros((SIZE[1],SIZE[0],4),dtype='uint8'); glow[:,:,:3]=[174,219,225]; glow[:,:,3]=alpha
 im=Image.alpha_composite(im,Image.fromarray(glow,'RGBA'))
 d=ImageDraw.Draw(im,'RGBA')
 # A tiny hard reflection core and a thin lens flare; it should read as an ON
 # flashlight, not a generic bright mirror or a supernatural face.
 d.ellipse((1074,414,1126,466),fill=(173,222,232,34),outline=(205,235,231,130),width=3)
 d.ellipse((1088,428,1112,452),fill=(228,242,228,218),outline=(244,247,226,235),width=3)
 d.ellipse((1096,436,1104,444),fill=(255,255,239,255))
 d.line((1048,440,1170,440),fill=(214,241,238,86),width=2)
 d.line((1100,392,1100,488),fill=(214,241,238,58),width=2)
 # Fine vertical reflected streaks and glints on old glass.
 for x,y0,y1,a in [(890,330,565,22),(1325,300,590,18),(1180,290,360,16)]:
  d.line((x,y0,x-4,y1),fill=(184,218,218,a),width=3)
 d.line((1130,475,1250,550),fill=(203,232,226,34),width=2)
 return save('C_C_MIRROR_LIGHT.webp',im)

def archive_sign():
 im=Image.new('RGBA',SIZE,(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
 # Replace only the existing small wall label above the first stockroom cabinet.
 # The plate's opaque body intentionally covers the old word while all nearby
 # wall/panel pixels remain untouched.
 x0,y0,x1,y1=62,119,472,222
 d.rounded_rectangle((x0+8,y0+9,x1+10,y1+11),radius=7,fill=(4,9,11,150))
 d.rounded_rectangle((x0,y0,x1,y1),radius=6,fill=(37,49,50,252),outline=(113,126,117,245),width=5)
 d.rounded_rectangle((x0+10,y0+10,x1-10,y1-10),radius=3,fill=(47,59,58,252),outline=(17,27,29,230),width=2)
 # Oxidized red edge stripe and tiny fasteners.
 d.rectangle((x0+15,y0+16,x0+25,y1-16),fill=(141,52,46,245))
 for x,y in [(x0+10,y0+10),(x1-10,y0+10),(x0+10,y1-10),(x1-10,y1-10)]:
  d.ellipse((x-5,y-5,x+5,y+5),fill=(147,151,132,240),outline=(15,24,26,245),width=2)
 # Scratched enamel, worn edges, stamped type.
 for i in range(24):
  x=x0+40+(i*53)%330; y=y0+18+(i*29)%68
  d.line((x,y,x+((i%5)+3),y-1),fill=(177,177,151,35+(i%4)*8),width=1)
 d.text((x0+42,y0+25),'АРХИВ-12',font=font(FONT_BOLD,44),fill=(218,216,187,255),stroke_width=1,stroke_fill=(19,29,30,210))
 d.text((x0+44,y0+72),'СЕКТОР ХРАНЕНИЯ',font=font(FONT,15),fill=(155,169,153,210))
 return save('F_F_ARCHIVE12.webp',im)

def after_v01():
 im=Image.new('RGBA',SIZE,(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
 # Center cabinet is open by a few centimetres: preserve the original frame and
 # paint only the dark reveal, inner shelf and the edge of the swung door.
 d.polygon([(855,291),(1330,291),(1330,627),(855,627)],fill=(9,15,17,118))
 d.polygon([(872,307),(1307,307),(1307,608),(872,608)],fill=(20,29,30,220))
 # Inner shelf and cold reflection from the corridor.
 d.polygon([(885,400),(1288,400),(1288,414),(885,414)],fill=(89,105,99,185))
 d.polygon([(885,522),(1288,522),(1288,536),(885,536)],fill=(75,91,86,160))
 d.polygon([(866,301),(1064,322),(1012,604),(866,604)],fill=(55,69,67,255),outline=(133,145,128,240))
 d.line((1064,322,1012,604),fill=(178,183,159,190),width=5)
 d.line((1027,340,982,590),fill=(15,24,25,230),width=8)
 d.ellipse((1021,454,1038,471),fill=(170,172,145,245),outline=(22,31,31,245),width=3)
 # Paper note taped inside the cabinet. Slight rotation gives it a physical edge.
 note=Image.new('RGBA',(278,154),(0,0,0,0)); nd=ImageDraw.Draw(note,'RGBA')
 nd.polygon([(8,9),(265,4),(270,144),(3,149)],fill=(8,13,14,115))
 nd.polygon([(3,3),(260,0),(266,137),(0,143)],fill=(196,188,157,255),outline=(91,91,76,240))
 nd.line((12,18,246,15),fill=(136,128,105,110),width=2)
 nd.text((18,34),'МЫ УЖЕ',font=font(FONT_BOLD,27),fill=(36,42,38,255))
 nd.text((18,68),'ЗНАКОМЫ',font=font(FONT_BOLD,27),fill=(36,42,38,255))
 nd.line((18,106,217,102),fill=(124,50,42,205),width=3)
 nd.text((18,116),'V01 / 1978',font=font(FONT,12),fill=(77,79,67,220))
 # Pin/tape and aged paper spots.
 nd.ellipse((126,4,139,17),fill=(135,49,41,245),outline=(57,32,28,255),width=2)
 for i in range(8):
  xx=24+i*27; nd.line((xx,24,xx+8,24),fill=(94,91,73,35),width=1)
 note=note.rotate(-1.5,resample=Image.Resampling.BICUBIC,expand=False)
 im.alpha_composite(note,(1010,372))
 # A thin strip of colder light on the open door edge.
 d=ImageDraw.Draw(im,'RGBA'); d.line((1061,326,1010,598),fill=(198,211,192,72),width=2)
 return save('H_H_AFTER_V01.webp',im)

if __name__=='__main__':
 source('C'); source('F'); source('H')
 mirror_light(); archive_sign(); after_v01()
