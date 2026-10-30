#!/usr/bin/env python3
"""Embed the supplied alpha voice MP3s; never synthesize or replace old media."""
import argparse, base64, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'window.BUILT_GAME='

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--pages', action='store_true')
    args = ap.parse_args()
    manifest = json.loads((ROOT/'game-project/audio/voice-alpha/manifest.json').read_text())
    project = json.loads((ROOT/'game-project/project.json').read_text())
    story = json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text())
    assert story == project['story']['adventure']
    entries = {a['id']: a for a in project['audio']}
    voices = {}
    for id, track in manifest['tracks'].items():
        entry = entries[id]
        assert entry['file'] == track['file'] and entry['mime'] == 'audio/mpeg'
        path = ROOT/'game-project'/entry['file']
        assert path.resolve().is_relative_to((ROOT/'game-project/audio/voice-alpha').resolve())
        blob = path.read_bytes()
        assert hashlib.sha256(blob).hexdigest() == track['sha256'], id
        voices[id] = {'mime': 'audio/mpeg', 'data': base64.b64encode(blob).decode('ascii')}
    paths = ['_site/index.html'] if args.pages else ['game/index.html', 'game-editor/index.html']
    for relative in paths:
        path = ROOT/relative
        html = path.read_text()
        assert html.count(MARKER) == 1
        start = html.index(MARKER)+len(MARKER)
        game, consumed = json.JSONDecoder().raw_decode(html[start:])
        if args.check:
            if args.pages:
                from web_assets import hydrate_payload
                game=hydrate_payload(game,path.parent)
            assert game['story']['adventure']['voiceAssets'] == story['voiceAssets']
            assert all(game['audio'].get(id) == asset for id, asset in voices.items()), relative
            assert 'class VoiceQueue' in html and 'voice:id=>' in html, relative
        else:
            game['story']['adventure'] = story
            game['audio'].update(voices)
            path.write_text(html[:start]+json.dumps(game,ensure_ascii=False,separators=(',',':'))+html[start+consumed:])
        print(('CHECKED' if args.check else 'EMBEDDED'), len(voices), 'voice recordings:', relative)

if __name__ == '__main__':
    main()
