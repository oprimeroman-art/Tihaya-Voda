/* Declarative adventure extension for Panorama Studio. No game-specific IDs or eval. */
(function(root){
'use strict';
const copy=x=>JSON.parse(JSON.stringify(x));
function test(c,s){
 if(!c)return true;if(typeof c==='string')return !!s.flags[c];
 if(Array.isArray(c))return c.every(x=>test(x,s));
 if(c.all&&!c.all.every(x=>test(x,s)))return false;
 if(c.any&&!c.any.some(x=>test(x,s)))return false;
 if(c.not&&test(c.not,s))return false;
 if(c.eq&&!Object.entries(c.eq).every(([k,v])=>s.flags[k]===v))return false;
 if(c.in&&!Object.entries(c.in).every(([k,v])=>v.includes(s.flags[k])))return false;
 if(c.item&&!s.inventory.includes(c.item))return false;
 if(c.min&&s.chapter<c.min)return false;if(c.max&&s.chapter>c.max)return false;
 if(c.variant&&s.variants[s.room]!==c.variant)return false;
 return true;
}
class Engine {
 constructor(data,hooks={}){this.data=data;this.hooks=hooks;this.reset();}
 reset(){this.state={version:1,project:this.data.id,chapter:1,room:this.data.startRoom,flags:copy(this.data.initial||{}),inventory:[],documents:[],done:[],fired:[],pending:[],journal:[],visits:{},variants:{},errors:{},progress:{},clock:0,lastOptional:-65,ended:false,checkpoint:null};this.modal=false;for(const r of this.data.rooms)this.state.variants[r.id]=r.default_variant;}
 export(){return copy(this.state);}
 load(s){if(!s||s.version!==1||s.project!==this.data.id||!this.data.rooms.some(r=>r.id===s.room)||!Array.isArray(s.done)||!s.flags)throw Error('Несовместимое сохранение сценария');this.state=copy(s);this.modal=false;this.changed();}
 changed(){this.hooks.change?.(this.state);}
 eligible(a){return !this.state.ended&&(!a.room||a.room===this.state.room)&&test(a.when,this.state)&&(!a.once||!this.state.done.includes(a.id));}
 actions(){return this.data.actions.filter(a=>this.eligible(a));}
 checkpoint(name){const snap=this.export();snap.checkpoint=null;this.state.checkpoint={name,state:snap};this.changed();}
 die(name){const old=this.state,cp=old.checkpoint;if(!cp)throw Error('Нет локального чекпоинта');this.state=copy(cp.state);this.state.checkpoint=cp;this.state.fired=[...new Set([...old.fired,...this.state.fired])];this.state.errors={...old.errors};this.state.journal=old.journal;this.state.pending=[...new Map([...this.state.pending,...old.pending].map(p=>[p.id,p])).values()].filter(p=>!this.state.fired.includes(p.id));this.state.flags.DEATHS=(old.flags.DEATHS||0)+1;this.modal=false;this.hooks.death?.(name);this.changed();}
 apply(fx=[]){for(const x of fx){if(x.set)Object.assign(this.state.flags,x.set);if(x.item&&!this.state.inventory.includes(x.item))this.state.inventory.push(x.item);if(x.document){if(!this.state.documents.includes(x.document))this.state.documents.push(x.document);this.state.flags['FOUND_'+x.document]=true;}
 if(x.dialogue){const line=this.data.dialogues.find(l=>l.id===x.dialogue);if(line){this.state.journal.push({text:line.speaker,lines:[line]});this.hooks.line?.(line);}}if(x.variant)Object.assign(this.state.variants,x.variant);if(x.signal)this.signal(x.signal);if(x.checkpoint)this.checkpoint(x.checkpoint);if(x.room)this.enter(x.room,true);if(x.death)this.die(x.death);if(x.ending){this.state.ended=x.ending;this.state.flags.ENDING=x.ending;this.state.flags.Q12_DONE=true;}}
 }
 signal(name){if(this.state.ended)return;for(const e of this.data.events){if(!(Array.isArray(e.signal)?e.signal.includes(name):e.signal===name)||this.state.fired.includes(e.id)||this.state.pending.some(p=>p.id===e.id)||!test(e.when,this.state))continue;this.state.pending.push({id:e.id,due:this.state.clock+(e.delay||0)});}}
 flush(dt=0){this.state.clock+=Math.max(0,dt);if(this.modal||this.state.ended)return null;
 // Revalidate queued events: flags and timeline state can change before execution.
 const events=new Map(this.data.events.map(e=>[e.id,e]));
 this.state.pending=this.state.pending.filter(p=>{const e=events.get(p.id);return e&&!this.state.fired.includes(e.id)&&test(e.when,this.state);});
 const ranks={mandatory:0,conditional:1,optional:2};
 this.state.pending.sort((a,b)=>(ranks[events.get(a.id).priority]??3)-(ranks[events.get(b.id).priority]??3)||a.due-b.due);
 const i=this.state.pending.findIndex(p=>{const e=events.get(p.id);return p.due<=this.state.clock&&(!e.room||e.room===this.state.room)&&(!e.horror||this.state.flags.Q02_DONE)&&(e.priority!=='optional'||this.state.clock-this.state.lastOptional>=65);});
 if(i<0)return null;const p=this.state.pending.splice(i,1)[0],e=events.get(p.id);this.state.fired.push(e.id);if(e.priority==='optional')this.state.lastOptional=this.state.clock;
 this.apply(e.effects);this.state.journal.push({id:e.id,text:e.presentation,lines:e.lines||[],time:this.state.clock});this.signal('event:'+e.id);this.changed();return e;
 }
 enter(room,force=false){if(this.state.ended)return false;if(!force){const edge=this.data.links.find(e=>e.from===this.state.room&&e.to===room);if(!edge||!test(edge.when,this.state))return false;}
 this.state.room=room;this.state.visits[room]=(this.state.visits[room]||0)+1;for(const hook of this.data.onEnter||[])if(hook.room===room&&test(hook.when,this.state))this.apply(hook.effects);this.signal('enter:'+room);this.advance();this.changed();return true;}
 start(){this.signal('game_start');this.enter(this.state.room,true);this.changed();}
 advance(){if(this.state.ended)return;for(const q of this.data.quests){if(q.chapter!==this.state.chapter||!test(q.complete,this.state))continue;this.state.flags[q.id+'_DONE']=true;this.signal(q.id.toLowerCase()+'_done');if(q.chapter<12){this.state.chapter=q.chapter+1;this.state.flags.CHAPTER=this.state.chapter;this.state.flags.WORLD_PHASE=this.data.quests[q.chapter].phase;this.signal('chapter:'+this.state.chapter);this.signal('enter:'+this.state.room);}if(q.checkpoint)this.checkpoint(q.id+'_DONE');}}
 begin(id){const a=this.data.actions.find(a=>a.id===id);if(!a||!this.eligible(a))return null;if(a.checkpoint)this.checkpoint(a.checkpoint);if(a.startSignal)this.signal(a.startSignal);this.modal=true;return a;}
 cancel(){this.modal=false;this.changed();}
 answer(id,value){const a=this.data.actions.find(a=>a.id===id);if(!a||!this.eligible(a))return {ok:false,message:'Действие сейчас недоступно'};
 let ok=true,fx=a.effects||[];
 if(a.template==='choice'||a.template==='sequence_choice'){const opt=a.options.find(x=>String(x.value)===String(value));if(!opt||!test(opt.when,this.state))return {ok:false,message:opt?.locked||'Нет условий для этого режима'};fx=[...fx,...(opt.effects||[])];}
 else if(a.answer){const want=a.answer,got=Array.isArray(value)?value:[value];ok=want.length===got.length&&want.every((v,i)=>typeof v==='number'?Number.isFinite(Number(got[i]))&&Math.abs(Number(got[i])-v)<=(a.tolerance?.[i]||0):String(v)===String(got[i]));}
 if(!ok){this.state.errors[id]=(this.state.errors[id]||0)+1;this.apply(a.failureEffects);if(a.deathAfter&&this.state.errors[id]%a.deathAfter===0){this.apply(a.deathEffects);this.die(a.deathName||a.label);return {ok:false,death:true,message:'Возврат к началу узла. Выполненная работа сохранена.'};}this.changed();return {ok:false,message:this.state.errors[id]>=2?a.hint:(a.error||'Показания не совпали. Проверьте инструкцию.')};}
 this.modal=false;if(fx.some(x=>x.ending))this.checkpoint('before_final_confirmation');if(!this.state.done.includes(id))this.state.done.push(id);this.apply(fx);if(a.signal)this.signal(a.signal);this.advance();this.changed();return {ok:true};
 }
}
root.GagarinAdventure={Engine,test,copy};if(typeof module!=='undefined')module.exports=root.GagarinAdventure;
})(typeof window==='undefined'?globalThis:window);
