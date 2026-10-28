/* UI-only route: no developer commands, no writes to engine state. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..'),out=path.join(ROOT,'reports/campaign-browser');fs.mkdirSync(out,{recursive:true});
const story=JSON.parse(fs.readFileSync(path.join(ROOT,'studio/content/TIHAYA_VODA/adventure.json')));
const {test}=require('../source/adventure-core.js');
const common=`take_BADGE04 take_STORAGE_KEY read_D01 TEA_SEQUENCE sign_shift take_FUSE_3 install_fuse3 read_D28 POWER_BASIC CORES_MARKING RADIO_TUNE send_report read_D19 PLUMB_SEQ watch_V01 mirror03 cabinet_message archive_return read_D20 count_cans read_D16 COOKING mirror04 mirror04_away mirror04_again mirror04_third plate_choice dinner_exit take_P17_SAMPLE SPECTRUM_MATCH MICROSCOPE read_D06 hidden_enter read_D03 hidden_exit WAVE_PHASE watch_A02 watch_A01 read_D02 read_D27 mirror06 mirror06_again read_D07 flip_acts read_D22 take_FLASHLIGHT take_ANTENNA_KEY take_BEACON ice_1 ice_2 ice_3 ANTENNA glass07 AIRLOCK_EQUALIZE inner_door take_VHS_FRAGMENT_A take_VHS_FRAGMENT_B read_D23 VHS_ASSEMBLE watch_V02 read_D13 read_D29 read_D05 take_VHS_V03 watch_V03 petr_letter wet_towel read_D04 read_D09 read_D21 take_PUNCHCARD_RU take_PUNCHCARD_DE PUNCHCARD_OVERLAY scan_uv enter_1978 read_D08 read_D12 calibration_plate watch_V06 watch_V09 watch_A03 exit_1978 read_D17 read_D18 watch_A04 CARDIOMATCH medic10 TIMELINE_SYNC watch_V04 late10 read_D14 read_D11 read_D15 watch_V08 handwriting_floor backward_clock reversed_exit_arrow leave_N false_act blanket11 watch_V01B`.split(' ');
const final=`SHUTTERS name_reply second_window third_window POWER_OFF take_SHUTTER_PIN PIN_INSERT ANALOG_READINGS_OK OBSERVER_SELECT`.split(' ');
let page,checks=[],errors=[],actionCount=0;
const state=()=>page.evaluate(()=>adventurePlayer.snapshot());
async function button(text){const b=page.getByRole('button',{name:text,exact:true});await b.click({timeout:10000,noWaitAfter:true});}
async function drain(){for(let i=0;i<35;i++){
 await page.clock.runFor(200);
 const cont=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await cont.count()){await cont.click({noWaitAfter:true});continue;}
 if(await page.locator('.ga-dialog').count())return;
 const s=await state();const pending=s.pending.map(p=>({p,e:story.events.find(e=>e.id===p.id)})).filter(({e})=>e&&(!e.room||e.room===s.room)&&test(e.when,s)&&e.priority!=='optional');
 if(!pending.length)return;const wait=Math.max(0,Math.min(...pending.map(({p})=>p.due))-s.clock);await page.clock.runFor(Math.ceil(wait*1000)+200);
 }throw Error('Event queue did not settle');}
async function sceneSafeClick(locator){for(let i=0;i<15;i++){try{await locator.click({timeout:1200,noWaitAfter:true});return;}catch(error){const c=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(!await c.count())throw error;await c.click({noWaitAfter:true});await drain();}}throw Error('Repeated scene interruptions');}
async function go(dest){let s=await state();if(s.room===dest)return;let queue=[[s.room,[]]],seen=new Set(),route;
 while(queue.length){const[r,steps]=queue.shift();if(r===dest){route=steps;break;}if(seen.has(r))continue;seen.add(r);for(const l of story.links.filter(l=>l.from===r&&test(l.when,s)))queue.push([l.to,[...steps,l.to]]);}
 assert(route,`No route ${s.room} to ${dest}, chapter ${s.chapter}`);
 for(const r of route){await drain();await sceneSafeClick(page.locator('.ga-nav').getByRole('button',{name:'→ '+story.rooms.find(x=>x.id===r).name,exact:true}));await drain();}
}
async function action(id,value){console.log('ACTION',actionCount,id);const a=story.actions.find(a=>a.id===id);await go(a.room);await drain();await sceneSafeClick(page.locator('.ga-actions').getByRole('button',{name:a.label,exact:true}));await drain();
 // Start-signal scenes may precede the instrument, which reopens after Continue.
 const box=page.locator('.ga-dialog');
 if(a.template==='document'){
  const doc=story.documents.find(d=>d.id===a.document);assert.equal(await box.locator('pre').last().textContent(),doc.text,'canonical document text '+a.document);
  const art=story.illustratedProps?.image?.[story.illustratedProps?.document?.[a.document]];
  if(art){const img=box.locator('img');assert.equal(await img.count(),1);assert.equal(await img.getAttribute('src'),art);await img.evaluate(i=>i.decode());}
 }
 const item=a.effects?.find(e=>e.item)?.item;
 if(item&&story.inventoryArt?.[item]){const img=box.locator('img').last();assert.equal(await img.getAttribute('src'),story.inventoryArt[item]);await img.evaluate(i=>i.decode());}

 if(a.template==='media'){
   for(let i=0;i<100;i++){const finish=box.getByRole('button',{name:'Завершить просмотр',exact:true});if(await finish.count()){await finish.click({noWaitAfter:true});break;}await box.getByRole('button',{name:'Следующий фрагмент · текстовый режим',exact:true}).click({noWaitAfter:true});if(i===99)throw Error('Media cannot finish '+id);}
 }else if(a.template==='document')await box.getByRole('button',{name:a.readLabel||'Сохранить в журнале',exact:true}).click({noWaitAfter:true});
 else if(['choice','sequence_choice'].includes(a.template)){
  const op=a.options.find(o=>String(o.value)===String(value??a.options[0].value));await box.getByRole('button',{name:op.label,exact:true}).click({noWaitAfter:true});if(a.confirm)await button('Подтвердить'+(a.template==='sequence_choice'?' и подписать':''));
 }else if(['sequence','order'].includes(a.template)){for(const token of a.answer)await box.getByRole('button',{name:String(token),exact:true}).click({noWaitAfter:true});}
 else if(a.answer){for(let i=0;i<a.fields.length;i++){const f=a.fields[i];const field=box.locator('label').nth(i).locator('input,select');if(f.options)await field.selectOption(String(a.answer[i]));else await field.fill(String(a.answer[i]));}await button(a.template==='triple_dial'?'КОНТРОЛЬ':'Проверить');}
 else{await button('Выполнить');if(a.confirm)await button('Подтвердить');}
 actionCount++;await drain();assert((await state()).done.includes(id),'Action did not complete '+id);
}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox','--allow-file-access-from-files']});try{
 for(const mode of 'ABCD'){
 page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 const harness=process.env.CAMPAIGN_UI_HARNESS==='1';let entry=path.join(ROOT,'game/index.html');
 if(harness){entry=path.join(out,'ui-harness.html');const core=fs.readFileSync(path.join(ROOT,'studio/source/adventure-core.js'),'utf8'),ui=fs.readFileSync(path.join(ROOT,'studio/source/adventure-ui.js'),'utf8');fs.writeFileSync(entry,'<!doctype html><meta charset="utf-8"><button id="new">Новая игра</button><script>'+core+'\n'+ui+'</script><script>let currentRoom='+JSON.stringify(story.startRoom)+';const adventurePlayer=new GagarinAdventure.UI('+JSON.stringify(story)+',{room:()=>currentRoom,go:r=>{currentRoom=r},newGame:()=>adventurePlayer.reset()});document.getElementById("new").onclick=()=>adventurePlayer.reset();</script>');}
 await page.clock.install();await page.goto(require('node:url').pathToFileURL(entry).href);await page.clock.runFor(1000);await button('Новая игра');await drain();
 let didReload=false;
 for(const id of common){await action(id,id==='false_act'?'NO':undefined);
  if(!didReload&&(await state()).chapter===6){const before=await state();await page.locator('.ga-nav').getByRole('button',{name:'Сохранить',exact:true}).click();await page.reload();await page.clock.runFor(1000);await button('Продолжить');await drain();const after=await state();for(const key of ['chapter','inventory','documents','done'])assert.deepEqual(after[key],before[key],key+' survives reload');didReload=true;checks.push(mode+': save/reload through player menu');}
 }
 await page.locator('.ga-actions').getByRole('button',{name:'Журнал и инвентарь',exact:true}).click();
 const actualInventory=(await state()).inventory;
 assert.equal(await page.locator('.ga-item').count(),actualInventory.length);
 assert.equal(await page.locator('.ga-item img').count(),actualInventory.length,'each acquired item has art');
 for(const img of await page.locator('.ga-item img').all())await img.evaluate(i=>i.decode());
 await button('Закрыть');checks.push(mode+': all acquired inventory art decoded');
 assert.equal((await state()).chapter,11);checks.push('New game through chapters 1–11 using visible controls');
 // All branching is played through the same actual game; checkpoints are the player-facing restore control.
 await action('NODE_POWER');await action('NODE_MEMORY',mode==='D'?'PETR':'TRUTH');await action('NODE_OBSERVER',mode==='B'?2:1);
  for(const id of final)await action(id,id==='name_reply'?({A:'NO',B:'SILENCE',C:'OFF',D:'NO'}[mode]):undefined);
  await page.screenshot({path:path.join(out,'before-panel.png')});
  await action('FINAL_PANEL',mode);assert.equal((await state()).ended,mode);
  await page.clock.runFor(300);assert(await page.getByRole('dialog',{name:story.endings[mode].title,exact:true}).count());
  const img=page.locator('.ga-dialog img');assert.equal(await img.count(),1);assert(await img.evaluate(i=>i.complete&&i.naturalWidth>0));
  await page.screenshot({path:path.join(out,`ending-${mode}.png`)});for(let i=0;i<3;i++)await button('Продолжить финал');if(story.voiceAssets){const voiceId={A:'DLG_045',B:'DLG_046',C:'A06',D:'DLG_047'}[mode];await page.waitForFunction(id=>adventurePlayer.voice?.currentId===id&&adventurePlayer.voice.audio.currentTime>.02,voiceId);checks.push(mode+': canonical ending voice actually playing');}await button('Титры');await button('Следующая проверка');assert((await state()).flags.POST_CREDITS);
  checks.push(`Ending ${mode}, illustration, credits and postcredits`);
  await button('Загрузить до панели');await button('Загрузить');assert.equal((await state()).ended,false);assert(!(await state()).done.includes('FINAL_PANEL'));
  await page.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({passed:true,harness:process.env.CAMPAIGN_UI_HARNESS==='1',actionCount,checks,errors},null,2));console.log(JSON.stringify({passed:true,actionCount,checks}));
}catch(e){if(page)await page.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({passed:false,actionCount,checks,errors,error:e.stack},null,2));console.error(e.stack);process.exitCode=1;}finally{await browser.close();}})();
