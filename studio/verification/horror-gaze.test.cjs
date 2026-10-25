/* Story-controlled mirror ghosts disappear on deliberate gaze and stay gone in saves. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const R=path.resolve(__dirname,'../..');
const runtime=fs.readFileSync(path.join(R,'studio/source/game-runtime.html'),'utf8');
const a=runtime.indexOf('/* HORROR_VISUALS_BEGIN'), b=runtime.indexOf('/* HORROR_VISUALS_END */',a);
assert(a>=0&&b>a,'The visuals module must be present');
const visuals=runtime.slice(a,b+'/* HORROR_VISUALS_END */'.length);
const story=JSON.parse(fs.readFileSync(path.join(R,'game-project/project.json'),'utf8')).story.adventure;
const state={flags:{Q02_DONE:true},progress:{},variants:{B:'B_GHOST_MIRROR'}};
const atmosphere={dataset:{},style:{}},figure={style:{}},canvas={style:{}};
let point={x:500,y:500},saves=0;
const ctx={game:{story:{adventure:story}},canvas,roomId:'B',sessionStarted:true,sessionPaused:false,
 innerWidth:1000,innerHeight:1000,
 adventurePlayer:{engine:{state,modal:false}},
 $:id=>id==='horror-atmosphere'?atmosphere:id==='horror-apparition'?figure:null,
 project(){return point},scheduleGameSave(){saves++},console};
vm.createContext(ctx);
vm.runInContext(visuals+';globalThis.gaze={paint:horrorPaint,get active(){return horrorGazeActive},get hold(){return horrorGazeHold}};',ctx);
const gaze=ctx.gaze;
gaze.paint();assert(gaze.active,'a visible mirror ghost is gaze-reactive');
assert.equal(figure.style.display,'block');
gaze.paint(.15);assert(gaze.hold>.14);
point={x:100,y:500};gaze.paint(.20);assert.equal(gaze.hold,0,'looking away resets dwell');
point={x:500,y:500};
ctx.adventurePlayer.engine.modal=true;gaze.paint(.8);assert.equal(gaze.hold,0,'dialogue must not count as staring');
ctx.adventurePlayer.engine.modal=false;
ctx.sessionPaused=true;gaze.paint(.8);assert.equal(gaze.hold,0,'pause must not advance gaze');
ctx.sessionPaused=false;
for(let i=0;i<8;i++)gaze.paint(.15);
assert.equal(saves,1,'ghost disappearing schedules exactly one save');
assert.equal(state.progress.seenApparitions['B:B_GHOST_MIRROR'],true);
assert.equal(figure.style.opacity,'0','ghost fades out without moving the camera');
assert.equal(gaze.active,false,'no ongoing processing after disappearance');
gaze.paint(.7);assert.equal(saves,1,'same ghost cannot disappear twice');
// Existing v1 story saves persist the apparition register as part of progress.
const {Engine}=require('../source/adventure-core.js');
const engine=new Engine(story);engine.state.progress=JSON.parse(JSON.stringify(state.progress));
const restored=new Engine(story);restored.load(engine.export());
assert.equal(restored.state.progress.seenApparitions['B:B_GHOST_MIRROR'],true,'vanish persists across load');
const oldState=ctx.adventurePlayer.engine.state;ctx.adventurePlayer.engine.state=restored.state;
restored.state.flags.Q02_DONE=true;restored.state.variants.B='B_GHOST_MIRROR';gaze.paint();
assert.equal(figure.style.opacity,'0','a saved ghost stays gone');
// Different mirror is an independent beat, not blocked by the earlier one.
ctx.roomId='H';restored.state.variants.H='H_ANNA_GLASS';gaze.paint();assert.equal(gaze.active,true);
ctx.roomId='B';restored.state.variants.B='B_NORMAL';gaze.paint();assert.equal(figure.style.display,'none');
ctx.roomId='B';restored.state.variants.B='B_GHOST_MIRROR';restored.state.flags.Q02_DONE=false;gaze.paint();
assert.equal(gaze.active,false,'quiet introduction remains free of ghosts');
// Renderer must update gaze while the panorama itself is still.
assert(runtime.includes('if(horrorGazeActive&&sessionStarted&&!sessionPaused)horrorPaint(dt);'));
console.log('PASS: focused stare, look-away reset, pause/modal, fade once, version-1 save persistence, room independence, calm intro');
