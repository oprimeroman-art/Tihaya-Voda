/* Full renderer smoke + UI import of existing route-earned legacy saves. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'reports/player-smoke');fs.mkdirSync(dir,{recursive:true});
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox','--allow-file-access-from-files']});let p,errors=[],checks=[];try{
 for(const mode of 'ABCD'){
  p=await b.newPage({viewport:{width:1024,height:768}});p.on('pageerror',e=>errors.push(e.message));p.on('dialog',d=>d.accept());
  await p.goto(require('node:url').pathToFileURL(path.join(root,'game/index.html')).href);
  await p.getByRole('button',{name:'Загрузить SAVE.json',exact:true}).click({noWaitAfter:true});
  await p.locator('#gs-load-file').setInputFiles(path.join(root,`reports/SAVE_BEFORE_${mode}.json`));
  await p.waitForFunction(()=>typeof adventurePlayer!=='undefined'&&adventurePlayer?.engine.state.chapter===12);
  for(let i=0;i<10;i++){const c=p.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await c.count())await c.click({noWaitAfter:true});else break;}
  const s=await p.evaluate(()=>adventurePlayer.snapshot());if(s.room!=='P'){const dest=await p.evaluate(()=>adventurePlayer.data.rooms.find(r=>r.id==='P').name);await p.locator('.ga-nav').getByRole('button',{name:'→ '+dest,exact:true}).click({noWaitAfter:true});}
  await p.locator('.ga-actions').getByRole('button',{name:'Выбрать режим и поставить подпись',exact:true}).click({noWaitAfter:true});
  const cont=p.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await cont.count())await cont.click({noWaitAfter:true});
  const option=await p.evaluate(m=>adventurePlayer.data.actions.find(a=>a.id==='FINAL_PANEL').options.find(o=>o.value===m).label,mode);
  await p.locator('.ga-dialog').getByRole('button',{name:option,exact:true}).click({noWaitAfter:true});await p.getByRole('button',{name:'Подтвердить и подписать',exact:true}).click({noWaitAfter:true});
  await p.waitForFunction(m=>adventurePlayer.engine.state.ended===m,mode);
  await p.getByRole('button',{name:'Титры',exact:true}).waitFor();assert(await p.locator('.ga-dialog img').evaluate(i=>i.complete&&i.naturalWidth>0));
  await p.screenshot({path:path.join(dir,'ending-'+mode+'.png')});await p.getByRole('button',{name:'Титры',exact:true}).click({noWaitAfter:true});await p.getByRole('button',{name:'Следующая проверка',exact:true}).click({noWaitAfter:true});
  assert(await p.evaluate(()=>adventurePlayer.engine.state.flags.POST_CREDITS));checks.push(mode+': real renderer, legacy save imported, signed mode, image loaded, credits and postcredits');await p.close();console.log(checks.at(-1));
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify({passed:true,checks,errors,note:'Legacy save import smoke; does not replace a fresh whole-game route.'},null,2));
}catch(e){if(p)await p.screenshot({path:path.join(dir,'failure.png')}).catch(()=>{});fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify({passed:false,checks,errors,error:e.stack},null,2));console.error(e.stack);process.exitCode=1;}finally{await b.close();}})();
