#!/usr/bin/env python3
"""One-time bridge-safe sync of the existing Studio runtime fixes."""
from pathlib import Path
p = Path("studio/index.html")
s = p.read_text(encoding="utf-8")

def replace(old, new, label, expected=1):
    global s
    count = s.count(old)
    if count != expected:
        raise SystemExit(f"ABORT {label}: expected {expected} matches, found {count}")
    s = s.replace(old, new)
    print(f"PATCH {label}: {count}")

replace("mute.onclick=()=>{this.volume.value=this.volume.value==='0'?'55':'0';this.adjustVolumes()};this.volume.oninput=()=>{this.adjustVolumes();this.opts.onVolume?.()};",
        "mute.onclick=()=>{this.volume.value=this.volume.value==='0'?'55':'0';this.adjustVolumes();this.opts.onVolume?.()};this.volume.oninput=()=>{this.adjustVolumes();this.opts.onVolume?.()};", "persist-mute", 2)
replace("btn.style.cssText=isGame?'position:fixed;z-index:400;right:14px;bottom:14px;padding:9px 13px;background:#272d36;color:#fff;border:1px solid #777;border-radius:9px;cursor:pointer;font-weight:700;':'flex:none;white-space:nowrap;font-weight:700;border:1px solid #c63439;';",
        "btn.style.cssText=isGame?'position:fixed;z-index:400;left:14px;top:96px;right:auto;bottom:auto;padding:9px 13px;background:#272d36;color:#fff;border:1px solid #777;border-radius:9px;cursor:pointer;font-weight:700;':'flex:none;white-space:nowrap;font-weight:700;border:1px solid #c63439;';", "language-position", 2)
replace("window.addEventListener('keydown',e=>{const k=e.key.toLowerCase();if(k==='escape'){if(sessionStarted){showSystem(sessionPaused?'': 'pause');}return;}if(!sessionStarted||sessionPaused||adventurePlayer?.engine.modal)return;",
        "window.addEventListener('keydown',e=>{const k=e.key.toLowerCase();if(k==='escape'){if(!sessionStarted)return;if(!sessionPaused){showSystem('pause');return;}if(systemPage==='pause'){closeSystem();return;}showSystem('pause');return;}if(!sessionStarted||sessionPaused||adventurePlayer?.engine.modal)return;", "escape-pause", 1)
old = "function validateSave(v){if(!v||v.kind!=='GAGARIN_PLAYER_SAVE'||v.version!==2||v.fingerprint!==gameFingerprint||!v.roomId||!game.rooms.some(r=>r.id===v.roomId))throw Error('Это сохранение другой игры или неподдерживаемой версии.');return v;}"
new = "function validateAdventureSave(v){const d=game.story?.adventure;const object=x=>x&&typeof x==='object'&&!Array.isArray(x);if(!d)return;if(!object(v)||v.version!==1||v.project!==d.id||!d.rooms?.some(r=>r.id===v.room)||!object(v.flags)||!Array.isArray(v.done)||!Number.isInteger(v.chapter)||!Array.isArray(d.quests)||v.chapter<1||v.chapter>d.quests.length)throw Error('Несовместимое сохранение сценария');if(adventurePlayer?.engine?.normalize)adventurePlayer.engine.normalize(v);}function validateSave(v){if(!v||v.kind!=='GAGARIN_PLAYER_SAVE'||v.version!==2||v.fingerprint!==gameFingerprint||!v.roomId||!game.rooms.some(r=>r.id===v.roomId))throw Error('Это сохранение другой игры или неподдерживаемой версии.');if(game.story?.adventure){if(!v.adventure)throw Error('В сохранении отсутствует состояние сценария.');validateAdventureSave(v.adventure);}return v;}"
replace(old, new, "validate-adventure-payload", 1)
old = "async function loadGameSave(data){directorStop();for(const c of mediaControllers.values()){c.video?.pause();c.audio?.pause();c.playing=false;}clearTimeout(saveDebounce);validateSave(data);if(adventurePlayer&&data.adventure)adventurePlayer.load(data.adventure);"
new = "async function loadGameSave(data){validateSave(data);directorStop();for(const c of mediaControllers.values()){c.video?.pause();c.audio?.pause();c.playing=false;}clearTimeout(saveDebounce);if(adventurePlayer&&data.adventure)adventurePlayer.load(data.adventure);"
replace(old, new, "validate-before-mutation", 1)
replace("const scratch=document.createElement('canvas');scratch.width=Math.min(750,w);scratch.height=Math.min(430,h);const out=scratch.getContext('2d'),image=e.ctx.getImageData(0,0,e.width,e.height),dest=out.createImageData(scratch.width,scratch.height),t=Math.tan(fov*Math.PI/360),cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);",
        "const scratch=document.createElement('canvas');const scale=Math.min(1,750/w,430/h);scratch.width=Math.max(1,Math.round(w*scale));scratch.height=Math.max(1,Math.round(h*scale));const out=scratch.getContext('2d'),image=e.ctx.getImageData(0,0,e.width,e.height),dest=out.createImageData(scratch.width,scratch.height),t=Math.tan(fov*Math.PI/360),cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);", "fallback-aspect", 1)
replace("function resetGame(){", "function clearPanoramaCache(){for(const entry of cache.values()){try{if(entry?.texture&&gl)gl.deleteTexture(entry.texture);}catch(_){}try{entry?.bitmap?.close?.();}catch(_){}}cache.clear();}function resetGame(){", "cache-disposal-helper", 1)
replace("for(const key of Object.keys(adventureVariantsApplied))delete adventureVariantsApplied[key];cache.clear();}", "for(const key of Object.keys(adventureVariantsApplied))delete adventureVariantsApplied[key];clearPanoramaCache();}", "cache-disposal-use", 1)
replace("$('right').style.display='none';$('footer').style.display='none';storyPlayer.questBox.style.display='none';",
        "const torchToggle=$('toggle');torchToggle.style.position='fixed';torchToggle.style.top='14px';torchToggle.style.right='14px';torchToggle.style.bottom='auto';torchToggle.style.left='auto';torchToggle.style.width='auto';torchToggle.style.minWidth='132px';torchToggle.style.zIndex='8';document.body.append(torchToggle);$('right').style.display='none';$('footer').style.display='none';storyPlayer.questBox.style.display='none';", "mobile-flashlight", 1)
p.write_text(s, encoding="utf-8")
print("WROTE", p, "chars", len(s))
