#!/usr/bin/env python3
"""Embed an opt-in B_NORMAL playtest in the EXISTING standalone game/index.html.

Normal gameplay and saves are unchanged. When the user opens game/index.html
with ?qa-kitchen=1, use the same compiled offline engine to display the newest
candidate and its real projected hotspot quads. QA saves have a distinct key.
This deliberately does not approve/replace game-project/rooms/B/original.png.
"""
from __future__ import annotations
import argparse, base64, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game/index.html"
PANO = ROOT / "art/candidates/B_B_NORMAL_360_geometry.webp"
HOTSPOTS = ROOT / "production/qa/B_NORMAL_hotspots_candidate.json"
START = "/* KITCHEN_QA_PREVIEW_BEGIN */"
END = "/* KITCHEN_QA_PREVIEW_END */"
SCRIPT = re.compile(r'<script>\s*/\* KITCHEN_QA_PREVIEW_BEGIN \*/.*?'
                    r'/\* KITCHEN_QA_PREVIEW_END \*/\s*</script>\s*', re.S)
BOUNDARY = "<script>/* Gagarin Panorama Engine 2.1"


def normalized_candidate_quads(data: dict) -> dict:
    if data.get('room') != 'B' or data.get('variant') != 'B_NORMAL':
        raise ValueError('Not a B_NORMAL candidate')
    out = {}
    for item in data['objects']:
        if item['status'] != 'needs_manual_in_game_approval':
            raise ValueError('Cannot preview action with missing prop: ' + item['action_id'])
        quads = item['candidate_quads']
        if len(quads) == 1:
            out[item['action_id']] = quads[0]
        elif len(quads) == 2 and item.get('seam_split'):
            # Native objectHit() unwraps a short circular edge crossing u=1 -> 0.
            left, right = sorted(quads, key=lambda q: q[0]['u'], reverse=True)
            if left[1]['u'] != 1 or right[0]['u'] != 0:
                raise ValueError('Expected split right/left meridian rectangles')
            if left[0]['v'] != right[0]['v'] or left[2]['v'] != right[2]['v']:
                raise ValueError('Seam split has disjoint vertical bounds')
            u1, u2 = left[0]['u'], right[1]['u']
            if u1 <= .5 or u2 >= .5:
                raise ValueError('Discontinuous longitude geometry')
            v1, v2 = left[0]['v'], left[2]['v']
            out[item['action_id']] = [{'u':u1,'v':v1},{'u':u2,'v':v1},
                                      {'u':u2,'v':v2},{'u':u1,'v':v2}]
        else:
            raise ValueError('More than two hotspot polygons require separate objects')
        quad=out[item['action_id']]
        if len(quad)!=4 or any(not 0<=p[x]<=1 for p in quad for x in ('u','v')):
            raise ValueError('Illegal game hotspot quad')
    if len(out)!=11:
        raise ValueError(f'Expected 11 verified hotspot candidates, got {len(out)}')
    return out


def snippet() -> str:
    from PIL import Image
    with Image.open(PANO) as im:
        if im.size != (2048, 1024):
            raise ValueError('Unapproved panorama dimensions: '+str(im.size))
    raw = PANO.read_bytes()
    if not raw.startswith(b'RIFF') or raw[8:12]!=b'WEBP':
        raise ValueError('Candidate is not a real WebP file')
    source = json.loads(HOTSPOTS.read_text(encoding='utf-8'))
    coords = normalized_candidate_quads(source)
    image_b64 = base64.b64encode(raw).decode('ascii')
    data = json.dumps(coords, ensure_ascii=True, separators=(',', ':'))
    # Bare minimal independent script. It runs after window.BUILT_GAME assignment
    # and before the original offline game engine is initialized.
    javascript = """
(function(){
  'use strict';
  // Only explicitly opt-in playtest mode. Never replace the public/default art.
  if (new URLSearchParams(window.location.search).get('qa-kitchen') !== '1') return;
  const game=window.BUILT_GAME;
  if (!game || !game.panoramas?.B) throw Error('Kitchen QA: missing B panorama');
  const room=game.rooms.find(x=>x.id==='B');
  if (!room || room.objects.length<11) throw Error('Kitchen QA: missing room actions');
  const quads=__HOTSPOTS__;
  let updates=0;
  for (const o of room.objects) {
    const action=o.tourKey?.startsWith('ga:') ? o.tourKey.slice(3) : '';
    if (!Object.prototype.hasOwnProperty.call(quads,action)) continue;
    o.corners=quads[action].map(p=>({u:p.u,v:p.v}));
    updates++;
  }
  if (updates!==11) throw Error('Kitchen QA: expected 11 actions, found '+updates);
  game.panoramas.B={mime:'image/webp',data:'__PANO__'};
  // A different game fingerprint makes QA saves unable to overwrite production.
  game.name += ' · Kitchen QA';
  document.addEventListener('DOMContentLoaded',()=>{
    const banner=document.createElement('aside');
    banner.id='kitchen-qa-banner';
    banner.textContent='АРТ-ТЕСТ B_NORMAL · черновая 360° кухня · сохранения изолированы';
    Object.assign(banner.style,{position:'fixed',left:'50%',bottom:'10px',
      transform:'translateX(-50%)',padding:'7px 11px',
      background:'#0b0d10e8',border:'1px solid #c63439',
      borderRadius:'6px',font:'12px system-ui,sans-serif',color:'#fff',
      zIndex:'3000',pointerEvents:'none',maxWidth:'92vw',textAlign:'center'});
    document.body.appendChild(banner);
  });
})();
"""
    javascript=javascript.replace('__HOTSPOTS__',data).replace('__PANO__',image_b64)
    if "</script" in javascript.lower():
        raise ValueError('Unsafe script terminator in generated QA injection')
    return "<script>\n"+START+"\n"+javascript+"\n"+END+"\n</script>\n"


def patched(html: str) -> str:
    if html.count(BOUNDARY)!=1 or html.count('window.BUILT_GAME=') != 1:
        raise ValueError('Unsupported existing game engine / BUILT_GAME payload')
    html = SCRIPT.sub('', html)
    return html.replace(BOUNDARY, snippet()+BOUNDARY, 1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='verify the in-place offline HTML already has this exact preview')
    args=parser.parse_args()
    original=GAME.read_text(encoding='utf-8')
    expected=patched(original)
    if args.check:
        if expected!=original:
            raise SystemExit('FAIL: embedded kitchen candidate preview is stale')
        print('PASS: kitchen playtest is embedded exactly once; production data intact')
    else:
        GAME.write_text(expected,encoding='utf-8')
        print(f'Updated existing {GAME}: preview enabled only with ?qa-kitchen=1; 11 QA hotspots')


if __name__=='__main__':main()
