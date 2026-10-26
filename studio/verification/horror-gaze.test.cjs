/* Authored panorama apparitions dismiss by gaze; placeholder apparitions still fade in CSS. */
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
const story=JSON.parse(fs.readFileSync(path.join(R,'studio/content/TIHAYA_VODA/adventure.json'),'utf8'));
const state={flags:{Q02_DONE:true},progress:{},variants:{B:'B_GHOST_MIRROR',H:'H_NORMAL',J:'J_NORMAL'}};
const atmosphere={dataset:{},style:{}},figure={style:{}},canvas={style:{}};
let point={x:500,y:500},saves=0;const appliedVariants=[];
const ctx={game:{story:{adventure:story}},canvas,roomId:'B',sessionStarted:true,sessionPaused:false,
 innerWidth:1000,innerHeight:1000,
 adventurePlayer:{engine:{state,modal:false}},
 $:id=>id==='horror-atmosphere'?atmosphere:id==='horror-apparition'?figure:null,
 project(){return point},adventureApplyVariant(room,variant){appliedVariants.push([room,variant]);},scheduleGameSave(){saves++},console};
vm.createContext(ctx);vm.runInContext(visuals+';globalThis.gaze={paint:horrorPaint,get active(){return horrorGazeActive},get hold(){return horrorGazeHold}};',ctx);
const gaze=ctx.gaze;
gaze.paint();assert(gaze.active,'authored mirror image is gaze-reactive');assert.equal(figure.style.display,'none','no duplicate CSS silhouette over authored art');
gaze.paint(.15);assert(gaze.hold>.14);
point={x:100,y:500};gaze.paint(.20);assert.equal(gaze.hold,0,'looking away resets dwell');
point={x:500,y:500};ctx.adventurePlayer.engine.modal=true;gaze.paint(.8);assert.equal(gaze.hold,0,'dialogue must not count as staring');
ctx.adventurePlayer.engine.modal=false;ctx.sessionPaused=true;gaze.paint(.8);assert.equal(gaze.hold,0,'pause must not advance gaze');assert.equal(gaze.active,false);
ctx.sessionPaused=false;
for(let i=0;i<8;i++)gaze.paint(.15);
assert.equal(state.variants.B,'B_NORMAL','looking at the authored ghost restores the normal panorama');assert(appliedVariants.some(([room,variant])=>room==='B'&&variant==='B_NORMAL'),'the panorama renderer must be notified of the state change');
assert.equal(saves,1,'dismissal schedules exactly one save');
assert.equal(state.progress.seenApparitions['B:B_GHOST_MIRROR'],true);
assert.equal(figure.style.display,'none','authored art has no CSS duplicate during dismissal');
assert.equal(gaze.active,false,'no ongoing processing after disappearance');
gaze.paint(.7);assert.equal(saves,1,'same ghost cannot disappear twice');
// Saved disappearance prevents the authored state from reappearing if a later event selects it again.
const {Engine}=require('../source/adventure-core.js');const engine=new Engine(story);engine.state.progress=JSON.parse(JSON.stringify(state.progress));engine.state.variants=JSON.parse(JSON.stringify(state.variants));
const restored=new Engine(story);restored.load(engine.export());restored.state.flags.Q02_DONE=true;restored.state.variants.B='B_GHOST_MIRROR';
ctx.adventurePlayer.engine.state=restored.state;gaze.paint();assert.equal(restored.state.variants.B,'B_NORMAL','saved ghost remains dismissed');
// A different authored apparition is independent and gaze-dismissable.
ctx.roomId='H';restored.state.variants.H='H_ANNA_GLASS';gaze.paint();assert(gaze.active);assert.equal(figure.style.display,'none');
for(let i=0;i<9;i++)gaze.paint(.15);assert.equal(restored.state.variants.H,'H_NORMAL');assert(appliedVariants.some(([room,variant])=>room==='H'&&variant==='H_NORMAL'));assert.equal(restored.state.progress.seenApparitions['H:H_ANNA_GLASS'],true);
// The authored Belov and tower images dismiss to their normal/empty variants.
ctx.roomId='J';restored.state.variants.J='J_FALSE_BELOV';gaze.paint();assert(gaze.active);assert.equal(figure.style.display,'none');
for(let i=0;i<8;i++)gaze.paint(.15);assert.equal(restored.state.variants.J,'J_NORMAL');assert.equal(restored.state.progress.seenApparitions['J:J_FALSE_BELOV'],true);
assert(appliedVariants.some(([room,variant])=>room==='J'&&variant==='J_NORMAL'));
ctx.roomId='K';restored.state.variants.K='K_TOWER_SILHOUETTE';gaze.paint();assert(gaze.active);assert.equal(figure.style.display,'none');
for(let i=0;i<9;i++)gaze.paint(.15);assert.equal(restored.state.variants.K,'K_TOWER_EMPTY');assert.equal(restored.state.progress.seenApparitions['K:K_TOWER_SILHOUETTE'],true);
assert(appliedVariants.some(([room,variant])=>room==='K'&&variant==='K_TOWER_EMPTY'));
// The final apparition in the long corridor can be watched until it disappears into an empty corridor.
ctx.roomId='N';restored.state.variants.N='N_LATE_EXIT';gaze.paint();assert(gaze.active);assert.equal(figure.style.display,'none');
for(let i=0;i<11;i++)gaze.paint(.15);assert.equal(restored.state.variants.N,'N_NORMAL');assert.equal(restored.state.progress.seenApparitions['N:N_LATE_EXIT'],true);
assert(appliedVariants.some(([room,variant])=>room==='N'&&variant==='N_NORMAL'));
// The indoor-tower monitor is authored art, not a second CSS apparition.
ctx.roomId='D';restored.state.variants.D='D_INDOOR_TOWER';gaze.paint();assert.equal(figure.style.display,'none');assert.equal(gaze.active,false);
// The legacy CSS fallback remains available for states without an authored visual profile.
const jRoom=story.rooms.find(r=>r.id==='J');const jProfile=jRoom.visualProfiles.J_FALSE_BELOV;delete jRoom.visualProfiles.J_FALSE_BELOV;
delete restored.state.progress.seenApparitions['J:J_FALSE_BELOV'];ctx.roomId='J';restored.state.variants.J='J_FALSE_BELOV';gaze.paint();assert(gaze.active);assert.equal(figure.style.display,'block');
for(let i=0;i<8;i++)gaze.paint(.15);assert.equal(restored.state.progress.seenApparitions['J:J_FALSE_BELOV'],true);assert.equal(figure.style.opacity,'0');
jRoom.visualProfiles.J_FALSE_BELOV=jProfile;
assert(runtime.includes('if(horrorGazeActive&&sessionStarted&&!sessionPaused)horrorPaint(dt);'));
console.log('PASS: authored image gaze dismissal, no duplicate CSS figures, save persistence, independent rooms, legacy CSS fallback, pause/modal and calm intro');
