#!/usr/bin/env python3
"""Integrate existing authored document/prop art into canonical source and exports.

Never changes panoramas or media. The same adventure data is used by both players
and the editable project. Already-produced art is reused, never regenerated.
"""
import base64,json,sys,html,textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'codex-scripts'))
from alpha_wave4_props import apply_wave4_props
from alpha_wave5_medical import apply_medical_props
from alpha_wave6_stockroom import apply_stockroom_props
from alpha_wave7_puzzle_docs import apply_puzzle_docs
from alpha_wave8_late_docs import apply_late_docs
from alpha_wave9_document_props import apply_wave9

def main():
    path=ROOT/'game-project/project.json'
    project=json.loads(path.read_text())
    # The producer starts from the verified bundle; later waves attach their art.
    for producer in (apply_wave4_props,apply_medical_props,apply_stockroom_props,apply_puzzle_docs,apply_late_docs,apply_wave9):
        producer(project,ROOT)
    d=project['story']['adventure']
    art=d['illustratedProps']
    # Complete the existing archival-document art system with exact canonical text.
    directory=ROOT/'game-project/assets/documents';directory.mkdir(exist_ok=True)
    for doc in d['documents']:
        if doc['id'] in art['document']:continue
        lines=[]
        for paragraph in doc['text'].splitlines():
            lines.extend(textwrap.wrap(paragraph,72,replace_whitespace=False,drop_whitespace=False) or [''])
        height=max(980,230+len(lines)*30)
        text=''.join(f'<text x="78" y="{190+i*30}" font-size="21" fill="#283035">{html.escape(line)}</text>' for i,line in enumerate(lines))
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="1100" height="{height}" fill="#dcd7c8"/><rect x="26" y="26" width="1048" height="{height-52}" fill="none" stroke="#9a9588"/><path d="M66 136H1034" stroke="#5c696b"/><g font-family="monospace"><text x="78" y="92" font-size="24" fill="#596365">МАЯК-9 / АРХИВ / {doc["id"]}</text>{text}</g></svg>'
        file=directory/(doc['id']+'.svg');file.write_text(svg)
        key='canonical_'+doc['id'];art['image'][key]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode();art['document'][doc['id']]=key
    d['inventoryArt']={}
    for item in d['items']:
        image=ROOT/f'game-project/assets/items/{item["id"]}.webp'
        if image.exists():d['inventoryArt'][item['id']]='data:image/webp;base64,'+base64.b64encode(image.read_bytes()).decode('ascii')
    for item,key in {'VHS_V01':'vhs_01','PUNCHCARD_RU':'punchcard_ru'}.items():
        if key in art['image']:d['inventoryArt'].setdefault(item,art['image'][key])
    for mode in 'ABCD':
        image=ROOT/f'game-project/assets/endings/{mode}.webp'
        if image.exists():
            d['endings'][mode]['image']='data:image/webp;base64,'+base64.b64encode(image.read_bytes()).decode('ascii')
    for mode,eid in zip('ABCD',range(108,112)):
        next(e for e in d['events'] if e['id']==f'E{eid}')['ending']=mode
    for eid in ('E007',):
        next(e for e in d['events'] if e['id']==eid)['when']['max']=3
    for target,value in ((path,project),(ROOT/'studio/content/TIHAYA_VODA/adventure.json',d),(ROOT/'reports/adventure.json',d)):
        target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    for name in ('game/index.html','game-editor/index.html'):
        target=ROOT/name;s=target.read_text();mark='window.BUILT_GAME=';start=s.index(mark)+len(mark)
        payload,n=json.JSONDecoder().raw_decode(s[start:]);payload['story']['adventure']=d
        target.write_text(s[:start]+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+s[start+n:])
    print('Integrated',len(d['illustratedProps']['image']),'existing story illustrations and',sum('image'in e for e in d['endings'].values()),'ending images')
if __name__=='__main__':main()
