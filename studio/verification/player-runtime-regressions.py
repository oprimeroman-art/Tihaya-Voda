#!/usr/bin/env python3
"""Static regression guard for the exported player and Studio runtime."""
from pathlib import Path

paths = [Path("game/index.html"), Path("studio/index.html")]
if Path("_site/index.html").exists():
    paths.append(Path("_site/index.html"))
checks = {
    "Esc closes pause instead of opening an empty page": "if(k==='escape'){if(!sessionStarted)return;e.preventDefault();if(!sessionPaused){showSystem('pause');return;}if(systemPage==='pause'){closeSystem();return;}showSystem('pause');return;}",
    "adventure saves are validated before load mutation": "async function loadGameSave(data){validateSave(data);",
    "missing adventure state is rejected": "if(!v.adventure)throw Error('В сохранении отсутствует состояние сценария.');validateAdventureSave(v.adventure);",
    "wrong adventure project is rejected": "v.project!==d.id",
    "mute updates saved preferences": "mute.onclick=()=>{this.volume.value=this.volume.value==='0'?'55':'0';this.adjustVolumes();this.opts.onVolume?.()};",
    "language toggle has a separate corner": "left:14px;top:96px;right:auto;bottom:auto",
    "fallback render preserves viewport aspect": "const scale=Math.min(1,750/w,430/h);scratch.width=Math.max(1,Math.round(w*scale));scratch.height=Math.max(1,Math.round(h*scale));",
    "reset releases WebGL textures": "function clearPanoramaCache(){for(const entry of cache.values()){try{if(entry?.texture&&gl)gl.deleteTexture(entry.texture);}",
    "flashlight stays available in adventure mode": "torchToggle.style.position='fixed';torchToggle.style.top='14px';torchToggle.style.right='14px';",
    "adaptive station ambience is implemented": "function startStationAmbience()",
    "ambience respects master volume": "const prefs=audioSettings?.master??55",
    "ambience suspends on pause": "pauseStationAmbience();for(const c of directorChannels.values())",
    "ambience changes only when room changes": "stationAmbienceRoom!==(roomId||'A')",
}
for path in paths:
    source = path.read_text(encoding="utf-8")
    missing = [label for label, needle in checks.items() if needle not in source]
    if missing:
        raise SystemExit(f"FAIL {path}: {missing}")
    if "showSystem(sessionPaused?'': 'pause')" in source:
        raise SystemExit(f"FAIL {path}: old Esc regression remains")
    if "scratch.width=Math.min(750,w);scratch.height=Math.min(430,h)" in source:
        raise SystemExit(f"FAIL {path}: distorted fallback dimensions remain")
    print(f"PASS {path}: {len(checks)} runtime regression guards")
