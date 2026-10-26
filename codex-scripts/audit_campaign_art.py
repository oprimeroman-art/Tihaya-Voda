#!/usr/bin/env python3
"""Whole-campaign art inventory. A fallback panorama is never called a finished variant."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
story=json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text())
project=json.loads((ROOT/'game-project/project.json').read_text())
props=story.get('illustratedProps',{});images=props.get('image',{})
rooms={r['id']:r for r in project['rooms']};assets={a['id']:a for a in project['assets']}
rows=[]
for r in story['rooms']:
 for variant in r['variants']:
  aid=r.get('variantAssets',{}).get(variant)
  file=assets.get(aid,{}).get('file') if aid else rooms[r['id']]['file'] if variant==r['default_variant'] else None
  ready=bool(file and (ROOT/'game-project'/file).is_file())
  rows.append({'room':r['id'],'variant':variant,'file':file,'status':'file_present_visual_qa_required' if ready else 'distinct_art_missing_uses_base_fallback'})
produced={fx['item'] for a in story['actions'] for fx in a.get('effects',[]) if 'item' in fx}
assert produced=={i['id'] for i in story['items']},'Item catalog does not cover actual rewards'
report={'scope':'all 12 chapters, 16 rooms, declared variants, inventory, documents and endings','variants':rows,
'inventory':[{'id':i['id'],'art_present':props.get('item',{}).get(i['id']) in images} for i in story['items']],
'documents':[{'id':d['id'],'readable_text':bool(d['text']),'illustration':props.get('document',{}).get(d['id']) in images} for d in story['documents']],
'endings':[{'id':mode,'art_present':props.get('ending',{}).get(mode) in images} for mode in story['endings']],
'limitations':['File presence does not establish correct panorama projection, matching hotspot placement or visual quality.','Automated routes do not establish human pacing or artistic completion.']}
(ROOT/'production/campaign_art_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Declared variants:',len(rows),'without separate art:',sum(r['status'].startswith('distinct') for r in rows))
print('Inventory art:',sum(r['art_present'] for r in report['inventory']),'/',len(report['inventory']))
print('Ending art:',sum(r['art_present'] for r in report['endings']),'/',len(report['endings']))
