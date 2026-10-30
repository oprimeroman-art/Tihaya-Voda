"""Every authored room/state must be a decodable image, including the final chamber."""
import base64,hashlib,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'codex-scripts'))
from web_assets import hydrate_payload
manifest=json.loads((ROOT/'production/final-scene-art.json').read_text())['assets']
for key,entry in manifest.items():
 p=ROOT/'game-project'/entry['file'];raw=p.read_bytes();assert raw,key+' is empty'
 assert hashlib.sha256(raw).hexdigest()==entry['sha256'],key
 with Image.open(p) as im:assert im.size==(entry['width'],entry['height']);im.verify()
for rel in ['game/index.html','game-editor/index.html','_site/index.html']:
 p=ROOT/rel;game,_=json.JSONDecoder().raw_decode(p.read_text().split('window.BUILT_GAME=',1)[1]);game=hydrate_payload(game,p.parent)
 for key,entry in manifest.items():assert hashlib.sha256(base64.b64decode(game['assets'][entry['assetId']]['data'])).hexdigest()==entry['sha256'],(rel,key)
 assert game['story']['adventure']['panoramaStaging']['N_CLOCK']['kind']=='clock'
print('PASS all 32 authored panoramas decode and match in game, editor and lazy web build')
