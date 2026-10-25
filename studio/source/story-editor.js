/* Story editor UI. Inserted into the main Panorama Studio script BEFORE start(). */
const STORY_TYPES={subtitle:'Субтитр (несколько секунд)',dialogue:'Реплика / диалог',choice:'Выбор игрока',sound:'Звуковой эффект',music:'Фоновая музыка',silence:'Остановить музыку',task:'Изменить задание',card:'Заставка / глава',credits:'Титры',wait:'Пауза'};
let currentSequenceId='',currentStepIndex=0,storyController=null;
function emptyStory(){return {sequences:[],quests:[]}}
function storyMark(){APP.dirty=true;setSaveStatus('Есть несохранённые изменения сюжета');}
function storyCurrent(){return APP.story.sequences.find(x=>x.id===currentSequenceId)||null}
function storyStep(){return storyCurrent()?.steps[currentStepIndex]||null}
function newStoryScene(){const s={id:uid('scene'),name:'Новая сюжетная сцена',steps:[{type:'subtitle',text:'Здесь начинается история.',duration:3}]};APP.story.sequences.push(s);currentSequenceId=s.id;currentStepIndex=0;storyMark();storyRender();}
function storySetTab(){setRulesTab('story');storyRender()}
function storyRefreshOptions(){const select=$('actionStory');if(!select)return;const selected=select.value;select.replaceChildren();for(const s of APP.story.sequences){const o=document.createElement('option');o.value=s.id;o.textContent=s.name;select.append(o);}if([...select.options].some(o=>o.value===selected))select.value=selected;}
function storyRender(){if(!$('storyScenes'))return;const scenes=$('storyScenes');scenes.replaceChildren();for(const s of APP.story.sequences){const b=document.createElement('button');b.className='story-entry'+(currentSequenceId===s.id?' current':'');b.textContent=s.name;b.onclick=()=>{currentSequenceId=s.id;currentStepIndex=0;storyRender()};scenes.append(b)}
 const current=storyCurrent();$('storyEditor').style.display=current?'block':'none';if(!current){storyRefreshOptions();storyRenderQuests();storyRenderSounds();return;}
 $('storyName').value=current.name;
 const list=$('storySteps');list.replaceChildren();for(let i=0;i<current.steps.length;i++){const st=current.steps[i];const row=document.createElement('div');row.className='story-step'+(currentStepIndex===i?' current':'');const choose=document.createElement('button');choose.textContent=`${i+1}. ${STORY_TYPES[st.type]||st.type} — ${(st.text||st.title||st.audio||st.quest||'').slice(0,32)}`;choose.onclick=()=>{currentStepIndex=i;storyRender()};const up=document.createElement('button');up.textContent='↑';up.title='Шаг раньше';up.onclick=()=>storyMoveStep(i,-1);const down=document.createElement('button');down.textContent='↓';down.title='Шаг позже';down.onclick=()=>storyMoveStep(i,1);row.append(choose,up,down);list.append(row)}
 storyRenderFields();storyRefreshOptions();storyRenderQuests();storyRenderSounds();}
function storyMoveStep(i,d){const s=storyCurrent();const n=i+d;if(!s||n<0||n>=s.steps.length)return;[s.steps[i],s.steps[n]]=[s.steps[n],s.steps[i]];currentStepIndex=n;storyMark();storyRender();}
function stLabel(parent,label,input,onchange,hint=''){const w=document.createElement('label');w.textContent=label;w.append(input);if(hint){const n=document.createElement('div');n.className='note';n.textContent=hint;w.append(n)}input.addEventListener('change',onchange);parent.append(w);return input;}
function inputFor(type,val=''){const e=document.createElement(type);if(type==='textarea'){e.rows=3;e.style.width='100%';e.value=String(val??'');}else {e.type='text';e.value=String(val??'');}return e;}
function selectFor(arr,value){const s=document.createElement('select');for(const [val,label] of arr){const o=document.createElement('option');o.value=val;o.textContent=label;s.append(o);}s.value=value;return s;}
function storyRenderFields(){const panel=$('storyStepFields');panel.replaceChildren();const st=storyStep();if(!st)return;
 stLabel(panel,'Тип шага',selectFor(Object.entries(STORY_TYPES),st.type),e=>{const was=st.type;st.type=e.target.value;if(was!==st.type){st.text='';st.title='';st.duration=3;}storyMark();storyRender()});
 const field=(name,label,value=st[name],hint='')=>stLabel(panel,label,inputFor(name==='text'?'textarea':'input',value),e=>{st[name]=e.target.value;storyMark();storyRenderListOnly()},hint);
 if(['subtitle','dialogue','choice','card','credits'].includes(st.type))field('text',st.type==='choice'?'Вопрос игроку':st.type==='credits'?'Текст титров (можно с переносами)':'Текст',st.text,'Текст будет показан игроку. Переносы строк поддерживаются.');
 if(st.type==='dialogue')field('speaker','Кто говорит',st.speaker||'Неизвестный');
 if(['card','credits'].includes(st.type))field('title','Заголовок',st.title||'Глава');
 if(['subtitle','wait'].includes(st.type))stLabel(panel,'Продолжительность (секунды)',(()=>{const i=inputFor('input',st.duration??3);i.type='number';i.min='0.1';i.max='90';i.step='0.1';return i})(),e=>{st.duration=Math.max(.1,Math.min(90,Number(e.target.value)||3));storyMark()});
 if(['sound','music'].includes(st.type)){stLabel(panel,'Звуковой файл',selectFor([['','Выбери звук'],...[...APP.soundAssets.values()].map(s=>[s.id,s.name])],st.audio||''),e=>{st.audio=e.target.value;storyMark()},'Звуки добавляются ниже в «Библиотеке звуков». Браузер включает звук после взаимодействия игрока.');}
 if(st.type==='task'){stLabel(panel,'Задание',selectFor([['','Выбери задание'],...APP.story.quests.map(q=>[q.id,q.name])],st.quest||''),e=>{st.quest=e.target.value;storyMark()});stLabel(panel,'Действие',selectFor([['start','Начать задание'],['complete','Завершить задание']],st.mode||'start'),e=>{st.mode=e.target.value;storyMark()});}
 if(st.type==='choice'){
  const n=document.createElement('div');n.className='help-line';n.textContent='Игрок выбирает ответ. Можно поменять глобальную переменную и при необходимости запустить другую сюжетную сцену. Создай переменную заранее во вкладке 3.';panel.append(n);
  st.options=Array.isArray(st.options)?st.options:[{label:'Да',key:'',value:'true',next:''},{label:'Нет',key:'',value:'false',next:''}];
  for(let i=0;i<st.options.length;i++){
   const opt=st.options[i],group=document.createElement('div');group.className='box';group.append(document.createTextNode('Вариант '+(i+1)));
   for(const [key,label] of [['label','Текст кнопки'],['key','Глобальная переменная (необязательно)'],['value','Значение переменной']])stLabel(group,label,inputFor('input',opt[key]||''),e=>{opt[key]=e.target.value;storyMark()});
   stLabel(group,'После выбора начать сцену',selectFor([['','Без дополнительной сцены'],...APP.story.sequences.filter(s=>s.id!==currentSequenceId).map(s=>[s.id,s.name])],opt.next||''),e=>{opt.next=e.target.value;storyMark()});panel.append(group);
  }
 }
 const row=document.createElement('div');row.className='row';const del=document.createElement('button');del.textContent='Удалить этот шаг';del.onclick=()=>{const s=storyCurrent();s.steps.splice(currentStepIndex,1);currentStepIndex=Math.max(0,Math.min(currentStepIndex,s.steps.length-1));storyMark();storyRender()};row.append(del);panel.append(row);
}
function storyRenderListOnly(){const s=storyCurrent();if(!s)return;const list=$('storySteps');[...list.children].forEach((row,i)=>{const st=s.steps[i],b=row.querySelector('button');b.textContent=`${i+1}. ${STORY_TYPES[st.type]||st.type} — ${(st.text||st.title||st.audio||st.quest||'').slice(0,32)}`})}
function storyAddStep(){const s=storyCurrent();if(!s)return;const t=$('storyNewType').value;const st={type:t,duration:3,text:'',speaker:'Голос',title:'Глава',options:[{label:'Да',key:'',value:'true'},{label:'Нет',key:'',value:'false'}]};s.steps.push(st);currentStepIndex=s.steps.length-1;storyMark();storyRender()}
function storyRenderQuests(){const box=$('storyQuests');box.replaceChildren();for(const q of APP.story.quests){const row=document.createElement('div');row.className='box';stLabel(row,'Название задания',inputFor('input',q.name),e=>{q.name=e.target.value;storyMark()});stLabel(row,'Описание (для автора)',inputFor('input',q.description||''),e=>{q.description=e.target.value;storyMark()});const id=document.createElement('small');id.textContent='ID: '+q.id;row.append(id);const del=document.createElement('button');del.textContent='Удалить';del.onclick=()=>{if(APP.story.sequences.some(s=>s.steps.some(st=>st.quest===q.id))&&!confirm('Задание используется в сюжетной сцене. Удалить?'))return;APP.story.quests=APP.story.quests.filter(x=>x.id!==q.id);storyMark();storyRender()};row.append(del);box.append(row)}}
function storyRenderSounds(){const box=$('storySounds');box.replaceChildren();for(const sound of APP.soundAssets.values()){
 const row=document.createElement('div');row.className='story-sound';const label=document.createElement('span');label.textContent=sound.name+' · '+(sound.bytes.length/1024).toFixed(0)+' КБ';const play=document.createElement('button');play.textContent='Слушать';play.onclick=()=>storyListen(sound.id);const del=document.createElement('button');del.textContent='×';del.title='Удалить звук';del.onclick=()=>{if(APP.story.sequences.some(s=>s.steps.some(x=>x.audio===sound.id))&&!confirm('Звук используется в сценах. Удалить?'))return;APP.soundAssets.delete(sound.id);storyMark();storyRender()};row.append(label,play,del);box.append(row)}}
function storyListen(id){const a=APP.soundAssets.get(id);if(!a)return;const raw=Array.from(a.bytes, v=>String.fromCharCode(v)).join('');const audio=new Audio('data:'+a.mime+';base64,'+btoa(raw));audio.volume=.55;audio.play().catch(e=>toast('Звук не запущен: '+e.message));}
async function storyAddSound(file){if(!file)return;if(!file.type.startsWith('audio/')&&!/\.(wav|mp3|ogg|m4a)$/i.test(file.name))throw Error('Загрузи MP3, WAV, OGG или M4A.');if(file.size>35*1024*1024)throw Error('Звук больше 35 МБ. Для игры лучше сжать аудио.');const id=uid('sound');APP.soundAssets.set(id,{id,name:file.name,mime:file.type||'audio/wav',bytes:new Uint8Array(await file.arrayBuffer())});storyMark();storyRender();toast('Звук добавлен. Создай шаг «Звуковой эффект» или «Фоновая музыка».');}
function storyDemoInstall(){APP.story=emptyStory();APP.soundAssets=new Map();
 const samples=[['ambient.wav','Низкий гул (демо)'],['clock.wav','Старинные часы (демо)'],['creak.wav','Скрип дерева (демо)'],['sting.wav','Тревожный удар (демо)']];for(const [file,name] of samples){const id='demo_'+file.replace('.wav','');APP.soundAssets.set(id,{id,name,mime:'audio/wav',bytes:abBase64(window.STORY_DEMO_AUDIO[file])})}
 APP.story.quests=[{id:'quest_hall',name:'Найти путь через коридор',description:'После гостиной добраться до спальни'},{id:'quest_bed',name:'Осмотреть спальню и необычную игрушку',description:'Посветить на лошадку и проверить зеркало'}];
 APP.story.sequences=[
  {id:'scene_intro',name:'01. Пролог: дом просыпается',steps:[{type:'music',audio:'demo_ambient'},{type:'card',title:'Дом, который помнит',text:'Учебная история · три комнаты\nВ этой игре события связаны с предметами, взглядами и светом.'},{type:'subtitle',text:'Осмотри гостиную. Начни с кресла у камина.',duration:4},{type:'task',quest:'quest_hall',mode:'start'}]},
  {id:'scene_chair',name:'02. Кресло: субтитр + скрип',steps:[{type:'sound',audio:'demo_creak'},{type:'subtitle',text:'Кресло скрипнуло, будто кто-то только что встал.',duration:3}]},
  {id:'scene_portrait',name:'03. Портрет: диалог и выбор',steps:[{type:'dialogue',speaker:'Голос из картины',text:'Ты точно хочешь подняться наверх?'},{type:'choice',text:'Как ответить голосу?',options:[{label:'Да. Мне нужно узнать правду.',key:'story_brave',value:'true',next:''},{label:'Нет. Но назад уже поздно.',key:'story_brave',value:'false',next:''}]},{type:'subtitle',text:'Выбор изменил переменную story_brave. Найди её во вкладке «Переменные».',duration:4}]},
  {id:'scene_clock',name:'04. Часы: звук по таймеру',steps:[{type:'sound',audio:'demo_clock'},{type:'subtitle',text:'В коридоре пробили часы. Звук запустился по таймеру события.',duration:4}]},
  {id:'scene_stairs',name:'05. Лестница: взгляд + реплика',steps:[{type:'sound',audio:'demo_sting'},{type:'subtitle',text:'На ступеньках возникли следы. Кто-то только что поднялся наверх.',duration:4}]},
  {id:'scene_door',name:'06. Дверь: сюжетный переход',steps:[{type:'sound',audio:'demo_creak'},{type:'subtitle',text:'Дверь поддаётся. В спальне холоднее.',duration:2},{type:'task',quest:'quest_hall',mode:'complete'},{type:'task',quest:'quest_bed',mode:'start'}]},
  {id:'scene_horse',name:'07. Игрушка: звук от фонарика',steps:[{type:'sound',audio:'demo_sting'},{type:'dialogue',speaker:'Шёпот за спиной',text:'Только не смотри в зеркало...'}]},
  {id:'scene_finale',name:'08. Финал: остановка музыки и титры',steps:[{type:'task',quest:'quest_bed',mode:'complete'},{type:'silence'},{type:'credits',title:'КОНЕЦ УЧЕБНОЙ ИСТОРИИ',text:'GAGARIN PANORAMA STUDIO\n\nТри комнаты · предметы · переменные\nСубтитры · диалоги · выборы\nМузыка · звуки · титры · задания\n\nТеперь открой вкладку «4. Сюжет».\nТам все эти сцены можно редактировать.'}]}
 ];
 if(!APP.globals.some(g=>g.key==='story_brave'))APP.globals.push({key:'story_brave',type:'bool',value:false});
 const append=(roomName,ruleName,id)=>{const r=APP.rooms.find(r=>r.id===roomName)?.rules.find(x=>x.name===ruleName);if(r)r.actions.push({type:'story',value:id})};
 append('room_living','Гостиная: считать посещения','scene_intro');
 append('room_living','Кресло: клик → новый вид + счётчик','scene_chair');
 append('room_living','Портрет: проверка локальной переменной','scene_portrait');
 append('room_hall','Часы: таймер в коридоре','scene_clock');
 append('room_hall','Лестница: взгляд при глобальном условии','scene_stairs');
 // Note: before transition so subtitles play in correct order; actions are asynchronous.
 append('room_hall','Дверь: действие → переход в спальню','scene_door');
 append('room_bed','Лошадка: держать свет','scene_horse');
 append('room_bed','Тень: скрыть по клику','scene_finale');
 currentSequenceId=APP.story.sequences[0].id;currentStepIndex=0;storyRender();
}
function storyNewProjectReset(){if(storyController){storyController.destroy();storyController=null;}APP.story=emptyStory();APP.soundAssets=new Map();currentSequenceId='';currentStepIndex=0;storyRender()}
function setupStoryUI(){
 $('tabBtn_story').onclick=storySetTab;
 $('storyNewScene').onclick=newStoryScene;
 $('storyRemoveScene').onclick=()=>{const s=storyCurrent();if(!s)return;if(!confirm('Удалить сюжетную сцену «'+s.name+'»? Убери её из событий вручную.'))return;APP.story.sequences=APP.story.sequences.filter(x=>x.id!==s.id);currentSequenceId=APP.story.sequences[0]?.id||'';currentStepIndex=0;storyMark();storyRender()};
 $('storyName').onchange=e=>{const s=storyCurrent();if(!s)return;s.name=e.target.value||'Сцена';storyMark();storyRender()};
 $('storyNewType').replaceChildren();for(const [value,label] of Object.entries(STORY_TYPES)){const o=document.createElement('option');o.value=value;o.textContent=label;$('storyNewType').append(o)}
 $('storyAddStep').onclick=storyAddStep;
 $('storyAddQuest').onclick=()=>{APP.story.quests.push({id:uid('quest'),name:'Новое задание',description:''});storyMark();storyRender()};
 $('storyAddSound').onclick=()=>$('storyAudioFile').click();
 $('storyAudioFile').onchange=async e=>{const file=e.target.files[0];e.target.value='';try{await storyAddSound(file)}catch(err){alertErr(err)}};
 $('storyPlayScene').onclick=()=>{const scene=storyCurrent();if(!scene)return;if(!APP.play)openPlay();if(storyController){storyController.stop();storyController.play(scene.id)}};
 storyRender();
}
