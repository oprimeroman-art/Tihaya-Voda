import re,json,csv,io,hashlib
from paths import *
contract=json.loads(read('DATA/07_PROJECT_CONTENT_CONTRACT.json'))
def blocks(text,pattern):
    matches=list(re.finditer(pattern,text,re.M))
    return [(m,text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip()) for i,m in enumerate(matches)]
docs=[]
for m,b in blocks(read('CANON/03_DOCUMENTS_FULLTEXT.txt'),r'^(D\d{2}) / (.+)$'):
    body=b.split('\nПодача:')[0].strip();docs.append(dict(id=m[1],title=m[2],text=body))
lines=[]
for m,b in blocks(read('CANON/04_DIALOGUE_AND_AUDIO.txt'),r'^(CH\d{2}|ENDING_[ABCD]) / (DLG_\d{3}|A\d{2}) / (.+)$'):
    # The literary paragraph is kept verbatim, including outer punctuation.
    paragraphs=b.split('\n');start=next(i for i,x in enumerate(paragraphs) if x.startswith('«'))
    body=paragraphs[start]
    lines.append(dict(id=m[2],chapter=m[1],speaker=m[3].split(' / ')[0],text=body))
lineby={x['id']:x for x in lines}
videos=[]
for m,b in blocks(read('PRODUCTION/05_FOUND_FOOTAGE_SHOTLIST.txt'),r'^(V\d{2}B?) «(.+?)» — (\d\d):(\d\d)(.*)$'):
    b=b.split('\nПОСТАНОВОЧНАЯ МАТРИЦА')[0].strip();frames=[]
    for t in re.finditer(r'^(\d\d):(\d\d)–(\d\d):(\d\d) (.+)$',b,re.M):frames.append(dict(start=int(t[1])*60+int(t[2]),end=int(t[3])*60+int(t[4]),text=t[5]))
    if not frames:frames=[dict(start=0,end=int(m[3])*60+int(m[4]),text=b)]
    refs={'V01':['DLG_009'],'V02':['DLG_025','DLG_026'],'V03':['DLG_027'],'V04':['DLG_033','DLG_034'],'V11':['DLG_042']}.get(m[1],[])
    videos.append(dict(id=m[1],title=m[2],duration=int(m[3])*60+int(m[4]),frames=frames,transcript=[lineby[x] for x in refs],production=b,slot=next(v['media_slot'] for v in contract['videos'] if v['id']==m[1])))
for l in lines:
    if l['id'].startswith('A'):
        videos.append(dict(id=l['id'],title=l['speaker'],duration=max(10,len(l['text'])/13),frames=[dict(start=0,end=max(10,len(l['text'])/13),text=l['text'])],transcript=[],slot='audio/'+l['id']+'.ogg'))
names=dict(zip('ABCDEFGHIJKLMNOP',['Жилой модуль','Кухня','Коридор','Радиорубка','Дизельная','Склад','Лаборатория','Архив','Медпункт','Шлюз','Двор','Галерея','Скважинный блок','Длинный коридор','Архив · 1978','Нижняя камера']))
A=[]
def cond(*all,**kw):return dict(all=list(all),**kw)
def flag(k,v=True):return {'set':{k:v}}
def sig(s):return {'signal':s}
def act(id,room,label,ch=None,req=None,fx=None,**kw):
    when=cond(*(req or []));
    if ch:when.update(min=ch,max=ch)
    a=dict(id=id,room=room,label=label,when=when,once=True,effects=fx or [],**kw);A.append(a);return a
def simple(id,room,label,ch,req=[],fx=[],**kw):return act(id,room,label,ch,req,[flag(id),*fx],**kw)
def puzzle(id,room,label,ch,req,answer,fields,hint,fx=[],template='matching',**kw):return simple(id,room,label,ch,req,fx,template=template,answer=answer,fields=fields,hint=hint,**kw)
def seq(id,room,label,ch,req,answer,hint,fx=[],**kw):return puzzle(id,room,label,ch,req,answer,[],hint,fx,template='sequence',buttons=list(dict.fromkeys(answer)),**kw)
def choice(id,room,label,ch,req,opts,fx=[],**kw):return simple(id,room,label,ch,req,fx,template='choice',options=opts,**kw)
def opt(v,label,fx=[],when=None,locked='Не выполнены условия'):
    return dict(value=v,label=label,effects=fx,when=when,locked=locked)
def item(id,room,label,ch,req=[],fx=[]):return simple('take_'+id,room,label,ch,req,[{'item':id},*fx])
def document(id,room,ch,req=[],**kw):
    d=next(x for x in docs if x['id']==id);a=act('read_'+id,room,d['title'].split(' / ')[-2] if 'ГЛАВА' in d['title'] else d['title'],None,req,[{'document':id}],template='document',document=id,once_override=False,**kw);a['when'].update(min=ch);a['once']=False;return a
def media(id,room,ch,req=[],fx=[]):
    a=act('watch_'+id,room,('Копия А · ' if id=='V01' else '')+next(x['title'] for x in videos if x['id']==id),None,req,[flag(('HEARD_' if id.startswith('A') else 'WATCHED_')+id),*fx],template='media',media=id,signal=id.lower()+'_end');a['when'].update(min=ch);a['once']=False;return a
item('BADGE04','A','Взять бейдж ОПЕРАТОР-04',1)
item('STORAGE_KEY','A','Осмотреть кружку: ключ под дном',1,['take_BADGE04'])
seq('TEA_SEQUENCE','B','Приготовить чай',1,['take_BADGE04'],['вода','нагрев','заварка','разлить'],'Синяя полоска: вода → нагрев → заварка → разлить.',[flag('TEA_DONE')],startSignal='inspect_kettle')
choice('sign_shift','D','Форма приёма · 18.01.2026',1,['TEA_DONE'],[opt('OK','ЗАМЕЧАНИЙ НЕТ',[flag('SIGNED_SHIFT'),sig('signed_shift')])])
item('FUSE_3','F','Открыть шкаф №3 ключом: предохранитель',1,['SIGNED_SHIFT',{'item':'STORAGE_KEY'}],[sig('take_fuse')])
simple('install_fuse3','E','Установить предохранитель №3',1,[{'item':'FUSE_3'}])
powerFields=[dict(label='Отопление · 4',options=['А','Б']),dict(label='Лаборатория · 3',options=['А','Б']),dict(label='Радио · 2',options=['А','Б'])]
puzzle('POWER_BASIC','E','Распределить нагрузку',2,[],['А','Б','Б'],powerFields,'D28: на А — отопление 4; на Б — лаборатория 3 + радио 2. Предел каждой шины 5.',[sig('power_basic_done')],template='switches')
puzzle('CORES_MARKING','G','Подписать три керна',2,['POWER_BASIC'],['840/A','877/B','899/C'],[dict(label=x,options=['840/A','877/B','899/C']) for x in ['P-14','P-15','P-16']],'Карточки: P-14 — 840 м / A; P-15 — 877 м / B; P-16 — 899 м / C.',[sig('cores_labeled')])
puzzle('RADIO_TUNE','D','Настроить контрольный эфир',2,['CORES_MARKING'],[4625,'..-'],[dict(label='Частота, кГц',min=4600,max=4650,step=1),dict(label='Код',options=['---','.-.','..-'])],'Метка 4625 кГц, допуск ±5. Код: точка, точка, тире.',template='dial',tolerance=[5,0])
simple('send_report','D','Отправить и закрыть отчёт',2,['RADIO_TUNE'],[sig('radio_report_sent')])
seq('PLUMB_SEQ','F','Снять четыре пломбы ящика №12',3,['FOUND_D19'],['2','4','1','3'],'D19: порядок 2 — 4 — 1 — 3.',[{'item':'VHS_V01'},{'item':'ARCHIVE_KEY'}])
media('V01','H',3,[{'item':'VHS_V01'}])
simple('cabinet_message','H','Осмотреть открывшийся шкаф',3,['WATCHED_V01','BUCKET_FALLEN'],[flag('ARCHIVE_MESSAGE_SHOWN'),sig('return_after_v01')],text='«НЕ ДЕЛАЙ ВИД, ЧТО МЫ НЕ ЗНАКОМЫ».')
simple('archive_return','C','Вернуться к обходу',3,['cabinet_message'])
puzzle('count_cans','F','Сверить банки с ведомостью',4,['FOUND_D20'],[5,4],[dict(label='Банок на полке',min=0,max=9),dict(label='Банок в ведомости',min=0,max=9)],'На полке пять банок, в ведомости четыре. Банку 2028 года не использовать.',[sig('inventory_check')])
seq('COOKING','B','Приготовить обед',4,['count_cans'],['вода','крупа','нагрев','тушёнка','выключить'],'Вода → крупа → нагрев → тушёнка → выключить.',[flag('COOKED'),sig('cooked')])
choice('plate_choice','B','Вторая тарелка',4,['COOKED'],[opt('LEFT','Поставить вторую порцию',[flag('SECOND_PLATE','LEFT')]),opt('REMOVED','Убрать тарелку',[flag('SECOND_PLATE','REMOVED')]),opt('UNTOUCHED','Оставить нетронутой',[flag('SECOND_PLATE','LEFT')])])
simple('dinner_exit','C','Закрыть обеденный отчёт',4,['plate_choice'],[sig('after_dinner_first_enter')])
item('P17_SAMPLE','G','Открыть холодильный бокс: P-17',5,[],[sig('p17_found')])
puzzle('SPECTRUM_MATCH','G','Совместить зубцы спектра',5,[{'item':'P17_SAMPLE'}],[2,5,1],[dict(label='Фрагмент '+str(i),min=0,max=7) for i in range(1,4)],'Контрольный силуэт: позиции зубцов 2, 5, 1.',[sig('spectrum_completed')],template='layer_match')
puzzle('MICROSCOPE','G','Повернуть поляризационный диск',5,['SPECTRUM_MATCH'],[90],[dict(label='Угол поляризатора, °',min=0,max=180,step=22.5)],'Четыре деления по 22,5° дают 90°.',[flag('P17_ANALYZED'),sig('microscope_completed')],template='dial')
simple('hidden_enter','C','Открыть дверь «ТИХАЯ»',5,['MICROSCOPE'],[{'variant':{'C':'C_HIDDEN'}},sig('inspect_hidden_sink')])
simple('hidden_exit','C','Открыть противоположную створку',5,['hidden_enter'],[{'variant':{'C':'C_NORMAL'}},flag('RETURNED_HIDDEN'),sig('return_from_hidden')])
puzzle('WAVE_PHASE','D','Настроить резервный приёмник',6,[],[40,70],[dict(label='Фаза',min=0,max=100),dict(label='Фильтр',min=0,max=100)],'Совпадение контрольной линии: фаза 40 ±5, фильтр 70 ±5.',template='dual_dial',tolerance=[5,5],startSignal='start_wave_minigame')
media('A01','D',6,['WAVE_PHASE'],[sig('wave_phase_success')]);media('A02','D',6,['WAVE_PHASE'],[sig('play_second_signal')])
simple('flip_acts','D','Перевернуть акт: прочитать оборот 17-Б',6,['FOUND_D07'],[flag('FOUND_ACT_BOTH')],text=next(d['text'] for d in docs if d['id']=='D07'))
for id,label in [('FLASHLIGHT','Фонарь'),('ANTENNA_KEY','Ключ антенны'),('BEACON','Маяк')]:item(id,'J','Взять: '+label,7)
for i in range(1,4):simple('ice_'+str(i),'K','Очистить крепление '+str(i),7,[],[sig('antenna_started')] if i==1 else [])
puzzle('ANTENNA','K','Соединить кабели антенны',7,['ice_1','ice_2','ice_3'],['1','3','2','отключён'],[dict(label='Кабель '+x,options=['1','2','3','отключён']) for x in 'ABCX'],'Схема: A→1, B→3, C→2. X повреждён — оставить отключённым.',[flag('K_COMMS_REPAIRED'),sig('repair_connector_two'),sig('antenna_repaired')])
puzzle('AIRLOCK_EQUALIZE','J','Выровнять давление · КОНТРОЛЬ',7,['ANTENNA'],[50,50,50],[dict(label=x,min=0,max=100) for x in ['Вход','Переход','Выход']],'D22: все три аналоговые стрелки 50 ±2; затем КОНТРОЛЬ. Не открывайте наружную створку.',[flag('AIRLOCK_SAFE'),sig('pressure_verified')],template='triple_dial',tolerance=[2,2,2],checkpoint='before_airlock_pressure')
a=act('outer_door','J','Открыть НАРУЖНУЮ створку',7,['ANTENNA',{'not':'AIRLOCK_SAFE'}],[sig('open_outer_without_pressure'),{'death':'Шлюз: наружная створка открыта до контроля давления'}],text='D22: при голосе снаружи не меняйте порядок действий. Открытие без КОНТРОЛЯ смертельно.',confirm='Открыть наружную створку вопреки инструкции?');a['once']=False
simple('inner_door','J','Открыть внутреннюю створку',7,['AIRLOCK_SAFE'],[flag('Q07_RETURN'),{'room':'C'},sig('return_from_airlock')])
for id in ['VHS_FRAGMENT_A','VHS_FRAGMENT_B']:item(id,'H','Взять фрагмент кассеты '+id[-1],8)
seq('VHS_ASSEMBLE','H','Склеить фрагменты плёнки',8,[{'item':'VHS_FRAGMENT_A'},{'item':'VHS_FRAGMENT_B'}],['КУХНЯ','ГАЛЕРЕЯ','РАДИО'],'D23: непрерывный гул — пищеблок → галерея → радио.',[sig('vhs_assembled')])
media('V02','H',8,['VHS_ASSEMBLE'],[sig('turn_off_vhs')])
simple('wet_towel','C','Осмотреть мокрое полотенце',8,['WATCHED_V02'],[sig('exit_after_v02')])
a=item('VHS_V03','H','Взять личную кассету для Оли',None,[],[]);a['when'].update(min=8)
media('V03','H',8,[{'item':'VHS_V03'}])
for id in ['PUNCHCARD_RU','PUNCHCARD_DE']:item(id,'H','Взять перфолист '+id[-2:],9)
puzzle('PUNCHCARD_OVERLAY','H','Совместить кресты перфолистов',9,['FOUND_D09',{'item':'PUNCHCARD_RU'},{'item':'PUNCHCARD_DE'}],[0,0],[dict(label='Горизонтальный сдвиг относительно креста',min=-4,max=4),dict(label='Вертикальный сдвиг относительно креста',min=-4,max=4)],'Совместить угловые кресты: оба смещения 0. Полученный индекс 0-4.',[flag('DRILL04_ID'),sig('punchcard_solved')],template='layer_match')
simple('scan_uv','G','Осмотреть шлиф P-17 под УФ',9,['PUNCHCARD_OVERLAY'])
simple('enter_1978','H','Открыть шкаф по старой схеме',9,['scan_uv'],[{'variant':{'H':'H_1978'}},sig('return_from_uv_scan'),sig('enter_after_swap')])
simple('calibration_plate','H','Осмотреть калибровочную пластину',9,['enter_1978'],[sig('inspect_calibration_plate'),sig('ozerov_count_four')])
simple('exit_1978','H','Закрыть шкаф и открыть снова',9,['enter_1978'],[{'variant':{'H':'H_NORMAL'}},sig('close_old_cabinet')])
# A repeated visit remains possible if the player left before collecting the safety note.
a=act('reenter_1978','H','Вернуться к старому шкафу',None,['scan_uv',{'not':'FOUND_D08'}],[{'variant':{'H':'H_1978'}}]);a['when'].update(min=9);a['once']=False
puzzle('CARDIOMATCH','I','Сопоставить карты пациентов',10,['FOUND_D17','FOUND_D18'],['А и Б'],[dict(label='Совпадающая последовательность фаз',options=['А и В','Б и В','А и Б'])],'D18: А и Б — одинаковые 72–88–72–64.',[sig('patient_match_done')])
puzzle('TIMELINE_SYNC','D','Восстановить запись инцидента',10,['CARDIOMATCH'],[37,37,37],[dict(label=x+' · секунда',min=0,max=60) for x in ['Рычаг','Звук','Давление']],'Маркеры всех трёх дорожек совмещаются на 00:37, допуск ±1 с.',[flag('RESTORED_V04'),sig('v04_restored')],template='timeline',tolerance=[1,1,1])
media('V04','D',10,['RESTORED_V04'],[sig('after_v04_end')])
for id,label,s in [('backward_clock','Отметить часы, идущие назад','enter_long_corridor'),('reversed_exit_arrow','Отметить обратную стрелку «ВЫХОД»','second_segment'),('handwriting_floor','Отметить свежую подпись на полу','third_segment')]:simple(id,'N',label,10,[],[sig(s)])
simple('leave_N','N','Открыть выход в обычный коридор',10,['backward_clock','reversed_exit_arrow','handwriting_floor'],[flag('EXIT_N_UNLOCKED'),sig('three_clues_found'),sig('open_exit_after_clues'),{'room':'C'}])
choice('false_act','C','Служебная форма объяснения',10,['EXIT_N_UNLOCKED'],[opt('NO','Акт не подтверждаю',[flag('FALSE_ACT_SIGNED',False)]),opt('YES','Подтверждаю: створка заклинила',[flag('FALSE_ACT_SIGNED')])],confirm='Подписанное свидетельство будет закреплено в контуре. Подтвердить выбранную формулировку?')
puzzle('NODE_POWER','E','Узел: энергия',11,[],['А','Б','Б'],powerFields,'D28: использовать аналоговые приборы. А=4, Б=3+2.',[flag('NODE_POWER_DONE')],template='switches',startSignal='start_power_node')
tapes=[opt('TRUTH','Признание и запись аварии',[flag('TAPE_CHOICE','TRUTH'),flag('NODE_MEMORY_DONE')],'RESTORED_V04','Восстановите запись аварии'),opt('PETR','Личное сообщение Петра',[flag('TAPE_CHOICE','PETR'),flag('NODE_MEMORY_DONE')],'WATCHED_V03','Просмотрите личную кассету в архиве'),opt('ARCHIVE','Первичный архив',[flag('TAPE_CHOICE','ARCHIVE'),flag('NODE_MEMORY_DONE')],{'any':['FOUND_D04','FOUND_D09']},'Прочитайте архивные документы')]
a=choice('NODE_MEMORY','H','Узел: записать катушку',None,[],tapes,[sig('after_copy_choice')],confirm='Выбранная катушка станет якорем. Предыдущая копия как якорь будет уничтожена; материалы для просмотра останутся. До финальной подписи можно перезаписать.');a['when'].update(min=11);a['once']=False
a=choice('NODE_OBSERVER','I','Узел: назначить наблюдателей',None,[],[opt(1,'Оператор — 1',[flag('OBSERVER_COUNT',1),flag('NODE_OBSERVER_DONE')]),opt(2,'Оператор и Поздний — 2',[flag('OBSERVER_COUNT',2),flag('NODE_OBSERVER_DONE')],['FOUND_ACT_BOTH','RESTORED_V04','FOUND_D08'],'Нужны обе стороны актов, восстановленная авария и инструкция Озерова')]);a['when'].update(min=11);a['once']=False
seq('SHUTTERS','L','Вернуть заслонки в нейтраль',11,['NODE_POWER_DONE','NODE_MEMORY_DONE','NODE_OBSERVER_DONE'],['L','R','C'],'Рисунок на приборе: 1 — левая L; 2 — правая R; 3 — центр C. Четыре ошибки смертельны.',[flag('SHUTTERS_SAFE'),sig('shutters_correct')],checkpoint='before_shutters',startSignal='start_shutters',failureEffects=[sig('wrong_shutter')],deathAfter=4,deathEffects=[sig('four_wrong_shutters')],deathName='Галерея: четыре ошибки заслонок')
a=simple('petr_letter','H','Копирующий терминал → «Для Оли» → исходящая почта',None,['FOUND_D05','WATCHED_V03',{'item':'VHS_V03'}],[flag('PETR_LETTER_DONE'),{'document':'D25'},sig('petr_letter_sent')]);a['when'].update(min=8)
choice('name_reply','D','Ответить Белову',11,['NODE_POWER_DONE','NODE_MEMORY_DONE','NODE_OBSERVER_DONE','SHUTTERS_SAFE'],[opt('NO','Нет',[flag('NAME_REPLY','NO'),sig('reply_no')]),opt('SILENCE','Молчать',[flag('NAME_REPLY','SILENCE'),sig('reply_silence')]),opt('OFF','Отключить передатчик',[flag('NAME_REPLY','OFF'),sig('reply_off')])],[sig('radio_choice_done')],text=lineby['DLG_037']['text'])
simple('second_window','L','Посмотреть во второе окно',12,[],[flag('window_1978_seen'),sig('inspect_second_window')]);simple('third_window','L','Посмотреть в третье окно',12,[],[sig('inspect_third_window')])
simple('POWER_OFF','M','Отключить внешний привод',12,['window_1978_seen'])
item('SHUTTER_PIN','M','Взять стопорный штифт',12,['POWER_OFF'])
simple('PIN_INSERT','M','Вставить механический стопор',12,['POWER_OFF',{'item':'SHUTTER_PIN'}],[sig('power_off_and_pin')])
simple('ANALOG_READINGS_OK','M','Сверить аналоговые стрелки',12,['PIN_INSERT'],[sig('inspect_monitor_still')])
simple('OBSERVER_SELECT','M','Подтвердить назначенных наблюдателей',12,['ANALOG_READINGS_OK'])
endfx=lambda mode:[sig('confirm_mode_'+mode),{'ending':mode}]
endnames=['ОСТАНОВКА','СОВМЕСТНОЕ НАБЛЮДЕНИЕ','ПЕРЕДАЧА','ЛОКАЛЬНЫЙ ПЕРЕНОС']
prices=['Цена: потеря личной идентификации.','Цена: наложение распространяется за остров.','Цена: люди получат несовместимые свидетельства.','Цена: сохранённые голоса размагничиваются, цикл остаётся открытым.']
opts=[]
for i,k in enumerate('ABCD'):
    src=contract['ending_conditions'][k];c=dict(all=src.get('all',[]),eq=src.get('equals',{}),**({'in':src['in']} if 'in' in src else {}))
    # Canon additionally requires the personal message, represented by the cassette/letter path.
    missing={'A':'','B':'Нужны два наблюдателя, обе стороны актов и запись исправного рычага.','C':'Нужны D02, D03, D04, D14, восстановленная авария и катушка признания либо архива.','D':'Нужны личная запись Петра, отправленное письмо Оле и отказ от ложного акта. Катушка должна хранить Петра.'}[k]
    opts.append(opt(k,endnames[i]+' — '+prices[i],endfx(k),c,missing))
choice('FINAL_PANEL','P','Выбрать режим и поставить подпись',12,['OBSERVER_SELECT'],opts,confirm='После подписи режим необратим. Подписать? Сохранение до панели останется доступным.',startSignal='show_modes')['template']='sequence_choice'
# Full document registry, with diegetic availability and persistent library copies.
docplaces={1:('B',1),2:('D',6),3:('C',5),4:('H',9),5:('F',8),6:('G',5),7:('D',6),8:('H',9),9:('H',9),10:('E',11),11:('D',10),12:('H',9),13:('H',8),14:('D',10),15:('D',10),16:('B',4),17:('I',10),18:('I',10),19:('F',3),20:('F',4),21:('H',9),22:('J',7),23:('H',8),24:('A',11),25:('H',8),26:('L',12),27:('D',6),28:('E',2),29:('H',8)}
for n,(r,ch) in docplaces.items():
    req={3:['hidden_enter'],6:['MICROSCOPE'],7:['HEARD_A01','HEARD_A02'],8:[{'eq':{'HISTORIC_AVAILABLE':True}}],12:['enter_1978'],14:['WATCHED_V04'],25:['PETR_LETTER_DONE'],27:['HEARD_A01']}.get(n,[])
    if n==8:req=['enter_1978']
    a=document(f'D{n:02}',r,ch,req)
    if n==3:a['effects']+=[sig('take_d03')]
media('V01B','H',11,['WATCHED_V01'],[sig('replay_v01_ch11')])
for id,r,ch,req in [('V05','H',9,['FOUND_D04']),('V06','H',9,['enter_1978']),('V07','H',11,[]),('V08','D',10,['FOUND_D11']),('V09','H',9,['enter_1978']),('V10','D',11,[]),('V11','H',11,['FOUND_D04','FOUND_D09','FOUND_D12']),('A03','H',9,['enter_1978']),('A04','I',10,['FOUND_D17']),('A05','B',11,[])]:media(id,r,ch,req)
# Calm interactions and controllable mirror beats are ordinary editable actions.
for id,r,label in [('slippers','A','Ровно поставить тапочки'),('wash_cup','B','Вымыть кружку'),('paper_tray','D','Убрать лист в лоток')]:
    a=act(id,r,label,fx=[flag(id)],text='Выполнено.');a['once']=False
for id,r,ch,label,req,signal in [
 ('mirror03','C',3,'Повторно посмотреть в металлическое зеркало',['WATCHED_V01'],'second_look_after_m03'),
 ('mirror04','B',4,'Посмотреть в зеркало над раковиной',['COOKED'],'inspect_sink_after_cooked'),
 ('mirror04_away','B',4,'Обернуться к пустому стулу',['mirror04'],'look_away_m04'),
 ('mirror04_again','B',4,'Снова посмотреть в зеркало',['mirror04_away'],'second_mirror_look'),
 ('mirror04_third','B',4,'Обернуться к двери и вернуть взгляд',['mirror04_again'],'third_mirror_look'),
 ('mirror06','D',6,'Осмотреть выключенный монитор',['HEARD_A01','HEARD_A02'],'inspect_off_monitor_after_audio'),
 ('mirror06_again','D',6,'Приблизиться к экрану',['mirror06'],'approach_monitor_after_m06'),
 ('glass07','J',7,'Осмотреть стекло шлюза',['ANTENNA'],'inspect_frosted_glass'),
 ('medic10','I',10,'Осмотреть зеркало медицинского шкафа',['CARDIOMATCH'],'inspect_medic_cabinet'),
 ('late10','D',10,'Обернуться от чёрного монитора',['WATCHED_V04'],'turn_from_late_mirror'),
 ('blanket11','I',11,'Поднять покрывало',[],'remove_blanket')]:
    a=simple(id,r,label,None,req,[sig(signal)]);a['when'].update(min=ch,max=(5 if ch==4 else ch))
# Navigation edges are enforced by both sidebar and native room switching.
links=[]
def link(a,b,when=None,locked='Дверь закрыта по протоколу.'):
    links.append(dict(from_=a,to=b,when=when,locked=locked));links[-1]['from']=links[-1].pop('from_')
for r in 'ABDEFGHIJL':
    c={'H':{'item':'ARCHIVE_KEY'},'I':{'min':4},'J':{'min':7},'L':{'min':11}}.get(r)
    link('C',r,c,{'H':'Нужен ключ из архивного ящика №12.','I':'Медпункт откроется после архивного обхода.','J':'Наружные работы ещё не разрешены.','L':'СКВАЖИНА 0-4: ЗАКРЫТО ПО ПРОТОКОЛУ'}.get(r,''))
    link(r,'C',{'not':{'all':['ANTENNA',{'not':'Q07_RETURN'}]}} if r=='J' else None,'Сначала выровняйте давление и откройте внутреннюю створку.')
link('J','K',cond(*[{'item':x} for x in ['FLASHLIGHT','ANTENNA_KEY','BEACON']],{'not':'ANTENNA'},min=7), 'Перед выходом: фонарь, ключ, маяк. После ремонта используйте контроль давления.')
link('K','J');link('L','M','Q11_DONE');link('M','L');link('M','P','OBSERVER_SELECT');link('P','M');link('C','N',cond('WATCHED_V04',{'not':'EXIT_N_UNLOCKED'},min=10));link('N','C',cond('backward_clock','reversed_exit_arrow','handwriting_floor'))
# Preserve the 16th logical room as the historic alias, never a second navigation island.
questneeds=[['take_BADGE04','take_STORAGE_KEY','TEA_DONE','SIGNED_SHIFT','install_fuse3'],['POWER_BASIC','CORES_MARKING','RADIO_TUNE','send_report'],['archive_return'],['dinner_exit'],['FOUND_D03','RETURNED_HIDDEN'],['HEARD_A01','HEARD_A02','FOUND_ACT_BOTH'],['Q07_RETURN'],['WATCHED_V02','wet_towel'],['exit_1978','calibration_plate','FOUND_D08','FOUND_D12'],['false_act','EXIT_N_UNLOCKED'],['name_reply'],['Q12_DONE']]
qnames=['Принять смену','Утренний обход','Проверить архивный пакет №12','Приготовить обед и сверить учёт','Проверить пробу P-17','Настроить резервный эфир','Восстановить антенну','Восстановить плёнку','Найти нулевую скважину','Сверить записи инцидента','Стабилизировать наблюдение','Остановить контур']
quests=[dict(id=f'Q{i+1:02}',chapter=i+1,title=qnames[i],phase=contract['narrative_chapters'][i]['world_phase'],complete=questneeds[i],checkpoint=True,help=read('PRODUCTION/02_QUEST_FLOW_AND_PUZZLES.txt').split(f'Q{i+1:02} /')[1].split('\n\nQ')[0].split('\nСТЕЙДЖИНГ')[0]) for i in range(12)]
events=list(csv.DictReader(io.StringIO(read('DATA/06_DIRECTOR_EVENT_MATRIX.tsv')),delimiter='\t'))
# Explicit bindings: no interpreting English trigger names or random events at runtime.
bindings={1:'game_start',2:'inspect_kettle',3:'signed_shift',4:'take_fuse',5:'power_basic_done',6:'cores_labeled',7:'radio_report_sent',8:'q02_done',9:'enter:F',10:'v01_end',11:'enter:C',12:'return_after_v01',13:'enter:C',14:'second_look_after_m03',15:'enter:A',16:'enter:D',17:'inventory_check',18:'cooked',19:'inspect_sink_after_cooked',20:'second_mirror_look',21:'third_mirror_look',22:'enter:B',23:'enter:B',24:'after_dinner_first_enter',25:'enter:B',26:'enter:C',27:'enter:A',28:'p17_found',29:'spectrum_completed',30:'microscope_completed',31:'enter:C',32:'inspect_hidden_sink',33:'take_d03',34:'return_from_hidden',35:'enter:C',36:'enter:A',37:'start_wave_minigame',38:'wave_phase_success',39:'play_second_signal',40:'inspect_off_monitor_after_audio',41:'approach_monitor_after_m06',42:'a02_end',43:'enter:I',44:'enter:A',45:'enter:B',46:'antenna_started',47:'repair_connector_two',48:'antenna_repaired',49:'enter:J',50:'open_outer_without_pressure',51:'inspect_frosted_glass',52:'pressure_verified',53:'return_from_airlock',54:'enter:B',55:'enter:A',56:'vhs_assembled',57:'v02_end',58:'turn_off_vhs',59:'exit_after_v02',60:'v03_end',61:'enter:B',62:'enter:H',63:'enter:A',64:'punchcard_solved',65:'return_from_uv_scan',66:'enter_after_swap',67:'inspect_calibration_plate',68:'ozerov_count_four',69:'close_old_cabinet',70:'enter:H',71:'enter:C',72:'enter:D',73:'patient_match_done',74:'inspect_medic_cabinet',75:'v04_restored',76:'after_v04_end',77:'turn_from_late_mirror',78:'enter_long_corridor',79:'second_segment',80:'third_segment',81:'three_clues_found',82:'open_exit_after_clues',83:'enter:B',84:'start_power_node',85:'enter:B',86:'enter:C',87:'enter:I',88:'remove_blanket',89:'replay_v01_ch11',90:'enter:A',91:'enter:F',92:'enter:D',93:'after_copy_choice',94:'start_shutters',95:'wrong_shutter',96:'four_wrong_shutters',97:'shutters_correct',98:'petr_letter_sent',99:'enter:D',100:'radio_choice_done',101:'enter:L',102:'inspect_second_window',103:'inspect_third_window',104:'power_off_and_pin',105:'inspect_monitor_still',106:'enter:P',107:'show_modes',108:'confirm_mode_A',109:'confirm_mode_B',110:'confirm_mode_C',111:'confirm_mode_D',112:'ending_done'}
guards={9:['Q02_DONE'],11:['WATCHED_V01'],13:['WATCHED_V01'],15:['WATCHED_V01'],16:['WATCHED_V01'],22:[{'eq':{'SECOND_PLATE':'LEFT'}}],23:[{'eq':{'SECOND_PLATE':'REMOVED'}}],25:['plate_choice'],26:['B_BOARD_TWO'],27:['plate_choice'],31:['MICROSCOPE'],35:['RETURNED_HIDDEN'],36:['RETURNED_HIDDEN'],42:['HEARD_A01','HEARD_A02'],49:['ANTENNA'],54:['Q07_RETURN'],55:['Q07_RETURN'],61:['WATCHED_V03'],62:['WATCHED_V02'],63:['WATCHED_V02'],70:['exit_1978'],71:['exit_1978'],72:['exit_1978'],83:['EXIT_N_UNLOCKED'],86:['B_TWO_GHOSTS'],99:['NODE_POWER_DONE','NODE_MEMORY_DONE','NODE_OBSERVER_DONE','SHUTTERS_SAFE']}
dialogue_map={1:[1],2:[2],3:[3],6:[4,5],7:[6],8:[7],9:[8],12:[10,11],20:[12],18:[13,14],28:[15],32:[16],34:[17],37:[18],41:[19,20],46:[21],49:[22,23],52:[24],57:[28],66:[29,30,31,32],76:[35],82:[36],85:[41],99:[43,37],107:[44],108:[45],109:[46],111:[47]}
variant_map={9:'F_ARCHIVE12',12:'H_AFTER_V01',13:'C_MIRROR_LIGHT',18:'B_SECOND_PLATE',19:'B_GHOST_MIRROR',28:'G_P17',30:'G_MIRROR_DOOR',31:'C_HIDDEN_DOOR',40:'D_FALSE_MONITOR',42:'D_DOUBLE_ACTS',46:'K_TOWER_SILHOUETTE',48:'K_TOWER_EMPTY',49:'J_FALSE_BELOV',52:'J_SAFE',53:'C_REVERSED_SNOW',58:'H_ANNA_GLASS',65:'H_1978',69:'H_NORMAL',76:'D_LATE_MIRROR',78:'N_CLOCK',79:'N_SIGN',80:'N_HANDWRITING',81:'N_LATE_EXIT',84:'E_FALSE_DIGITAL',85:'B_TWO_GHOSTS',87:'I_COVERED_BODY',88:'I_EMPTY_BED',89:'H_V01B',91:'F_SUIT_STANDING',92:'D_INDOOR_TOWER',94:'L_SHUTTER_DANGER',101:'L_THREE_WINDOWS',104:'M_DELAY_MONITOR',108:'P_END_A',109:'P_END_B',110:'P_END_C',111:'P_END_D'}
for e in events:
    n=int(e['event_id'][1:]);ch=int(e['chapter']);e.update(id=e['event_id'],chapter=ch,signal=bindings[n],when=cond(*guards.get(n,[]),min=ch,max=ch),effects=[flag(e['sets_flag'])],horror=e['category'] not in ['normal'],lines=[lineby[f'DLG_{x:03}'] for x in dialogue_map.get(n,[])])
    if n==8:e['when']={'all':['Q02_DONE']}
    if n in [22,23,24,27,34,42,53,54,55,59,60,61,69,70,71,72,81,82,98,100]:e['when'].pop('max',None)
    if n in [8,24,34,53,69,82,100]:e['when']['min']=min(ch, e['when'].get('min',ch))
    if n==34:e['delay']=12
    if n in [50,96]:e['room']=None
    if n==100:e['room']=None
    if n in variant_map:e['effects'].append({'variant':{e['room'] or 'C':variant_map[n]}})
    # The queue is cosmetic; progression flags are established by actual interactions.
    if n==38:e['effects']=[x for x in e['effects'] if 'set' not in x]
    if n==39:e['effects']=[x for x in e['effects'] if 'set' not in x]
for n in [8,24,53,59,69,82,100,112]:events[n-1]['when'].pop('max',None)
# Bind every remaining spoken line to an explicit interaction or chapter transition.
used={l['id'] for e in events for l in e['lines']}|{l['id'] for v in videos for l in v['transcript']}
reply={'DLG_038':'reply_no','DLG_039':'reply_silence','DLG_040':'reply_off'}
dialogues=[dict(id=l['id'],signal=reply.get(l['id'],'chapter:'+l['chapter'][2:]),line=l) for l in lines if l['id'] in reply]
script=read('CANON/01_SCRIPT_DIRECTORS_CUT_V2.txt')
ends={}
for m,b in blocks(script,r'^([ABCD]) «([^»]+)»\. (.+)$'):
    # All final-scene paragraphs occur on the heading line itself.
    ends[m[1]]=dict(title=m[2],text=m[3])
events[41]['signal']=['a01_end','a02_end']
events[97]['when']['min']=8
events[85]['signal']='event:E085'
for n in [81,82]:events[n-1]['room']=None
# Return-visit beats remain available immediately after the quest's completion.
for n in [15,16,27,35,36,54,55,61,63,83]:events[n-1]['when'].pop('max',None)
for a in A:
    if a['id']=='name_reply':
        for op,line in zip(a['options'],['DLG_038','DLG_039','DLG_040']):op['effects'].append({'dialogue':line})
    if a['id']=='read_D07':a['readLabel']='Прочитана лицевая сторона · перевернуть отдельно'
    if a['id']=='outer_door':a['deathHelp']=next(d['text'] for d in docs if d['id']=='D22')
for m in videos:m['kind']='audio' if m['id'].startswith('A') else 'video'
for k,e in ends.items():
    # Keep source prose intact; remove production-only unlock conditions from the player scene.
    e['sourceText']=e['text']
    e['text']=re.sub(r'^Условия:.*?\. ', '', e['text'])
    e['text']=re.sub(r'^Доступен всегда\. ', '', e['text'])
    e['extraLines']=['A06'] if k=='C' else []
    if k=='D':e['media']='V12'
    post=next(d['text'] for d in docs if d['id']=='D30')
    post=re.sub(r'\[зависит от финала;[^\]]+\]',{'A':'0','B':'2','C':'НЕ УСТАНОВЛЕНО','D':'1'}[k],post)
    e['postcredit']=re.sub(r'\[A: НЕТ[^\]]+\]',{'A':'НЕТ','B':'ДВА ПОДТВЕРЖДЕНИЯ','C':'НЕ СОВПАДАЮТ СВИДЕТЕЛЬСТВА','D':'ПРИНЯТО БЕЗ ЗАМЕЧАНИЙ'}[k],post)
data=dict(version=1,id='tihaya_voda_v2',title='ПОЛЯРНАЯ СМЕНА',startRoom='A',initial=contract['initial_state'],rooms=[dict(r,name=names[r['id']]) for r in contract['rooms']],links=links,quests=quests,actions=A,documents=docs,media=videos,dialogues=lines,replyDialogues=dialogues,events=events,endings=ends,endingConditions=contract['ending_conditions'],onEnter=[dict(room='J',when=cond('ANTENNA',{'not':'AIRLOCK_SAFE'},min=7,max=7),effects=[{'checkpoint':'before_airlock_pressure'}])],assetSlots=list(csv.DictReader(io.StringIO(read('PRODUCTION/09_ASSET_SLOTS.tsv')),delimiter='\t')),items=contract['items'],sourceHashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['CANON/01_SCRIPT_DIRECTORS_CUT_V2.txt','CANON/03_DOCUMENTS_FULLTEXT.txt','CANON/04_DIALOGUE_AND_AUDIO.txt','DATA/06_DIRECTOR_EVENT_MATRIX.tsv']})
assert len(docs)==30 and len(lines)==53 and len(events)==112 and len(videos)==19
data['credits']='Сценарий: «Протокол „Тихая вода“», редакция 2.0.\nДвижок: Gagarin Panorama Studio.\nАвторские панорамы, озвучка и видео ожидаются.'
for r in data['rooms']:r['variantAssets']={}
PROJECT=ROOT/'TIHAYA_VODA';PROJECT.mkdir(exist_ok=True)
(PROJECT/'adventure.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'actions':len(A),'documents':len(docs),'dialogues':len(lines),'media':len(videos),'events':len(events)}))
