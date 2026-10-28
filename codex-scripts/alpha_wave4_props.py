#!/usr/bin/env python3
"""Add existing illustrated canonical story props to the published game.

No independent scene or new story event; illustrations are supplementary to
canonical UI text and appear only via authored action / room variant gating.
"""
from __future__ import annotations
import base64
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'site-assets/story-props-wave2'
EXPECTED = 'e0dfff60462b7188f3127ae7a29d999e1d37489184eb823dea44bf3fa9d4ddbc'
PARTS = 71
PROP_ACTIONS = {
    'read_D01': 'D01_note',
    'cabinet_message': 'case_12',
    'take_PUNCHCARD_RU': 'punchcard_ru',
    'watch_V01': 'vhs_01',
}
DOCUMENTS = {'D01': 'D01_note'}
GHOST_VARIANTS = {
    'B:B_GHOST_MIRROR': ['ghost_b1'],
    'B:B_TWO_GHOSTS': ['ghost_b1', 'ghost_b2'],
    'C:C_MIRROR_LIGHT': ['ghost_red1'],
    'H:H_ANNA_GLASS': ['ghost_red2'],
}
EXPECTED_ARTS = set(PROP_ACTIONS.values()) | {a for b in GHOST_VARIANTS.values() for a in b}


def collect():
    chunks = sorted(DIR.glob('part_*.b64'))
    if len(chunks) != PARTS:
        raise ValueError(f'Story props incomplete: {len(chunks)}/{PARTS}')
    if any(x.name != f'part_{i:03}.b64' for i, x in enumerate(chunks)):
        raise ValueError('Noncontiguous story art package')
    encoded = ''.join(p.read_text('ascii').strip() for p in chunks)
    raw = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(raw).hexdigest() != EXPECTED:
        raise ValueError('Story art bundle checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        files = {f.name: archive.extractfile(f).read() for f in archive if f.isfile()}
    if set(files) != {a+'.webp' for a in EXPECTED_ARTS} | {'manifest.json'}:
        raise ValueError('Unexpected prop file inventory')
    manifest = json.loads(files['manifest.json'])
    if set(manifest['assets']) != EXPECTED_ARTS:
        raise ValueError('Manifest inventory mismatch')
    for name in EXPECTED_ARTS:
        data = files[name+'.webp']
        if not (data[:4] == b'RIFF' and data[8:12] == b'WEBP'):
            raise ValueError('Invalid illustration '+name)
        if hashlib.sha256(data).hexdigest() != manifest['assets'][name]['sha256']:
            raise ValueError('Wrong artwork bytes '+name)
    return files


def apply_wave4_props(payload, root=ROOT):
    art = collect()
    adv = payload['story']['adventure']
    actions = {a['id']: a for a in adv['actions']}
    docs = {d['id']: d for d in adv['documents']}
    variants = {r['id']: set(r['variants']) for r in adv['rooms']}
    for action, image in PROP_ACTIONS.items():
        if action not in actions: raise ValueError('Missing canonical prop action: '+action)
        if image == 'D01_note' and (actions[action].get('document') != 'D01'):
            raise ValueError('D01 art wrong document')
        if image == 'vhs_01' and actions[action].get('media') != 'V01':
            raise ValueError('V01 art wrong media')
    for name in DOCUMENTS:
        if name not in docs: raise ValueError('Missing document '+name)
    for key in GHOST_VARIANTS:
        rid, variant = key.split(':',1)
        if variant not in variants[rid]: raise ValueError('Unknown canon ghost scene '+key)
    art_images = {name:'data:image/webp;base64,'+base64.b64encode(art[name+'.webp']).decode('ascii')
                  for name in EXPECTED_ARTS}
    # Publishing an early art wave must not erase later canonical document art.
    props = adv.setdefault('illustratedProps', {})
    for key, values in {'image': art_images, 'action': PROP_ACTIONS,
                        'document': DOCUMENTS, 'haunt': GHOST_VARIANTS}.items():
        props.setdefault(key, {}).update(values)
    return {'story_props': len(EXPECTED_ARTS)}


def decorate_game_ui(html):
    """Patch only existing adventure UI template, retaining its game logic.

    All data lives in BUILT_GAME and is offline; no network fetches. Standard
    text and button behavior remains unchanged. Fail loudly if Studio changes.
    """
    if ' showArt(parent,src,' in html:
        return html  # Shared canonical UI now renders its own illustrated props.
    marker = 'class UI{\n constructor(data,hooks={})'
    assert html.count(marker) == 1, 'Adventure UI template changed'
    helpers = '''class UI{\n artData(){return this.data.illustratedProps||null;}\n showArt(box,id){
  const p=this.artData();const key=p?.image?.[id];if(!key)return;
  const wrapper=el('figure',undefined,'ga-art-figure');
  const img=el('img');img.src=key;img.alt='Сюжетная иллюстрация';img.loading='eager';
  img.style.cssText='display:block;max-width:min(100%,390px);max-height:45vh;object-fit:contain;margin:0 auto;';
  const caption=el('figcaption','Художественное изображение · текст ниже — из сценария','ga-muted');
  caption.style.cssText='font:12px system-ui,sans-serif;text-align:center;margin:7px 0 12px';
  wrapper.style.cssText='margin:12px auto 18px;max-width:440px;text-align:center;';
  wrapper.append(img,caption);box.append(wrapper);
 }\n updateArtHaunt(){
  if(!this.ghostFrame){this.ghostFrame=el('div',undefined,'ga-illustrated-haunt');
   this.ghostFrame.style.cssText='pointer-events:none;position:absolute;inset:0;display:flex;justify-content:center;align-items:center;overflow:hidden;z-index:1;';
   this.root.insertBefore(this.ghostFrame,this.left);}
  const st=this.engine.state,r=st.room,variant=st.variants[r];
  const p=this.artData();const ids=p?.haunt?.[r+':'+variant]||[];
  const signature=r+':'+variant+':'+ids.join(',');if(this._hauntSignature===signature)return;
  this._hauntSignature=signature;this.ghostFrame.replaceChildren();
  for(let i=0;i<ids.length;i++){const src=p.image[ids[i]];if(!src)continue;
   const img=el('img');img.alt='';img.src=src;
   img.style.cssText='position:absolute;max-width:35vw;max-height:75vh;object-fit:contain;opacity:.40;filter:grayscale(.25);left:'+(ids.length===1?'45%':(i?'60%':'27%'))+';top:48%;transform:translate(-50%,-50%);';
   this.ghostFrame.append(img);}
 }\n constructor(data,hooks={})'''
    html = html.replace(marker, helpers, 1)
    variant = re.search(r"this\.variant\.textContent=authored\?[^;]+;",html)
    if not variant: raise ValueError('Variant UI layout changed')
    html = html[:variant.end()] + 'this.updateArtHaunt();' + html[variant.end():]
    needle = 'const b=this.panel(a.label);this.currentAction=id;'
    if html.count(needle) != 1: raise ValueError('Action dialog opening changed')
    html = html.replace(needle, needle + 'const art=this.artData()?.action?.[id];if(art&&!this.data.illustratedProps?.document?.[a.document])this.showArt(b,art);',1)
    # The media action opens a new dialog; show artwork there as well.
    needle = 'b.append(warning);let t=0,started=false,frame=0,finished=false;'
    if html.count(needle)!=1:raise ValueError('Media scene layout changed')
    html=html.replace(needle,"b.append(warning);const ar=this.artData()?.action?.['watch_'+m.id];if(ar)this.showArt(b,ar);let t=0,started=false,frame=0,finished=false;",1)
    # Re-reading the authentic document from journal retains its illustration.
    needle="const box=this.panel(d.title);this.documentView(box,d);"
    if html.count(needle)!=1:raise ValueError('Journal page reader changed')
    # documentView owns the inline illustration; avoid a duplicate overlay.
    if html.count('updateArtHaunt()') != 2:raise ValueError('Haunting scene hook is absent')
    return html
