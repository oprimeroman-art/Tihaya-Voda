import base64,hashlib,json
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'codex-scripts'))
from web_assets import hydrate_payload
ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'production/quiet-scene-art.json').read_text())
project=json.loads((ROOT/'game-project/project.json').read_text());story=project['story']['adventure']
assert json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text())==story
for variant,entry in manifest['variants'].items():
    file=ROOT/'game-project'/entry['file'];im=Image.open(file)
    assert im.width==im.height*2 and im.size==(entry['width'],entry['height'])
    assert hashlib.sha256(file.read_bytes()).hexdigest()==entry['sha256']
    assert hashlib.sha256((ROOT/'game-project'/entry['baseFile']).read_bytes()).hexdigest()==entry['baseSha256'],'normal panorama overwritten'
    assert next(r for r in story['rooms'] if variant in r['variants'])['variantAssets'][variant]==entry['assetId']
for relative in ['game/index.html','game-editor/index.html','_site/index.html']:
    html=(ROOT/relative).read_text();game,_=json.JSONDecoder().raw_decode(html.split('window.BUILT_GAME=',1)[1]);game=hydrate_payload(game,(ROOT/relative).parent)
    for variant,entry in manifest['variants'].items():
        assert hashlib.sha256(base64.b64decode(game['assets'][entry['assetId']]['data'])).hexdigest()==entry['sha256'],relative
        meta=next(r for r in game['story']['adventure']['rooms'] if variant in r['variants'])
        assert meta['variantAssets'][variant]==entry['assetId']
    event=next(e for e in game['story']['adventure']['events'] if e['id']=='E100')
    assert event['room']=='C' and event['visualCue']=={'mode':'panorama','panoramaVariant':'C_DAYLIGHT','duration':3}
print('PASS five authored quiet panoramas embedded in game/editor/Pages; default panoramas preserved; real event bindings')
