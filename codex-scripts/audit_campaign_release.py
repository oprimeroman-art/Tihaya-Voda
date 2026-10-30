#!/usr/bin/env python3
"""Conservative whole-campaign asset and export audit; never promotes release ready."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'game-project/project.json').read_text())['story']['adventure']
items=[i['id'] for i in d['items'] if not d.get('inventoryArt',{}).get(i['id'])]
docs=[v['id'] for v in d['documents'] if v['id'] not in d.get('illustratedProps',{}).get('document',{})]
variants=[]
for r in d['rooms']:
 for v in r['variants']:
  if v!=r['default_variant'] and v not in r.get('variantAssets',{}) and not(v.startswith('P_END_') and d['endings'].get(v[-1],{}).get('image')):variants.append({'room':r['id'],'variant':v})
signs=[]
for room in json.loads((ROOT/'game-project/project.json').read_text())['rooms']:
 for o in room.get('objects',[]):
  if any(str(x).startswith('sign_') for x in o.get('states',[])):signs.append({'room':room['id'],'object':o['id']})
audit={'chapters':len(d['quests']),'rooms':len(d['rooms']),'actions':len(d['actions']),
 'inventoryArt':len(d.get('inventoryArt',{})),'missingInventoryArt':items,'missingDocumentArt':docs,
 'endingImages':sum(bool(e.get('image'))for e in d['endings'].values()),
 'variantsWithoutAuthoredPanorama':variants,'objectsStillUsingSignArt':signs,
 'technicalInteractionArtPlayerMode':'compact-screen-hotspots; sign textures retained only in editable project',
 'releaseReady':False,'reason':'Unmatched room variants, provisional hotspot placement and human pacing review remain; automated routes do not certify final artistic quality.'}
(ROOT/'reports/CAMPAIGN_RELEASE_GAPS.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k not in ['objectsStillUsingSignArt','variantsWithoutAuthoredPanorama']}));print('Unmatched variants:',len(variants),'sign-art objects:',len(signs))
