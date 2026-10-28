/* One interruptible narration channel. It never changes story progression. */
(function(api){
'use strict';
class VoiceQueue{
 constructor({resolve,volume=()=>1,createAudio=()=>new Audio(),blocked=()=>{}}){this.resolve=resolve;this.volume=volume;this.createAudio=createAudio;this.blocked=blocked;this.queue=[];this.generation=0;this.paused=false;this.mediaPaused=false;}
 enqueue(ids){for(const id of ids){const asset=this.resolve(id);if(asset?.url)this.queue.push({id,url:asset.url});}if(!this.audio)this.next();}
 next(){if(this.audio||this.paused||this.mediaPaused||!this.queue.length)return;const track=this.queue.shift(),generation=this.generation;
  const audio=this.createAudio();this.audio=audio;this.currentId=track.id;audio.dataset.voiceId=track.id;audio.preload='auto';audio.src=track.url;this.syncVolume();
  audio.onended=()=>{if(generation!==this.generation||this.audio!==audio)return;this.release();this.next();};
  audio.onerror=()=>{if(generation!==this.generation||this.audio!==audio)return;this.blocked('error',track.id);this.release();this.next();};this.play();
 }
 play(){const audio=this.audio,generation=this.generation;if(!audio||this.paused||this.mediaPaused)return;this.syncVolume();
  try{Promise.resolve(audio.play()).then(()=>{if(generation===this.generation&&this.audio===audio)this.blocked(null);}).catch(error=>{if(generation!==this.generation||this.audio!==audio)return;if(error?.name==='AbortError')return;this.blocked(error?.name==='NotAllowedError'?'gesture':'error',this.currentId);});}catch(error){this.blocked('error',this.currentId);}
 }
 syncVolume(){if(this.audio){const v=Number(this.volume());this.audio.volume=Number.isFinite(v)?Math.max(0,Math.min(1,v)):1;}}
 setPaused(value,media=false){const key=media?'mediaPaused':'paused';if(this[key]===!!value)return;this[key]=!!value;if(this.paused||this.mediaPaused)this.audio?.pause();else if(this.audio)this.play();else this.next();}
 release(){if(this.audio){this.audio.onended=this.audio.onerror=null;this.audio.pause();this.audio.removeAttribute('src');this.audio.load();this.audio.remove?.();this.audio=null;}this.currentId=null;}
 stop(){this.generation++;this.queue=[];this.release();this.mediaPaused=false;this.blocked(null);}
}
api.VoiceQueue=VoiceQueue;
})(window.GagarinAdventure);
