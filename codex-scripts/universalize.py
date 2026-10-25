from paths import *
p=STUDIO/'source/adventure-core.js';s=p.read_text(encoding='utf-8')
s=s.replace("if(x.variant)Object.assign", "if(x.dialogue){const line=this.data.dialogues.find(l=>l.id===x.dialogue);if(line){this.state.journal.push({text:line.speaker,lines:[line]});this.hooks.line?.(line);}}if(x.variant)Object.assign")
p.write_text(s,encoding='utf-8')
p=STUDIO/'source/adventure-ui.js';s=p.read_text(encoding='utf-8')
s=s.replace("this.engine=new api.Engine(data,{change:", "this.pendingLines=[];this.engine=new api.Engine(data,{line:l=>this.pendingLines.push(l),change:")
start=s.index("map(){const b=");end=s.index('\n+ journal()',start) if '\n+ journal()' in s[start:] else s.index('\n journal()',start)
s=s[:start]+"map(){const b=this.panel('Схема помещений');const names=Object.fromEntries(this.data.rooms.map(r=>[r.id,r.name]));for(const r of this.data.rooms){const destinations=this.data.links.filter(l=>l.from===r.id).map(l=>names[l.to]);if(destinations.length)b.append(el('p',r.name+' → '+destinations.join(', ')));}this.button(b,'Закрыть',()=>this.close());}"+s[end:]
s=s.replace("a.document==='D07'?'Прочитана лицевая сторона · перевернуть отдельно':'Сохранить в журнале'", "a.readLabel||'Сохранить в журнале'")
s=s.replace("a.id==='FINAL_PANEL'", "a.template==='sequence_choice'")
start=s.index("b.append(el('p',message),el('p','Антенный ремонт")
end=s.index("this.button(b,'Повторить узел'",start)
s=s[:start]+"b.append(el('p',message),el('p','Выполненные до чекпоинта действия сохранены.'));if(a.deathHelp||a.hint)b.append(el('pre',a.deathHelp||a.hint));"+s[end:]
start=s.index("if(a.id==='name_reply')");end=s.index('return r;}',start)
s=s[:start]+"if(this.pendingLines.length){const lines=this.pendingLines.splice(0),b=this.panel('Эфир');for(const line of lines)b.append(el('pre',line.text));this.button(b,'Продолжить',()=>this.close());}"+s[end:]
s=s.replace("m.id.startsWith('V')?'video':'audio'", "m.kind==='audio'?'audio':'video'")
start=s.index(' ending(){');end=s.index('\n}\napi.UI=UI;',start)
s=s[:start]+''' ending(){this.endingShown=true;const mode=this.engine.state.ended,e=this.data.endings[mode];const b=this.panel(e.title);b.append(el('div','ВРЕМЕННО: финальная постановка без авторского видео и звука.','ga-slot'),el('pre',e.text));for(const id of e.extraLines||[]){const line=this.data.dialogues.find(l=>l.id===id);if(line)b.append(el('pre',line.text));}if(e.media)this.button(b,'Посмотреть эпилог',()=>this.playMedia(this.data.media.find(m=>m.id===e.media),null));
 this.button(b,'Титры',()=>{const box=this.panel(this.data.title);box.append(el('p',this.data.credits||''));this.button(box,'Следующая проверка',()=>{this.engine.signal('ending_done');const p=this.panel('Журнал следующей смены');p.append(el('pre',e.postcredit||''));this.button(p,'Загрузить до панели',()=>this.restoreCheckpoint());this.button(p,'Новая игра',()=>this.hooks.newGame?.());});});}
''' +s[end:]
p.write_text(s,encoding='utf-8')
print('Removed game IDs and lore from generic UI; callbacks and ending text come from project data.')
