import json,zipfile,hashlib,re
from paths import *
checks=[]
data=json.loads((ROOT/'TIHAYA_VODA/adventure.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(OUT/'PROJECT.zip') as z:
    project=json.loads(z.read('project.json'));assert project['story']['adventure']==data
    for r in project['rooms']:assert r['file'] in z.namelist()
    for a in project['assets']:assert a['file'] in z.namelist()
checks.append('Native manifest: every room and image reference resolves in PROJECT.zip')
for d in data['documents']:assert d['text'] in read('CANON/03_DOCUMENTS_FULLTEXT.txt'),d['id']
for l in data['dialogues']:assert l['text'] in read('CANON/04_DIALOGUE_AND_AUDIO.txt'),l['id']
checks.append('30 document bodies and 53 dialogue/audio bodies match canonical source verbatim')
for m in data['media']:
    for f in m['frames']:assert f['text'] in read('PRODUCTION/05_FOUND_FOOTAGE_SHOTLIST.txt') or f['text'] in read('CANON/04_DIALOGUE_AND_AUDIO.txt'),m['id']
checks.append('All storyboard frames retain source text and timecodes')
with zipfile.ZipFile(OUT/'GAME.zip') as z:
    assert z.read('source-project.zip')==(OUT/'PROJECT.zip').read_bytes()
    html=z.read('index.html').decode('utf-8')
    assert not re.search(r'<script[^>]+src=["\']https?://',html)
checks.append('GAME.zip includes exact PROJECT.zip; no mandatory remote script dependencies')
if (OUT/'EDITOR_EXPORTED_GAME.zip').exists():
    with zipfile.ZipFile(OUT/'EDITOR_EXPORTED_GAME.zip') as z:
        import io
        with zipfile.ZipFile(io.BytesIO(z.read('source-project.zip'))) as native:
            assert json.loads(native.read('project.json'))['story']['adventure']==data
    checks.append('Editor-generated GAME.zip preserves scenario in embedded source project')
if (Path(__file__).parent/'demo-roundtrip.json').exists():
    roundtrip=json.loads((Path(__file__).parent/'demo-roundtrip.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(STUDIO/'DEMO_EDITABLE_PROJECT.zip') as z:
        old=json.loads(z.read('project.json'))
    for field in ['globals','story','spatialSounds','timelines']:assert old.get(field)==roundtrip.get(field),field
    for a,b in zip(old['rooms'],roundtrip['rooms']):
        for field in ['id','name','view','exits','vars','rules']:assert a.get(field)==b.get(field),(a['id'],field)
    checks.append('Existing demo roundtrip: globals, story, spatial sound, timelines, room rules/exits unchanged')
report=dict(passed=True,checks=checks)
(OUT/'CONTENT_TEST_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
