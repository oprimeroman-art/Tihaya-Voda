"""Content-addressed lazy web assets; offline exports retain embedded media."""
import base64,hashlib,json,re
from pathlib import Path
MIMES={'image/webp':'webp','image/png':'png','image/jpeg':'jpg','image/jpg':'jpg','image/svg+xml':'svg','image/gif':'gif','audio/mpeg':'mp3','audio/ogg':'ogg','audio/wav':'wav','audio/x-wav':'wav','video/mp4':'mp4','video/webm':'webm','audio/webm':'webm'}
URL=re.compile(r'^web-assets/([a-f0-9]{64})[.]([a-z0-9]+)$')
DATA=re.compile(r'^data:([^;,]+);base64,(.*)$',re.S)
def externalize_payload(payload,dest):
 dest=Path(dest);folder=dest/'web-assets';folder.mkdir(parents=True,exist_ok=True);files={};references=0
 def put(raw,mime):
  nonlocal references
  if mime not in MIMES:raise ValueError('Unsupported web asset MIME '+mime)
  sha=hashlib.sha256(raw).hexdigest();url='web-assets/'+sha+'.'+MIMES[mime];references+=1
  if url not in files:
   (dest/url).write_bytes(raw);files[url]={'sha256':sha,'bytes':len(raw),'mime':mime}
  return url
 def walk(value):
  if isinstance(value,dict):
   if isinstance(value.get('data'),str) and value.get('mime') in MIMES:
    url=put(base64.b64decode(value['data'],validate=True),value['mime']);return {**{k:walk(v) for k,v in value.items() if k!='data'},'url':url}
   return {k:walk(v)for k,v in value.items()}
  if isinstance(value,list):return [walk(v)for v in value]
  if isinstance(value,str):
   match=DATA.fullmatch(value)
   if match:return put(base64.b64decode(match[2],validate=True),match[1])
  return value
 result=walk(payload);manifest={'version':1,'assetCount':len(files),'references':references,'assetBytes':sum(f['bytes']for f in files.values()),'files':files};(dest/'web-assets.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');return result,manifest

def hydrate_payload(payload,base):
 """Read exact on-disk bytes for canonical checks, validating every lazy reference."""
 base=Path(base);manifest_path=base/'web-assets.json'
 if not manifest_path.exists():return payload
 manifest=json.loads(manifest_path.read_text());files=manifest['files'];cache={}
 def raw(url):
  match=URL.fullmatch(url)
  if not match or url not in files:raise ValueError('Unregistered web asset '+url)
  if url not in cache:
   data=(base/url).read_bytes()
   if len(data)!=files[url]['bytes'] or hashlib.sha256(data).hexdigest()!=match[1]:raise ValueError('Corrupt web asset '+url)
   cache[url]=base64.b64encode(data).decode('ascii')
  return cache[url]
 def walk(value):
  if isinstance(value,dict):
   if value.get('mime') in MIMES and isinstance(value.get('url'),str) and URL.fullmatch(value['url']):return {**{k:walk(v)for k,v in value.items()if k!='url'},'data':raw(value['url'])}
   return {k:walk(v)for k,v in value.items()}
  if isinstance(value,list):return [walk(v)for v in value]
  if isinstance(value,str) and URL.fullmatch(value):return 'data:'+files[value]['mime']+';base64,'+raw(value)
  return value
 return walk(payload)
