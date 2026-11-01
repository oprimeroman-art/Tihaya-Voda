/* The radio speaks the canonical Belov line before the player signs shift. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const source=fs.readFileSync(path.join(root,'studio/source/game-runtime.html'),'utf8');
const a=source.indexOf('/* EARLY_RADIO_ECHO:'),b=source.indexOf('/* EARLY_RADIO_ECHO_END */',a);
assert(a>0&&b>a,'authored radio scene must exist in the actual game runtime');
const script=source.slice(a,b+'/* EARLY_RADIO_ECHO_END */'.length);
const state={room:'D',chapter:1,flags:{TEA_DONE:true},progress:{},journal:[],clock:12,variants:{D:'D_NORMAL'}};
const buttons=[],events=[],audio=[];
class TestAudio{
 constructor(src){this.src=src;this.currentTime=0;this.volume=0;audio.push(this);}
 play(){events.push('play '+this.src);return Promise.resolve();}
 pause(){events.push('pause');}
}
const ctx={
 roomId:'D',sessionStarted:true,sessionPaused:false,sessionReady:true,
 adventurePlayer:{engine:{state,modal:false,changed(){events.push('saved')}}},
 game:{story:{adventure:{rooms:[{id:'D',variantAssets:{D_FALSE_MONITOR:'D_FALSE'}}]}},
  assets:{D_FALSE:{data:'pano'}},audio:{DLG_003:{url:'voice-belov.mp3'}}},
 stationAmbience:{ctx:null},audioSettings:{master:70},Audio:TestAudio,
 assetSource:x=>x.url,
 document:{createElement(tag){const b={tag,type:'',hidden:true,style:{},setAttribute(){},title:'',innerHTML:'',onclick:null};buttons.push(b);return b;},body:{append(){}}},
 horrorSpatialSfx(k){events.push('sound '+k)},
 directorSubtitleShow(t){events.push('subtitle '+t)},
 adventureApplyVariant(room,variant){events.push('variant '+variant);return Promise.resolve();},
 project(){return{x:430,y:320};},innerWidth:1280,innerHeight:720,
 cameraAllowed(){return true;},console,Promise
};
vm.createContext(ctx);
vm.runInContext(script+';this.radio={eligible:radioEchoEligible,init:radioEchoInit,frame:radioEchoFrame,reset:radioEchoReset,finish:radioEchoFinish,get scene(){return radioEchoScene}};',ctx);
const next=()=>new Promise(resolve=>setImmediate(resolve));
async function start(){
 state.flags.TEA_DONE=true;state.flags.SIGNED_SHIFT=false;state.chapter=1;state.room='D';
 ctx.roomId='D';
 for(let i=0;i<24;i++)ctx.radio.frame(.15);
 await next();
 assert(ctx.radio.scene?.ready,'radio should begin after time for an ordinary player to enter');
 assert(events.includes('variant D_FALSE_MONITOR'),'the canonical false-monitor panorama is used');
 assert(events.includes('play voice-belov.mp3'),'original recorded Belov voice must play diegetically');
 ctx.radio.frame(.15);
 assert.equal(buttons[0].hidden,false,'physical radio switch appears over the in-world receiver');
}
(async()=>{
 ctx.radio.init();
 assert.equal(ctx.radio.eligible(state),true);
 assert.equal(state.progress.radioEcho,undefined);
 await start();buttons[0].onclick();
 assert.equal(state.progress.radioEcho.choice,'cut');
 assert.equal(state.journal.length,1);
 assert(events.includes('variant D_NORMAL'),'the normal room is restored after tuning off');
 assert.equal(ctx.radio.eligible(state),false,'encounter cannot repeat after a completed outcome');
 state.flags.SIGNED_SHIFT=true;
 for(let i=0;i<20;i++)ctx.radio.frame(.15);
 assert.equal(state.progress.radioEcho.heardReply,true,'canonical report retrospectively reveals the earlier impossible transmission');
 assert.equal(state.journal.length,2);
 ctx.radio.reset();state.progress={};state.journal=[];events.length=0;
 await start();
 for(let i=0;i<95;i++)ctx.radio.frame(.15);
 assert.equal(state.progress.radioEcho.choice,'listened','waiting is a valid alternative outcome');
 ctx.radio.reset();state.progress={};state.journal=[];events.length=0;
 await start();ctx.roomId='C';ctx.radio.frame(.15);
 assert.equal(state.progress.radioEcho.choice,'left','leaving never blocks the main quest or radio-room exits');
 assert.equal(state.journal.length,1);
 console.log('PASS early radio: pre-signed recorded dialogue, real panorama, physical power switch, cut/listen/leave branches, journal/save and later recognition');
})().catch(e=>{console.error(e);process.exitCode=1});
