#!/usr/bin/env node
'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
const {route}=require('./campaign-route.cjs');
const ROOT=path.resolve(__dirname,'../..');const out=process.env.QA_OUTPUT||path.join(ROOT,'reports/browser-current');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const results=[];
 for(const mode of (process.env.QA_MODES||'ABCD')){
  const context=await browser.newContext({viewport:{width:960,height:720}}),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(ROOT,'game/index.html'));await page.getByRole('button',{name:'Новая игра',exact:true}).click();
  // Only event waiting is accelerated. No flags, inventory, chapters or saves are fabricated.
  async function drain(){for(let i=0;i<150;i++){
   const shown=await page.locator('.ga-dialog').count();
   if(shown){const next=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await next.count()){await next.click();continue;}return;}
   const event=await page.evaluate(()=>{const e=adventurePlayer.engine.flush(70);if(e)adventurePlayer.scene(e);return !!e;});if(!event)break;
  }}
  async function go(dest){const steps=await page.evaluate(dest=>{
   const {engine,data}=adventurePlayer,s=engine.state,q=[[s.room,[]]],seen=new Set();
   while(q.length){const [r,p]=q.shift();if(r===dest)return p;if(seen.has(r))continue;seen.add(r);for(const l of data.links.filter(l=>l.from===r&&GagarinAdventure.test(l.when,s)))q.push([l.to,[...p,l.to]]);}throw Error('No available route to '+dest);
  },dest);
   for(const room of steps){await drain();const name=await page.evaluate(id=>adventurePlayer.data.rooms.find(r=>r.id===id).name,room);await page.locator('.ga-nav').getByRole('button',{name:'→ '+name,exact:true}).click();await drain();}
  }
  await drain();let count=0,saved=false;
  for(const step of route){if(step.room){await go(step.room);continue;}
   const [id,raw]=Array.isArray(step)?step:[step];const a=await page.evaluate(id=>adventurePlayer.data.actions.find(a=>a.id===id),id);await go(a.room);await drain();
   await page.locator('.ga-actions').getByRole('button',{name:a.label,exact:true}).click();const dialog=page.locator('.ga-dialog');
   const value=typeof raw==='function'?raw(mode):raw??a.answer??a.options?.[0]?.value;
   if(a.template==='media'){
    const media=await page.evaluate(id=>adventurePlayer.data.media.find(m=>m.id===id),a.media);
    for(let i=0;i<media.frames.length;i++)await dialog.getByRole('button',{name:'Следующий фрагмент · текстовый режим',exact:true}).click();
    await dialog.getByRole('button',{name:'Завершить просмотр',exact:true}).click();
   }else if(a.template==='document')await dialog.getByRole('button',{name:a.readLabel||'Сохранить в журнале',exact:true}).click();
   else if(a.template==='choice'||a.template==='sequence_choice'){
    const opt=a.options.find(o=>String(o.value)===String(value));await dialog.getByRole('button',{name:opt.label,exact:true}).click();
    if(a.confirm)await dialog.getByRole('button',{name:'Подтвердить'+(a.template==='sequence_choice'?' и подписать':''),exact:true}).click();
   }else if(a.template==='sequence'||a.template==='order'){for(const token of a.answer)await dialog.getByRole('button',{name:token,exact:true}).click();}
   else if(a.answer){const fields=dialog.locator('label');for(let i=0;i<a.fields.length;i++){const f=fields.nth(i);if(a.fields[i].options)await f.locator('select').selectOption(String(a.answer[i]));else await f.locator('input').fill(String(a.answer[i]));}await dialog.getByRole('button',{name:a.template==='triple_dial'?'КОНТРОЛЬ':'Проверить',exact:true}).click();}
   else {await dialog.getByRole('button',{name:'Выполнить',exact:true}).click();if(a.confirm)await dialog.getByRole('button',{name:'Подтвердить',exact:true}).click();}
   count++;if(count%20===0)console.log(mode,'interactions',count);await drain();
   const state=await page.evaluate(()=>({chapter:adventurePlayer.engine.state.chapter,done:adventurePlayer.engine.state.done,inventory:adventurePlayer.engine.state.inventory}));assert(state.done.includes(id),mode+': action failed '+id);
   if(state.chapter===6&&!saved){await page.locator('.ga-nav').getByRole('button',{name:'Сохранить',exact:true}).click();await page.reload();await page.getByRole('button',{name:'Продолжить',exact:true}).click();await drain();const loaded=await page.evaluate(()=>({chapter:adventurePlayer.engine.state.chapter,done:adventurePlayer.engine.state.done,inventory:adventurePlayer.engine.state.inventory}));assert.deepEqual(loaded,state);saved=true;}
   if(id==='read_D17'&&mode==='A')await page.screenshot({path:path.join(out,'chapter10.png')});
  }
  await page.waitForTimeout(300);await page.waitForFunction(()=>adventurePlayer.engine.state.ended&&adventurePlayer.endingShown);
  assert.equal(await page.evaluate(()=>adventurePlayer.engine.state.ended),mode);
  await page.waitForFunction(()=>{const i=document.querySelector('.ga-dialog img');return i&&i.complete&&i.naturalWidth>0;});await page.screenshot({path:path.join(out,'ending-'+mode+'.png')});
  while(await page.locator('.ga-dialog').getByRole('button',{name:'Продолжить финал',exact:true}).count())await page.locator('.ga-dialog').getByRole('button',{name:'Продолжить финал',exact:true}).click();
  await page.locator('.ga-dialog').getByRole('button',{name:'Титры',exact:true}).click();await page.locator('.ga-dialog').getByRole('button',{name:'Следующая проверка',exact:true}).click();await page.locator('.ga-dialog').getByRole('button',{name:'Новая игра',exact:true}).click();
  assert.equal(await page.evaluate(()=>adventurePlayer.endingShown),false);assert.equal(await page.evaluate(()=>adventurePlayer.engine.state.chapter),1);assert.deepEqual(errors,[]);
  results.push({ending:mode,interactions:count,saveReload:saved,credits:true,newGame:true,browserErrors:errors});console.log('PASS',mode,count);await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({passed:true,results,note:'Automated DOM clicks; event waiting accelerated through engine.flush. Not human pacing or fear assessment.'},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
