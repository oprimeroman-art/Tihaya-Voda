#!/usr/bin/env python3
"""Audit the Q01-Q03 production art contract without pretending missing art is ready."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production/asset_manifest_q01_q03.json"
PROJECT = ROOT / "game-project/project.json"


def dimensions(path: Path) -> tuple[int, int]:
    with path.open('rb') as stream:
        data = stream.read(65536)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack('>II', data[16:24])
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        chunk, payload = data[12:16], data[20:]
        if chunk == b'VP8X' and len(payload) >= 10:
            return (int.from_bytes(payload[4:7], 'little')+1, int.from_bytes(payload[7:10], 'little')+1)
        if chunk == b'VP8 ' and len(payload) >= 10 and payload[3:6] == b'\x9d\x01\x2a':
            return (int.from_bytes(payload[6:8], 'little') & 0x3fff, int.from_bytes(payload[8:10], 'little') & 0x3fff)
        if chunk == b'VP8L' and len(payload) >= 5 and payload[0] == 0x2f:
            bits = int.from_bytes(payload[1:5], 'little')
            return ((bits & 0x3fff)+1, ((bits >> 14) & 0x3fff)+1)
        raise ValueError('Unsupported WebP chunk layout')
    if data[:2] == b'\xff\xd8':
        offset = 2
        while offset+4 <= len(data):
            if data[offset] != 0xff:
                offset += 1
                continue
            while offset < len(data) and data[offset] == 0xff:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]; offset += 1
            if marker in (0xd8, 0xd9, 0x01) or 0xd0 <= marker <= 0xd7:
                continue
            if offset+2 > len(data):
                break
            length = int.from_bytes(data[offset:offset+2], 'big')
            if marker in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf) and offset+7 <= len(data):
                return (int.from_bytes(data[offset+5:offset+7], 'big'), int.from_bytes(data[offset+3:offset+5], 'big'))
            offset += length
        raise ValueError('JPEG dimensions not found in first 64KB')
    raise ValueError('Unsupported image type (expected PNG, JPEG or WebP)')


def audit() -> dict:
    spec = json.loads(MANIFEST.read_text(encoding='utf-8'))
    game = json.loads(PROJECT.read_text(encoding='utf-8'))
    qs = game['story']['adventure']['quests']
    assert [x['id'] for x in qs[:3]] == ['Q01', 'Q02', 'Q03']
    assert len(spec['canonical_rooms']) == 8
    assert {r['room_id'] for r in spec['canonical_rooms']} == {'A','B','C','D','E','F','G','H'}
    room_map = {r['id']:r for r in game['rooms']}
    issues = []
    accepted = 0
    overlay_ready = 0
    overlay_missing = 0
    uncalibrated = 0
    for scene in spec['canonical_rooms']:
        id = scene['room_id']
        if scene['source_image_path'] != room_map[id]['file']:
            issues.append(id+': changed game source path')
        current = {o['id'] for o in room_map[id].get('objects', [])}
        for spot in scene['hotspots']:
            if spot['id'] not in current:
                issues.append(id+': removed hotspot '+str(spot['id']))
            if not spot['calibrated']:
                uncalibrated += 1
        target = ROOT / scene['target_asset']
        if not target.is_file():
            issues.append(id+': missing panorama '+scene['target_asset'])
            continue
        try:
            w,h = dimensions(target)
            if w < 2048 or h < 1024 or w != 2*h:
                issues.append(f'{id}: panorama must be 2:1 and >= 2048x1024, got {w}x{h}')
            else:
                accepted += 1
        except ValueError as exc:
            issues.append(id+': '+str(exc))
    for variant in spec['required_variant_assets']:
        room=next(r for r in spec['canonical_rooms'] if r['room_id']==variant['room'])
        v=next(e for e in room['changed_variants'] if e['id']==variant['variant'])
        if not (ROOT/v['asset_path']).is_file():
            overlay_missing += 1
            issues.append('Missing overlay '+v['asset_path'])
        else:
            overlay_ready += 1
    if uncalibrated:
        issues.append(f'{uncalibrated} hotspot corners still require visual calibration')
    return {'base_panorama_ready':accepted,'base_panorama_needed':8,
            'overlay_ready':overlay_ready,'overlay_needed':len(spec['required_variant_assets']),
            'overlay_missing':overlay_missing,
            'uncalibrated_hotspots':uncalibrated,'issues':issues,
            'ready':not issues}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true',help='return nonzero if art is incomplete')
    parser.add_argument('--json', action='store_true',help='print structured report')
    args=parser.parse_args()
    report=audit()
    if args.json:
        print(json.dumps(report,ensure_ascii=False,indent=2))
    else:
        print(f"Panoramas: {report['base_panorama_ready']}/{report['base_panorama_needed']}; overlays: {report['overlay_ready']}/{report['overlay_needed']} (missing {report['overlay_missing']}); hotspot calibration pending: {report['uncalibrated_hotspots']}")
        for issue in report['issues']:
            print('PENDING:',issue)
        print('PRODUCTION_READY:',report['ready'])
    return 1 if args.strict and not report['ready'] else 0


if __name__=='__main__':
    raise SystemExit(main())
