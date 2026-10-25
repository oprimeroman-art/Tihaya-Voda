from paths import *
src=STUDIO/'source'
p=src/'adventure-ui.js';s=p.read_text(encoding='utf-8')
s=s.replace("this.root.hidden=true;this.root.append", "this.root.hidden=true;this.root.setAttribute('translate','no');this.root.append")
s=s.replace("sync(){if(this.engine.state.room", "sync(){this.hooks.variant?.(this.engine.state.room,this.engine.state.variants[this.engine.state.room]);if(this.engine.state.room")
s=s.replace("this.changed();return e;", "this.changed();return e;")
s=s.replace("scene(e){const b=this.panel", "scene(e){this.hooks.variant?.(this.engine.state.room,this.engine.state.variants[this.engine.state.room]);if(e.timelineId)this.hooks.timeline?.(e.timelineId);const b=this.panel")
s=s.replace("const transcript=el('details');transcript.append", "const transcript=el('details');transcript.open=true;transcript.append")
s=s.replace("if(a.hint){const d=el('details');d.append", "if(a.hint){const d=el('details');d.open=true;d.append")
# Announce persistent scene state, not only an internal asset key.
s=s.replace("this.variant.textContent='ОТСУТСТВУЕТ АССЕТ: '+s.variants[s.room]+' · временная панорама';", "const room=this.data.rooms.find(r=>r.id===s.room),authored=room?.variantAssets?.[s.variants[s.room]];this.variant.textContent=authored?'Состояние помещения: '+s.variants[s.room]:'ОТСУТСТВУЕТ АССЕТ: '+s.variants[s.room]+' · временная панорама';")
p.write_text(s,encoding='utf-8')
p=src/'game-runtime.html';s=p.read_text(encoding='utf-8')
if 'const adventureVariantsApplied={};' not in s:
    s=s.replace('let adventurePlayer=null;','let adventurePlayer=null;const adventureVariantsApplied={};')
    s=s.replace("room:()=>roomId,go:id=>switchRoom(id,true),", """room:()=>roomId,go:id=>switchRoom(id,true),timeline:id=>directorStart(id),
 variant:(rid,variant)=>{const meta=game.story.adventure.rooms.find(r=>r.id===rid),asset=game.assets[meta?.variantAssets?.[variant]];if(asset&&adventureVariantsApplied[rid]!==variant){adventureVariantsApplied[rid]=variant;game.panoramas[rid]=asset;cache.delete(rid);switchRoom(rid,true);}},""")
    s=s.replace("function resetGame(){adventurePlayer?.reset();", "function resetGame(){if(adventurePlayer)adventurePlayer.endingShown=false;adventurePlayer?.reset();")
p.write_text(s,encoding='utf-8')
# Translation must never rewrite authored dialogue, documents or minigame answers.
p=src/'i18n.js';old=p.read_text(encoding='utf-8-sig');new=old.replace("const p=node.parentNode;if(!p||", "const p=node.parentNode;if(p?.closest?.('[translate=no]'))return;if(!p||").replace("function patchAttr(el,key){", "function patchAttr(el,key){if(el.closest?.('[translate=no]'))return;")
p.write_text(new,encoding='utf-8')
index=STUDIO/'index.html';html=index.read_text(encoding='utf-8')
html=html.replace(old,new)
import json,re
m=re.search(r'window\.GPE_I18N_SOURCE\s*=\s*',html)
if m:
    start=m.end();_,end=json.JSONDecoder().raw_decode(html[start:]);html=html[:start]+json.dumps(new,ensure_ascii=False).replace('</script','<\\/script')+html[start+end:]
index.write_text(html,encoding='utf-8')
print('Author text protected; explicit physical hints and full media transcript visible; variant asset bindings enabled.')
