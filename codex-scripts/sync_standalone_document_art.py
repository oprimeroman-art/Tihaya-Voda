#!/usr/bin/env python3
"""Embed D27-D29 SVG data in the existing offline game HTML without rebuilding its runtime."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
MARKER = "window.BUILT_GAME="
TARGETS = (ROOT / "game/index.html", ROOT / "game-editor/index.html")
def patch_html(html: str) -> tuple[str, bool]:
    if html.count(MARKER) != 1:
        raise ValueError("Expected exactly one built-game payload in standalone HTML")
    start = html.index(MARKER) + len(MARKER)
    payload, consumed = json.JSONDecoder().raw_decode(html[start:])
    from alpha_wave9_document_props import apply_wave9
    result = apply_wave9(payload, ROOT)
    from alpha_wave10_kitchen_state import apply_wave10
    result.update(apply_wave10(payload, ROOT))
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    updated = html[:start] + encoded + html[start + consumed:]
    return updated, bool(result)
def main() -> int:
    sys.path.insert(0, str(ROOT / "codex-scripts"))
    changed = []
    for target in TARGETS:
        old = target.read_text(encoding="utf-8-sig")
        new, _ = patch_html(old)
        if new != old:
            target.write_text(new, encoding="utf-8")
            changed.append(str(target.relative_to(ROOT)))
    if changed:
        print("UPDATED: " + ", ".join(changed) + " embed document art and the kitchen ghost-mirror state")
    else:
        print("OK: game and editor already embed document art and the kitchen ghost-mirror state")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
