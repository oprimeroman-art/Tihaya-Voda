#!/usr/bin/env python3
"""Split an equirectangular image into lossless independently loadable UV tiles.

Runs offline, needs Pillow. Written for Tihaya Voda, not a second engine.
A tile contains real source pixels; generating tiles never improves sharpness.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]


def tile_image(image_path: Path, room: str, size: int = 1024,
               output_dir: Path | None = None, verify: bool = True):
    if size < 64 or size > 4096:
        raise ValueError('Tile size must be in 64..4096')
    image = Image.open(image_path).convert('RGBA')
    width, height = image.size
    if width < 64 or height < 32 or abs(width - 2 * height) > 1:
        raise ValueError('360 input must be equirectangular 2:1')
    out = output_dir or ROOT / 'site-assets/panorama-patches'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    rebuilt = Image.new('RGBA', image.size) if verify else None
    for y in range(0, height, size):
        for x in range(0, width, size):
            right, bottom = min(width, x+size), min(height, y+size)
            segment = image.crop((x,y,right,bottom))
            dest = out / f'{image_path.stem}-{room}-{x}-{y}.png'
            segment.save(dest, optimize=True)
            rows.append({'id':f'{room}_{image_path.stem}_{x}_{y}', 'room':room,
                         'path':str(dest.relative_to(ROOT)) if dest.is_relative_to(ROOT) else str(dest),
                         'mime':'image/png',
                         'rect':[x/width,y/height,right/width,bottom/height]})
            if verify: rebuilt.paste(Image.open(dest), (x,y))
    if verify and ImageChops.difference(image,rebuilt).getbbox():
        raise AssertionError('Pixel-perfect tile roundtrip failed')
    return rows


def main():
    ap=argparse.ArgumentParser(description='Split 2:1 360 panorama into exact RGBA tile grid.')
    ap.add_argument('image',type=Path)
    ap.add_argument('--room',required=True)
    ap.add_argument('--size',type=int,default=1024)
    ap.add_argument('--manifest',type=Path,default=ROOT/'production/panorama-detail-tiles.json')
    ap.add_argument('--condition',default=None,help='JSON: e.g. {"flag":"slippers"}')
    ap.add_argument('--variant',default=None)
    ap.add_argument('--no-verify',action='store_true')
    args=ap.parse_args()
    tiles=tile_image(args.image,args.room,args.size,verify=not args.no_verify)
    if args.condition:
        condition=json.loads(args.condition)
        for tile in tiles:tile['when']=condition
    if args.variant:
        for tile in tiles:tile['variant']=args.variant
    data=json.loads(args.manifest.read_text(encoding='utf8')) if args.manifest.exists() else {'schema':1,'tiles':[]}
    ids={t['id'] for t in tiles}
    data['tiles']=[x for x in data['tiles'] if x['id'] not in ids]+tiles
    args.manifest.parent.mkdir(parents=True,exist_ok=True)
    args.manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
    print('Exact pixels preserved:',args.image,'->',len(tiles),'tiles; manifest:',args.manifest)

if __name__=='__main__':main()
