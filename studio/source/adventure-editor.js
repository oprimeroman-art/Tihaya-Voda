/* Structured authoring for the optional story.adventure extension. */
function adventureEditorOpen(){
 const data=APP.story.adventure;if(!data){toast('В этом проекте нет расширения приключения. Старый формат сохранён.');return;}
 const shade=document.createElement('div');shade.style.cssText='position:fixed;inset:0;z-index:9000;background:#071017e8;display:flex;align-items:center;justify-content:center';
 const box=document.createElement('section');box.style.cssText='width:min(1100px,96vw);height:92vh;background:#14242d;color:#e6edf1;padding:24px;border:1px solid #6a818e;border-radius:14px;display:flex;flex-direction:column;gap:10px';shade.append(box);document.body.append(shade);
 const head=document.createElement('h2');head.textContent='Сценарий · задания, предметы, документы, медиа, события';box.append(head);
 const top=document.createElement('div');top.style.cssText='display:flex;gap:10px';box.append(top);const group=document.createElement('select'),select=document.createElement('select');
 for(const [v,label] of Object.entries({actions:'Взаимодействия / головоломки',quests:'Задания',documents:'Документы',media:'Медиаслоты / субтитры',events:'Режиссёрские события',rooms:'Состояния помещений',links:'Переходы',dialogues:'Реплики',items:'Предметы'}))group.add(new Option(label,v));top.append(group,select);
 const desc=document.createElement('p');desc.textContent='Редактируется выбранная сущность. Все поля сохраняются в PROJECT.zip и GAME.zip. when — условия; effects — действия; answer — ответ шаблона. Для медиа загрузите файл на вкладке 5/6 и назначьте его ID в поле assetId.';box.append(desc);
 const area=document.createElement('textarea');area.spellcheck=false;area.style.cssText='flex:1;min-height:200px;background:#09151c;color:#dfe9ed;font:14px/1.5 Consolas,monospace;padding:16px;resize:none';box.append(area);
 const status=document.createElement('p');status.setAttribute('aria-live','polite');box.append(status);const controls=document.createElement('div');controls.style.cssText='display:flex;gap:12px';box.append(controls);
 function button(text,fn){const b=document.createElement('button');b.textContent=text;b.onclick=fn;controls.append(b);return b;}
 function renderList(){select.replaceChildren();(data[group.value]||[]).forEach((a,i)=>select.add(new Option((a.id||a.from+' → '+a.to)+' · '+(a.label||a.title||a.presentation||a.name||''),String(i))));renderItem();}
 function renderItem(){area.value=JSON.stringify(data[group.value][Number(select.value)],null,2);status.textContent='';}
 group.onchange=renderList;select.onchange=renderItem;
 button('Применить сущность',()=>{try{const edited=JSON.parse(area.value),i=Number(select.value),old=data[group.value][i];if(!edited||typeof edited!=='object'||Array.isArray(edited))throw Error('Ожидается объект JSON');if(old.id&&edited.id!==old.id)throw Error('ID связан с другими сущностями: сохраните исходный ID');data[group.value][i]=edited;APP.dirty=true;setSaveStatus('Сценарий изменён — сохраните проект');status.textContent='Изменения применены.';}catch(e){status.textContent='Не применено: '+e.message;}});
 button('Экспорт сценария JSON',()=>downloadBlob(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),'adventure.json'));
 button('Закрыть',()=>shade.remove());renderList();
}
function adventureEditorInstall(){const b=document.createElement('button');b.id='adventureEdit';b.textContent='7. Сценарий';b.onclick=adventureEditorOpen;const host=document.getElementById('editorTabs');if(host)host.append(b);}
