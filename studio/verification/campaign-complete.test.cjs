#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Engine,test}=require('../source/adventure-core.js');
const {route}=require('./campaign-route.cjs');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../content/TIHAYA_VODA/adventure.json')));
const results=[];
for(const mode of ['A','B','C','D']){
 const e=new Engine(data);let count=0;const chapters=new Set();
 function drain(){for(let i=0;i<150;i++)if(!e.flush(70))break;chapters.add(e.state.chapter);}
 function go(dest){const queue=[[e.state.room,[]]],seen=new Set();let steps;
  while(queue.length){const [r,p]=queue.shift();if(r===dest){steps=p;break;}if(seen.has(r))continue;seen.add(r);for(const l of data.links.filter(l=>l.from===r&&test(l.when,e.state)))queue.push([l.to,[...p,l.to]]);}
  assert(steps,`${mode}: no route ${e.state.room} -> ${dest} in chapter ${e.state.chapter}`);
  for(const room of steps){assert(e.enter(room));drain();}
 }
 e.start();drain();
 for(const step of route){if(step.room){go(step.room);continue;}
  const [id,raw]=Array.isArray(step)?step:[step];const a=data.actions.find(a=>a.id===id);assert(a,id);go(a.room);
  assert(e.begin(id),`${mode}: unavailable ${id} chapter ${e.state.chapter}`);
  const value=typeof raw==='function'?raw(mode):raw??a.answer??a.options?.[0]?.value;
  assert(e.answer(id,value).ok,`${mode}: failed ${id}`);count++;drain();
  if(count%11===0){const save=e.export();e.load(save);assert.deepEqual(e.export(),save,'save/load changed progress');}
 }
 assert.equal(e.state.ended,mode);assert.equal(chapters.size,12,'all twelve chapters traversed');
 assert.equal(e.state.flags.Q12_DONE,true);assert.equal(e.state.checkpoint.name,'before_final_confirmation');
 if(process.env.QA_SAVE_DIR){fs.mkdirSync(process.env.QA_SAVE_DIR,{recursive:true});fs.writeFileSync(path.join(process.env.QA_SAVE_DIR,mode+'.json'),JSON.stringify(e.state.checkpoint.state));}
 results.push({ending:mode,chapters:chapters.size,interactions:count,saveReloads:Math.floor(count/11)});
}
console.log(JSON.stringify({passed:true,routes:results,note:'Engine routes from fresh games; not visual or human playtesting.'},null,2));
