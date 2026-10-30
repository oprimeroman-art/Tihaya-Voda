"""Lazy delivery must preserve exact media bytes and keep offline exports self-contained."""
import base64,copy,hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'codex-scripts'))
from web_assets import externalize_payload,hydrate_payload
raw=b'<svg xmlns="http://www.w3.org/2000/svg" width="2" height="1"></svg>';encoded=base64.b64encode(raw).decode();uri='data:image/svg+xml;base64,'+encoded
source={'assets':{'one':{'mime':'image/svg+xml','data':encoded},'two':{'mime':'image/svg+xml','data':encoded}},'art':[uri]}
with tempfile.TemporaryDirectory() as folder:
 lazy,manifest=externalize_payload(source,Path(folder));assert manifest['assetCount']==1 and manifest['references']==3
 assert source['art'][0]==uri and hydrate_payload(lazy,Path(folder))==source
 target=Path(folder)/next(iter(manifest['files']));target.write_bytes(b'broken')
 try:hydrate_payload(lazy,Path(folder));raise AssertionError('Corrupted resource accepted')
 except ValueError:pass
p=ROOT/'_site/index.html';manifest=json.loads((p.parent/'web-assets.json').read_text());assert len(p.read_bytes())<2_500_000
for url,entry in manifest['files'].items():assert hashlib.sha256((p.parent/url).read_bytes()).hexdigest()==entry['sha256']
for rel in ['game/index.html','game-editor/index.html']:
 game,_=json.JSONDecoder().raw_decode((ROOT/rel).read_text().split('window.BUILT_GAME=',1)[1]);assert all(a.get('data') for a in game['panoramas'].values()),rel
print('PASS byte-identical deduplicated web assets, corruption detection and embedded offline panoramas')
