from pathlib import Path
import zipfile
from paths import *
p=OUT/'GAME_EDITOR';p.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT/'EDITOR_EXPORTED_GAME.zip') as z:(p/'index.html').write_bytes(z.read('index.html'))
s=Path('work/browser-test.cjs').read_text(encoding='utf-8')
s=s[:s.index(" await navigate(path.join(out,'GAME/index.html'))")]+r'''
 await navigate(path.join(out,'GAME_EDITOR/index.html'));await until('typeof sessionReady!=="undefined" && sessionReady');await ev('resetGame()');await dismissEvents();checks.push('Native editor-exported GAME boots directly from file');
 await clickAction('take_BADGE04');await cmd('Page.bringToFront');await ev("[...document.querySelectorAll('.ga-dialog button')].find(b=>b.textContent==='Выполнить').focus()");await cmd('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r',unmodifiedText:'\r'});await cmd('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await sleep(200);assert(await ev("adventurePlayer.engine.state.inventory.includes('BADGE04')"));checks.push('Keyboard Enter activates focused interaction');
 await ev("adventurePlayer.engine.enter('C');adventurePlayer.engine.enter('B');adventurePlayer.sync()");await until("roomId==='B'");await clickAction('read_D01');const canon=await ev("document.querySelector('.ga-dialog pre').textContent");await ev("GPE_I18N.setLanguage('en')");assert.equal(await ev("document.querySelector('.ga-dialog pre').textContent"),canon);await ev("GPE_I18N.setLanguage('ru')");checks.push('Language toggle leaves authored Russian document verbatim');await ev('adventurePlayer.close()');
 const original=await ev('game.panoramas.B.data');await ev("game.assets.variantTest=game.panoramas.A;game.story.adventure.rooms.find(r=>r.id==='B').variantAssets.B_TEST='variantTest';adventurePlayer.engine.state.variants.B='B_TEST';adventurePlayer.sync()");await sleep(700);assert.equal(await ev('game.panoramas.B.data===game.panoramas.A.data'),true);await ev('resetGame()');await dismissEvents();assert.equal(await ev('game.panoramas.B.data'),original);checks.push('Authored room variant asset changes panorama; new game restores original');
 assert.equal(errors.length,0);const result={passed:true,checks,uncaughtErrors:errors};fs.writeFileSync(path.join(out,'FINAL_BROWSER_TEST_REPORT.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}catch(e){console.error(e.stack);fs.writeFileSync(path.join(out,'FINAL_BROWSER_TEST_REPORT.json'),JSON.stringify({passed:false,checks,error:e.message,uncaughtErrors:errors},null,2));process.exitCode=1;}finally{try{await cmd('Browser.close')}catch{}sock?.close();chrome.kill();}})();
'''
Path('work/final-browser.cjs').write_text(s,encoding='utf-8')
