---
name: documentation
description: Maintain indexed, focused source-linked project documentation with every relevant feature change.
---
# Documentation update

- Open docs/INDEX.md and call python3 scripts/ai_docs.py related PATH for modified sources.
- Maintain a short topic document rather than appending endless historical reports.
- New markdown docs should include YAML frontmatter with title, summary and JSON code_paths: ["studio/**"].
- Update only docs affected by the change; preserve all original reports and scenario texts.
- Run python3 scripts/ai_docs.py index, then python3 scripts/ai_docs.py check.
