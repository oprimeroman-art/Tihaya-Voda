/* UI-only route: no developer commands, no writes to engine state. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..'),out=path.join(ROOT,'reports/campaign-browser');fs.mkdirSync(out,{recursive:true});
const story=JSON.parse(fs.readFileSync(path.join(ROOT,'studio/content/TIHAYA_VODA/adventure.json')));
const {test}=require('../source/adventure-core.js');
const common=`take_BADGE04 take_STORAGE_KEY read_D01 TEA_SEQUENCE sign_shift take_FUSE_3 install_fuse3 read_D28 POWER_BASIC CORES_MARKING RADIO_TUNE send_report read_D19 PLUMB_SEQ watch_V01 mirror03 cabinet_message archive_return read_D20 count_cans read_D16 COOKING mirror04 mirror04_away mirror04_again mirror04_third plate_choice dinner_exit take_P17_SAMPLE SPECTRUM_MATCH MICROSCOPE read_D06 hidden_enter read_D03 hidden_exit WAVE_PHASE watch_A02 watch_A01 read_D02 read_D27 mirror06 mirror06_again read_D07 flip_acts read_D22 take_FLASHLIGHT take_ANTENNA_KEY take_BEACON ice_1 ice_2 ice_3 ANTENNA glass07 AIRLOCK_EQUALIZE inner_door take_VHS_FRAGMENT_A take_VHS_FRAGMENT_B read_D23 VHS_ASSEMBLE watch_V02 read_D13 read_D29 read_D05 take_VHS_V03 watch_V03 petr_letter wet_towel read_D04 read_D09 read_D21 take_PUNCHCARD_RU take_PUNCHCARD_DE PUNCHCARD_OVERLAY scan_uv enter_1978 read_D08 read_D12 calibration_plate watch_V06 watch_V09 watch_A03 exit_1978 read_D17 read_D18 watch_A04 CARDIOMATCH medic10 TIMELINE_SYNC watch_V04 late10 read_D14 read_D11 read_D15 watch_V08 handwriting_floor backward_clock reversed_exit_arrow leave_N false_act blanket11 watch_V01B`.split(' ');
const final=`SHUTTERS name_reply second_window third_window POWER_OFF take_SHUTTER_PIN PIN_INSERT ANALOG_READINGS_OK OBSERVER_SELECT`.split(' ');
let page,currentMode,checks=[],errors=[],actionCount=0,pace=[];const voiceManifest=JSON.parse(fs.readFileSync(path.join(ROOT,'game-project/audio/voice-alpha/manifest.json'),'utf8'));
const progressFile=path.join(out,'progress.json');let completedRoutes=[];if(process.env.CAMPAIGN_RESUME==='1'&&fs.existsSync(progressFile)){const saved=JSON.parse(fs.readFileSync(progressFile));({checks,actionCount,pace,completedRoutes}=saved);}
function saveProgress(){fs.writeFileSync(progressFile,JSON.stringify({checks,actionCount,pace,completedRoutes}));}
function recordPace(kind,id,text,duration=0){const words=String(text||'').trim().split(/\s+/).length;pace.push({route:currentMode,kind,id,words,readingSeconds:Number((words/3).toFixed(1)),mediaSeconds:duration});}
async function sameImage(img,expected){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());const actual=await img.evaluate(async i=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await(await fetch(i.src)).arrayBuffer()))).map(x=>x.toString(16).padStart(2,'0')).join(''));const hash=require('node:crypto').createHash('sha256').update(Buffer.from(expected.split(',')[1],'base64')).digest('hex');assert.equal(actual,hash,'image bytes match canonical asset');}

const state=()=>page.evaluate(()=>adventurePlayer.snapshot());
async function button(text){const b=page.getByRole('button',{name:text,exact:true});await b.waitFor({state:'visible'});assert(await b.isEnabled(),text+' enabled');await b.focus();await b.press('Enter');}

async function showPanel(kind){const button=page.locator('.ga-dock button[aria-controls$="-'+kind+'"]');await button.waitFor({state:'visible'});if(await button.getAttribute('aria-expanded')!=='true')await button.press('Enter');}
async function drain(){for(let i=0;i<35;i++){
 await page.clock.runFor(200);
 const cont=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await cont.count()){const sceneId=await page.locator('.ga-dialog').getAttribute('data-event-id');const event=story.events.find(e=>e.id===sceneId);if(event)recordPace('event',sceneId,[event.presentation,...(event.lines||[]).map(l=>l.text)].join(' '),Math.max(0,...(event.lines||[]).map(l=>voiceManifest.tracks[l.id]?.duration||0)));if(sceneId==='E027')assert.equal(await page.locator('.ga-dialog img').count(),1,'pillow scene uses its real artwork');await cont.press('Enter');if(sceneId==='E100')await verifyDaylight();continue;}
 if(await page.locator('.ga-dialog').count())return;
 const s=await state();const pending=s.pending.map(p=>({p,e:story.events.find(e=>e.id===p.id)})).filter(({e})=>e&&(!e.room||e.room===s.room)&&test(e.when,s)&&e.priority!=='optional');
 if(!pending.length)return;const wait=Math.max(0,Math.min(...pending.map(({p})=>p.due))-s.clock);await page.clock.runFor(Math.ceil(wait*1000)+200);
 }throw Error('Event queue did not settle');}
async function verifyDaylight(){
 const previous=(await state()).variants.C;
 await page.waitForFunction(()=>horrorCue?.panoramaVariant==='C_DAYLIGHT'&&horrorCue.ready);
 assert(await page.evaluate(()=>game.panoramas.C===game.assets.authored_C_DAYLIGHT),'actual daylight panorama is rendered');
 await page.clock.runFor(1000);const elapsed=await page.evaluate(()=>horrorCue.elapsed);assert(elapsed>.8&&elapsed<1.3);
 await button('Меню / Esc');const pausedElapsed=await page.evaluate(()=>horrorCue.elapsed);await page.clock.runFor(1000);assert.equal(await page.evaluate(()=>horrorCue.elapsed),pausedElapsed,'menu freezes visible-time clock');
 await button('Сохранить сейчас');assert.equal(await page.evaluate(()=>readSaved().adventure.variants.C),previous,'save contains the real room state');await button('Вернуться в игру');
 if(currentMode==='A'){
  await page.reload();await page.clock.runFor(1000);await button('Продолжить');assert.equal(await page.evaluate(()=>horrorCue),null,'reload cancels temporary daylight');assert.equal((await state()).variants.C,previous);
 }else{await page.clock.runFor(2300);assert.equal(await page.evaluate(()=>horrorCue),null,'daylight expires after three active seconds');}
 assert(await page.evaluate(()=>{const v=adventurePlayer.engine.state.variants.C,id=game.story.adventure.rooms.find(r=>r.id==='C').variantAssets[v];return game.panoramas.C===(game.assets[id]||adventureBasePanoramas.C);}),'previous panorama restored');
 checks.push(currentMode+': actual three-second daylight, pause, stable save and restoration');
}
async function sceneSafeClick(locator){for(let i=0;i<15;i++){try{await locator.waitFor({state:'visible',timeout:5000});await locator.focus();await locator.press('Enter',{timeout:5000});return;}catch(error){const c=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(!await c.count())throw error;await c.press('Enter');await drain();}}throw Error('Repeated scene interruptions');}
async function go(dest){let s=await state();if(s.room===dest)return;let queue=[[s.room,[]]],seen=new Set(),route;
 while(queue.length){const[r,steps]=queue.shift();if(r===dest){route=steps;break;}if(seen.has(r))continue;seen.add(r);for(const l of story.links.filter(l=>l.from===r&&test(l.when,s)))queue.push([l.to,[...steps,l.to]]);}
 assert(route,`No route ${s.room} to ${dest}, chapter ${s.chapter}`);
 for(const r of route){await drain();await showPanel('routes');await sceneSafeClick(page.locator('.ga-nav').getByRole('button',{name:'→ '+story.rooms.find(x=>x.id===r).name,exact:true}));await drain();}
}
async function physicalPuzzle(a,box){await box.locator('.ga-physical').scrollIntoViewIfNeeded();
 if(currentMode==='A'&&a.id==='PUNCHCARD_OVERLAY'){await box.locator('[data-punch-layer]').focus();await box.locator('[data-punch-layer]').press('ArrowRight');const draft=await box.locator('label').first().locator('input').inputValue();await page.keyboard.press('Escape');await button('Меню / Esc');await button('Сохранить сейчас');await page.reload();await page.clock.runFor(1000);await button('Продолжить');await drain();await showPanel('objects');await sceneSafeClick(page.locator('.ga-actions').getByRole('button',{name:a.label,exact:true}));await drain();assert.equal(await box.locator('label').first().locator('input').inputValue(),draft,'physical puzzle draft survives real save/reload');checks.push('A: physical puzzle draft saved and restored through player controls');await box.locator('.ga-physical').scrollIntoViewIfNeeded();}

 if(a.id==='PUNCHCARD_OVERLAY'){const layer=box.locator('[data-punch-layer]');await layer.focus();for(let i=0;i<2;i++){const current=Number(await box.locator('label').nth(i).locator('input').inputValue()),delta=Number(a.answer[i])-current;for(let n=0;n<Math.abs(delta);n++)await layer.press(i===0?(delta>0?'ArrowRight':'ArrowLeft'):(delta>0?'ArrowDown':'ArrowUp'));}}
 else if(a.id==='SPECTRUM_MATCH'){for(let i=0;i<3;i++){const strip=box.locator('[data-strip="'+i+'"]');const current=Number(await strip.getAttribute('aria-valuenow')),delta=Number(a.answer[i])-current;if(i===0&&delta){const bounds=await strip.boundingBox(),svg=await box.locator('.ga-physical-board>svg').boundingBox();await page.mouse.move(bounds.x+bounds.width/2,bounds.y+bounds.height/2);await page.mouse.down();await page.mouse.move(bounds.x+bounds.width/2+delta*68*svg.width/640,bounds.y+bounds.height/2,{steps:10});await page.mouse.up();}else{await strip.focus();for(let n=0;n<Math.abs(delta);n++)await strip.press(delta>0?'ArrowRight':'ArrowLeft');}assert.equal(Number(await strip.getAttribute('aria-valuenow')),Number(a.answer[i]));}}
 else{for(let i=0;i<a.fields.length;i++){const cable=box.locator('[data-cable="'+i+'"]'),socket=box.locator('[data-socket="'+a.answer[i]+'"]');if(i===0){const from=await cable.boundingBox(),to=await socket.boundingBox();await page.mouse.move(from.x+from.width/2,from.y+from.height/2);await page.mouse.down();await page.mouse.move(to.x+to.width/2,to.y+to.height/2,{steps:10});await page.mouse.up();}else{await cable.press('Enter');await socket.press('Enter');}assert.equal(await box.locator('label').nth(i).locator('select').inputValue(),String(a.answer[i]));}}
 checks.push(currentMode+': '+a.id+' solved through tangible controls');
}
async function action(id,value){console.log('ACTION',actionCount,id);const a=story.actions.find(a=>a.id===id);await go(a.room);await drain();await showPanel('objects');await sceneSafeClick(page.locator('.ga-actions').getByRole('button',{name:a.label,exact:true}));await drain();
 // Start-signal scenes may precede the instrument, which reopens after Continue.
 const box=page.locator('.ga-dialog');recordPace('action',id,a.text||a.label,a.template==='media'?(story.media.find(m=>m.id===a.media)?.duration||0):0);if(a.template==='document')recordPace('document',a.document,story.documents.find(d=>d.id===a.document)?.text);
 if(a.template==='document'){
  const doc=story.documents.find(d=>d.id===a.document);assert.equal(await box.locator('pre').last().textContent(),doc.text,'canonical document text '+a.document);
  const art=story.illustratedProps?.image?.[story.illustratedProps?.document?.[a.document]];
  if(art){const img=box.locator('img');assert.equal(await img.count(),1);await sameImage(img,art);}
 }
 const item=a.effects?.find(e=>e.item)?.item;
 if(item&&story.inventoryArt?.[item]){const img=box.getByRole('img',{name:await page.evaluate(id=>adventurePlayer.itemName(id),item),exact:true});await sameImage(img,story.inventoryArt[item]);}

 if(a.template==='media'){
   for(let i=0;i<100;i++){const finish=box.getByRole('button',{name:'Завершить просмотр',exact:true});if(await finish.count()){await finish.press('Enter');break;}await box.getByRole('button',{name:'Следующий фрагмент · текстовый режим',exact:true}).press('Enter');if(i===99)throw Error('Media cannot finish '+id);}
 }else if(a.template==='document')await box.getByRole('button',{name:a.readLabel||'Сохранить в журнале',exact:true}).press('Enter');
 else if(['choice','sequence_choice'].includes(a.template)){
  const op=a.options.find(o=>String(o.value)===String(value??a.options[0].value));await box.getByRole('button',{name:op.label,exact:true}).press('Enter');if(a.confirm)await button('Подтвердить'+(a.template==='sequence_choice'?' и подписать':''));
 }else if(['sequence','order'].includes(a.template)){for(const token of a.answer){await box.getByRole('button',{name:String(token),exact:true}).press('Enter');}}
 else if(['PUNCHCARD_OVERLAY','SPECTRUM_MATCH','ANTENNA'].includes(a.id)){await physicalPuzzle(a,box);await button('Проверить');}
 else if(a.answer){for(let i=0;i<a.fields.length;i++){const f=a.fields[i];const field=box.locator('label').nth(i).locator('input,select');if(f.options)await field.selectOption(String(a.answer[i]));else await field.fill(String(a.answer[i]));}await button(a.template==='triple_dial'?'КОНТРОЛЬ':'Проверить');}
 else{await button('Выполнить');if(a.confirm)await button('Подтвердить');}
 actionCount++;await drain();saveProgress();fs.writeFileSync(path.join(out,'latest-'+currentMode+'.json'),await page.evaluate(()=>JSON.stringify(saveObject())));if(currentMode==='A'&&['ANTENNA','PUNCHCARD_OVERLAY','backward_clock','ANALOG_READINGS_OK'].includes(id)){fs.writeFileSync(path.join(out,'earned-'+id+'.json'),await page.evaluate(()=>JSON.stringify(saveObject())));}assert((await state()).done.includes(id),'Action did not complete '+id);
 if(currentMode==='A'&&['backward_clock','ANALOG_READINGS_OK'].includes(id)){await page.waitForFunction(()=>cameraAllowed()&&cache.get(roomId)?.motionCanvas);await page.clock.runFor(500);const before=await page.evaluate(()=>cache.get(roomId).motionCanvas.toDataURL());await page.clock.runFor(600);const after=await page.evaluate(()=>cache.get(roomId).motionCanvas.toDataURL());assert.notEqual(before,after,'authored clock/monitor visibly animates');await button('Меню / Esc');const paused=await page.evaluate(()=>cache.get(roomId).motionTime);await page.clock.runFor(1000);assert.equal(await page.evaluate(()=>cache.get(roomId).motionTime),paused);await button('Вернуться в игру');checks.push('A: '+id+' panorama motion and pause freeze');}

}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox','--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});try{
 for(const mode of process.env.CAMPAIGN_MODES||'ABCD'){if(completedRoutes.includes(mode))continue;currentMode=mode;
 page=await browser.newPage({viewport:{width:960,height:640}});page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 const harness=process.env.CAMPAIGN_UI_HARNESS==='1';let entry=path.join(ROOT,'game/index.html');
 if(harness){entry=path.join(out,'ui-harness.html');const core=fs.readFileSync(path.join(ROOT,'studio/source/adventure-core.js'),'utf8'),ui=fs.readFileSync(path.join(ROOT,'studio/source/adventure-ui.js'),'utf8');fs.writeFileSync(entry,'<!doctype html><meta charset="utf-8"><button id="new">Новая игра</button><script>'+core+'\n'+ui+'</script><script>let currentRoom='+JSON.stringify(story.startRoom)+';const adventurePlayer=new GagarinAdventure.UI('+JSON.stringify(story)+',{room:()=>currentRoom,go:r=>{currentRoom=r},newGame:()=>adventurePlayer.reset()});document.getElementById("new").onclick=()=>adventurePlayer.reset();</script>');}
 await page.clock.install();await page.goto(!harness&&process.env.CAMPAIGN_GAME_URL||require('node:url').pathToFileURL(entry).href);await page.clock.runFor(1000);await button('Новая игра');await drain();
 if(process.env.CAMPAIGN_RESUME==='1'&&fs.existsSync(path.join(out,'latest-'+mode+'.json'))){const restored=JSON.parse(fs.readFileSync(path.join(out,'latest-'+mode+'.json')));await page.locator('#gs-load-file').setInputFiles(path.join(out,'latest-'+mode+'.json'));await page.waitForFunction(n=>adventurePlayer.snapshot().done.length===n,restored.adventure.done.length);await drain();checks.push(mode+': resumed real earned SAVE.json through file input');}
 let didReload=false;
 for(const id of common){if((await state()).done.includes(id))continue;await action(id,id==='false_act'?'NO':undefined);
  if(id==='plate_choice'&&mode==='A'){await go('A');for(let i=0;i<4&&!(await state()).fired.includes('E027');i++){await page.clock.runFor(66000);await drain();}assert((await state()).fired.includes('E027'),'pillow event reached through a real return visit');assert.equal((await state()).variants.A,'A_SECOND_PILLOW');assert(await page.evaluate(()=>game.panoramas.A===game.assets.authored_A_SECOND_PILLOW));await go('C');await go('A');assert.equal((await state()).variants.A,'A_SECOND_PILLOW');checks.push('A: second pillow dent appears on return and persists on revisiting');}
  if(!didReload&&(await state()).chapter===6){const before=await state();await showPanel('routes');await page.locator('.ga-nav').getByRole('button',{name:'Сохранить',exact:true}).press('Enter');await page.reload();await page.clock.runFor(1000);await button('Продолжить');await drain();const after=await state();for(const key of ['chapter','inventory','documents','done'])assert.deepEqual(after[key],before[key],key+' survives reload');didReload=true;checks.push(mode+': save/reload through player menu');}
 }
 await page.locator('.ga-dock').getByRole('button',{name:'Журнал',exact:true}).click();
 const actualInventory=(await state()).inventory;
 assert.equal(await page.locator('.ga-item').count(),actualInventory.length);
 assert.equal(await page.locator('.ga-item img').count(),actualInventory.length,'each acquired item has art');
 for(const img of await page.locator('.ga-item img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());}
 await button('Закрыть');checks.push(mode+': all acquired inventory art decoded');
 assert.equal((await state()).chapter,11);checks.push('New game through chapters 1–11 using visible controls');
 // All branching is played through the same actual game; checkpoints are the player-facing restore control.
 for(const id of ['NODE_POWER','NODE_MEMORY','NODE_OBSERVER'])if(!(await state()).done.includes(id))await action(id,id==='NODE_MEMORY'?(mode==='D'?'PETR':'TRUTH'):id==='NODE_OBSERVER'?(mode==='B'?2:1):undefined);
  for(const id of final)if(!(await state()).done.includes(id))await action(id,id==='name_reply'?({A:'NO',B:'SILENCE',C:'OFF',D:'NO'}[mode]):undefined);
  await page.screenshot({path:path.join(out,'before-panel.png')});
  await action('FINAL_PANEL',mode);assert.equal((await state()).ended,mode);
  await page.clock.runFor(300);assert(await page.getByRole('dialog',{name:story.endings[mode].title,exact:true}).count());
  const img=page.locator('.ga-dialog img');assert.equal(await img.count(),1);await img.evaluate(i=>i.decode());assert(await img.evaluate(i=>i.complete&&i.naturalWidth>0));
  await page.screenshot({path:path.join(out,`ending-${mode}.png`)});for(let i=0;i<3;i++){const caption=await page.locator('.ga-ending-body .ga-scene').textContent();recordPace('ending',mode+'-'+i,caption);await page.clock.runFor(1600);await button('Продолжить финал');}if(story.voiceAssets){const voiceId={A:'DLG_045',B:'DLG_046',C:'A06',D:'DLG_047'}[mode];await page.waitForFunction(id=>adventurePlayer.voice?.currentId===id&&adventurePlayer.voice.audio.currentTime>.02,voiceId);checks.push(mode+': canonical ending voice actually playing');}await button('Титры');await button('Следующая проверка');assert((await state()).flags.POST_CREDITS);
  checks.push(`Ending ${mode}, illustration, credits and postcredits`);
  await button('Загрузить до панели');await button('Загрузить');assert.equal((await state()).ended,false);assert(!(await state()).done.includes('FINAL_PANEL'));
  completedRoutes.push(mode);saveProgress();await page.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({passed:true,harness:process.env.CAMPAIGN_UI_HARNESS==='1',actionCount,checks,errors,pace,paceMethod:'Reading model at 180 words/minute plus supplied media durations; not a human emotional pacing certification'},null,2));console.log(JSON.stringify({passed:true,actionCount,checks}));
}catch(e){if(page)await page.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({passed:false,actionCount,checks,errors,pace,error:e.stack},null,2));console.error(e.stack);process.exitCode=1;}finally{await browser.close();}})();
