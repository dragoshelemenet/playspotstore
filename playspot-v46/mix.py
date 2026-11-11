#!/usr/bin/env python3
"""V46: stable product-specific natural copy and diversified internal link labels.

Never rotates/replaces URLs, canonical, hreflang, sitemap or JSON-LD. Uses
existing catalog descriptions, not invented reviews or unverifiable facts.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

CATS = ('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
ROOT_SITE = 'https://playspotstore.online'
START = '<!-- P44 MOLDOVA FULFILMENT START -->'
END = '<!-- P44 MOLDOVA FULFILMENT END -->'
COMMENT = '<!-- P45 LOCALIZED PRODUCT DESCRIPTION -->'
HOOK = 'P46_NATURAL_MIX_HOOK'
GUIDE = {'ro':'/jocuri-video-chisinau-moldova.html','ru':'/ru/videoigry-kishinev-moldova.html'}
PLATFORM={'ps2':'PS2','ps4':'PS4','ps5':'PS5','nintendo':'Nintendo','xbox':'Xbox','consoles':'PlayStation','accessories':'gaming'}
# Phrasing is intentional and directly useful to the reader. Never call a new
# arrival new/unused. No claims about guaranteed delivery, specific stock or price.
RO_OPEN = (
    '{title} pentru {platform} — ',
    'În catalogul PlaySpotStore găsești {title} pentru {platform}. ',
    'Despre {title} pe {platform}: ',
    '{title} pe {platform}: ',
    'Te interesează {title} pentru {platform}? ',
    'Pentru platforma {platform}, {title} propune următoarea experiență: ',
    'Ce oferă {title} pe {platform}? ',
    '{title} ({platform}) face parte din selecția PlaySpotStore. ',
    'Dacă urmărești {title} pe {platform}, iată ce trebuie să știi: ',
    'O privire asupra {title} pentru {platform}: ',
    'Înainte să alegi {title} pe {platform}, descoperă jocul: ',
    'Jocul {title} pentru {platform} — ',
)
RU_OPEN = (
    '{title} для {platform}: ',
    'В каталоге PlaySpotStore представлен {title} для {platform}. ',
    'Об игре {title} на {platform}: ',
    '{title} на {platform} — ',
    'Интересует {title} для {platform}? ',
    'Для {platform} игра {title} предлагает следующее: ',
    'Чем интересен {title} на {platform}? ',
    '{title} ({platform}) есть в каталоге PlaySpotStore. ',
    'Если ищете {title} для {platform}, обратите внимание на описание: ',
    'Кратко о {title} для {platform}: ',
    'Перед выбором {title} для {platform} ознакомьтесь с игрой: ',
    'Игра {title} для {platform} — ',
)
# Ensure every localized copy mentions Chișinău/Кишинёв and courier, satisfying
# the existing V45 factual copy invariant. Place names appear sparingly.
RO_DELIVERY = (
    'În Chișinău putem conveni predarea personală; pentru restul Moldovei discutăm livrarea prin curier.',
    'Predarea în Chișinău se stabilește de comun acord, iar pentru alte localități din Moldova verificăm expedierea prin curier.',
    'Dacă ești în Chișinău, discutăm o întâlnire pentru predare; în alte orașe putem organiza un curier după confirmare.',
    'Pentru Chișinău există opțiunea unei predări convenite; pentru Bălți și alte orașe confirmăm disponibilitatea curierului.',
    'Poți întreba de predarea în Chișinău sau despre curier pentru Orhei și celelalte localități din Moldova.',
    'În Chișinău putem aranja predarea directă, iar pentru Ungheni și alte orașe din Moldova verificăm livrarea prin curier.',
    'Predarea personală poate fi stabilită în Chișinău. În Cahul și în alte localități discutăm opțiunile de curier.',
    'Din Chișinău putem conveni o predare personală; spre alte orașe ale Moldovei expedierea prin curier se confirmă individual.',
    'Locuiești în Chișinău? Putem stabili predarea. Pentru Soroca și alte localități verificăm curierul înainte de comandă.',
    'În Chișinău ne putem înțelege pentru predare, iar către Comrat și alte orașe putem discuta expedierea prin curier.',
    'Pentru o comandă din Chișinău se poate discuta predarea personală; pentru restul Moldovei, livrarea prin curier.',
    'Dacă ai nevoie de produs în afara Chișinăului, întreabă despre curier; în oraș predarea se stabilește prin înțelegere.',
    'Predarea în Chișinău și expedierea prin curier în Moldova se discută la confirmarea comenzii.',
    'În Chișinău există posibilitatea unei predări convenite. Pentru livrare prin curier în Moldova, solicită mai întâi detaliile.',
    'Putem discuta predarea personală în Chișinău sau o variantă de curier pentru alte orașe din Republica Moldova.',
    'În Chișinău stabilim împreună predarea; pentru Bălți, Orhei și restul Moldovei verificăm opțiunile de curier.',
)
RU_DELIVERY = (
    'В Кишинёве можно договориться о личной передаче; для других городов Молдовы уточняем доставку курьером.',
    'Личная встреча в Кишинёве возможна по договорённости, а для остальных населённых пунктов Молдовы обсуждаем курьера.',
    'В Кишинёве можно согласовать передачу при встрече; в другие города отправку курьером подтверждаем заранее.',
    'Для Кишинёва есть вариант личной передачи; для Бельц и других городов уточняем курьерскую доставку.',
    'Можно спросить о встрече в Кишинёве или курьере для Оргеева и других населённых пунктов Молдовы.',
    'В Кишинёве передачу обсуждаем лично, а для Унген и других городов проверяем вариант с курьером.',
    'Договориться о встрече можно в Кишинёве. Для Кагула и других городов обсуждаем курьерскую доставку.',
    'В Кишинёве возможна личная передача по договорённости; доставку курьером по Молдове подтверждаем отдельно.',
    'Вы в Кишинёве? Можем обсудить передачу. Для Сорок и других городов уточняем доставку курьером.',
    'Для Кишинёва можно согласовать встречу, а для Комрата и других городов — отправку курьером.',
    'В Кишинёве можно уточнить передачу при встрече; для остальной Молдовы — доставку курьером.',
    'Если заказ нужен за пределами Кишинёва, уточните курьера; в городе возможна встреча по договорённости.',
    'Передачу в Кишинёве и курьерскую доставку по Молдове согласовываем перед заказом.',
    'В Кишинёве можно договориться о передаче; курьер по Молдове обсуждается индивидуально.',
    'Уточните личную встречу в Кишинёве или возможность курьерской отправки в другие города Республики Молдова.',
    'В Кишинёве возможна встреча; доставку курьером в Бельцы, Оргеев и другие города Молдовы согласовываем заранее.',
)
RO_LINKS = (
    'Cum primești comanda', 'Detalii despre predare', 'Opțiuni de livrare în Moldova',
    'Informații despre livrare', 'Predare sau curier', 'Vezi cum funcționează livrarea',
    'Condițiile de livrare', 'Mai multe despre curier', 'Despre primirea comenzii',
    'Predare personală și curier', 'Cum cumpăr de la PlaySpotStore', 'Întrebări despre livrare',
    'Află detaliile de livrare', 'Livrare și predare', 'Informații pentru cumpărători',
    'Cum se stabilește predarea',
)
RU_LINKS = (
    'Как получить заказ', 'Условия передачи', 'Доставка по Молдове',
    'Подробнее о доставке', 'Встреча или курьер', 'Как работает доставка',
    'Условия доставки', 'Информация о курьере', 'Получение заказа',
    'Личная встреча и доставка', 'Как купить в PlaySpotStore', 'Вопросы по доставке',
    'Детали доставки', 'Доставка и передача', 'Для покупателей',
    'Как договориться о встрече',
)
RO_CONFIRM = (
    'Înainte de cumpărare confirmăm disponibilitatea, starea exemplarului, prețul și costul transportului.',
    'Starea produsului, prețul și modalitatea de livrare se verifică înainte de comandă.',
    'Solicită confirmarea stării, prețului și eventualelor costuri de transport înainte de plată.',
    'Informațiile despre disponibilitate, condiție și costul livrării se clarifică înainte de cumpărare.',
    'Verifică împreună cu noi starea produsului și condițiile comenzii înainte de achiziție.',
    'Confirmăm dacă exemplarul este nou sau b/u doar după verificare, împreună cu prețul și livrarea.',
    'Înainte de a plasa comanda, întreabă despre preț, disponibilitate și starea fizică a exemplarului.',
    'Disponibilitatea și starea produsului sunt confirmate individual, înainte de expediere.',
)
RU_CONFIRM = (
    'Перед покупкой уточняем наличие, состояние экземпляра, цену и стоимость отправки.',
    'Состояние товара, цена и способ доставки подтверждаются перед заказом.',
    'Перед оплатой уточните состояние, цену и возможные расходы на доставку.',
    'Наличие, состояние и условия курьерской отправки обсуждаются до покупки.',
    'Перед заказом проверяем состояние конкретного экземпляра и условия получения.',
    'Новый или б/у экземпляр — уточняем индивидуально вместе с ценой и доставкой.',
    'Перед оформлением уточните цену, наличие и физическое состояние товара.',
    'Наличие и состояние каждого товара подтверждаем отдельно, до отправки.',
)
RO_CAT_LINKS=('Vezi predarea și livrarea','Despre livrare în Moldova','Cum ajunge comanda la tine','Condiții de predare','Mai multe despre curier','Cum cumperi și primești comanda','Informatii despre comenzi')
RU_CAT_LINKS=('Передача и доставка','О доставке по Молдове','Как получить покупку','Условия получения','Подробнее о курьере','Как оформить заказ','Информация о заказах')

def idx(pid:str,lang:str,namespace:str,mod:int)->int:
    digest=hashlib.sha256((namespace+'|'+lang+'|'+pid).encode('utf-8')).digest()
    return int.from_bytes(digest[:8],'big') % mod

def compact(s:str)->str:
    return ' '.join(str(s).split())

def assemble(pid:str,title:str,cat:str,lang:str,desc:str)->str:
    # Each SKU/language chooses a STABLE combination of a real synopsis, opener,
    # factual fulfilment wording and order. Not randomized on page load.
    title,desc=compact(title),compact(desc)
    opens=RU_OPEN if lang=='ru' else RO_OPEN
    delivery=RU_DELIVERY if lang=='ru' else RO_DELIVERY
    opener=opens[idx(pid,lang,'open',len(opens))].format(title=title,platform=PLATFORM[cat])
    shipping=delivery[idx(pid,lang,'ship',len(delivery))]
    # The original synopsis is included intact, not auto-synonymized.
    pattern=idx(pid,lang,'order',4)
    if pattern==0:return opener+desc+' '+shipping
    if pattern==1:return opener+shipping+' '+desc
    if pattern==2:return desc+' '+opener+shipping
    return shipping+' '+opener+desc

def aside(pid:str,lang:str)->str:
    link=GUIDE[lang]
    label=(RU_LINKS if lang=='ru' else RO_LINKS)[idx(pid,lang,'anchor',16)]
    note=(RU_CONFIRM if lang=='ru' else RO_CONFIRM)[idx(pid,lang,'confirm',8)]
    aria='Получение товара' if lang=='ru' else 'Informații despre comandă'
    return (f'<aside class="p44-fulfilment p44-product" aria-label="{aria}">\n'
            f'<p>{html.escape(note,quote=True)} <a href="{link}">{html.escape(label,quote=True)}</a></p></aside>')

def category_aside(cat:str,lang:str)->str:
    labels=RU_CAT_LINKS if lang=='ru' else RO_CAT_LINKS
    label=labels[idx(cat,lang,'catlink',len(labels))]
    link=GUIDE[lang]
    if lang=='ro':
        sentences=[
            'Pentru jocurile din această categorie putem conveni o predare în Chișinău sau discuta expedierea prin curier în Moldova.',
            'Cumpărătorii din Chișinău pot întreba despre predarea personală; pentru alte orașe discutăm curierul înainte de comandă.',
            'O comandă pentru această platformă se poate preda în Chișinău prin înțelegere sau expedia prin curier după confirmare.',
            'Detaliile de predare în Chișinău ori de livrare prin curier în Moldova se clarifică înainte de cumpărare.',
            'Starea și disponibilitatea produsului se confirmă individual, împreună cu predarea în Chișinău sau curierul în Moldova.',
            'Pentru această categorie sunt posibile predarea convenită în Chișinău și livrarea prin curier în alte localități.',
            'Alege produsul dorit, apoi verificăm disponibilitatea și posibilitatea de predare în Chișinău ori curier în Moldova.',
        ]
        aria='Predare și livrare'
    else:
        sentences=[
            'Товары этой категории можно получить при встрече в Кишинёве по договорённости или обсудить доставку курьером по Молдове.',
            'Покупатели из Кишинёва могут уточнить личную передачу; для других городов обсуждаем курьера перед заказом.',
            'Товар для этой платформы можно передать в Кишинёве по договорённости или отправить курьером после подтверждения.',
            'Условия встречи в Кишинёве и курьерской доставки по Молдове уточняем перед покупкой.',
            'Состояние и наличие товара согласуем индивидуально вместе с передачей в Кишинёве или доставкой курьером.',
            'Для этой категории можно обсудить встречу в Кишинёве и отправку курьером в другие города.',
            'Выберите товар, затем уточните наличие и возможность встречи в Кишинёве или отправки курьером по Молдове.',
        ]
        aria='Передача и доставка'
    sentence=sentences[idx(cat,lang,'catnote',len(sentences))]
    return (f'<aside class="p44-fulfilment p44-category" aria-label="{aria}">\n'
            f'<p>{html.escape(sentence,quote=True)} <a href="{link}">{html.escape(label,quote=True)}</a></p></aside>')

def replace_block(source:str,old_start:str,old_end:str,new_block:str,identifier:str)->str:
    if source.count(old_start)!=1 or source.count(old_end)!=1:
        raise ValueError(f'{identifier}: corrupted/missing V44 block')
    pat=re.compile(re.escape(old_start)+r'.*?'+re.escape(old_end),flags=re.S)
    return pat.sub(lambda _:old_start+'\n'+new_block+'\n'+old_end,source,count=1)

def product_page(source:str,p:dict,cat:str,lang:str)->str:
    pid=str(p['id']);name=p['title'];desc=p['description']
    if '<!-- P45 LEGACY REDIRECT -->' in source:
        raise ValueError(pid+': attempted to modify redirect instead of canonical product')
    if f'"sku":"{pid}"' not in source:
        raise ValueError(pid+': incorrect canonical product file')
    if source.count(COMMENT)!=1:raise ValueError(pid+': V45 copy marker missing')
    pat=re.compile(r'(<p class="seo-detail-description">)(.*?)(</p>)',re.S)
    if len(pat.findall(source))!=1:raise ValueError(pid+': description block missing or duplicated')
    new_text=html.escape(assemble(pid,name,cat,lang,desc),quote=True)
    source=pat.sub(lambda m:m.group(1)+new_text+m.group(3),source,count=1)
    source=replace_block(source,START,END,aside(pid,lang),pid)
    return source

def page_map(root:Path)->dict[str,str]:
    path=root/'playspot-v45/url-map.json'
    if not path.is_file():raise FileNotFoundError('V45 installed URL map missing: '+str(path))
    mapping=json.loads(path.read_text(encoding='utf-8'))
    if len(mapping)<570 or len(set(mapping.values()))!=len(mapping):raise ValueError('Unexpected V45 URL map')
    return mapping

def patch_generator(source:str)->str:
    if HOOK in source:return source
    anchor="    print(f'✅ Generated {total*2} product pages"
    if source.count(anchor)!=1:raise ValueError('V29 regenerate hook missing')
    add=("    # P46_NATURAL_MIX_HOOK: preserve stable editorial variants after V45 migration.\n"
         "    mix46 = root / 'playspot-v46' / 'mix.py'\n"
         "    if mix46.is_file(): subprocess.run([sys.executable, str(mix46), '--root', str(root)], check=True)\n")
    if 'P45_GEO_URL_HOOK' not in source:raise ValueError('V45 not installed in generator')
    return source.replace(anchor,add+anchor,1)

def plan(root:Path)->tuple[dict[Path,str],dict]:
    root=root.resolve();mapping=page_map(root)
    changes={};counts={'products':0,'categories':0,'changed_products':0,'changed_categories':0,'generator_changed':False}
    mapping_by_key={}
    for old,new in mapping.items():
        if '/produse/' in '/'+old:
            lang='ru' if old.startswith('ru/') else 'ro'
            mapping_by_key[(lang,old.split('/')[-2],new.rsplit('/',1)[-1])]=new
    for cat in CATS:
        for lang in ('ro','ru'):
            localized=root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json'
            records=json.loads(localized.read_text(encoding='utf-8'))
            dircat='console' if cat=='consoles' else cat
            prefix='ru/produse' if lang=='ru' else 'produse'
            dirp=root/prefix/dircat
            canonicals={}
            for old,new in mapping.items():
                if old.startswith(f'{prefix}/{dircat}/'):
                    canonicals[old.rsplit('/',1)[-1]]=root/new
            if len(canonicals)!=len(records):raise ValueError(f'{cat}/{lang}: canonical count != catalog')
            pages={}
            for old_basename,path in canonicals.items():
                source=path.read_text(encoding='utf-8')
                m=re.search(r'"sku"\s*:\s*"([^"]+)"',source)
                if not m:raise ValueError(f'No SKU in {path}')
                if m.group(1) in pages:raise ValueError(f'Duplicate SKU {m.group(1)}')
                pages[m.group(1)]=path
            if set(pages)!={str(x['id']) for x in records}:
                raise ValueError(f'{cat}/{lang}: product IDs inconsistent')
            for p in records:
                target=pages[str(p['id'])]
                original=target.read_text(encoding='utf-8')
                updated=product_page(original,p,cat,lang)
                if updated!=original:changes[target]=updated;counts['changed_products']+=1
                counts['products']+=1
            oldcat=f'{"ru/" if lang=="ru" else ""}categorii/{cat}.html'
            path=root/mapping[oldcat]
            original=path.read_text(encoding='utf-8')
            updated=replace_block(original,START,END,category_aside(cat,lang),oldcat)
            if updated!=original:changes[path]=updated;counts['changed_categories']+=1
            counts['categories']+=1
    gp=root/'playspot-v29/generate.py';original=gp.read_text(encoding='utf-8')
    updated=patch_generator(original)
    if updated!=original:changes[gp]=updated;counts['generator_changed']=True
    return changes,counts

def main(root:Path,check:bool):
    changes,stats=plan(root)
    print(('V46 PREVIEW' if check else 'V46 NATURAL MIX')+': '+str(stats))
    if not check:
        for path,body in changes.items():path.write_text(body,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');parser.add_argument('--check',action='store_true')
    args=parser.parse_args();main(Path(args.root),args.check)
