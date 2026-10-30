/* Actual player controls; no story flag/state writes. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const ROOT=path.resolve(__dirname,'../..'),out=path.join(ROOT,'reports/compact-interactions');fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||undefined,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
try{
 await p.goto(process.env.CAMPAIGN_GAME_URL||require('node:url').pathToFileURL(path.join(ROOT,'game/index.html')).href);await p.getByRole('button',{name:'Новая игра',exact:true}).click();
 async function drain(){for(let i=0;i<12;i++){await p.waitForTimeout(220);const b=p.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true});if(await b.count())await b.click();else break;}}
 await p.locator('.ga-dialog').getByRole('button',{name:'Продолжить',exact:true}).waitFor();await drain();
 const marker=p.locator('.ga-hotspot[data-action-id="take_BADGE04"]');
 // Point the actual view at the marker; this changes only the camera, never story state.
 await p.evaluate(()=>{const o=current().objects.find(o=>o.tourKey==='ga:take_BADGE04'),c=centroid(o);yaw=(c.u-.5)*TAU;pitch=(.5-c.v)*Math.PI;refresh();});
 await marker.waitFor({state:'visible'});assert.equal(await marker.evaluate(e=>Math.round(e.getBoundingClientRect().width)),44);
 await marker.focus();assert(await marker.locator('span').isVisible(),'keyboard focus reveals label');await p.keyboard.press('Enter');assert(await p.locator('.ga-dialog').isVisible());
 await p.getByRole('button',{name:'Меню / Esc',exact:true}).click();await p.keyboard.press('Tab');assert(await p.locator('#gs-system').evaluate(e=>e.contains(document.activeElement)),'pause menu owns keyboard focus while a document is open');await p.keyboard.press('Escape');await p.locator('.ga-dialog').waitFor({state:'visible'});
 await p.keyboard.press('Tab');assert(await p.locator('.ga-dialog').evaluate(e=>e.contains(document.activeElement)),'Tab enters modal controls');
 await p.locator('.ga-dialog button').last().focus();await p.keyboard.press('Tab');assert(await p.locator('.ga-dialog').evaluate(e=>document.activeElement===e.querySelector('button')),'Tab wraps inside dialog');
 await p.keyboard.press('Shift+Tab');assert(await p.locator('.ga-dialog').evaluate(e=>document.activeElement===[...e.querySelectorAll('button')].at(-1)),'Shift+Tab wraps inside dialog');
 await p.keyboard.press('Escape');assert(await marker.evaluate(e=>document.activeElement===e),'focus returns to hotspot');
 await marker.click();await p.locator('.ga-dialog').getByRole('button',{name:'Выполнить',exact:true}).click();await drain();assert((await p.evaluate(()=>adventurePlayer.snapshot())).inventory.includes('BADGE04'));assert.equal(await p.locator('.ga-hotspot[data-action-id="take_BADGE04"]').count(),0,'acquired object disappears');
 async function mapGo(name){await p.locator('.ga-dock').getByRole('button',{name:'Схема',exact:true}).click();await p.locator('.ga-dialog').getByRole('button',{name:'→ '+name,exact:true}).click();await drain();}
 await mapGo('Коридор');await p.locator('.ga-dock').getByRole('button',{name:'Схема',exact:true}).click();assert(await p.locator('.ga-dialog').getByRole('button',{name:'→ Архив',exact:true}).isDisabled(),'map respects archive key lock');await p.locator('.ga-dialog').getByRole('button',{name:'Закрыть',exact:true}).click();await mapGo('Кухня');
 await p.waitForFunction(()=>roomId==='B'&&cache.has('B'));assert.equal(await p.evaluate(()=>adventurePlayer.snapshot().room),'B');
 assert(await p.evaluate(()=>current().objects.filter(o=>o.visible&&adventureSign(o)).every(o=>o.states.every(id=>!cache.get(roomId).imgs[id]))),'technical signs are neither loaded nor composited');
 for(const size of [{width:1440,height:900},{width:800,height:700},{width:390,height:844},{width:844,height:390}]){
  await p.setViewportSize(size);await p.locator('.ga-dock').getByRole('button',{name:'Журнал',exact:true}).waitFor();
  const rects=await p.locator('.ga-panel:visible,.ga-dock:visible').evaluateAll(nodes=>nodes.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,scroll:e.scrollWidth,client:e.clientWidth};}));for(const r of rects){assert(r.x>=0&&r.y>=0&&r.x+r.w<=size.width+1&&r.y+r.h<=size.height+1);assert(r.scroll<=r.client+1,'no horizontal overflow');}assert(rects.reduce((n,r)=>n+r.w*r.h,0)<size.width*size.height*.3,'panels leave at least 70% of room unobscured');
  assert(!await p.locator('.ga-variant').isVisible(),'internal state IDs hidden');await p.screenshot({path:path.join(out,'kitchen-'+size.width+'x'+size.height+'.png')});
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({passed:true,checks:['real hotspot acquisition and disappearance','modal focus containment and restoration','map travel and plot lock','technical signs skipped','four viewport layouts'],errors},null,2));console.log('PASS compact player interactions, map, focus and four viewports');
}catch(e){await p.screenshot({path:path.join(out,'failure.png')}).catch(()=>{});throw e;}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
