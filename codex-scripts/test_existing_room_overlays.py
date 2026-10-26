#!/usr/bin/env python3
"""Verify all three transparent overlays required by the Q01-Q03 art manifest."""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'codex-scripts'))
from audit_art_ready import dimensions, audit
EXPECTED={
 'C_C_MIRROR_LIGHT.webp':'022efd8711404c6fffb8e2fe6c9c70543c067a0b00d5734644fa35fa9d6bda96',
 'F_F_ARCHIVE12.webp':'8f93f98269989a49cb757e01e2c3c3d112e51e1ff2962e31e126b080a709a43d',
 'H_H_AFTER_V01.webp':'063c48657fd82e7d0e1cebb57061646367a30aadd844f71699e02806baf64c0a',
}
spec=json.loads((ROOT/'production/asset_manifest_q01_q03.json').read_text(encoding='utf-8'))
canonical=json.loads((ROOT/'studio/content/TIHAYA_VODA/adventure.json').read_text(encoding='utf-8'))
assert {x['asset_path'].split('/')[-1] for r in spec['canonical_rooms'] for x in r['changed_variants']} == set(EXPECTED)
for filename,sha in EXPECTED.items():
 p=ROOT/'art/overlays'/filename
 raw=p.read_bytes()
 assert raw[:4]==b'RIFF' and raw[8:12]==b'WEBP',filename
 assert dimensions(p)==(2048,1024),(filename,dimensions(p))
 # VP8L header: alpha_is_used is bit 28 in the four-byte image header.
 assert raw[12:16]==b'VP8L' and ((int.from_bytes(raw[21:25],'little')>>28)&1)==1,filename+' must preserve transparency'
 assert hashlib.sha256(raw).hexdigest()==sha,filename+' checksum mismatch'
 print('PASS',filename,'2048x1024 transparent WebP',len(raw),'bytes')
expected_events={'C_C_MIRROR_LIGHT':('E013','C','C_MIRROR_LIGHT'),'F_F_ARCHIVE12':('E009','F','F_ARCHIVE12'),'H_H_AFTER_V01':('E012','H','H_AFTER_V01')}
for filename,(event_id,room_id,state) in expected_events.items():
 event=next(e for e in canonical['events'] if e.get('event_id')==event_id)
 assert event.get('room')==room_id and any(eff.get('variant',{}).get(room_id)==state for eff in event.get('effects',[])),event_id
report=audit()
assert report['overlay_ready']==3 and report['overlay_missing']==0,report
assert not any(x.startswith('Missing overlay ') for x in report['issues']),report['issues']
# Base panorama and hotspot calibration are separate production tasks; don't mask them.
print(f"PASS art audit: overlays {report['overlay_ready']}/{report['overlay_needed']}; base panoramas {report['base_panorama_ready']}/{report['base_panorama_needed']}; uncalibrated hotspots {report['uncalibrated_hotspots']}")
