#!/usr/bin/env python3
"""Regression checks for embedded and rendered D27-D29 artwork."""
import base64, hashlib, json, re
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "_site/index.html").read_text(encoding="utf-8")
assert html.count("window.BUILT_GAME=") == 1
payload, _ = json.JSONDecoder().raw_decode(html[html.index("window.BUILT_GAME=") + len("window.BUILT_GAME="):])
adv = payload["story"]["adventure"]
assert len(payload["rooms"]) == 16 and len(adv["events"]) == 112 and len(adv["documents"]) == 30
art = adv["illustratedProps"]
expected = {
 "D27": ("read_D27", "D27_radio_transmission", "726764aec794f7fd5c80e134644c46fe879f8efba900790490f6f2476727d58e"),
 "D28": ("read_D28", "D28_generator_bus_panel", "aecfed87b642bf3e89f1f74d33f47787ba6e80469e8b5704b17097dcc0d5cc55"),
 "D29": ("read_D29", "D29_anna_draft", "1546b17aff50504175e82a074da67902a980d0436a984cb05f792e56eb78951e"),
}
for doc, (action, art_id, sha) in expected.items():
 assert art["document"][doc] == art_id and art["action"][action] == art_id
 uri = art["image"][art_id]; prefix = "data:image/svg+xml;base64,"; assert uri.startswith(prefix)
 raw = base64.b64decode(uri[len(prefix):], validate=True); assert hashlib.sha256(raw).hexdigest() == sha
 assert ET.fromstring(raw).tag == "{http://www.w3.org/2000/svg}svg"
assert ".ga-document-art" in html and "documentView(parent,doc)" in html
assert "this.documentView(b,this.data.documents.find(d=>d.id===a.document))" in html
print("PASS D27-D29: canonical actions/documents unchanged; 3 SVGs embedded offline and document renderer present")
