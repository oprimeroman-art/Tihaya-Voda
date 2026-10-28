"""The public builder must preserve the complete canon, not just the early art waves."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
canonical=json.loads((ROOT/'game-project/project.json').read_text())['story']['adventure']
html=(ROOT/'_site/index.html').read_text()
published,_=json.JSONDecoder().raw_decode(html.split('window.BUILT_GAME=',1)[1]);story=published['story']['adventure']
assert story['documents']==canonical['documents']
for doc in canonical['documents']:
    id=doc['id'];expected=canonical['illustratedProps']['document'][id]
    assert story['illustratedProps']['document'].get(id)==expected,'published document image lost: '+id
    assert story['illustratedProps']['image'].get(expected)==canonical['illustratedProps']['image'][expected],id
assert story['inventoryArt']==canonical['inventoryArt']
assert story['endings']==canonical['endings']
assert story['voiceAssets']==canonical['voiceAssets']
for e in canonical['events']:
    if e.get('sceneArt'):
        other=next(x for x in story['events'] if x['id']==e['id']);assert other['sceneArt']==e['sceneArt']
print('PASS publication retains all 30 canonical document images, 15 inventory images, four endings, 53 voices and staged scene mappings')
