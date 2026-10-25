const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),assert=require('assert/strict');
const root='C:/Users/user/Desktop/TIHAYA_VODA_CODEX_PACK_V2',studio=root+'/Gagarin_Panorama_Studio_2_8_RU_EN_OFFLINE/Gagarin_Panorama_Studio_2_8';
const out=path.resolve(__dirname,'../outputs'),sleep=ms=>new Promise(r=>setTimeout(r,ms));
const port=9500+Math.floor(Math.random()*2000);
const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless=new','--no-first-run','--no-default-browser-check','--disable-gpu','--remote-debugging-port='+port,'--remote-allow-origins=*','--allow-file-access-from-files','--user-data-dir='+path.resolve(__dirname,'chrome-test-'+Date.now()),'--window-size=1440,1000','about:blank'],{windowsHide:true,stdio:'ignore'});
let sock,seq=0,requests=new Map(),errors=[],checks=[];
async function cmd(method,params={}){const id=++seq;return new Promise((resolve,reject)=>{requests.set(id,{resolve,reject});sock.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(requests.has(id)){requests.delete(id);reject(Error('Timeout '+method));}},25000).unref();});}
async function ev(expression){const r=await cmd('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result?.value;}
async function until(expression,ms=25000){const end=Date.now()+ms;while(Date.now()<end){if(await ev(expression))return;await sleep(180);}throw Error('Wait failed '+expression+' '+await ev('document.body?.innerText.slice(0,2500)'));}
async function navigate(file){let r;for(let i=0;i<3;i++){r=await cmd('Page.navigate',{url:require('url').pathToFileURL(file).href});if(!r.errorText){await sleep(800);return;}if(r.errorText!=='net::ERR_ABORTED')break;await sleep(1000);}throw Error('Navigation: '+r.errorText);}
async function screenshot(name){const r=await cmd('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,name),Buffer.from(r.data,'base64'));}
async function importFile(file){const doc=await cmd('DOM.getDocument');const node=await cmd('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'#projectFile'});await cmd('DOM.setFileInputFiles',{nodeId:node.nodeId,files:[file]});}
async function dismissEvents(){for(let i=0;i<30;i++){const did=await ev(`(()=>{const b=[...document.querySelectorAll('.ga-dialog button')].find(b=>b.textContent==='Продолжить');if(b)b.click();return !!b})()`);await sleep(180);if(!did&&!(await ev(`!!adventurePlayer.engine.state.pending.find(p=>{const e=adventurePlayer.data.events.find(e=>e.id===p.id);return (!e.room||e.room===adventurePlayer.engine.state.room)&&p.due<=adventurePlayer.engine.state.clock})`)))break;}}
async function clickAction(id){await dismissEvents();await ev(`adventurePlayer.openAction(${JSON.stringify(id)})`);await until(`!!document.querySelector('.ga-dialog')`);}
async function clickText(text){const ok=await ev(`(()=>{const b=[...document.querySelectorAll('.ga-dialog button')].find(b=>b.textContent===${JSON.stringify(text)}&&!b.disabled);if(b)b.click();return !!b})()`);assert(ok,'Button missing '+text);await sleep(200);}
(async()=>{try{
 let tabs;for(let i=0;i<50;i++){try{tabs=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();break;}catch{await sleep(200);}}
 assert(tabs,'Chrome did not start');sock=new WebSocket(tabs[0].webSocketDebuggerUrl);await new Promise(r=>sock.onopen=r);sock.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=requests.get(m.id);if(p){requests.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Page.javascriptDialogOpening')cmd('Page.handleJavaScriptDialog',{accept:false}).catch(()=>{});};
 await cmd('Page.enable');await cmd('Runtime.enable');await cmd('DOM.enable');

 for(const url of ['data:text/html,<h1>probe</h1>',require('url').pathToFileURL(studio+'/index.html').href,require('url').pathToFileURL(path.join(out,'GAME/index.html')).href]){
 console.log('URL',url);console.log('NAV',JSON.stringify(await cmd('Page.navigate',{url})));await sleep(1500);console.log('DOM',JSON.stringify(await ev('({href:location.href,ready:document.readyState,text:document.body?.innerText.slice(0,300)})')));}
 console.log('ERRORS',errors);
}catch(e){console.error(e);}finally{try{await cmd('Browser.close')}catch{}sock?.close();chrome.kill();}})();
