/* Read the player's objective, follow its map and complete the first three chapters through UI. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..'),out=path.join(ROOT,'reports/player-guidance-browser');fs.mkdirSync(out,{recursive:true});
const story=JSON.parse(fs.readFileSync(path.join(ROOT,'studio/content/TIHAYA_VODA/adventure.json')));
let page,actions=0;const errors=[];
const press=async locator=>{await locator.waitFor({state:'visible'});await locator.focus();await locator.press('Enter');};
const button=name=>press(page.getByRole('button',{name,exact:true}));
const snapshot=()=>page.evaluate(()=>adventurePlayer.snapshot());
async function drain(){for(let n=0;n<30;n++){await page.clock.runFor(600);const next=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await next.isVisible()){await press(next);continue;}if(!await page.locator('.ga-dialog').count())return;return;}throw Error('Scene did not settle');}
async function objective(){await press(page.getByRole('button',{name:/^Текущая цель:/}));assert.equal(await page.getByRole('button',{name:'Задачи',exact:true}).getAttribute('aria-pressed'),'true');return page.locator('.ga-dialog>.ga-journal-list .ga-task-current').first();}
async function guidedAction(){
 let card=await objective(),id=await card.getAttribute('data-action-id');const a=story.actions.find(a=>a.id===id);assert(a,'The visible objective identifies a real action');
 for(let n=0;(await snapshot()).room!==a.room;n++){
  assert(n<12,'Objective route must terminate');await button('Показать путь на схеме');
  const hop=page.locator('.ga-map-next').getByRole('button');assert.equal(await hop.count(),1,'Map identifies one actual adjacent route');assert(await hop.isEnabled());await press(hop);await drain();card=await objective();assert.equal(await card.getAttribute('data-action-id'),id,'Navigation preserves unfinished objective');
 }
 if(await page.getByRole('button',{name:'Вернуться к осмотру',exact:true}).isVisible()){await button('Вернуться к осмотру');await drain();return;}
 await button('К объектам в комнате');const target=page.locator('.ga-actions [data-action-id="'+id+'"]');assert(await target.isVisible());assert((await target.getAttribute('class')||'').includes('ga-recommended'),'Real object is visibly recommended');await press(target);await drain();const box=page.locator('.ga-dialog');
 if(a.template==='document'){assert.equal(await box.locator('pre').last().textContent(),story.documents.find(d=>d.id===a.document).text);await button(a.readLabel||'Сохранить в журнале');}
 else if(a.template==='media'){for(let n=0;n<100;n++){const finish=box.getByRole('button',{name:'Завершить просмотр',exact:true});if(await finish.count()){await press(finish);break;}await press(box.getByRole('button',{name:'Следующий фрагмент · текстовый режим',exact:true}));if(n===99)throw Error('Media cannot finish');}}
 else if(a.answer&&a.template!=='sequence'&&a.template!=='order'){
  const entered=[];for(let n=0;n<a.fields.length;n++){const field=box.locator('label').nth(n).locator('input,select');if(a.fields[n].options)await field.selectOption(String(a.answer[n]));else await field.fill(String(a.answer[n]));entered.push(await field.inputValue());}
  if(id==='POWER_BASIC'){
   const img=box.locator('.ga-inspection img');await img.evaluate(i=>i.decode());assert(await img.evaluate(i=>i.naturalWidth===1536&&i.naturalHeight===1024));
   await press(box.locator('.ga-inspection button'));assert(await page.locator('.ga-art-view').isVisible());await page.locator('.ga-art-view img').evaluate(i=>i.decode());await page.screenshot({path:path.join(out,'power-inspection.png')});await button('К прибору');
   for(let n=0;n<entered.length;n++)assert.equal(await box.locator('label').nth(n).locator('input,select').inputValue(),entered[n],'Inspecting artwork preserves entered settings');
  }
  await button(a.template==='triple_dial'?'КОНТРОЛЬ':'Проверить');
 }else if(a.template==='sequence'||a.template==='order'){for(const token of a.answer)await press(box.getByRole('button',{name:String(token),exact:true}));}
 else if(a.template==='choice'||a.template==='sequence_choice'){await press(box.getByRole('button',{name:a.options[0].label,exact:true}));if(a.confirm)await button('Подтвердить'+(a.template==='sequence_choice'?' и подписать':''));}
 else{await button('Выполнить');if(a.confirm)await button('Подтвердить');}
 await drain();assert((await snapshot()).done.includes(id),'Actual action completed: '+id);actions++;
}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox','--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});try{
 page=await browser.newPage({viewport:{width:1440,height:900}});page.on('pageerror',e=>errors.push(e.message));await page.clock.install();await page.goto(process.env.CAMPAIGN_GAME_URL||require('node:url').pathToFileURL(path.join(ROOT,'game/index.html')).href,{waitUntil:'domcontentloaded'});await page.clock.runFor(1000);await button('Новая игра');await drain();
 for(const [width,height]of [[1440,900],[390,844],[844,390]]){await page.setViewportSize({width,height});await objective();assert.equal(await page.locator('.ga-task-current').count(),1,'Future branch is hidden at start');assert(!await page.getByText('Остановить контур',{exact:true}).count(),'Future quest is not disclosed');assert(!await page.locator('.ga-journal-search').isVisible());assert(!await page.locator('#gameLanguage').isVisible(),'Language control does not overlap the journal');const toolbar=await page.locator('#gs-quick').boundingBox(),dialog=await page.locator('.ga-dialog').boundingBox();assert(toolbar.y+toolbar.height<=dialog.y,'Pause control stays outside the reading surface');await page.screenshot({path:path.join(out,`tasks-${width}x${height}.png`)});await button('Закрыть');}
 await page.setViewportSize({width:960,height:640});
 let iterations=0;while((await snapshot()).chapter<4){assert(++iterations<32&&actions<24,'Guided route advances');await guidedAction();}
 await objective();const before=await page.locator('.ga-task-current').first().getAttribute('data-action-id');assert.equal(before,'read_D20');await button('Закрыть');await button('Меню / Esc');await button('Сохранить сейчас');await page.reload({waitUntil:'domcontentloaded'});await page.clock.runFor(1000);await button('Продолжить');await drain();await objective();assert.equal(await page.locator('.ga-task-current').first().getAttribute('data-action-id'),before,'Actual menu save/load restores current objective');await page.screenshot({path:path.join(out,'chapter-4-after-load.png')});
 assert.deepEqual(errors,[]);const result={passed:true,actualUiActions:actions,checks:['Visible current objective','No future plot or branch at start','Three viewport layouts','Actual route through task map','Recommended object activation','Full-size inspection artwork','Instrument draft retained','Save/load restores objective'],errors};fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}catch(error){if(page)await page.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});console.error(error.stack);process.exitCode=1;}finally{await browser.close();}})();
