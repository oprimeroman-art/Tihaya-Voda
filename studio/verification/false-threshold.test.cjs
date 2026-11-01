/* Spatial corridor false-exit: valid canonical exits, recoverable scene, actual player choice. */
'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
const runtime=fs.readFileSync(path.join(root,'studio/source/game-runtime.html'),'utf8');
const ui=fs.readFileSync(path.join(root,'studio/source/adventure-ui.js'),'utf8');
const a=runtime.indexOf('/* CORRIDOR_FALSE_THRESHOLD:'),b=runtime.indexOf('/* CORRIDOR_FALSE_THRESHOLD_END */',a);
assert(a>=0&&b>a,'corridor scene must be in player runtime');
assert(ui.includes('this.hooks.beforeTravel?.(id)===true'),'player exits need an optional pre-travel director hook');
const source=runtime.slice(a,b+'/* CORRIDOR_FALSE_THRESHOLD_END */'.length);
const changed=[],visuals=[],sounds=[],notes=[];
const state={room:'C',chapter:6,progress:{},journal:[],variants:{C:'C_NORMAL'},clock:5};
const created=[];
const ctx={
 adventurePlayer:{engine:{state,changed(){changed.push('change')}}},
 roomId:'C',sessionPaused:false,sessionStarted:true,
 game:{story:{adventure:{rooms:[{id:'C',variantAssets:{C_HIDDEN_DOOR:'corridor'} }]}},assets:{corridor:{data:'authored'}}},
 document:{createElement(tag){const b={tag,hidden:true,style:{setProperty(){}},setAttribute(){},onclick:null,innerHTML:''};created.push(b);return b;},body:{append(){}}},
 innerWidth:1280,innerHeight:720,
 cameraAllowed(){return true;},refresh(){},
 project(){return{x:660,y:340};},
 horrorCueStop(){},horrorCueStart(){return true;},horrorSpatialSfx(kind){sounds.push(kind)},
 note(m){notes.push(m)},
 adventureApplyVariant(r,variant){visuals.push([r,variant]);return Promise.resolve();},
 console
};
vm.createContext(ctx);
vm.runInContext(source+';\nthis.scene={begin:falseThresholdBeforeTravel,init:falseThresholdInit,frame:falseThresholdFrame,end:falseThresholdFinish,reset:falseThresholdReset,get state(){return falseThresholdScene}};',ctx);
(async()=>{
 const scene=ctx.scene;
 scene.init();
 assert.equal(scene.begin('D'),true,'first legitimate corridor exit returns to wrong corridor');
 assert.equal(state.room,'C','false exit never changes engine room');
 assert.equal(state.progress.falseThreshold.status,'active');
 await new Promise(resolve=>setImmediate(resolve));
 assert.deepEqual(visuals[0],['C','C_HIDDEN_DOOR'],'uses authored panorama, not a generic popup');
 scene.frame(.15);
 assert.equal(created[0].hidden,false,'handle visible in projected panorama');
 created[0].onclick();
 assert.equal(state.progress.falseThreshold.status,'examined');
 assert.equal(state.journal.length,1);
 assert.deepEqual(visuals.at(-1),['C','C_NORMAL'],'canonical panorama restored');
 assert.equal(scene.begin('D'),false,'legitimate travel remains available immediately');
 scene.reset();
 state.progress={};state.journal=[];
 assert.equal(scene.begin('B'),true);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(scene.begin('B'),false,'retry proceeds without trapping player');
 assert.equal(state.progress.falseThreshold.status,'fled');
 scene.reset();
 state.progress={};state.journal=[];
 assert.equal(scene.begin('A'),true);
 await new Promise(resolve=>setImmediate(resolve));
 for(let i=0;i<76;i++)scene.frame(.15);
 assert.equal(state.progress.falseThreshold.status,'missed','waiting also resolves the encounter');
 assert.equal(scene.begin('A'),false);
 console.log('PASS false threshold: one nonblocking loop, authored corridor swap, real handle, investigate/flee/wait, restored panorama and save progress');
})().catch(e=>{console.error(e);process.exitCode=1});
