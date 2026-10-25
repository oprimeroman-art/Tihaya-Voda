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
    # The original offline exports predate the optional ambient visual layer.
    css_a, css_b = "/* HORROR_STYLE_BEGIN", "/* HORROR_STYLE_END */"
    css = RUNTIME[RUNTIME.index(css_a):RUNTIME.index(css_b)+len(css_b)]
    if css_a in html:
        a, b = html.index(css_a), html.index(css_b, html.index(css_a))+len(css_b)
        html = html[:a] + css + html[b:]
    else:
        if html.count("</style></head><body>") != 1:
            raise ValueError("Cannot find main style boundary in exported game")
        html = html.replace("</style></head><body>", css + "</style></head><body>", 1)
    cue_a, cue_b = "/* HORROR_CUE_STYLE_BEGIN", "/* HORROR_CUE_STYLE_END */"
    cue_css = RUNTIME[RUNTIME.index(cue_a):RUNTIME.index(cue_b)+len(cue_b)]
    if cue_a in html:
        a, b = html.index(cue_a), html.index(cue_b, html.index(cue_a))+len(cue_b)
        html = html[:a] + cue_css + html[b:]
    else:
        if html.count("</style></head><body>") != 1:
            raise ValueError("Expected one CSS insertion point")
        html = html.replace("</style></head><body>", cue_css + "</style></head><body>", 1)
    veil = '<div id="veil"></div>'
    overlays = '<div id="horror-atmosphere" aria-hidden="true"></div><div id="horror-apparition" aria-hidden="true"></div>'
    if html.count(veil) != 1:
        raise ValueError("Expected exactly one panorama veil")
    if 'id="horror-atmosphere"' not in html:
        html = html.replace(veil, veil + overlays, 1)
    if html.count('id="horror-atmosphere"') != 1 or html.count('id="horror-apparition"') != 1:
        raise ValueError("Duplicate horror overlay nodes")
    cue_node = '<div id="horror-cue" aria-hidden="true"></div>'
    if 'id="horror-cue"' not in html:
        apparition = '<div id="horror-apparition" aria-hidden="true"></div>'
        if html.count(apparition) != 1:
            raise ValueError("Expected exactly one apparition overlay")
        html = html.replace(apparition, apparition + cue_node, 1)
    if html.count('id="horror-cue"') != 1:
        raise ValueError("Duplicated timed horror overlay")
    html = replace_between(html, RUNTIME, "async function prepare(r){", "// Live 4-corner media surfaces")
    horror_start = "/* HORROR_VISUALS_BEGIN"
    state_start = "function adventureReflectState(){"
    variant_start = "function adventureApplyVariant(rid,variant){"
    boot_start = "function boot(){try{"
    if horror_start in html:
        html = replace_between(html, RUNTIME, horror_start, boot_start)
    elif state_start in html:
        html = replace_between(html, RUNTIME, state_start, boot_start, horror_start)
    elif variant_start in html:
        html = replace_between(html, RUNTIME, variant_start, boot_start, horror_start)
    else:
        html = replace_between(html, RUNTIME, "function adventureSetup(){", boot_start, horror_start)
    html = replace_between(html, RUNTIME, "async function switchRoom(id,adventureSync=false){", "function varsChanged(){")
    html = replace_between(html, RUNTIME, "function resetGame(){", "async function loadGameSave(data){")
    html = replace_between(html, RUNTIME, "function tick(ts){", "requestAnimationFrame(tick);boot();")
    html = replace_between(html, RUNTIME, "function render(){", "function refresh(){")
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
