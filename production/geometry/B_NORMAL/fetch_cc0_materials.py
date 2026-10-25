#!/usr/bin/env python3
"""Fetch pinned Poly Haven CC0 photoscanned albedo maps into this repository.

The downloaded CC0 JPGs are committed by GitHub Actions alongside the candidate.
No third-party URLs are needed at game runtime. Only pinned URLs/checksums are used.
"""
from pathlib import Path
import hashlib
import urllib.request
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'art/materials/cc0'
TEXTURES={
    'rusty_painted_metal':('https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/rusty_painted_metal/rusty_painted_metal_diff_1k.jpg','3846f5567b6e7985b275a6b3867a648f',471866),
    'concrete_floor':('https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/concrete_floor/concrete_floor_diff_1k.jpg','99b94da291a4f038fa6af93c3993cbec',927975),
    'wood_table':('https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/wood_table/wood_table_diff_1k.jpg','45af5766b300f7e940ee8984c5fabd4f',987969),
    'metal_plate':('https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/metal_plate/metal_plate_diff_1k.jpg','bd9daf4c04046ca392a38b8df955ed26',692234),
}
def good(data,md5,length):
    return len(data)==length and hashlib.md5(data).hexdigest()==md5

def fetch_all():
    DEST.mkdir(parents=True,exist_ok=True)
    for name,(url,md5,size) in TEXTURES.items():
        dest=DEST/(name+'_diff_1k.jpg')
        if dest.exists() and good(dest.read_bytes(),md5,size):
            print('VALID:',name,md5)
            continue
        last=None
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'Tihaya-Voda-Art/1.0 (Poly Haven CC0)'})
                payload=urllib.request.urlopen(req,timeout=40).read()
                if not good(payload,md5,size):
                    raise ValueError('Remote asset changed: size or md5 mismatch')
                dest.write_bytes(payload)
                print('DOWNLOADED:',name,len(payload))
                break
            except Exception as ex:
                last=ex
                if attempt<2:time.sleep(1+attempt)
        else:
            raise RuntimeError('Cannot download verified CC0 texture '+name) from last
if __name__=='__main__':fetch_all()
