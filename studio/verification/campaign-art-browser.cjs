#!/usr/bin/env node
'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../..'),OUT=process.env.QA_OUTPUT||path.join(ROOT,'reports/browser-current');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('file://'+path.join(ROOT,'game/index.html'));await page.getByRole('button',{name:'Новая игра',exact:true}).click();
 for(const mode of 'ABCD'){
  const save=JSON.parse(fs.readFileSync(path.join(process.env.QA_SAVE_DIR,mode+'.json')));
  // These checkpoints were produced by campaign-complete.test.cjs from fresh games.
  await page.evaluate(save=>adventurePlayer.load(save),save);
  for(let i=0;i<10;i++){await page.waitForTimeout(200);const next=page.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(!await next.count())break;await next.click();}
  await page.locator('.ga-actions').getByRole('button',{name:'Журнал и инвентарь',exact:true}).click();
  await page.waitForFunction(()=>[...document.querySelectorAll('.ga-item img')].every(i=>i.complete&&i.naturalWidth>0));
  assert.equal(await page.locator('.ga-item img').count(),15,'all acquired items have visible icons');
  assert.equal(await page.locator('.ga-item').count(),15,'no uncatalogued items without art');
  if(mode==='A'){await page.screenshot({path:path.join(OUT,'inventory.png')});await page.locator('.ga-item').first().click();await page.waitForFunction(()=>document.querySelector('.ga-dialog img')?.naturalWidth>0);await page.getByRole('button',{name:'К журналу',exact:true}).click();}
  await page.getByRole('button',{name:'Закрыть',exact:true}).click();
  // Invalid saves must keep the currently open dialog and the running state.
  await page.locator('.ga-actions').getByRole('button',{name:'Журнал и инвентарь',exact:true}).click();
  assert.equal(await page.evaluate(()=>{const before=JSON.stringify(adventurePlayer.snapshot()),dialog=adventurePlayer.dialog;try{adventurePlayer.load({project:'wrong'});}catch{return before===JSON.stringify(adventurePlayer.snapshot())&&adventurePlayer.dialog===dialog;}return false;}),true);
  await page.getByRole('button',{name:'Закрыть',exact:true}).click();
  await page.locator('.ga-actions').getByRole('button',{name:'Выбрать режим и поставить подпись',exact:true}).click();
  const label=await page.evaluate(mode=>adventurePlayer.data.actions.find(a=>a.id==='FINAL_PANEL').options.find(o=>o.value===mode).label,mode);
  await page.locator('.ga-dialog').getByRole('button',{name:label,exact:true}).click();await page.getByRole('button',{name:'Подтвердить и подписать',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.ga-dialog img')?.naturalWidth>0);
  let shots=1;while(await page.getByRole('button',{name:'Продолжить финал',exact:true}).count()){await page.getByRole('button',{name:'Продолжить финал',exact:true}).click();shots++;}
  assert.equal(shots,4);await page.screenshot({path:path.join(OUT,'staged-ending-'+mode+'.png')});
  await page.keyboard.press('Escape');await page.getByRole('button',{name:'Финал и титры',exact:true}).click();
  while(await page.getByRole('button',{name:'Продолжить финал',exact:true}).count())await page.getByRole('button',{name:'Продолжить финал',exact:true}).click();
  await page.getByRole('button',{name:'Титры',exact:true}).click();await page.getByRole('button',{name:'Следующая проверка',exact:true}).click();await page.getByRole('button',{name:'Новая игра',exact:true}).click();
  assert.equal(await page.evaluate(()=>adventurePlayer.endingShown),false);console.log('PASS art, inventory, save rejection, four ending beats, credits and new game:',mode);
 }
 assert.deepEqual(errors,[]);await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
