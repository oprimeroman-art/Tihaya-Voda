// Studio 2.7: directional sound points and timecoded cutscenes. Fully data driven.
let g27SelSound=null,g27SelTimeline=null,g27Active=null,g27PrevAudio=null;
function g27Sound(){return APP.soundNodes.find(s=>s.id===g27SelSound)||null}
function g27Timeline(){return APP.timelines.find(t=>t.id===g27SelTimeline)||null}
function g27Mark(){APP.dirty=true;if(typeof setSaveStatus==='function')setSaveStatus('Есть несохранённые изменения режиссуры')}
function g27Element(tag,text,cls){const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x;}
function g27Select(options,value,onchange){const el=document.createElement('select');for(const [v,label] of options){const o=document.createElement('option');o.value=v;o.textContent=label;el.append(o);}el.value=value;el.onchange=e=>onchange(e.target.value);return el}
function g27Field(parent,label,tag,value,onchange){const lab=g27Element('label',label);const f=document.createElement(tag);if(tag==='input')f.type='text';f.value=value??'';f.onchange=e=>onchange(f.value);lab.append(f);parent.append(lab);return f}
function g27RefreshOptions(select,options,value){select.replaceChildren();for(const [v,label] of options){const o=document.createElement('option');o.value=v;o.textContent=label;select.append(o);}select.value=value||'';}
function g27SoundOptions(){return APP.soundNodes.map(x=>[x.id,x.name+' / '+(APP.rooms.find(r=>r.id===x.roomId)?.name||'нет комнаты')])}
function g27TimeOptions(){return APP.timelines.map(x=>[x.id,x.name]);}
function directorActionOptions(type){const options=type==='timeline'?g27TimeOptions():g27SoundOptions();g27RefreshOptions($('actionSceneSelect'),options,options[0]?.[0]);}
function directorEditorRefresh(){
 if(!g27SelSound&&APP.soundNodes.length)g27SelSound=APP.soundNodes[0].id;
 if(!g27SelTimeline&&APP.timelines.length)g27SelTimeline=APP.timelines[0].id;
 const sList=$('directorSoundList');sList.replaceChildren();for(const s of APP.soundNodes){const row=g27Element('div',undefined,'g27row'+(g27SelSound===s.id?' sel':''));const b=g27Element('button',s.name+' — '+(APP.rooms.find(r=>r.id===s.roomId)?.name||'неизвестно'),'mini');b.onclick=()=>{g27SelSound=s.id;directorEditorRefresh()};row.append(b);sList.append(row)}
 const sound=g27Sound();$('g27SoundEdit').style.display=sound?'block':'none';if(sound){
  $('g27SoundName').value=sound.name;g27RefreshOptions($('g27SoundRoom'),APP.rooms.map(r=>[r.id,r.name]),sound.roomId);
  g27RefreshOptions($('g27SoundAsset'),Array.from(APP.soundAssets.values()).map(a=>[a.id,a.name]),sound.audioId);
  $('g27SoundU').value=sound.u??.5;$('g27SoundV').value=sound.v??.5;$('g27SoundVol').value=Math.round((sound.volume??.7)*100);$('g27SoundAuto').checked=!!sound.autoplay;$('g27SoundLoop').value=String(!!sound.loop);
 }
 const tList=$('directorTimelineList');tList.replaceChildren();for(const t of APP.timelines){const row=g27Element('div',undefined,'g27row'+(g27SelTimeline===t.id?' sel':''));const b=g27Element('button',t.name+' ('+(t.steps||[]).length+' шагов)','mini');b.onclick=()=>{g27SelTimeline=t.id;directorEditorRefresh()};row.append(b);tList.append(row)}
 const t=g27Timeline();$('g27TimelineEdit').style.display=t?'block':'none';if(t){$('g27TimelineName').value=t.name;g27RefreshOptions($('g27TimelineRoom'),APP.rooms.map(r=>[r.id,r.name]),t.roomId);g27RenderSteps(t)}
}
const G27_TYPES={subtitle:'Субтитр',message:'Сообщение',camera:'Повернуть камеру (градусы)',sound:'Проиграть 3D-звук',state:'Сменить изображение объекта',show:'Показать объект',hide:'Скрыть объект',story:'Запустить сюжетную сцену',flag:'Изменить глобальную переменную'};
function g27RenderSteps(t){const box=$('g27Steps');box.replaceChildren();(t.steps||[]).forEach((st,i)=>{
 const wrapper=g27Element('div',undefined,'g27row');const name=g27Element('b',`Шаг ${i+1} — ${G27_TYPES[st.type]||st.type}`);wrapper.append(name);
 const time=g27Field(wrapper,'Время (секунда от запуска)','input',st.at??0,v=>{st.at=Math.max(0,Math.min(600,parseFloat(v)||0));t.steps.sort((a,b)=>a.at-b.at);g27Mark();directorEditorRefresh()});time.type='number';time.min=0;time.step=.1;
 const label=g27Element('label','Что сделать');const ty=g27Select(Object.entries(G27_TYPES),st.type,v=>{st.type=v;st.value='';st.target='';g27Mark();directorEditorRefresh()});label.append(ty);wrapper.append(label);
 if(['state','show','hide'].includes(st.type)){
  const opts=APP.rooms.flatMap(r=>r.objects.map(o=>[o.id,r.name+' / '+o.name]));const lab=g27Element('label','Какой объект');lab.append(g27Select(opts,st.target||opts[0]?.[0],v=>{st.target=v;g27Mark()}));wrapper.append(lab);
 }
 if(st.type==='sound'||st.type==='story'){
  const opts=st.type==='sound'?g27SoundOptions():(APP.story?.sequences||[]).map(o=>[o.id,o.name]);const lab=g27Element('label',st.type==='sound'?'Звуковая точка':'Сюжетная сцена');lab.append(g27Select(opts,st.value||opts[0]?.[0],v=>{st.value=v;g27Mark()}));wrapper.append(lab);
 }else{
  const field=g27Field(wrapper,st.type==='camera'?'Направление камеры: градусы 0–360':st.type==='state'?'Номер изображения (с нуля)':st.type==='flag'?'Формат: имя_переменной=true':'Текст / значение','input',st.value??'',v=>{st.value=v;g27Mark()});if(['camera','state'].includes(st.type)){field.type='number';field.step=st.type==='state'?'1':'5';}
 }
 const btn=g27Element('button','Удалить шаг','mini');btn.onclick=()=>{t.steps.splice(i,1);g27Mark();directorEditorRefresh()};wrapper.append(btn);box.append(wrapper);
 });}
function directorPreviewStop(){if(g27Active){g27Active=null;}if(g27PrevAudio){g27PrevAudio.pause();URL.revokeObjectURL(g27PrevAudio.src);g27PrevAudio=null;}}
function directorPreviewSound(id){const node=APP.soundNodes.find(x=>x.id===id),data=APP.soundAssets.get(node?.audioId);if(!node||!data){diagLine('warn','Звуковая точка не найдена или нет аудио','Вкладка 6 → Звуковые точки');return;}if(g27PrevAudio){g27PrevAudio.pause();g27PrevAudio=null;}const u=URL.createObjectURL(new Blob([data.bytes],{type:data.mime})),a=new Audio(u);a.volume=Math.min(1,Math.max(0,node.volume??.7));a.loop=!!node.loop;g27PrevAudio=a;a.onended=()=>{URL.revokeObjectURL(u);if(g27PrevAudio===a)g27PrevAudio=null};a.play().catch(e=>diagLine('warn','Звук требует действия пользователя: '+e.message));diagLine('ok','Звук: '+node.name+'; в готовой игре он пространственный.');}
function directorPreviewTimeline(id){const t=APP.timelines.find(x=>x.id===id);if(!t){diagLine('error','Катсцена не найдена');return;}g27Active={id,time:0,done:new Set(),roomId:APP.current};diagLine('ok','Старт катсцены: '+t.name)}
function directorPreviewTick(dt){if(!g27Active||!APP.play)return;const active=g27Active;if(APP.current!==active.roomId){directorPreviewStop();return;}active.time+=Math.min(.12,Math.max(0,dt));const t=APP.timelines.find(t=>t.id===active.id);if(!t)return;
 (t.steps||[]).forEach((st,i)=>{if(active.done.has(i)||active.time+.0001<(Number(st.at)||0))return;active.done.add(i);if(st.type==='sound')directorPreviewSound(st.value);
 else if(st.type==='subtitle'||st.type==='message')toast(String(st.value||''));
 else if(st.type==='camera'){currentRoom().view.yaw=(Number(st.value)||0)*Math.PI/180;requestDraw();}
 else if(['state','show','hide'].includes(st.type)){const found=GagarinRules.objectById(engineProject(),st.target);if(found){const obj=found.obj;if(st.type==='state')obj.state=Math.max(0,Math.min(obj.states.length-1,Number(st.value)||0));else obj.visible=st.type==='show';found.room.dirty=true;requestDraw()}}
 else if(st.type==='story')storyController?.play(st.value);
 else if(st.type==='flag'){const [key,val]=String(st.value||'').split('=');const v=APP.globals.find(x=>x.key===key);if(v)v.value=GagarinRules.scalar(val,v.type);}
 diagLine('ok','Катсцена «'+t.name+'» / '+(Number(st.at)||0)+'с: '+(G27_TYPES[st.type]||st.type));});
 if(active.done.size>=t.steps.length)g27Active=null;
}
function setupDirectorUI(){
 $('tabBtn_director').onclick=()=>setRulesTab('director');
 $('g27NewSound').onclick=()=>{const r=currentRoom();if(!r)return;const uv=screenToUv(stageSize().w/2,stageSize().h/2)||{u:.5,v:.5};const s={id:uid('spatial'),name:'Новый звук',roomId:r.id,audioId:APP.soundAssets.keys().next().value||'',u:uv.u,v:uv.v,volume:.7,loop:false,autoplay:false};APP.soundNodes.push(s);g27SelSound=s.id;g27Mark();directorEditorRefresh()};
 $('g27NewTimeline').onclick=()=>{const t={id:uid('timeline'),name:'Новая катсцена',roomId:APP.current,steps:[{at:0,type:'subtitle',value:'Начало катсцены'}]};APP.timelines.push(t);g27SelTimeline=t.id;g27Mark();directorEditorRefresh()};
 for(const [id,key,conv] of [['g27SoundName','name',v=>v],['g27SoundRoom','roomId',v=>v],['g27SoundAsset','audioId',v=>v],['g27SoundU','u',v=>Math.min(1,Math.max(0,+v||0))],['g27SoundV','v',v=>Math.min(1,Math.max(0,+v||0))],['g27SoundVol','volume',v=>Math.min(1,Math.max(0,+v/100||0))],['g27SoundLoop','loop',v=>v==='true'],['g27SoundAuto','autoplay',v=>v]])$(id).onchange=e=>{const s=g27Sound();if(s){s[key]=conv(e.target.type==='checkbox'?e.target.checked:e.target.value);g27Mark();}};
 $('g27Aim').onclick=()=>{const s=g27Sound();if(!s)return;const uv=screenToUv(stageSize().w/2,stageSize().h/2);if(!uv)return;s.roomId=APP.current;s.u=uv.u;s.v=uv.v;g27Mark();directorEditorRefresh();toast('Точка поставлена по направлению текущего взгляда.')};
 $('g27TestSound').onclick=()=>{if(g27Sound())directorPreviewSound(g27SelSound)};$('g27StopSound').onclick=directorPreviewStop;
 $('g27DeleteSound').onclick=()=>{APP.soundNodes=APP.soundNodes.filter(s=>s.id!==g27SelSound);g27SelSound=null;g27Mark();directorEditorRefresh()};
 $('g27TimelineName').onchange=e=>{const t=g27Timeline();if(t){t.name=e.target.value;g27Mark();directorEditorRefresh()}};
 $('g27TimelineRoom').onchange=e=>{const t=g27Timeline();if(t){t.roomId=e.target.value;g27Mark()}};
 $('g27NewStep').onclick=()=>{const t=g27Timeline();if(!t)return;t.steps.push({at:t.steps.length?Math.max(...t.steps.map(s=>+s.at||0))+1:0,type:'subtitle',value:'Новая реплика'});g27Mark();directorEditorRefresh()};
 $('g27DeleteTimeline').onclick=()=>{APP.timelines=APP.timelines.filter(t=>t.id!==g27SelTimeline);g27SelTimeline=null;g27Mark();directorEditorRefresh()};
 $('g27TestTimeline').onclick=()=>{const t=g27Timeline();if(!t)return;if(APP.current!==t.roomId)selectRoom(t.roomId);if(!APP.play)openPlay();directorPreviewTimeline(t.id)};
 $('g27StopTimeline').onclick=directorPreviewStop;
 directorEditorRefresh();
}
