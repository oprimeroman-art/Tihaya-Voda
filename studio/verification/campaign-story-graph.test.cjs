#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const ROOT=path.resolve(__dirname,'../..');const data=JSON.parse(fs.readFileSync(path.join(ROOT,'studio/content/TIHAYA_VODA/adventure.json'),'utf8'));const project=JSON.parse(fs.readFileSync(path.join(ROOT,'game-project/project.json'),'utf8'));const {Engine}=require('../source/adventure-core.js');
const roomIds=new Set(data.rooms.map(r=>r.id));assert.equal(roomIds.size,16,'room IDs must be unique');
const variantSets=new Map(data.rooms.map(room=>[room.id,new Set(room.variants||[])]));
function checkVariants(owner,effects=[]){for(const fx of effects){if(!fx.variant)continue;for(const [room,variant] of Object.entries(fx.variant)){assert(variantSets.get(room)?.has(variant),`${owner} selects undeclared variant ${room}:${variant}`);}}}
for(const action of data.actions){checkVariants(`action ${action.id}`,action.effects);for(const option of action.options||[])checkVariants(`action ${action.id} option`,option.effects);}
for(const event of data.events)checkVariants(`event ${event.id}`,event.effects);for(const hook of data.onEnter||[])checkVariants(`onEnter ${hook.room}`,hook.effects);
const actions=new Map(data.actions.map(a=>[a.id,a]));assert.equal(actions.size,128,'action IDs must be unique');
const hotspots=[];for(const room of project.rooms){assert(roomIds.has(room.id),'project room absent from story: '+room.id);for(const o of room.objects||[]){const key=o.tourKey||'';if(key.startsWith('ga:'))hotspots.push({room:room.id,id:o.id,action:key.slice(3)});}}
assert.equal(hotspots.length,128,'each action must have a matching hotspot');const mapped=new Set(hotspots.map(h=>h.action));assert.equal(mapped.size,128,'hotspot action mappings must be unique');for(const h of hotspots){assert(actions.has(h.action),`${h.room}/${h.id} points to missing action ${h.action}`);assert.equal(actions.get(h.action).room,h.room,`${h.action} room must match hotspot room`);}
for(const a of data.actions)assert(roomIds.has(a.room),`${a.id} references missing room ${a.room}`);for(const e of data.events)if(e.room)assert(roomIds.has(e.room),`${e.id} references missing room ${e.room}`);for(const l of data.links){assert(roomIds.has(l.from)&&roomIds.has(l.to),'link references unknown room '+JSON.stringify(l));}
const refs=new Set(),produced=new Set(Object.keys(data.initial||{}));
function condition(c){if(!c)return;if(typeof c==='string'){refs.add(c);return;}if(Array.isArray(c)){for(const x of c)condition(x);return;}if(typeof c!=='object')return;
 for(const k of ['all','any','not'])if(k in c)condition(c[k]);for(const k of ['eq','in','equals'])if(c[k]&&typeof c[k]==='object')for(const flag of Object.keys(c[k]))refs.add(flag);if(c.item){} }
function effects(list=[]){for(const fx of list){if(fx.set)for(const k of Object.keys(fx.set))produced.add(k);if(fx.document)produced.add('FOUND_'+fx.document);}}
for(const a of data.actions){condition(a.when);effects(a.effects);effects(a.failureEffects);for(const o of a.options||[]){condition(o.when);effects(o.effects);}}
for(const e of data.events){condition(e.when);effects(e.effects);}for(const q of data.quests){condition(q.complete);produced.add(q.id+'_DONE');}for(const l of data.links)condition(l.when);for(const h of data.onEnter||[])condition(h.when);for(const c of Object.values(data.endingConditions||{}))condition(c);
for(const d of data.documents||[])produced.add('FOUND_'+d.id);for(const key of ['CHAPTER','WORLD_PHASE','ENDING','DEATHS','Q12_DONE'])produced.add(key);
const missing=[...refs].filter(x=>!produced.has(x)&&!x.startsWith('event:')&&!x.startsWith('enter:')&&!x.endsWith('_done')).sort();assert.deepEqual(missing,[],'story conditions reference flags with no producer');
// Exercise each terminal choice against the actual engine with the documented prerequisites.
for(const mode of ['A','B','C','D']){const e=new Engine(data);Object.assign(e.state,{chapter:12,room:'P'});Object.assign(e.state.flags,{OBSERVER_SELECT:true,OBSERVER_COUNT:2,FOUND_ACT_BOTH:true,RESTORED_V04:true,FOUND_D02:true,FOUND_D03:true,FOUND_D04:true,FOUND_D14:true,TAPE_CHOICE:mode==='D'?'PETR':'TRUTH',PETR_LETTER_DONE:true,WATCHED_V03:true,FALSE_ACT_SIGNED:false});const result=e.answer('FINAL_PANEL',mode);assert.equal(result.ok,true,`ending ${mode} should be selectable with prerequisites`);assert.equal(e.state.ended,mode,`ending ${mode} should terminate the run`);}
console.log('PASS: 16 room IDs, 128 actions ↔ 128 unique hotspots, all room references valid, all condition flags have producers.');console.log('PASS: all four terminal endings A/B/C/D execute through the actual story engine.');
