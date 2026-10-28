"""Validate supplied recordings against canonical IDs, text and original media."""
import hashlib,json,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
story=json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text())
project=json.loads((ROOT/'game-project/project.json').read_text())
manifest=json.loads((ROOT/'game-project/audio/voice-alpha/manifest.json').read_text())
expected={f'DLG_{i:03}' for i in range(1,48)}|{f'A{i:02}' for i in range(1,7)}
assert set(manifest['tracks'])==set(story['voiceAssets'])==expected
assert project['story']['adventure']==story
lines={l['id']:l for l in story['dialogues']}
audio={a['id']:a for a in project['audio']}
for id,track in manifest['tracks'].items():
    assert story['voiceAssets'][id]==id
    assert track['textSha256']==hashlib.sha256(lines[id]['text'].encode()).hexdigest(),id
    assert track['speaker']==lines[id]['speaker']
    path=ROOT/'game-project'/audio[id]['file']
    assert audio[id]['file']==track['file'] and audio[id]['mime']=='audio/mpeg'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==track['sha256'],id
    if shutil.which('ffprobe'):
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))
        assert duration>0 and abs(duration-track['duration'])<.01,id
used={l['id'] for e in story['events'] for l in e.get('lines',[])}
for action in story['actions']:
    for option in action.get('options',[]):
        used.update(fx['dialogue'] for fx in option.get('effects',[]) if fx.get('dialogue'))
for m in story['media']:
    if m['id'].startswith('A'):
        assert m['assetId']==m['id'];used.add(m['id'])
    cues=m.get('voiceCues',[])
    if cues:
        assert {c['id'] for c in cues}=={l['id'] for l in m['transcript']}
        assert all(0<=c['at']<m['duration'] for c in cues)
        assert [c['at'] for c in cues]==sorted(c['at'] for c in cues)
        used.update(c['id'] for c in cues)
        if shutil.which('ffprobe'):
            video=next(v for v in project['videos'] if v['id']==m['id'])
            streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type','-of','json',str(ROOT/'game-project'/video['file'])]))['streams']
            assert not any(s['codec_type']=='audio' for s in streams),'authored video audio requires reviewing additional voice: '+m['id']
for e in story['endings'].values():used.update(e.get('extraLines',[]))
assert used==expected,expected-used
original=json.loads((ROOT/'reports/voice-original-media-sha256.json').read_text())
assert len(original)==29
for name,sha in original.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
assert len(list((ROOT/'game-project/audio/voice-alpha').glob('*.mp3')))==53
print('PASS 47 dialogue MP3 + 6 archive MP3, canonical ID/text mapping, real cue destinations, 29 original media unchanged')
