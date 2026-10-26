#!/usr/bin/env python3
"""Synchronize only the shared adventure UI into existing standalone HTML builds.

Unlike the full engine synchronizer, this preserves the shipped renderer, saves,
flashlight, ambience, and other runtime fixes outside the shared UI module.
"""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "studio/source/adventure-ui.js").read_text(encoding="utf-8-sig").rstrip()
MARKER = "/* UI shared by the editor preview and the compiled offline runtime. */"
OUTPUTS = (ROOT / "game/index.html", ROOT / "game-editor/index.html")
def sync(text: str) -> str:
    if text.count(MARKER) != 1:
        raise ValueError("Expected exactly one shared adventure UI marker")
    start = text.index(MARKER)
    end = text.find("</script>", start)
    if end < 0:
        raise ValueError("Could not find closing script tag after shared adventure UI")
    if UI.count(MARKER) != 1 or "</script>" in UI:
        raise ValueError("Shared UI source has unexpected script boundaries")
    return text[:start] + UI + "\n" + text[end:]
def main() -> int:
    changed = []
    for path in OUTPUTS:
        old = path.read_text(encoding="utf-8-sig")
        new = sync(old)
        if old != new:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    studio = ROOT / "studio/index.html"
    old = studio.read_text(encoding="utf-8")
    text = old
    marker = "window.STORY_SOURCE="
    if text.count(marker) != 1:
        raise ValueError("Expected one Studio story source")
    pos = text.index(marker)+len(marker)
    template, consumed = json.JSONDecoder().raw_decode(text[pos:])
    if template.count(MARKER)!=1:raise ValueError("Expected one exported story UI")
    template = template[:template.index(MARKER)]+UI+"\n"
    encoded = json.dumps(template,ensure_ascii=False).replace("</", "<\\/")
    text = text[:pos]+encoded+text[pos+consumed:]
    # The live preview also has its own script, after the template string.
    pos = text.rindex(MARKER)
    end = text.index("</script>",pos)
    text = text[:pos]+UI+"\n"+text[end:]
    if text != old:
        studio.write_text(text,encoding="utf-8")
        changed.append("studio/index.html")
    print("UPDATED: " + ", ".join(changed) if changed else "OK: shared UI is up to date")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
