/* Gagarin Panorama Engine 2.1 — offline, safe declarative event runtime. */
window.GagarinRules=(function(){
 const types={click:'Нажатие',enter:'Вход в комнату',gaze:'Взгляд',light:'Фонарик',timer:'Таймер комнаты'};
 const actions={story:'Запустить сюжетную сцену',cycle:'Следующий вид',state:'Выбрать вид',show:'Показать',hide:'Скрыть',set:'Записать переменную',add:'Прибавить число',message:'Сообщение',room:'Перейти',media_play:'Воспроизвести медиа',media_stop:'Остановить медиа',timeline:'Запустить катсцену',spatial_play:'Проиграть звук из точки'};
 const scalar=(v,type)=>type==='bool'?(v===true||v==='true'||v===1||v==='1'):type==='number'?(Number(v)||0):String(v??'');
 const roomById=(p,id)=>p.rooms.find(r=>r.id===id);
 function objectById(p,id){for(const room of p.rooms)for(const obj of room.objects||[])if(obj.id===id)return {room,obj};return null;}
 function variableInfo(p,roomId,scope,key){const room=roomById(p,roomId),arr=scope==='local'?room?.vars:p.globals;return (arr||[]).find(v=>v.key===key);}
 const getVariable=(p,roomId,scope,key)=>variableInfo(p,roomId,scope,key)?.value;
 function comparison(value,op,want){if(op==='none')return true;if(value===undefined)return false;let need=typeof value==='boolean'?scalar(want,'bool'):typeof value==='number'?Number(want):String(want);if(op==='eq')return value===need;if(op==='ne')return value!==need;if(op==='gte')return Number(value)>=Number(need);if(op==='lte')return Number(value)<=Number(need);return false;}
 function conditionDetail(p,roomId,c){if(!c||c.op==='none')return {ok:true};if(!c.key)return {ok:false,why:'Выбрана проверка, но не заполнено имя переменной.',help:'В шаге 2 выбери «Без условий» либо впиши существующую переменную.'};const v=variableInfo(p,roomId,c.scope,c.key);if(!v)return {ok:false,why:'Переменная «'+c.key+'» не существует '+(c.scope==='local'?'в этой комнате.':'глобально.'),help:'Создай её на вкладке «3. Переменные» или выбери правильную область.'};const ok=comparison(v.value,c.op,c.value);return {ok,why:ok?'':`Условие не прошло: ${c.key} сейчас ${JSON.stringify(v.value)}, а требуется ${c.op} ${JSON.stringify(c.value)}.`,help:'Проверь начальное значение переменной и событие, которое должно его изменить.'};}
 const allowed=(p,id,c)=>conditionDetail(p,id,c).ok;
 function Runtime(project,hooks={}){this.project=project;this.hooks=hooks;this.visits={};this.elapsedRoom=0;this.progress={};this.fired={};this.current=project.current||project.rooms[0]?.id;this.log=[];this.depth=0;}
 Runtime.prototype.emit=function(level,text,help,ruleId){const item={level,text,help:help||'',roomId:this.current,ruleId:ruleId||null};this.log.unshift(item);this.log=this.log.slice(0,70);this.hooks.trace?.(item);if(level==='ok')this.hooks.log?.(text);return item;};
 Runtime.prototype.report=function(txt){this.emit('ok',txt)};
 Runtime.prototype.enter=function(roomId){const room=roomById(this.project,roomId);if(!room){this.emit('error','Комната не найдена: '+roomId,'Проверь переходы между комнатами.');return false;}this.current=roomId;this.project.current=roomId;this.elapsedRoom=0;this.progress={};this.visits[roomId]=(this.visits[roomId]||0)+1;this.hooks.room?.(roomId);this.emit('info','Вход: '+room.name+'. Посещение №'+this.visits[roomId]);this.fire('enter',null,roomId);return true;};
 Runtime.prototype.fire=function(type,sourceId=null,roomId=this.current){const room=roomById(this.project,roomId);if(!room)return 0;let count=0,matched=0;if(this.depth>8){this.emit('error','Слишком длинная цепочка событий.','Проверь переходы между комнатами в действиях.');return 0;}this.depth++;
 try{const source=sourceId?objectById(this.project,sourceId)?.obj:null;
 if(type==='click'){this.emit('info','Клик: '+(source?.name||'пустое место')+' в комнате «'+room.name+'»');}
 for(const rule of room.rules||[]){if(rule.trigger!==type)continue;if(rule.source && rule.source!==sourceId)continue;matched++;
 if(!rule.enabled){this.emit('skip','«'+rule.name+'»: отключено.','Поставь галочку «Событие включено».',rule.id);continue;}
 if(rule.once&&this.fired[rule.id]){this.emit('skip','«'+rule.name+'»: уже выполнено один раз.','Сними «Только один раз» или начни игровой просмотр заново.',rule.id);continue;}
 const cond=conditionDetail(this.project,roomId,rule.condition);if(!cond.ok){this.emit('skip','«'+rule.name+'»: '+cond.why,cond.help,rule.id);continue;}
 if(!rule.actions?.length){this.emit('warn','«'+rule.name+'» сработало, но список действий ПУСТОЙ.','В шаге 3 добавь действие «Переключить вид» или другое.',rule.id);continue;}
 this.fired[rule.id]=(this.fired[rule.id]||0)+1;count++;this.emit('ok','СРАБОТАЛО: «'+rule.name+'». Действий: '+rule.actions.length,'',rule.id);
 for(let i=0;i<rule.actions.length;i++){if(this.current!==roomId&&i>0){this.emit('warn','Комната изменилась в середине цепочки — остальные действия выполняются в исходном контексте.', 'Переход между комнатами лучше ставить последним.',rule.id);}this.perform(rule.actions[i],roomId,rule.id,i+1);}
 }
 if(type==='click'&&!matched)this.emit('warn','На объект «'+(source?.name||'пустое место')+'» нет событий «Нажали на объект».','Открой вкладку «2. События» нужной комнаты, создай событие и в шаге 1 выбери этот предмет.');
 return count;
 }finally{this.depth--;}};
 Runtime.prototype.perform=function(a,roomId,ruleId=null,index=0){const pr=index?`Действие ${index}: `:'';const ref=a.target?objectById(this.project,a.target):null,o=ref?.obj;
 if(['cycle','state','show','hide'].includes(a.type)){
  if(!o){this.emit('error',pr+'объект для действия не найден.','В шаге 3 выбери существующий объект в списке «Объект».',ruleId);return false;}
  const elsewhere=ref.room.id!==roomId?' ВНИМАНИЕ: объект находится в другой комнате («'+ref.room.name+'»).':'';
  if(a.type==='cycle'||a.type==='state'){
   if(!o.states?.length){this.emit('error',pr+'«'+o.name+'» не имеет изображений.','Добавь изображения в шаге «1. Объект».',ruleId);return false;}
   const old=Math.max(0,Math.min(o.states.length-1,o.state||0)),next=a.type==='cycle'?(old+1)%o.states.length:Math.max(0,Math.min(o.states.length-1,Math.floor(Number(a.value)||0)));
   o.state=next;this.hooks.visual?.(ref.room.id);
   if(next===old){this.emit('warn',pr+'«'+o.name+'»: изображение осталось №'+(old+1)+' из '+o.states.length+'.'+elsewhere,'Добавь хотя бы 2 изображения или задай другую цель действия.',ruleId);}else{this.emit('ok',pr+'«'+o.name+'»: вид '+(old+1)+' → '+(next+1)+' из '+o.states.length+'.'+elsewhere+(o.visible?'':' ОБЪЕКТ СКРЫТ.'),o.visible?'':'Добавь действие «Показать объект», иначе изменение останется невидимым.',ruleId);}return true;
  }
  const old=!!o.visible;o.visible=a.type==='show';this.hooks.visual?.(ref.room.id);this.emit(old===o.visible?'warn':'ok',pr+'«'+o.name+'»: '+(o.visible?'показан':'скрыт')+'.'+elsewhere,old===o.visible?'Он уже был в таком состоянии.':'',ruleId);return true;
 }
 if(a.type==='set'||a.type==='add'){
  const scope=a.scope==='local'?'local':'global',v=variableInfo(this.project,roomId,scope,a.key);if(!v){this.emit('error',pr+'переменная «'+a.key+'» не найдена.','Перейди в «3. Переменные» и создай её в правильной области.',ruleId);return false;}
  if(a.type==='add'&&v.type!=='number'){this.emit('error',pr+'складывать можно только числа. «'+v.key+'» имеет тип '+v.type+'.','Создай переменную типа «Число» или выбери действие «Изменить переменную».',ruleId);return false;}
  const old=v.value;v.value=scalar(a.type==='add'?Number(old||0)+Number(a.value||0):a.value,v.type);this.hooks.variables?.();this.emit('ok',pr+(scope==='global'?'Глобальная':'Локальная')+' «'+v.key+'»: '+JSON.stringify(old)+' → '+JSON.stringify(v.value),'',ruleId);return true;
 }
 if(a.type==='story'){if(!a.value){this.emit('error',pr+'сюжетная сцена не выбрана.','В шаге 3 укажи сцену на вкладке «4. Сюжет».',ruleId);return false;} const ok=this.hooks.story?.(a,roomId);if(ok===false){this.emit('error',pr+'сюжетная сцена «'+a.value+'» не найдена.','Открой вкладку «4. Сюжет», создай или выбери сцену.',ruleId);return false;}this.emit('ok',pr+'запущена сюжетная сцена «'+a.value+'»','',ruleId);return true;}
 if(a.type==='media_play'||a.type==='media_stop'){
  if(!o){this.emit('error',pr+'медиаобъект не найден.','Выбери предмет на вкладке «5. Медиа».',ruleId);return false;}
  if(!o.media||o.media.kind==='none'){this.emit('warn',pr+'для «'+o.name+'» не задано медиа.','Открой вкладку 5 и назначь видео, кадры или голос.',ruleId);return false;}
  this.hooks.media?.(ref.room.id,o.id,a.type==='media_play');
  this.emit('ok',pr+'«'+o.name+'»: '+(a.type==='media_play'?'воспроизвести':'остановить')+' '+o.media.kind,'',ruleId);return true;
 }
 if(a.type==='timeline'||a.type==='spatial_play'){
  if(!a.value){this.emit('error',pr+'не выбрана '+(a.type==='timeline'?'катсцена':'звуковая точка')+'.','Открой вкладку «6. Режиссура» и выбери объект.',ruleId);return false;}
  const source=a.type==='timeline'?(this.project.timelines||[]).find(t=>t.id===a.value):(this.project.spatialSounds||[]).find(q=>q.id===a.value);
  if(!source){this.emit('error',pr+'катсцена или звуковая точка удалена: '+a.value+'.','На вкладке «6. Режиссура» выбери существующий элемент.',ruleId);return false;}
  this.hooks.director?.(a.type,a.value,roomId);
  this.emit('ok',pr+(a.type==='timeline'?'Катсцена: ':'Звук: ')+source.name,'',ruleId);return true;
 }
 if(a.type==='message'){this.hooks.message?.(String(a.value??''));this.emit('ok',pr+'сообщение «'+String(a.value??'')+'»','',ruleId);return true;}
 if(a.type==='room'){const dest=roomById(this.project,a.value);if(!dest){this.emit('error',pr+'целевая комната не найдена.','Выбери действующую комнату для перехода.',ruleId);return false;}this.emit('ok',pr+'переход в «'+dest.name+'»');this.enter(dest.id);return true;}
 this.emit('error',pr+'неизвестный тип действия: '+a.type,'Проверь настройку действия в редакторе.',ruleId);return false;
 };
 Runtime.prototype.tick=function(dt,lookId,lightId){this.elapsedRoom+=dt;const room=roomById(this.project,this.current);if(!room)return;for(const rule of room.rules||[]){if(!rule.enabled||!['gaze','light','timer'].includes(rule.trigger))continue;if(rule.once&&this.fired[rule.id])continue;
  const active=rule.trigger==='timer'||(!!rule.source&&rule.trigger==='gaze'&&rule.source===lookId)||(!!rule.source&&rule.trigger==='light'&&rule.source===lightId);if(!active){this.progress[rule.id]=0;continue;}
  this.progress[rule.id]=(this.progress[rule.id]||0)+dt;
  if(this.progress[rule.id]>=Math.max(.1,Number(rule.delay)||1)){this.progress[rule.id]=0;this.fire(rule.trigger,rule.source||null,room.id);}
 }};
 return {Runtime,types,actions,allowed,conditionDetail,getVariable,objectById,scalar};
})();
