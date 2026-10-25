/* Regression checks for stage-driven horror treatment (no authored art required). */
'use strict';
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {join}=require('node:path');
const vm=require('node:vm');
const root=join(__dirname,'../..');
const script=readFileSync(join(root,'studio/source/game-runtime.html'),'utf8');
const data=JSON.parse(readFileSync(join(root,'game-project/project.json'),'utf8')).story.adventure;
const start=script.indexOf('/* HORROR_VISUALS_BEGIN');
const end=script.indexOf('/* HORROR_VISUALS_END */',start);
assert(start!==-1 && end>start,'visual treatment must be present in canonical renderer');
const source=script.slice(start,end+'/* HORROR_VISUALS_END */'.length);
const cells={layer:{dataset:{},style:{}},figure:{style:{}}};
const canvas={style:{}};
const globals={
 game:{story:{adventure:data}},
 canvas,sessionStarted:true,sessionPaused:false,
 $:id=>id==='horror-atmosphere'?cells.layer:id==='horror-apparition'?cells.figure:null,
 project:p=>({x:p.u*1000,y:p.v*1000}),console,roomId:'B',
 adventurePlayer:{engine:{state:{flags:{Q02_DONE:false},variants:{B:'B_GHOST_MIRROR'}}}}
};
const vmContext=vm.createContext(globals);
vm.runInContext(source+';globalThis.api={horrorProfile,horrorPaint};',vmContext);
const {horrorProfile,horrorPaint}=vmContext.api;
const room=id=>data.rooms.find(r=>r.id===id);
function p(id,variant,done=true){
 return horrorProfile(room(id),variant,{flags:{Q02_DONE:done}});
}
assert.equal(p('B','B_GHOST_MIRROR',false).strength,0,'no horror during warm-up phase');
for(const meta of data.rooms){
 assert.equal(horrorProfile(meta,meta.default_variant,{flags:{Q02_DONE:true}}).strength,0,
    meta.id+': normal room stays normal');
}
for(const [rid,v] of [['B','B_GHOST_MIRROR'],['H','H_ANNA_GLASS'],['J','J_FALSE_BELOV'],['F','F_SUIT_STANDING']]){
 const val=p(rid,v);
 assert(val.strength>0 && val.figure,'signature apparition must be visually staged: '+v);
}
assert.equal(p('H','H_1978').signal,'temporal');
assert.equal(p('L','L_SHUTTER_DANGER').signal,'severe');
assert.equal(p('B','B_GHOST_MIRROR').figure.u,.44);
let cold=p('B','B_GHOST_MIRROR');
assert(cold.strength<.5,'avoid large disruptive brightness jumps');
horrorPaint();
assert.equal(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'none');
globals.adventurePlayer.engine.state.flags.Q02_DONE=true;
horrorPaint();
assert.notEqual(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'block');
assert(Number(cells.figure.style.opacity)>0);
assert.equal(cells.figure.style.left,'440px');
globals.sessionPaused=true;horrorPaint();
assert.equal(cells.figure.style.display,'none');
assert.equal(cells.layer.style.opacity,'0');
globals.sessionPaused=false;
globals.adventurePlayer.engine.state.variants.B='B_NORMAL';horrorPaint();
assert.equal(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'none');
const custom={default_variant:'normal',visualProfiles:{custom:{signal:'temporal',strength:.5,figure:{u:.2,v:.6}}}};
assert.equal(horrorProfile(custom,'custom',{flags:{Q02_DONE:true}}).strength,.5);
assert.equal(horrorProfile({...custom,visualProfiles:{custom:{disabled:true}}},'custom',{flags:{Q02_DONE:true}}).strength,0);
const fxScript=readFileSync(join(root,'game/index.html'),'utf8');
assert(fxScript.includes('HORROR_VISUALS_BEGIN')&&fxScript.includes('id="horror-apparition"'));
console.log('PASS: calm phase, 16 normal variants, apparition/temporal/danger modes, pause, save variants, custom overrides');
