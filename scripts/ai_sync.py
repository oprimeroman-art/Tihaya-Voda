#!/usr/bin/env python3
'Copy canonical agent skills into ignored provider-specific directories.'
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / '.ai'
for path in sorted((SOURCE / 'skills').glob('*/SKILL.md')):
    for vendor in ('.agents', '.claude'):
        target = ROOT / vendor / 'skills' / path.parent.name / 'SKILL.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
claude_rule = ROOT / '.claude/rules/by-gagarin.md'
claude_rule.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(SOURCE / 'rules/CORE.md', claude_rule)
cursor = ROOT / '.cursor/rules/by-gagarin.mdc'
cursor.parent.mkdir(parents=True, exist_ok=True)
cursor.write_text('---\ndescription: Common byGagarin project rules\nalwaysApply: true\n---\n\n' +
                  (SOURCE / 'rules/CORE.md').read_text(encoding='utf-8'), encoding='utf-8')
claude_root = ROOT / 'CLAUDE.md'
if not claude_root.exists():
    claude_root.write_text('Read AGENTS.md and docs/README.md. Canonical agent rules are in .ai/.\n', encoding='utf-8')
print('Agent skills synced; canonical source: .ai/')
