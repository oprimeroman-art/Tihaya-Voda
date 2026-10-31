/* Follow only player-facing recommendations through normal engine actions. No flag injection. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..');
const data=JSON.parse(fs.readFileSync(path.join(root,'studio/content/TIHAYA_VODA/adventure.json')));
const {Engine,test}=require('../source/adventure-core.js');globalThis.window=globalThis;require('../source/adventure-ui.js');
const UI=globalThis.GagarinAdventure.UI;
let total=0;const results=[];
for(const mode of 'ABCD'){
 const engine=new Engine(data),ui=Object.assign(Object.create(UI.prototype),{data,engine});
 const drain=()=>{for(let n=0;n<150;n++)if(!engine.flush(70))return;throw Error('Unsettled event queue');};
 function perform(guide){
  assert(guide?.action,'A current objective exists');const a=guide.action,route=ui.guidanceRoute(a.room);
  assert(route,mode+': objective room is reachable: '+a.id);
  for(const room of route){assert(engine.enter(room),'Only an open player route is used');drain();}
  assert(engine.begin(a.id),mode+': recommended action is available: '+a.id);
  let value=a.answer??a.options?.find(o=>test(o.when,engine.state))?.value;
  if(a.id==='NODE_MEMORY')value=mode==='D'?'PETR':'TRUTH';
  if(a.id==='NODE_OBSERVER')value=mode==='B'?2:1;
  if(a.id==='false_act')value='NO';
  if(a.id==='name_reply')value={A:'NO',B:'SILENCE',C:'OFF',D:'NO'}[mode];
  if(a.id==='FINAL_PANEL')value=mode;
  assert(engine.answer(a.id,value).ok,mode+': objective can be completed: '+a.id);drain();total++;
 }
 engine.start();drain();let iterations=0,checkedRestore=false;
 while(!engine.state.ended){
  assert(++iterations<110,'The guidance must not loop');
  if(mode==='D'&&engine.state.chapter>=8&&!engine.state.flags.PETR_LETTER_DONE){
   const branch=data.playerGuidance.branches.find(b=>b.id==='petr');assert(test(branch.when,engine.state));
   for(let n=0;n<branch.steps.length&&!test(branch.complete,engine.state);n++)perform(ui.guide(branch));
   assert(engine.state.flags.PETR_LETTER_DONE,'Optional letter can be completed without leaving the main campaign');
  }
  const current=ui.guide();assert.equal(current.quest.chapter,engine.state.chapter);perform(current);
  if(!checkedRestore&&engine.state.chapter===6&&engine.state.done.includes('WAVE_PHASE')){
   const saved=engine.export(),next=ui.guide(),expected=next.action.id;perform(next);
   assert.notEqual(ui.guide()?.action?.id,expected,'Completed objective advances');
   engine.load(saved);assert.equal(ui.guide()?.action?.id,expected,'Loading restores the unfinished objective');checkedRestore=true;
  }
 }
 assert.equal(engine.state.ended,mode);assert.equal(ui.guide(),null,'No stale active objective after an ending');
 assert(engine.state.flags.FOUND_D14,'The corridor document is recommended before the exit closes');
 results.push({mode,iterations});
}
assert.equal(Object.keys(data.playerGuidance.quests).length,data.quests.length);
for(const [id,entry] of Object.entries(data.illustratedProps.inspections))assert(data.illustratedProps.image[entry.image]?.startsWith('data:image/webp;base64,'),id+' has actual inspection artwork');
console.log(JSON.stringify({passed:true,normalActions:total,allFourGuidedRoutes:results,plotFlagsWrittenByTest:false}));
