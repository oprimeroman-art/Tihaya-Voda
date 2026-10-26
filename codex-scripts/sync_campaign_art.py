#!/usr/bin/env python3
"""Keep approved story illustrations identical in project, canon and offline builds.

Does not replace panoramas, calibrations or media. Reuses checksum-verified art.
"""
from pathlib import Path
import base64,copy,json
from alpha_wave4_props import apply_wave4_props
from alpha_wave5_medical import apply_medical_props
from alpha_wave6_stockroom import apply_stockroom_props
from alpha_wave7_puzzle_docs import apply_puzzle_docs
from alpha_wave8_late_docs import apply_late_docs
from alpha_wave9_document_props import apply_wave9
ROOT=Path(__file__).resolve().parents[1]

def write_json(path,value):
    new=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if path.read_text(encoding='utf-8')!=new:path.write_text(new,encoding='utf-8')

def main():
    canonical=ROOT/'studio/content/TIHAYA_VODA/adventure.json'
    story=json.loads(canonical.read_text(encoding='utf-8'))
    payload={'story':{'adventure':copy.deepcopy(story)}}
    for apply in (apply_wave4_props,apply_medical_props,apply_stockroom_props,apply_puzzle_docs,apply_late_docs,apply_wave9):apply(payload,ROOT)
    enriched=payload['story']['adventure']
    # The archive key is actually awarded by PLUMB_SEQ but was absent from the item catalog.
    if not any(i['id']=='ARCHIVE_KEY' for i in enriched['items']):
        enriched['items'].append({'id':'ARCHIVE_KEY','pickup_room':'F','used_by':'Q03','type':'quest_item','persistent_across_checkpoints':True})
    names={'BADGE04':'Бейдж ОПЕРАТОР-04','STORAGE_KEY':'Ключ склада','FUSE_3':'Предохранитель №3','VHS_V01':'Кассета 01','ARCHIVE_KEY':'Ключ архива','P17_SAMPLE':'Образец P-17','FLASHLIGHT':'Фонарь','ANTENNA_KEY':'Ключ антенны','BEACON':'Радиомаяк','VHS_FRAGMENT_A':'Фрагмент кассеты A','VHS_FRAGMENT_B':'Фрагмент кассеты B','PUNCHCARD_RU':'Перфолист RU','PUNCHCARD_DE':'Перфолист DE','VHS_V03':'Личная кассета для Оли','SHUTTER_PIN':'Стопорный штифт'}
    for item in enriched['items']:item['name']=names[item['id']]
    for item in enriched['items']:
        raw=(ROOT/'art/inventory'/f"{item['id']}.webp").read_bytes()
        enriched['illustratedProps']['image']['item_'+item['id']]='data:image/webp;base64,'+base64.b64encode(raw).decode('ascii')
    enriched['illustratedProps']['item']={item['id']:'item_'+item['id'] for item in enriched['items']}
    for mode in ('A','B','C','D'):
        raw=(ROOT/'art/endings'/f'{mode}.webp').read_bytes()
        enriched['illustratedProps']['image']['ending_'+mode]='data:image/webp;base64,'+base64.b64encode(raw).decode('ascii')
    enriched['illustratedProps']['ending']={mode:'ending_'+mode for mode in ('A','B','C','D')}
    enriched['illustratedProps']['endingScenes']={
        'A':[
            {'caption':'Контур перекрыт. Осталось одно наблюдение.'},
            {'caption':'Три монитора. Одна пустая кровать. Три разные даты.'},
            {'caption':'«Маяк, база. Подтверждаю. У нас сходятся часы».\n\n«Если ты там... Ты мне не отвечай. Я просто побуду на линии».'},
            {'caption':'Через несколько месяцев в архиве числятся ноль работников. В пустой столовой поднимается пар от одной кружки.\n\nМир устойчив. Оператор исчез из официальной памяти.'}],
        'B':[
            {'caption':'За столом двое. Поздний держит руки на коленях. За стеной кипит чайник.'},
            {'caption':'«Я не думал, что ты останешься».\n\nОтвета нет. Смена передана вдвоём.'},
            {'caption':'На материке кассир достаёт два билета. Оба на одно место. Двери электрички открываются с двух сторон — к разным платформам.'},
            {'caption':'Второй наблюдатель сохранён. Наложение вышло за пределы острова.'}],
        'C':[
            {'caption':'Аналоговый передатчик включён. Вместо имени — шорох магнитной ленты.'},
            {'caption':'«Створка была исправна. Закрыл я. Сказал обратное».\n\nПриборы теряют даты. Передача продолжается.'},
            {'caption':'Спустя несколько месяцев в редакции сопоставляют распечатки и интервью. Свидетельства не сходятся. На фотографии комиссии виден оператор. На обороте указано: снимал он сам.'},
            {'caption':'Правда стала публичной. Полученные людьми факты несовместимы.'}],
        'D':[
            {'caption':'Сохранённые голоса расходуются на локальную синхронизацию. Катушки размагничиваются.'},
            {'caption':'В кухне на прежнем стуле сидит живой Сухов. Руки сильно мёрзнут.\n\n«Грей воду. И давай без красивых речей — мне домой надо».'},
            {'caption':'За открытой дверью — ясный полярный день.\n\nЧерез неделю новый сотрудник заполняет форму. Под его «Смену принял» уже стоит знакомый чужой почерк.'},
            {'caption':'Возможно, один человек возвращён. Цикл не закрыт.'}]
    }
    enriched['illustratedProps']={kind:dict(sorted(values.items())) for kind,values in sorted(enriched['illustratedProps'].items())}
    # Cosmetic maps only; preserve all authored quests, choices and timings.
    for key in story:
        if key not in ('illustratedProps','items'):assert story[key]==enriched[key],key
    write_json(canonical,enriched)
    project_path=ROOT/'game-project/project.json'
    project=json.loads(project_path.read_text(encoding='utf-8'))
    assert project['story']['adventure']==story,'Project and canon diverged before enrichment'
    project['story']['adventure']=copy.deepcopy(enriched)
    write_json(project_path,project)
    marker='window.BUILT_GAME='
    for rel in ('game/index.html','game-editor/index.html'):
        path=ROOT/rel;html=path.read_text(encoding='utf-8');assert html.count(marker)==1
        pos=html.index(marker)+len(marker);built,end=json.JSONDecoder().raw_decode(html[pos:])
        # Preserve existing kitchen variant mappings and supplied media, renderer, assets.
        assert built['story']['adventure']==story,rel+' story differs from canon'
        built['story']['adventure']=copy.deepcopy(enriched)
        encoded=json.dumps(built,ensure_ascii=False,separators=(',',':'))
        new=html[:pos]+encoded+html[pos+end:]
        if new!=html:path.write_text(new,encoding='utf-8')
    props=enriched['illustratedProps']
    print(f"Approved art synchronized: {len(props['image'])} images, {len(props['action'])} actions, {len(props['document'])} documents")
if __name__=='__main__':main()
