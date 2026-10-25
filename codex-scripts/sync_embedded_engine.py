#!/usr/bin/env python3
"""Keep embedded adventure runtime in the shipped offline HTML files in sync.

Run from any directory:
    python codex-scripts/sync_embedded_engine.py --check
    python codex-scripts/sync_embedded_engine.py

This updates the existing files in place; no new game copies or ZIP releases.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "studio/source/adventure-core.js"
OUTPUTS = (ROOT / "game/index.html", ROOT / "game-editor/index.html")
START = "/* Declarative adventure extension for Panorama Studio. No game-specific IDs or eval. */"
END = "/* UI shared by the editor preview and the compiled offline runtime. */"


def synchronize(html: str, source: str) -> str:
    if source.count(START) != 1 or source.count(END) != 0:
        raise ValueError("Unexpected adventure core source markers")
    if html.count(START) != 1 or html.count(END) != 1:
        raise ValueError("Expected exactly one adventure core in shipped HTML")
    a = html.index(START)
    b = html.index(END, a)
    return html[:a] + source.rstrip() + "\n\n" + html[b:]


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--check"):
        print("Usage: sync_embedded_engine.py [--check]", file=sys.stderr)
        return 2
    check = "--check" in sys.argv
    source = SOURCE.read_text(encoding="utf-8-sig")
    stale = []
    for path in OUTPUTS:
        old = path.read_text(encoding="utf-8-sig")
        updated = synchronize(old, source)
        if updated == old:
            print(f"OK: {path.relative_to(ROOT)}")
        elif check:
            stale.append(str(path.relative_to(ROOT)))
            print(f"STALE: {path.relative_to(ROOT)}")
        else:
            path.write_text(updated, encoding="utf-8")
            print(f"UPDATED: {path.relative_to(ROOT)}")
    if stale:
        print("Run: python codex-scripts/sync_embedded_engine.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
