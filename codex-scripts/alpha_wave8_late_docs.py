#!/usr/bin/env python3
"""Attach three canon-checked late-game document illustrations to existing actions."""
from __future__ import annotations
import base64, hashlib
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
DOCS = {
    "D24": ("read_D24", "A", 11, "ЖИЛОЙ МОДУЛЬ / ЛИЧНАЯ СТРАНИЦА БЕЗ НОМЕРА", "D24_personal_page", "D24_personal_page.svg", "03f77edc820d6265f83cef79fb60a5d94dc50ab038dcf3a735ead104504ae4b9", ("Я помню комнату с зелёным половиком.", "Но человеку за дверью я его должен")),
    "D25": ("read_D25", "H", 8, "АРХИВ / КВИТАНЦИЯ ОТПРАВКИ ДЛЯ ОЛИ", "D25_outgoing_receipt", "D25_outgoing_receipt.svg", "4558001b117633ca8f575296125022727131655947441b307b3c4df58013183c", ("Дата передачи: 21.01.2028.", "Дата приёма: 18.01.2026.", "ДОСТАВКА НЕ ПОДТВЕРЖДЕНА")),
    "D26": ("read_D26", "L", 12, "ГАЛЕРЕЯ / ЗАПИСКА ИРИНЫ НА ДВЕРИ", "D26_irina_door_note", "D26_irina_door_note.svg", "4c37a8e8c9d44ebcf4f91a06c27a19f6b9bfd66cba33f64485ee6b15a1aff6e0", ("Я запустила повторное наблюдение.", "меня можно винить по имени")),
}
def apply_late_docs(payload, root=ROOT):
    adventure = payload["story"]["adventure"]
    if len(adventure["rooms"]) != 16 or len(adventure["events"]) != 112 or len(adventure["documents"]) != 30:
        raise ValueError("Canonical room/event/document counts changed")
    actions = {a["id"]: a for a in adventure["actions"]}
    docs = {d["id"]: d for d in adventure["documents"]}
    art = adventure["illustratedProps"]
    for doc_id, (action_id, room, chapter, title_prefix, art_id, filename, expected_sha, fragments) in DOCS.items():
        action = actions[action_id]
        if (action.get("room") != room or action.get("document") != doc_id
                or action.get("when", {}).get("min") != chapter
                or not any(effect.get("document") == doc_id for effect in action.get("effects", []))):
            raise ValueError("Canonical action changed: " + action_id)
        if not docs[doc_id]["title"].startswith(title_prefix):
            raise ValueError("Canonical title changed: " + doc_id)
        if any(fragment not in docs[doc_id]["text"] for fragment in fragments):
            raise ValueError("Canonical text check failed: " + doc_id)
        raw = (root / "site-assets/late-docs" / filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("Late document art checksum mismatch: " + filename)
        svg = ET.fromstring(raw)
        if svg.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Invalid SVG root: " + filename)
        for node in svg.iter():
            if node.tag.endswith("script") or any(
                    key.lower().endswith(("href", "onload", "onclick", "onerror"))
                    for key in node.attrib):
                raise ValueError("External or executable SVG content prohibited: " + filename)
        if art_id in art["image"] or action_id in art["action"] or doc_id in art["document"]:
            raise ValueError("Refusing to overwrite existing art mapping: " + doc_id)
        art["image"][art_id] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
        art["action"][action_id] = art_id
        art["document"][doc_id] = art_id
    return {"late_document_art": len(DOCS)}
