/* Gagarin Story 0.1: small offline scripted narrative runtime. No external dependencies. */
window.GagarinStory = (()=>{
 const STYLE=`
 .gs-host{position:fixed;inset:0;z-index:110;pointer-events:none;color:#fff;font:14px/1.45 'Segoe UI',Arial,sans-serif}
 .gs-sub{position:absolute;bottom:8%;left:50%;transform:translateX(-50%);max-width:min(760px,82vw);width:max-content;text-align:center;padding:13px 22px;background:rgba(0,0,0,.76);border-radius:9px;text-shadow:0 1px 3px #000;box-shadow:0 4px 22px #0009;pointer-events:none;font-size:17px}
 .gs-panel{position:absolute;left:50%;bottom:4%;transform:translateX(-50%);width:min(700px,91vw);background:#101217ec;border:1px solid #666b75;border-radius:13px;padding:17px 20px;box-shadow:0 16px 55px #000a;pointer-events:auto}
 .gs-speaker{font-size:12px;letter-spacing:.08em;color:#e49598;font-weight:700;text-transform:uppercase;margin-bottom:7px}
 .gs-line{font-size:18px;white-space:pre-wrap;margin-bottom:14px}
 .gs-btn{border:1px solid #60646e;border-radius:8px;background:#252932;color:white;padding:9px 15px;cursor:pointer;font:inherit}
 .gs-btn:hover{background:#433038;border-color:#b8444c}
 .gs-choices{display:grid;gap:8px}
 .gs-card{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:8vw;background:#020304ed;pointer-events:auto}
 .gs-card h2{font:600 clamp(25px,3vw,48px)/1.3 Georgia,serif;margin:0 0 16px;color:#f3eeee}
 .gs-card pre{white-space:pre-wrap;font:16px/1.7 Georgia,serif;color:#c4c4c9;max-width:760px;max-height:65vh;overflow:auto;margin:0 0 20px}
 .gs-quest{position:absolute;left:18px;bottom:24px;max-width:min(360px,45vw);padding:10px 13px;border:1px solid #ffffff3e;border-radius:8px;background:#090b0ad0;font-size:12px;color:#dadde4}
 .gs-quest b{display:block;color:#eac5c5;margin-bottom:3px}
 .gs-top{position:absolute;top:14px;left:50%;transform:translateX(-50%);padding:10px 15px;background:#1c2029e8;border:1px solid #89939e;border-radius:9px;font-size:13px;max-width:75%;text-align:center}
 .gs-settings{position:absolute;bottom:14px;right:14px;pointer-events:auto;border:1px solid #636975;background:#171b22ed;border-radius:8px;padding:7px;color:#d9dce0;display:flex;gap:8px;align-items:center;font-size:11px}
 .gs-settings input{width:64px;accent-color:#c63439}
 .gs-settings button{background:#262b34;border:1px solid #4e535e;border-radius:5px;color:white;cursor:pointer;font-size:11px}
 .gs-settings label{display:flex;gap:5px;align-items:center}
 .gs-off{display:none!important}
 `;
 const el=(tag,cls,txt)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n};
 const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
 class Controller {
  constructor(project,opts={}){
   this.project=project;this.opts=opts;this.token=0;this.queues=[];this.running=false;this.currentAudio=null;this.music=null;this.questStates={};this.knownAudio=[];this._pendingResolve=null;this._cardResolve=null;this.paused=false;this.musicRatio=.43;this._unlock=()=>{if(!this.paused&&this.music?.paused){this.music.play().catch(()=>{})}};document.addEventListener('pointerdown',this._unlock,true);
   if(!document.getElementById('gs-css')){const style=el('style');style.id='gs-css';style.textContent=STYLE;document.head.append(style)}
   this.host=el('div','gs-host');(opts.host||document.body).append(this.host);
   this.sub=el('div','gs-sub gs-off');this.panel=el('div','gs-panel gs-off');this.card=el('div','gs-card gs-off');this.questBox=el('div','gs-quest gs-off');this.top=el('div','gs-top gs-off');
   const settings=el('div','gs-settings');const lab=el('label',null,'Звук');this.volume=el('input');this.volume.type='range';this.volume.min='0';this.volume.max='100';this.volume.value='55';lab.append(this.volume);const mute=el('button',null,'Выкл.');mute.onclick=()=>{this.volume.value=this.volume.value==='0'?'55':'0';this.adjustVolumes()};this.volume.oninput=()=>{this.adjustVolumes();this.opts.onVolume?.()};settings.append(lab,mute);
   this.host.append(this.sub,this.panel,this.card,this.questBox,this.top,settings);this.showQuests();
  }
  setProject(project){this.stop();this.project=project;this.questStates={};this.showQuests()}
  trace(level,text){this.opts.trace?.(level,text)}
  audioFile(id){return this.project?.audio?.[id]||this.project?.sounds?.[id]||null}
  createAudio(id,loop=false){const a=this.audioFile(id);if(!a){this.trace('warn','Звук «'+id+'» отсутствует. Загрузи его на вкладке «Сюжет».');return null;}let media;
   try{media=new Audio('data:'+(a.mime||'audio/wav')+';base64,'+a.data);media.loop=loop;media.volume=clamp(Number(this.volume.value)/100,0,1)*(loop?this.musicRatio:1);this.knownAudio.push(media);}catch(e){this.trace('error','Ошибка аудио: '+e.message);return null;}return media;
  }
  adjustVolumes(){for(const a of this.knownAudio){try{a.volume=clamp(Number(this.volume.value)/100,0,1)*(a.loop?this.musicRatio:1)}catch(_){}}}
  playAudio(id,loop=false){const a=this.createAudio(id,loop);if(!a)return;const task=a.play();if(task?.catch)task.catch(()=>this.trace('warn','Браузер не разрешил звук. Кликни внутри игры и повтори событие.'));
   if(loop){if(this.music){this.music.pause();this.music.currentTime=0;}this.music=a;}return a;}
  stopMusic(){if(this.music){this.music.pause();this.music.currentTime=0;this.music=null}}
  async sleep(ms,token){let left=clamp(ms,50,120000);while(left>0&&this.token===token){if(this.paused){await new Promise(r=>setTimeout(r,80));continue;}const slice=Math.min(left,80);await new Promise(r=>setTimeout(r,slice));left-=slice;}return this.token===token;}
  setPaused(yes){if(this.paused===!!yes)return;this.paused=!!yes;for(const a of this.knownAudio){if(this.paused){a._wasPlaying=!a.paused;a.pause();}else if(a._wasPlaying){a.play().catch(()=>{});a._wasPlaying=false;}}}
  async waitUnpaused(token){while(this.paused&&this.token===token)await new Promise(r=>setTimeout(r,80));return token===this.token;}
  cancelPanels(){for(const v of [this.sub,this.panel,this.card,this.top])v.classList.add('gs-off')}
  stop(){this.token++;this._pendingResolve?.(null);this._pendingResolve=null;this._cardResolve?.();this._cardResolve=null;this.queues=[];this.running=false;this.cancelPanels();this.stopMusic();for(const a of this.knownAudio){a.pause();a.src=''}this.knownAudio=[]}
  destroy(){this.stop();document.removeEventListener('pointerdown',this._unlock,true);this.host.remove()}
  play(id){const seq=(this.project?.story?.sequences||[]).find(s=>s.id===id);if(!seq){this.trace('error','Сюжетная сцена «'+id+'» отсутствует. Проверь действие в событии.');return false;}
   this.queues.push(id);this.trace('info','Сюжетная сцена в очереди: '+seq.name);if(!this.running)this.runQueue();return true;
  }
  async runQueue(){if(this.running)return;this.running=true;const token=this.token;
   try{while(this.queues.length && this.token===token){const id=this.queues.shift();const seq=this.project.story.sequences.find(s=>s.id===id);if(!seq)continue;
    for(const step of seq.steps||[]){if(this.token!==token)break;await this.runStep(step,token)}if(this.token===token)this.cancelPanels();}}
   finally{if(this.token===token)this.running=false}
  }
  waitButton(parent,labels,token){return new Promise(resolve=>{this._pendingResolve=resolve;labels.forEach((label,i)=>{const b=el('button','gs-btn',label);b.onclick=()=>{if(this.token===token){this._pendingResolve=null;resolve(i)}};parent.append(b)})})}
  async runStep(st,token){if(!st)return;await this.waitUnpaused(token);const t=st.type||'subtitle';const dur=clamp(Number(st.duration)||3,0.1,90)*1000;
   if(t==='sound'||t==='music'){if(st.audio)this.playAudio(st.audio,t==='music');return;}
   if(t==='silence'){this.stopMusic();return;}
   if(t==='task'){const id=st.quest;const q=(this.project.story.quests||[]).find(q=>q.id===id);if(!q){this.trace('warn','Задание «'+id+'» не найдено.');return;}this.questStates[id]=st.mode==='complete'?'done':'active';this.showQuests();this.opts.stateChanged?.();this.announce(st.mode==='complete'?'Задание выполнено: '+q.name:'Новая цель: '+q.name);return;}
   if(t==='wait'){await this.sleep(dur,token);return;}
   if(t==='subtitle'){this.sub.textContent=st.text||'…';this.sub.classList.remove('gs-off');await this.sleep(dur,token);this.sub.classList.add('gs-off');return;}
   if(t==='dialogue'){this.panel.replaceChildren();this.panel.append(el('div','gs-speaker',st.speaker||'Неизвестный'),el('div','gs-line',st.text||'…'));
    const controls=el('div');this.panel.append(controls);this.panel.classList.remove('gs-off');await this.waitButton(controls,['Продолжить →'],token);this.panel.classList.add('gs-off');return;}
   if(t==='choice'){
    this.panel.replaceChildren();this.panel.append(el('div','gs-speaker','РЕШЕНИЕ'),el('div','gs-line',st.text||'Что сделать?'));
    const buttons=el('div','gs-choices');this.panel.append(buttons);this.panel.classList.remove('gs-off');const opts=Array.isArray(st.options)?st.options:[];
    if(!opts.length){this.trace('warn','В сцене выбора нет ответов. Добавь варианты в редакторе.');this.panel.classList.add('gs-off');return;}const selection=await this.waitButton(buttons,opts.map(x=>x.label||'Выбрать'),token);this.panel.classList.add('gs-off');const picked=opts[selection];if(picked){if(picked.key){const variable=(this.project.globals||[]).find(g=>g.key===picked.key);if(variable){const old=variable.value;variable.value=variable.type==='bool'?(picked.value===true||picked.value==='true'):variable.type==='number'?Number(picked.value||0):String(picked.value??'');this.trace('ok',`Выбор: ${picked.label}; ${picked.key}: ${old} → ${variable.value}`);this.opts.variables?.();this.opts.stateChanged?.();}else this.trace('warn','Переменная «'+picked.key+'» не найдена — выбор не изменил сюжет.');}if(picked.next)this.queues.unshift(picked.next);}
    return;
   }
   if(t==='card'||t==='credits'){
    this.card.replaceChildren();const head=el('h2',null,st.title|| (t==='credits'?'Титры':'Глава'));const body=el('pre',null,st.text||'');this.card.append(head,body);const btn=el('button','gs-btn','Продолжить');btn.onclick=()=>{this.card.classList.add('gs-off');this._cardResolve?.()};this.card.append(btn);this.card.classList.remove('gs-off');
    await new Promise(resolve=>{this._cardResolve=resolve});this._cardResolve=null;return;
   }
   this.trace('warn','Незнакомый сюжетный шаг «'+t+'».');
  }
  announce(text){this.top.textContent=text;this.top.classList.remove('gs-off');const token=this.token;setTimeout(()=>{if(this.token===token)this.top.classList.add('gs-off')},3400)}
  showQuests(){this.questBox.replaceChildren();const a=(this.project?.story?.quests||[]).filter(q=>this.questStates[q.id]==='active');if(!a.length){this.questBox.classList.add('gs-off');return;}this.questBox.append(el('b',null,'ТЕКУЩАЯ ЦЕЛЬ'));a.forEach(q=>this.questBox.append(el('div',null,q.name)));this.questBox.classList.remove('gs-off');}
 }
 return {Controller,types:{subtitle:'Субтитр',dialogue:'Реплика с продолжением',choice:'Выбор игрока',card:'Заставка / глава',credits:'Финальные титры',sound:'Звуковой эффект',music:'Фоновая музыка',silence:'Остановить музыку',task:'Изменить задание',wait:'Пауза'}};
})();
