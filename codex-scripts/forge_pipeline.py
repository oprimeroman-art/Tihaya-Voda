#!/usr/bin/env python3
"""Prepare 360 detail tiles from the actual user-supplied Panorama Forge core.

An authoring utility of Tihaya Voda, not an alternative game engine.
Processing is offline; the game lazily loads generated independent PNG tiles.
"""
from __future__ import annotations
import argparse
import json
import tempfile
from pathlib import Path
from panorama_forge_engine import Settings, enhance
from forge_tile_image import tile_image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "production/panorama-detail-tiles.json"
DEFAULT_ASSETS = ROOT / "site-assets/panorama-patches"


def prepare(input_image:Path, room:str, *, scale:int=2, mode:str='precision',
            tile_size:int=1024, sharpen:int=20, denoise:int=0, seam:int=48,
            model:str='realesrgan-x4plus', variant:str|None=None,
            condition:dict|None=None, register:bool=False,
            manifest:Path=DEFAULT_MANIFEST, output_dir:Path=DEFAULT_ASSETS):
    if not input_image.is_file():raise FileNotFoundError(input_image)
    settings=Settings.parse({'scale':scale,'mode':mode,'fmt':'png','sharpen':sharpen,
                             'denoise':denoise,'seam':seam,'model':model})
    if tile_size not in (256,512,1024,2048):
        raise ValueError('Use 256, 512, 1024 or 2048 pixel tiles')
    with tempfile.TemporaryDirectory(prefix='tv-forge-') as tmp:
        upgraded=Path(tmp)/(room+'-'+input_image.stem+'-enhanced.png')
        report=enhance(input_image,upgraded,settings,root=ROOT,notify=lambda s:print(s,flush=True))
        rows=tile_image(upgraded,room,tile_size,output_dir=output_dir,verify=True)
    for row in rows:
        if variant:row['variant']=variant
        if condition:row['when']=condition
        row['priority']=-10  # Full-coverage detail tiles are behind interactive patches.
    if register:
        for row in rows:
            raw=Path(row['path'])
            if raw.is_absolute() or raw.parts[:2]!=('site-assets','panorama-patches'):
                raise ValueError('Registered tile files must reside under site-assets/panorama-patches')
        stored=json.loads(manifest.read_text('utf8')) if manifest.exists() else {'schema':1,'tiles':[]}
        old={row['id'] for row in rows}
        stored['tiles']=[x for x in stored['tiles'] if x['id'] not in old]+rows
        manifest.parent.mkdir(parents=True,exist_ok=True)
        manifest.write_text(json.dumps(stored,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report,rows


def main():
    p=argparse.ArgumentParser(description='Panorama Forge restoration -> native UV image tiles inside Tihaya Voda')
    p.add_argument('image',type=Path)
    p.add_argument('--room',required=True,help='Canonical room ID, e.g. A')
    p.add_argument('--variant',help='Only for a specified authored room visual variant')
    p.add_argument('--mode',choices=('precision','ai'),default='precision')
    p.add_argument('--scale',type=int,choices=(2,4),default=2)
    p.add_argument('--tile-size',type=int,default=1024)
    p.add_argument('--sharpen',type=int,default=20)
    p.add_argument('--denoise',type=int,default=0)
    p.add_argument('--seam',type=int,default=48)
    p.add_argument('--model',default='realesrgan-x4plus')
    p.add_argument('--condition',help='When condition JSON: {"flag":"slippers"}')
    p.add_argument('--register',action='store_true',help='Append tile descriptors to game manifest')
    args=p.parse_args()
    report,rows=prepare(args.image,args.room,scale=args.scale,mode=args.mode,
        tile_size=args.tile_size,sharpen=args.sharpen,denoise=args.denoise,
        seam=args.seam,model=args.model,variant=args.variant,
        condition=json.loads(args.condition) if args.condition else None,
        register=args.register)
    print(json.dumps({'report':report,'tiles':len(rows),'registered':args.register},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
