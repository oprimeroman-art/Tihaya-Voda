#!/usr/bin/env python3
"""Synchronize selected engine/UI/render sections into existing offline HTML outputs.

No new copies or releases. Run with --check to detect stale built files.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (ROOT / "game/index.html", ROOT / "game-editor/index.html")
CORE = (ROOT / "studio/source/adventure-core.js").read_text(encoding="utf-8-sig")
UI = (ROOT / "studio/source/adventure-ui.js").read_text(encoding="utf-8-sig")
RUNTIME = (ROOT / "studio/source/game-runtime.html").read_text(encoding="utf-8-sig")
CORE_START = "/* Declarative adventure extension for Panorama Studio. No game-specific IDs or eval. */"
UI_START = "/* UI shared by the editor preview and the compiled offline runtime. */"


def replace_between(target, source, begin, end, source_begin=None):
    source_begin = source_begin or begin
    if target.count(begin) != 1 or target.count(end) != 1:
        raise ValueError(f"Missing or duplicated built runtime marker: {begin[:75]}")
    if source.count(source_begin) != 1 or source.count(end) != 1:
        raise ValueError(f"Missing or duplicated runtime source marker: {source_begin[:75]}")
    a, b = target.index(begin), target.index(end, target.index(begin))
    i, j = source.index(source_begin), source.index(end, source.index(source_begin))
    return target[:a] + source[i:j] + target[b:]


def synchronize(html):
    if html.count(CORE_START) != 1 or html.count(UI_START) != 1:
        raise ValueError("Expected exactly one story engine and UI module")
    a, b = html.index(CORE_START), html.index(UI_START)
    if a >= b or CORE.count(CORE_START) != 1 or UI.count(UI_START) != 1:
        raise ValueError("Unexpected script module order")
    # The UI is the final part of its script tag in both shipped HTML files.
    end = html.index("</script>", b)
    html = html[:a] + CORE.rstrip() + "\n\n" + UI.rstrip() + "\n" + html[end:]
    html = replace_between(html, RUNTIME, "async function prepare(r){", "// Live 4-corner media surfaces")
    variant_start = "function adventureApplyVariant(rid,variant){"
    boot_start = "function boot(){try{"
    if variant_start in html:
        html = replace_between(html, RUNTIME, variant_start, boot_start)
    else:
        # One-time upgrade of old builds whose adventureSetup had no variant helper.
        html = replace_between(html, RUNTIME, "function adventureSetup(){", boot_start, variant_start)
    html = replace_between(html, RUNTIME, "async function loadGameSave(data){", "function setAudio(){")
    return html


def main():
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--check"):
        print("Usage: sync_embedded_engine.py [--check]", file=sys.stderr)
        return 2
    checking = "--check" in sys.argv
    stale = []
    for path in OUTPUTS:
        old = path.read_text(encoding="utf-8-sig")
        updated = synchronize(old)
        if updated == old:
            print(f"OK: {path.relative_to(ROOT)}")
        elif checking:
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
