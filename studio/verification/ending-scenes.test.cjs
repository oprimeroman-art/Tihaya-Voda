/* Signed terminal scenes must commit their dialogue/variant before ending guard. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),{Engine}=require('../source/adventure-core.js');
const d=JSON.parse(fs.readFileSync(path.join(root,'studio/content/TIHAYA_VODA/adventure.json')));
for(const mode of 'ABCD'){
 const checkpoint=JSON.parse(fs.readFileSync(path.join(root,`reports/CHECKPOINT_${mode}.json`)));
 const e=new Engine(d);e.load(checkpoint);assert.equal(e.state.ended,false);
 e.begin('FINAL_PANEL');e.modal=false;assert.equal(e.flush(0)?.id,'E107');
 assert.equal(e.answer('FINAL_PANEL',mode).ok,true);
 assert.equal(e.state.ended,mode);assert.equal(e.state.flags['ENDING_'+mode],true);assert.equal(e.state.variants.P,'P_END_'+mode);
 const event=d.events.find(ev=>ev.ending===mode);assert(e.state.fired.includes(event.id));assert.equal(e.state.journal.filter(j=>j.id===event.id).length,1);
 e.signal(event.signal);assert.equal(e.flush(999),null);assert.equal(e.state.journal.filter(j=>j.id===event.id).length,1);
 assert.equal(e.state.checkpoint.state.ended,false);assert(!e.state.checkpoint.state.done.includes('FINAL_PANEL'));
}
console.log('PASS: four route-earned checkpoints, pre-signature Belov, all terminal variants/dialogues committed once and checkpoint retained');
