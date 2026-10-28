const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const window={GagarinAdventure:{}};vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../source/voice-queue.js'),'utf8'),{window,Audio:null});
const Queue=window.GagarinAdventure.VoiceQueue;
(async()=>{let playing=0,max=0,volume=.55,blocked=[],reject=false,created=[];
 function createAudio(){const a={dataset:{},paused:true,currentTime:0,play(){if(reject){const e=Error('gesture');e.name='NotAllowedError';return Promise.reject(e);}if(this.paused){playing++;max=Math.max(max,playing);}this.paused=false;return Promise.resolve();},pause(){if(!this.paused)playing--;this.paused=true;},removeAttribute(){},load(){},remove(){},end(){this.pause();this.onended?.();}};created.push(a);return a;}
 const q=new Queue({resolve:id=>id==='missing'?null:{url:id},volume:()=>volume,createAudio,blocked:r=>blocked.push(r)});
 q.enqueue(['DLG_004','missing','DLG_005']);assert.equal(q.currentId,'DLG_004');assert.equal(created.length,1);assert.equal(q.audio.volume,.55);
 q.audio.currentTime=2;q.setPaused(true);assert.equal(playing,0);q.setPaused(false);assert.equal(q.audio.currentTime,2);
 q.audio.end();assert.equal(q.currentId,'DLG_005');assert.equal(max,1,'voices cannot overlap');
 volume=0;q.syncVolume();assert.equal(q.audio.volume,0);volume=.8;q.syncVolume();assert.equal(q.audio.volume,.8);
 q.setPaused(true,true);q.setPaused(true);q.setPaused(false);assert.equal(playing,0,'system resume respects media pause');q.setPaused(false,true);assert.equal(playing,1);
 const stale=q.audio.onended;q.stop();stale();assert.equal(q.audio,null);assert.equal(q.queue.length,0);assert.equal(playing,0);
 reject=true;q.enqueue(['DLG_001','DLG_002']);await new Promise(r=>setImmediate(r));assert.equal(blocked.at(-1),'gesture');assert.equal(q.currentId,'DLG_001');
 reject=false;q.play();await new Promise(r=>setImmediate(r));assert.equal(blocked.at(-1),null);q.stop();
 q.setPaused(true);q.enqueue(['DLG_003']);assert.equal(q.audio,null);q.setPaused(false);assert.equal(q.currentId,'DLG_003');q.stop();
 console.log('PASS sequential voice IDs, no overlap, pause/resume, mute, close cancellation, stale callbacks and autoplay retry');
})().catch(e=>{console.error(e);process.exit(1)});
