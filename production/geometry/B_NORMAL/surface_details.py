"""Baked Cyrillic maintenance signage placed on *physical* kitchen objects.

Printed lettering, pens, stamps and pencil lines are generated in memory from
regular fonts. No online textures, font files or separate runtime dependencies.
The photo-mapped image remains a single offline 360 x 180 panorama.
"""
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont

PRINTED={
 'note_page':('ПАМЯТКА','ПОСЛЕ СМЕНЫ',
     ['Выключить плиту','Перекрыть кран','Записать расход','П. Сухов'], 'red'),
 'tea_instruction':('ИНСТРУКЦИЯ','ЧАЙНАЯ КАРТА',
     ['1. ВОДА','2. НАГРЕВ','3. ЗАВАРКА','4. РАЗЛИТЬ'], 'blue'),
 'work_notice':('МАЯК-9','ДЕЖУРСТВО',
     ['18 ЯНВАРЯ 2026','КУХНЯ / БЫТОВОЙ ОТСЕК','ДЕРЖАТЬ В ПОРЯДКЕ'], 'red'),
 'fridge_badge':('МАЯК-9','ХОЛОДИЛЬНИК',
     ['ПРОВЕРИТЬ УПЛОТНИТЕЛЬ','+2 ... +5  C'], 'blue'),
}
def font(size,bold=False):
    choices=['DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%
                ('-Bold' if bold else '')]
    for path in choices:
        try:return ImageFont.truetype(path,size=size)
        except OSError:pass
    raise RuntimeError('Cyrillic DejaVuSans font required for reproducible station labels')

@lru_cache(maxsize=12)
def paper(name):
    if name not in PRINTED:return None
    title,subtitle,lines,stamp=PRINTED[name]
    canvas=Image.new('RGB',(512,768),(217,211,187))
    d=ImageDraw.Draw(canvas)
    # Border, subtle ruled paper and left-hand mounting strip.
    d.rectangle((20,20,492,745),outline=(110,110,95),width=3)
    d.rectangle((32,32,480,119),fill=(186,190,171))
    d.text((43,41),title,font=font(41,True),fill=(40,51,55))
    d.text((40,142),subtitle,font=font(29,True),fill=(38,49,53))
    d.line((40,199,463,199),fill=(115,122,112),width=4)
    for i,line in enumerate(lines):
        y=248+i*99
        if name=='tea_instruction':
            d.rectangle((42,y-5,67,y+20),outline=(86,101,112),width=3)
            d.text((81,y-8),line,font=font(23),fill=(45,53,58))
        else:
            d.ellipse((43,y+3,56,y+16),fill=(84,89,79))
            d.text((70,y-12),line,font=font(19),fill=(47,54,54))
        d.line((42,y+43,456,y+43),fill=(188,185,166),width=2)
    if stamp=='red':
        d.rectangle((244,650,454,714),outline=(138,62,57),width=4)
        d.text((264,659),'ПРОВЕРЕНО',font=font(24,True),fill=(151,69,63))
    else:
        d.line((226,697,455,677),fill=(64,76,106),width=3)
    # Repeated noise adds small scratches and uneven yellow paper.
    yy,xx=np.mgrid[0:768,0:512]
    grain=(np.sin(xx*.071+yy*.031)*np.cos(yy*.11-xx*.053)*2.8 +
           2.1*np.sin((xx+yy)*.17))
    arr=np.asarray(canvas,dtype=np.float32).copy()
    arr=np.clip(arr+grain[...,None],0,255).astype('uint8')
    return arr

def sampled_label(name,position,lo,hi):
    """Look up the photographed object's correct wall-facing paper UV pixels."""
    image=paper(name)
    if image is None:return None
    # Every station label lies on an x-facing (east/west) plane.
    # Horizontal axis is -Z or +Z for the two opposite walls.
    size=np.maximum(hi-lo,1e-6)
    if (hi[0]+lo[0])>0:
        u=(hi[2]-position[...,2])/size[2]
    else:
        u=(position[...,2]-lo[2])/size[2]
    v=(hi[1]-position[...,1])/size[1]
    row=np.clip(np.floor(v*image.shape[0]).astype('int32'),0,image.shape[0]-1)
    col=np.clip(np.floor(u*image.shape[1]).astype('int32'),0,image.shape[1]-1)
    return image[row,col].astype(np.float32)
