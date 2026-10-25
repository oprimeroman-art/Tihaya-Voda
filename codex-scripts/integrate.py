import re,json
from paths import *
src=STUDIO/'source'
html=(STUDIO/'index.html').read_text(encoding='utf-8-sig')
runtime=(src/'game-runtime.html').read_text(encoding='utf-8-sig')
core=(src/'adventure-core.js').read_text(encoding='utf-8')
ui=(src/'adventure-ui.js').read_text(encoding='utf-8')
editor=(src/'adventure-editor.js').read_text(encoding='utf-8')
def replace_once(s,a,b):
    if a not in s:
        if b in s:return s
        raise Exception('Patch anchor missing: '+a[:140])
    return s.replace(a,b,1)
# The extension is nested in story so all existing ZIP paths preserve it.
if 'let adventurePlayer=null;' not in runtime:
    runtime=replace_once(runtime,"let sessionReady=false,",'let adventurePlayer=null;\nlet sessionReady=false,')
    runtime=replace_once(runtime,"function boot(){try{",'''function adventureSetup(){if(!game.story?.adventure)return;adventurePlayer=new GagarinAdventure.UI(game.story.adventure,{
 room:()=>roomId,go:id=>switchRoom(id,true),paused:()=>sessionPaused||!sessionStarted,save:()=>saveProgress(true),newGame:()=>resetGame(),
 change:()=>{const s=adventurePlayer?.engine.state;if(!s)return;for(const v of game.globals)if(v.key in s.flags)v.value=s.flags[v.key];for(const r of game.rooms)for(const o of r.objects){if(o.tourKey?.startsWith('ga:')){const a=game.story.adventure.actions.find(a=>a.id===o.tourKey.slice(3));o.visible=!!a&&adventurePlayer.engine.eligible(a);}}for(const c of cache.values())c.dirty=true;refresh();scheduleGameSave();},
 media:id=>{const slot=game.story.adventure.media.find(m=>m.id===id),a=game.video?.[slot?.assetId||id]||game.audio?.[slot?.assetId||id];return a?{url:bytesBase64(a.data,a.mime)}:null;}});
 $('right').style.display='none';$('footer').style.display='none';storyPlayer.questBox.style.display='none';
}
function boot(){try{''')
    runtime=replace_once(runtime," sessionReady=true;",' adventureSetup();\n sessionReady=true;')
    runtime=replace_once(runtime,'async function switchRoom(id){','''async function switchRoom(id,adventureSync=false){if(adventurePlayer&&sessionStarted&&!adventureSync&&id!==adventurePlayer.engine.state.room){if(!adventurePlayer.engine.enter(id))return;}''')
    runtime=replace_once(runtime,"story:{quests:storyPlayer?.questStates||{}},",'adventure:adventurePlayer?.snapshot()||null,\n story:{quests:storyPlayer?.questStates||{}},')
    runtime=replace_once(runtime,"function resetGame(){directorStop();",'function resetGame(){adventurePlayer?.reset();directorStop();')
    runtime=replace_once(runtime,"clearTimeout(saveDebounce);validateSave(data);storyPlayer.stop();",'clearTimeout(saveDebounce);validateSave(data);if(adventurePlayer&&data.adventure)adventurePlayer.load(data.adventure);storyPlayer.stop();')
    runtime=replace_once(runtime,"if(o){runtime.fire('click',o.id);", "if(o){if(o.tourKey?.startsWith('ga:'))adventurePlayer?.openAction(o.tourKey.slice(3));else runtime.fire('click',o.id);")
    # No room-clock horror advances while an adventure interaction owns focus.
    runtime=runtime.replace('runtime.tick(dt,','if(!adventurePlayer?.engine.modal)runtime.tick(dt,')
    runtime=replace_once(runtime,'function directorTick(dt){if(!sessionStarted||!sessionReady||sessionPaused)return;','function directorTick(dt){if(!sessionStarted||!sessionReady||sessionPaused||adventurePlayer?.engine.modal)return;')
    runtime=replace_once(runtime,"if(!sessionStarted||sessionPaused)return;if(k==='f')", "if(!sessionStarted||sessionPaused||adventurePlayer?.engine.modal)return;if(k==='f')")
    runtime=replace_once(runtime,"const saved=saveObject();let ok=storageWrite", "const saved=saveObject();if(adventurePlayer?.engine.state.ended&&adventurePlayer.engine.state.checkpoint){const cp=adventurePlayer.engine.state.checkpoint;saved.adventure=GagarinAdventure.copy(cp.state);saved.adventure.checkpoint=GagarinAdventure.copy(cp);saved.roomId=saved.adventure.room;}let ok=storageWrite")
(src/'game-runtime.html').write_text(runtime,encoding='utf-8')
# Refresh embedded constants by decoding JSON strings, not broad regex over embedded source.
def js_string(s,name,value):
    m=re.search(r'window\.'+name+r'\s*=\s*',s)
    assert m,name
    start=m.end();_,end=json.JSONDecoder().raw_decode(s[start:]);return s[:start]+json.dumps(value,ensure_ascii=False).replace('</script','<\\/script')+s[start+end:]
story=(src/'story-core.js').read_text(encoding='utf-8-sig')+'\n'+core+'\n'+ui
html=js_string(html,'STORY_SOURCE',story)
html=js_string(html,'GAME_TEMPLATE',runtime)
# Inline extension once for editor preview, refreshable on subsequent builds.
marker='/* ADVENTURE_EXTENSION_BEGIN */';endmarker='/* ADVENTURE_EXTENSION_END */'
payload=marker+'\n'+core+'\n'+ui+'\n'+editor+'\n'+endmarker
if marker in html:
    begin=html.index(marker);end=html.index(endmarker,begin)+len(endmarker);html=html[:begin]+payload+html[end:]
else:
    # Insert inside the final main script before async start, after APP is declared.
    pos=html.rfind('</script>');html=html[:pos]+payload+'\nadventureEditorInstall();\n'+html[pos:]
if 'let adventurePreview=null;' not in html:
    html=replace_once(html,"function beginRulesPreview(){",'''let adventurePreview=null;
function beginRulesPreview(){''')
    html=replace_once(html,'currentRuntime.enter(APP.current);}', '''currentRuntime.enter(APP.current);if(APP.story.adventure){adventurePreview=new GagarinAdventure.UI(APP.story.adventure,{room:()=>APP.current,go:id=>{APP.current=id;currentRuntime.current=id;updateUI();updatePlaybar();requestDraw();},paused:()=>!APP.play,save:()=>toast('Сохранения игрока доступны в собранной игре.'),newGame:()=>{adventurePreview.reset();adventurePreview.sync();},media:id=>{const slot=APP.story.adventure.media.find(m=>m.id===id),a=APP.videoAssets.get(slot?.assetId||id)||APP.soundAssets.get(slot?.assetId||id);return a?{url:URL.createObjectURL(new Blob([a.bytes],{type:a.mime}))}:null;}});adventurePreview.reset();adventurePreview.sync();}}''')
    html=replace_once(html,'function endRulesPreview(){','function endRulesPreview(){adventurePreview?.destroy();adventurePreview=null;')
    html=replace_once(html,'function sendClick(obj){if(currentRuntime)',"function sendClick(obj){if(obj?.tourKey?.startsWith('ga:')&&adventurePreview){adventurePreview.openAction(obj.tourKey.slice(3));return;}if(currentRuntime)")
(STUDIO/'index.html').write_text(html,encoding='utf-8')
print('Updated existing editor and embedded runtime; story.adventure retained by native ZIP format.')
