/* Regression checks for queued scenes and ending transitions. */
'use strict';
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const {join}=require('node:path');
const {Engine}=require('../source/adventure-core.js');
function fixture(){return {
 id:'pending-qa',startRoom:'A',initial:{READY:true,Q02_DONE:true},
 rooms:[{id:'A',default_variant:'plain'},{id:'B',default_variant:'plain'}],
 links:[{from:'A',to:'B'}],actions:[],quests:[],
 events:[
  {id:'STALE',signal:'test',priority:'mandatory',when:'READY',effects:[{set:{BAD:true}}]},
  {id:'DELAYED',signal:'delayed',priority:'conditional',delay:5,room:'B',effects:[{set:{OK:true}}]},
  {id:'AFTER_END',signal:'finish',priority:'mandatory',effects:[{set:{POST_END:true}}]},
 ]};}
{
 const e=new Engine(fixture());e.signal('test');assert.deepEqual(e.state.pending.map(p=>p.id),['STALE']);
 e.state.flags.READY=false;
 assert.equal(e.flush(1),null,'a stale queued event must not fire');
 assert.equal(e.state.flags.BAD,undefined);assert.deepEqual(e.state.pending,[]);
}
{
 const e=new Engine(fixture());e.signal('delayed');
 assert.equal(e.flush(9),null,'a room-specific event must wait for the right room');
 assert.deepEqual(e.state.pending.map(p=>p.id),['DELAYED']);
 e.enter('B');assert.equal(e.flush(0)?.id,'DELAYED');assert.equal(e.state.flags.OK,true);
}
{
 const e=new Engine(fixture());e.state.pending.push({id:'REMOVED_EVENT',due:0});
 assert.equal(e.flush(),null,'old saves must ignore removed event IDs');
 assert.deepEqual(e.state.pending,[]);
}
{
 const e=new Engine(fixture());e.signal('finish');e.apply([{ending:'END_A'}]);
 assert.equal(e.flush(10),null,'pending scenes must not run after ending');
 assert.equal(e.state.flags.POST_END,undefined);
 e.signal('finish');assert.equal(e.state.pending.length,1,'an ending cannot enqueue additional events');
}
{
 const full=JSON.parse(readFileSync(join(__dirname,'../../game-project/project.json'),'utf8')).story.adventure;
 const e=new Engine(full);e.start();
 assert.equal(e.flush(0)?.id,'E001','the shipped story must still begin with its opening scene');
}
console.log('PASS: queued scene revalidation, room delays, obsolete save events, ending guard, shipped story start');
