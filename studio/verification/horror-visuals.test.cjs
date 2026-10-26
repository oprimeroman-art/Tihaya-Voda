/* Regression checks for authored panorama states plus the remaining procedural apparition. */
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
 project:p=>({x:p.u*1000,y:p.v*1000}),console,roomId:'J',
 adventurePlayer:{engine:{state:{flags:{Q02_DONE:false},variants:{J:'J_FALSE_BELOV'}}}}
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
for(const [rid,v] of [['B','B_GHOST_MIRROR'],['H','H_ANNA_GLASS'],['F','F_SUIT_STANDING'],['D','D_LATE_MIRROR'],['G','G_MIRROR_DOOR']]){
 const val=p(rid,v);const custom=room(rid).visualProfiles?.[v];
 assert(val.strength>0,'authored apparition still needs atmosphere: '+v);
 assert.equal(val.figure,null,'authored art must not get a duplicate CSS silhouette: '+v);
 assert.equal(custom?.figure,false,'explicitly suppress CSS figure: '+v);
 if(v!=='F_SUIT_STANDING')assert(custom.gazePoint&&custom.dismissTo,'authored apparition must be gaze-dismissable: '+v);
}
for(const [rid,v] of [['J','J_FALSE_BELOV'],['K','K_TOWER_SILHOUETTE']])assert(p(rid,v).figure,'unillustrated apparition keeps its procedural placeholder: '+v);
assert.equal(p('H','H_1978').signal,'temporal');
assert.equal(p('L','L_SHUTTER_DANGER').signal,'severe');
assert.equal(p('J','J_FALSE_BELOV').figure.u,.41);
let cold=p('J','J_FALSE_BELOV');
assert(cold.strength<.5,'avoid large disruptive brightness jumps');
horrorPaint();
assert.equal(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'none');
globals.adventurePlayer.engine.state.flags.Q02_DONE=true;
horrorPaint();
assert.notEqual(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'block');
assert(Number(cells.figure.style.opacity)>0);
assert.equal(cells.figure.style.left,'410px');
globals.sessionPaused=true;horrorPaint();
assert.equal(cells.figure.style.display,'none');
assert.equal(cells.layer.style.opacity,'0');
globals.sessionPaused=false;
globals.adventurePlayer.engine.state.variants.J='J_NORMAL';horrorPaint();
assert.equal(cells.layer.style.opacity,'0');
assert.equal(cells.figure.style.display,'none');
const custom={default_variant:'normal',visualProfiles:{custom:{signal:'temporal',strength:.5,figure:{u:.2,v:.6}}}};
assert.equal(horrorProfile(custom,'custom',{flags:{Q02_DONE:true}}).strength,.5);
assert.equal(horrorProfile({...custom,visualProfiles:{custom:{disabled:true}}},'custom',{flags:{Q02_DONE:true}}).strength,0);
const fxScript=readFileSync(join(root,'game/index.html'),'utf8');
assert(fxScript.includes('HORROR_VISUALS_BEGIN')&&fxScript.includes('id="horror-apparition"'));
console.log('PASS: calm phase, 16 normal variants, apparition/temporal/danger modes, pause, save variants, custom overrides');
