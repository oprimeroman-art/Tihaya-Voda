"""Panorama Forge core: spherical-aware offline panorama restoration.
Dependencies: Pillow, numpy. Tested with Python 3.11+.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
import json
import math
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = 270_000_000


class PanoramaError(Exception):
    pass


@dataclass
class Settings:
    scale: int = 2
    mode: str = "precision"                 # precision | ai
    model: str = "realesrgan-x4plus"
    sharpen: int = 30                        # 0..150
    denoise: int = 0                         # 0..100
    seam: int = 48                           # 0..256 output pixels
    tile: int = 256                          # GPU AI inference
    fmt: str = "png"
    quality: int = 94
    zones: Optional[list[dict]] = None

    @classmethod
    def parse(cls, raw: dict) -> 'Settings':
        kwargs = {k: raw[k] for k in cls.__dataclass_fields__ if k in raw}
        st = cls(**kwargs)
        if st.scale not in (2, 4):
            raise PanoramaError("Допустимые масштабы: ×2 или ×4")
        if st.mode not in ("precision", "ai"):
            raise PanoramaError("Режим должен быть precision или ai")
        if st.model not in ("realesrgan-x4plus", "realesrnet-x4plus", "realesrgan-x4plus-anime"):
            raise PanoramaError("Неизвестная AI-модель")
        if st.fmt not in ("png", "jpg", "webp"):
            raise PanoramaError("Формат: png, jpg или webp")
        for field, lo, hi in (("sharpen", 0, 150), ("denoise", 0, 100),
                              ("seam", 0, 256), ("tile", 64, 1024), ("quality", 60, 100)):
            val = getattr(st, field)
            if not isinstance(val, int) or val < lo or val > hi:
                raise PanoramaError(f"Некорректный параметр {field}")
        if st.zones is None:
            st.zones = []
        if len(st.zones) > 25:
            raise PanoramaError("Максимум 25 локальных зон")
        return st


def validate_pano(im: Image.Image) -> None:
    w, h = im.size
    if w < 128 or h < 64:
        raise PanoramaError("Слишком маленькая панорама (минимум 128×64)")
    if abs(w / h - 2.0) > 0.015:
        raise PanoramaError(f"Изображение {w}×{h} не является эквиректангулярной панорамой 2:1")
    if w * h > 75_000_000:
        raise PanoramaError("Исходник слишком большой; максимум 75 млн пикселей")


def to_pano_rgb(im: Image.Image) -> Image.Image:
    # EXIF orientation must be applied before ratio validation.
    im = ImageOps.exif_transpose(im)
    if im.mode == "RGBA" or 'transparency' in im.info:
        rgba = im.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        background.alpha_composite(rgba)
        im = background.convert('RGB')
    else:
        im = im.convert('RGB')
    validate_pano(im)
    w,h=im.size
    if w != 2*h:
        # Small export rounding error: use exact equirectangular width.
        im = im.resize((2*h,h), Image.Resampling.LANCZOS)
    return im


def spherical_pad(im: Image.Image, pad_x: int, pad_y: int) -> Image.Image:
    """Wrap horizontally; across poles mirror latitude + rotate longitude 180°.

    Supports panoramas of even pixel width, and padding smaller than a full height.
    """
    if pad_x < 0 or pad_y < 0:
        raise ValueError('Padding cannot be negative')
    a = np.asarray(im.convert('RGB'))
    h, w, _ = a.shape
    if w % 2 or pad_y > h:
        raise ValueError('Panorama width must be even and pad_y <= height')
    ys = np.arange(-pad_y, h+pad_y, dtype=np.int32)
    period = np.mod(ys, 2*h)
    iy = np.where(period < h, period, 2*h - period - 1)
    half_turn = np.where((ys < 0) | (ys >= h), w//2, 0)
    xx = np.arange(-pad_x, w+pad_x, dtype=np.int32)
    ix = np.mod(xx[None,:] + half_turn[:,None], w)
    return Image.fromarray(a[iy[:,None],ix,:])


def seam_score(im: Image.Image) -> float:
    # The first/last columns should meet: MAE on sRGB channels.
    a = np.asarray(im.crop((0, 0, 1, im.height)), dtype=np.int16)
    b = np.asarray(im.crop((im.width-1, 0, im.width, im.height)), dtype=np.int16)
    return round(float(np.abs(a-b).mean()), 3)


def fix_seam(im: Image.Image, feather: int) -> Image.Image:
    """Make first/last panorama columns continuous without disturbing center.

    Applies smooth symmetric color offsets (not crossfading unrelated scene geometry).
    """
    if feather <= 0:
        return im
    k=min(feather, im.width//4)
    if k <= 1:
        return im
    a=np.array(im.crop((0,0,k,im.height)), dtype=np.float32)
    b=np.array(im.crop((im.width-k,0,im.width,im.height)), dtype=np.float32)
    left=a[:,0,:].copy()
    right=b[:,-1,:].copy()
    delta=(right-left)/2.0
    x=np.linspace(0, 1, k, dtype=np.float32)
    weights=1 - (x*x*(3-2*x))
    a += delta[:,None,:]*weights[None,:,None]
    b -= delta[:,None,:]*weights[::-1][None,:,None]
    out=im.copy()
    out.paste(Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')), (0,0))
    out.paste(Image.fromarray(np.clip(np.rint(b),0,255).astype('uint8')), (im.width-k,0))
    return out


def denoise(im: Image.Image, intensity: int) -> Image.Image:
    if intensity<=0: return im
    # Only modest median-denoise to avoid erasing fine structural features.
    filtered=im.filter(ImageFilter.MedianFilter(size=3))
    return Image.blend(im, filtered, min(0.75, intensity / 130))


def sharpen(im: Image.Image, intensity: int) -> Image.Image:
    if intensity<=0: return im
    return im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=round(intensity*1.5), threshold=3))


def apply_zones(im: Image.Image, zones: list[dict]) -> Image.Image:
    out=im
    W,H=im.size
    for zone in zones:
        try:
            x,y,w,h=[float(zone[k]) for k in ('x','y','w','h')]
            power=float(zone.get('power',1))
            if not all(math.isfinite(v) for v in (x,y,w,h,power)):
                continue
            if w<=0 or h<=0 or power<=0: continue
            x1=max(0, min(W-1, int(x*W))); y1=max(0, min(H-1, int(y*H)))
            x2=max(x1+1, min(W, int((x+w)*W))); y2=max(y1+1,min(H,int((y+h)*H)))
            # Widen patch to allow feather of the local enhancement.
            margin=min(36,max(8,int(min(x2-x1,y2-y1)*0.08)))
            bx1=max(0,x1-margin); by1=max(0,y1-margin)
            bx2=min(W,x2+margin); by2=min(H,y2+margin)
            patch=out.crop((bx1,by1,bx2,by2))
            variant=patch.filter(ImageFilter.UnsharpMask(radius=2.0,percent=int(min(340,100+power*135)),threshold=2))
            mask=Image.new('L',patch.size,0)
            from PIL import ImageDraw
            d=ImageDraw.Draw(mask)
            d.rectangle((x1-bx1,y1-by1,x2-bx1,y2-by1), fill=255)
            mask=mask.filter(ImageFilter.GaussianBlur(radius=max(3,margin/2)))
            patch.paste(variant,(0,0),mask)
            if out is im: out=im.copy()
            out.paste(patch,(bx1,by1))
        except (TypeError,ValueError,KeyError):
            continue
    return out


def locate_ai_exe(root: Path) -> Optional[Path]:
    for name in ('realesrgan-ncnn-vulkan.exe','realesrgan-ncnn-vulkan'):
        options=[root/'ai'/name,root/name]
        for p in options:
            if p.exists() and p.is_file(): return p
    exe=shutil.which('realesrgan-ncnn-vulkan')
    return Path(exe) if exe else None


def upscale_ai(im: Image.Image, scale: int, model: str, tile: int, root: Path, notify: Callable[[str],None]) -> Image.Image:
    exe=locate_ai_exe(root)
    if not exe:
        raise PanoramaError('AI-движок не установлен. Запусти INSTALL_AI_WINDOWS.bat или используй точный режим.')
    with tempfile.TemporaryDirectory(prefix='panoforge-ai-') as t:
        folder=Path(t)
        input_path=folder/'padded.png'
        output_path=folder/'ai.png'
        # RealESRGAN receptive field demands overlap at seam and near poles.
        pad=64
        notify('Подготовка бесшовной 360°-развёртки для нейросети')
        spherical_pad(im,pad,pad).save(input_path)
        cmd=[str(exe.absolute()),'-i',str(input_path),'-o',str(output_path),'-n',model,'-s','4','-t',str(tile),'-f','png']
        notify('Нейросеть восстанавливает изображение на GPU (может занять время)')
        try:
            run=subprocess.run(cmd, cwd=str(exe.parent),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=3600)
        except (OSError,subprocess.TimeoutExpired) as e:
            raise PanoramaError(f'Ошибка запуска AI-движка: {e}') from e
        if run.returncode!=0 or not output_path.is_file():
            msg=run.stdout[-1100:] if run.stdout else 'Нет вывода от AI-движка'
            raise PanoramaError(f'AI-движок завершился с ошибкой: {msg}')
        with Image.open(output_path) as processed:
            factor=4
            expected=((im.width+2*pad)*factor,(im.height+2*pad)*factor)
            if processed.size!=expected:
                raise PanoramaError(f'AI вернул неожиданный размер {processed.size}; ожидали {expected}')
            inner=processed.crop((pad*factor,pad*factor,(pad+im.width)*factor,(pad+im.height)*factor)).convert('RGB')
        if scale!=factor:
            notify('Приведение AI-результата к выбранному разрешению')
            inner=inner.resize((im.width*scale,im.height*scale),Image.Resampling.LANCZOS)
        return inner


def upscale_precision(im: Image.Image, scale: int, notify: Callable[[str],None]) -> Image.Image:
    pad=16
    notify('Сферическая интерполяция, без разрыва на шве и полюсах')
    enlarged=spherical_pad(im,pad,pad).resize(((im.width+2*pad)*scale,(im.height+2*pad)*scale),Image.Resampling.LANCZOS)
    return enlarged.crop((pad*scale,pad*scale,(pad+im.width)*scale,(pad+im.height)*scale))


def enhance(input_path: Path, output_path: Path, settings: Settings, root: Optional[Path]=None,
            notify: Optional[Callable[[str],None]]=None) -> dict:
    notify=notify or (lambda _msg:None)
    root=root or Path(__file__).resolve().parent
    notify('Открытие панорамы')
    with Image.open(input_path) as src:
        im=to_pano_rgb(src)
    base_size=im.size
    before=seam_score(im)
    if im.width*im.height*settings.scale**2 > 125_000_000:
        raise PanoramaError('Панорама после увеличения превышает лимит 125 млн пикселей')
    if settings.mode=='ai':
        out=upscale_ai(im,settings.scale,settings.model,settings.tile,root,notify)
    else:
        out=upscale_precision(im,settings.scale,notify)
    notify('Тонкая обработка деталей')
    out=denoise(out,settings.denoise)
    out=sharpen(out,settings.sharpen)
    out=apply_zones(out,settings.zones or [])
    seam_before=seam_score(out)
    notify('Сшивка границ панорамы')
    out=fix_seam(out,settings.seam)
    after=seam_score(out)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    notify('Сохранение полного разрешения')
    opt={}
    if settings.fmt=='jpg': opt={'quality':settings.quality,'subsampling':0}
    elif settings.fmt=='webp': opt={'quality':settings.quality,'method':5}
    else: opt={'compress_level':5}
    out.save(output_path,**opt)
    return {'source':list(base_size),'output':list(out.size),'mode':settings.mode,
            'file':output_path.name,'bytes':output_path.stat().st_size,
            'seam_source':before,'seam_raw':seam_before,'seam_final':after,'scale':settings.scale,
            'note':('AI-реконструкция выполнена Real-ESRGAN' if settings.mode=='ai' else 'Геометрически корректное увеличение Lanczos; недостающие объекты не восстановлены')}


def make_preview(path:Path,target:Path, width:int=2400) -> None:
    with Image.open(path) as im:
        im=to_pano_rgb(im)
        if im.width>width:
            im.thumbnail((width,width//2),Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True,exist_ok=True)
        im.save(target,format='JPEG',quality=84,optimize=True)