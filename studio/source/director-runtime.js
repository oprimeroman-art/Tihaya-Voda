// Director 2.7. Audio is linked to a direction in each panoramic room.
let directorTimeline=null,directorSubtitle=null;
const directorChannels=new Map();
let directorAudioContext=null;
function directorAudioContextGet(){try{if(!directorAudioContext){const C=window.AudioContext||window.webkitAudioContext;if(C)directorAudioContext=new C();}if(directorAudioContext?.state==='suspended')directorAudioContext.resume().catch(()=>{});}catch(e){console.warn('Spatial audio unavailable',e)}return directorAudioContext;}
function directorSound(id){const s=(game.spatialSounds||[]).find(x=>x.id===id);if(!s){note('Звуковая точка удалена: '+id);return false;}if(s.roomId!==roomId){console.info('Звук находится в другой комнате',s.name);return false;}
 const file=game.audio?.[s.audioId];if(!file){note('Нет звука для точки «'+s.name+'»');return false;}
 let c=directorChannels.get(id);if(!c){const url=bytesBase64(file.data,file.mime);const audio=new Audio(url);audio.preload='auto';audio.loop=!!s.loop;c={audio,node:s,url,pan:null};const ctx=directorAudioContextGet();if(ctx){try{const source=ctx.createMediaElementSource(audio),pan=ctx.createStereoPanner();source.connect(pan).connect(ctx.destination);c.pan=pan;}catch(e){console.warn('StereoPanner unsupported',e);}}directorChannels.set(id,c);audio.onended=()=>{if(!audio.loop)directorChannels.delete(id);};}
 c.audio.currentTime=0;c.audio.loop=!!s.loop;directorUpdateSound(c);c.audio.play().catch(e=>{note('Для звука нажми на экран. '+e.message)});return true;
}
function directorUpdateSound(c){const s=c.node,az=(Number(s.u||.5)-.5)*TAU,delta=Math.atan2(Math.sin(az-yaw),Math.cos(az-yaw));const front=Math.cos(delta);const backFactor=.48+.52*((front+1)/2);c.audio.volume=clamp((Number(s.volume)||0)*backFactor*(audioSettings?.master??55)/100,0,1);if(c.pan)c.pan.pan.value=Math.sin(delta)*.93;}
function directorStopSound(){for(const c of directorChannels.values()){c.audio.pause();c.audio.currentTime=0;}directorChannels.clear();}
function directorStop(){directorTimeline=null;directorSubtitle?.remove();directorSubtitle=null;directorStopSound();}
function directorEnter(nextRoom){directorStop();}
function directorAutoEnter(){for(const s of game.spatialSounds||[])if(s.roomId===roomId&&s.autoplay)directorSound(s.id);}
function directorSubtitleShow(text){if(!directorSubtitle){directorSubtitle=document.createElement('div');directorSubtitle.id='directorSubtitle';Object.assign(directorSubtitle.style,{position:'fixed',bottom:'18%',left:'50%',transform:'translateX(-50%)',maxWidth:'min(700px,80vw)',padding:'12px 18px',zIndex:90,background:'rgba(6,8,12,.87)',border:'1px solid #ffffff35',borderRadius:'9px',textAlign:'center',color:'#fff',fontSize:'18px',pointerEvents:'none'});document.body.append(directorSubtitle);}directorSubtitle.textContent=String(text||'');directorSubtitle.dataset.until=String(performance.now()+3600);}
function directorStart(id){const t=(game.timelines||[]).find(x=>x.id===id);if(!t){note('Катсцена не найдена: '+id);return false;}if(t.roomId&&t.roomId!==roomId){note('Катсцена настроена для другой комнаты.');return false;}directorTimeline={id,time:0,done:new Set(),roomId};console.info('[Катсцена]',t.name);return true;}
function directorExecute(st){const type=st.type||'';
 if(type==='sound')directorSound(st.value);
 else if(type==='subtitle')directorSubtitleShow(st.value);
 else if(type==='message')note(st.value||'');
 else if(type==='camera'){const goal=(Number(st.value)||0)*Math.PI/180;yaw=goal;refresh();}
 else if(['state','show','hide'].includes(type)){const hit=GagarinRules.objectById(game,st.target||'');if(hit){const obj=hit.obj;if(type==='state')obj.state=clamp(parseInt(st.value,10)||0,0,obj.states.length-1);else obj.visible=type==='show';visualChanged(hit.room.id);scheduleGameSave();}}
 else if(type==='story')storyPlayer?.play(st.value);
 else if(type==='flag'){const [key,val]=String(st.value||'').split('=');const v=game.globals.find(x=>x.key===key);if(v){v.value=GagarinRules.scalar(val,v.type);scheduleGameSave();}}
}
function directorTick(dt){if(!sessionStarted||!sessionReady||sessionPaused)return;
 if(directorAudioContext?.state==='suspended')directorAudioContext.resume().catch(()=>{});
 for(const [id,c] of directorChannels){if(c.node.roomId!==roomId){c.audio.pause();directorChannels.delete(id);continue;}directorUpdateSound(c);}
 if(directorSubtitle&&performance.now()>Number(directorSubtitle.dataset.until)){directorSubtitle.remove();directorSubtitle=null;}
 if(!directorTimeline)return;const run=directorTimeline;if(run.roomId!==roomId){directorTimeline=null;return;}const t=(game.timelines||[]).find(x=>x.id===run.id);if(!t){directorTimeline=null;return;}run.time+=Math.max(0,Math.min(.15,dt));
 for(let i=0;i<(t.steps||[]).length;i++){const st=t.steps[i];if(run.done.has(i)||run.time+.001<(Number(st.at)||0))continue;run.done.add(i);directorExecute(st);console.info('[Катсцена / шаг]',t.name,st.type,st.at);}
 if(run.done.size>=t.steps.length)directorTimeline=null;
}
