/* Timed, pause-safe scare cues driven by authored story events. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const runtime=fs.readFileSync(path.join(root,'studio/source/game-runtime.html'),'utf8');
const ui=fs.readFileSync(path.join(root,'studio/source/adventure-ui.js'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'game-project/project.json'),'utf8')).story.adventure;
const a=runtime.indexOf('/* HORROR_CUES_BEGIN'),b=runtime.indexOf('/* HORROR_CUES_END */',a);
assert(a>=0&&b>a,'cue director markers must be present');
const source=runtime.slice(a,b+'/* HORROR_CUES_END */'.length);
const layer={style:{},dataset:{}};
const ctx={roomId:'B',sessionStarted:true,sessionPaused:false,
 adventurePlayer:{engine:{state:{flags:{Q02_DONE:true}}}},
 $:id=>id==='horror-cue'?layer:null};
vm.createContext(ctx);vm.runInContext(source+';globalThis.director={horrorCuePlan,horrorCueStart,horrorCueFrame,horrorCueStop,get cue(){return horrorCue;}};',ctx);
const {horrorCuePlan:plan,horrorCueStart:start,horrorCueFrame:frame,horrorCueStop:stop}=ctx.director;
const event=id=>data.events.find(x=>x.id===id);
assert.equal(plan(event('E019')).mode,'apparition','mirror event stages an apparition');
ctx.roomId='C';assert.equal(plan(event('E031')).mode,'temporal','spatial event stages a temporal anomaly');ctx.roomId='B';
assert.equal(plan({...event('E019'),category:'threat'}).mode,'blackout');
assert.equal(plan(event('E012')),null,'ordinary trace is not a generic jump scare');
assert.equal(plan({...event('E019'),category:'quiet'}),null);
assert.equal(plan({...event('E019'),room:'H'}),null,'never trigger distant room scare');
ctx.adventurePlayer.engine.state.flags.Q02_DONE=false;
assert.equal(plan(event('E019')),null,'quiet early game stays quiet');
ctx.adventurePlayer.engine.state.flags.Q02_DONE=true;
const custom={...event('E019'),visualCue:{mode:'temporal',duration:3.2,strength:.5}};
assert.equal(plan(custom).duration,3.2);assert.equal(plan(custom).strength,.5);
assert.equal(plan({...custom,visualCue:{disabled:true}}),null);
assert.equal(plan({...custom,visualCue:{mode:'javascript:alert(1)'}}),null,'reject invalid mode');
assert.equal(start(event('E019')),true);
frame(.13);const progressing=ctx.director.cue.elapsed;
assert(progressing>0&&Number(layer.style.opacity)>0);
ctx.sessionPaused=true;frame(.15);frame(.15);
assert.equal(ctx.director.cue.elapsed,progressing,'pause must freeze cue animation');
assert.equal(layer.style.opacity,'0','pause must hide scare overlay');
ctx.sessionPaused=false;frame(.15);assert(ctx.director.cue.elapsed>progressing);
ctx.roomId='H';frame(.15);assert.equal(ctx.director.cue,null,'room exits clear scene effects');
ctx.roomId='B';start(event('E019'));
for(let i=0;i<100;i++)frame(.15);
assert.equal(ctx.director.cue,null,'timed cue cleans itself up');
assert.equal(layer.style.opacity,'0');
stop();assert.equal(ctx.director.cue,null);
let eligible=0;
for(const ev of data.events){ctx.roomId=ev.room||'B';if(plan(ev))eligible++;}
assert(eligible>=20&&eligible<100,'only meaningful story categories get nonrandom cues');
// The scene dialog must commit the cue when dismissed, not while text is covering the viewport.
const window={GagarinAdventure:{}};
const doc={createElement(tag){return {tag,textContent:'',className:'',setAttribute(){},append(){},remove(){}};}};
vm.runInNewContext(ui,{window,document:doc,console});
const UI=window.GagarinAdventure.UI;let triggered=[],continued=[];
const mock={engine:{state:{room:'B',variants:{B:'B_GHOST_MIRROR'}},cancel(){}},
 hooks:{variant(){},cue:e=>triggered.push(e.id)},panel(){return {append(){}}},
 button(_p,_label,fn){continued.push(fn)},dialog:null,root:{},sync(){},close:UI.prototype.close};
UI.prototype.scene.call(mock,event('E019'));
assert.equal(triggered.length,0,'no scare while player reads scene card');
assert.equal(continued.length,1);
continued[0]();
assert.deepEqual(triggered,['E019'],'cue runs once when scene is dismissed');
UI.prototype.close.call(mock);assert.deepEqual(triggered,['E019'],'closing again cannot replay');
assert(runtime.includes('function resetGame(){horrorCueStop();'));
assert(runtime.includes('async function loadGameSave(data){validateSave(data);horrorCueStop();'));
assert(runtime.includes('cue:horrorCueStart'));
console.log('PASS: '+eligible+' cinematic scenes, gated warmup, pause/resume, room exits, expiry, save/reset, UI close');
