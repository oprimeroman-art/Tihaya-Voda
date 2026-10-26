#!/usr/bin/env python3
"""Embed D27-D29 SVG data in the existing offline game HTML without rebuilding its runtime."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
MARKER = "window.BUILT_GAME="
TARGET = ROOT / "game/index.html"
def patch_html(html: str) -> tuple[str, bool]:
    if html.count(MARKER) != 1:
        raise ValueError("Expected exactly one built-game payload in standalone HTML")
    start = html.index(MARKER) + len(MARKER)
    payload, consumed = json.JSONDecoder().raw_decode(html[start:])
    from alpha_wave9_document_props import apply_wave9
    result = apply_wave9(payload, ROOT)
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    updated = html[:start] + encoded + html[start + consumed:]
    return updated, bool(result)
def main() -> int:
    sys.path.insert(0, str(ROOT / "codex-scripts"))
    old = TARGET.read_text(encoding="utf-8-sig")
    new, _ = patch_html(old)
    if new != old:
        TARGET.write_text(new, encoding="utf-8")
        print("UPDATED: game/index.html now embeds D27-D29 document art")
    else:
        print("OK: standalone game already embeds D27-D29 document art")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
