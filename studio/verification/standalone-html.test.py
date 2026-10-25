"""Verify every inline script in both offline HTML entry points parses with Node."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
for rel in ('game/index.html', 'game-editor/index.html'):
    html = (ROOT / rel).read_text(encoding='utf-8')
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script\s*>', html, flags=re.DOTALL | re.IGNORECASE)
    if len(scripts) < 5:
        raise AssertionError(f'{rel}: missing inline scripts')
    for number, script in enumerate(scripts):
        result = subprocess.run(['node', '--check'], input=script, text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(f'{rel}: script #{number} syntax error:\n{result.stderr[:1500]}')
    print(f'PASS: {rel} ({len(scripts)} parsed inline scripts)')
