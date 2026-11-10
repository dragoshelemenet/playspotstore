#!/usr/bin/env python3
"""PlaySpotStore V41: lengthen verified V40 product summaries for shoppers.

Uses the existing per-product RO/RU source synopsis, curated supplemental facts,
and restrained genre guidance. No invented stock, condition, ratings or features.
The visible product text is built ahead of time, not injected by JavaScript.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, re, sys, unicodedata
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')

# Editorial taxonomy is indicative, not a fictional claim about individual modes.
# Keep each advice sentence focused on what a shopper learns about the experience.
GENRES={
'platform':(
 ["Platformele, obstacolele și ritmul mișcării sunt esențiale: observă traseul, încearcă variante de abordare și descoperă cum fiecare secvență testează reflexele și atenția.",
  "Nivelurile combină deplasarea cu momente în care trebuie să calculezi sărituri, să urmărești pericolele din jur și să înțelegi cum funcționează fiecare mecanică.",
  "Farmecul unui platformer vine din alternanța dintre explorare și precizie, nu doar din viteza cu care ajungi la capătul unui nivel. Obstacolele dau ritm aventurii."],
 ["В платформере важны движение, препятствия и ритм: изучайте маршрут, пробуйте разные подходы и замечайте, как отдельные участки проверяют реакцию и внимание.",
  "Уровни сочетают перемещение с моментами, когда нужно рассчитывать прыжки, следить за опасностями и разбираться в работе игровых механик.",
  "Интерес платформера — в сочетании исследования и точности, а не только скорости прохождения. Расположение препятствий задаёт темп приключения."]),
'racing':(
 ["În centru stau traseele, alegerea momentului pentru accelerare și modul în care reacționează vehiculul. Fiecare viraj poate schimba rezultatul unei curse sau al unei provocări.",
  "Pentru a progresa, contează mai mult decât viteza maximă: controlul la frânare, intrarea în curbe și atenția la particularitățile circuitului fac diferența.",
  "Este o experiență pentru cei care preferă să își perfecționeze traseele și să compare stiluri de pilotaj. Cursa se construiește din decizii rapide, nu doar din accelerație."],
 ["В центре внимания — трассы, выбор момента для ускорения и реакция транспорта на управление. Каждый поворот может изменить исход гонки или испытания.",
  "Для прогресса важна не только максимальная скорость: торможение, вход в поворот и знание особенностей трассы заметно влияют на результат.",
  "Такая игра интересна тем, кто любит совершенствовать прохождение маршрутов и сравнивать стили вождения. Гонка требует решений, а не только ускорения."]),
'football':(
 ["Meciurile pun în joc pasele, poziționarea, recuperarea mingii și alegerea momentului potrivit pentru șut. Tactica poate fi la fel de importantă ca reacția la fazele rapide.",
  "Când construiești o fază, contează spațiile dintre jucători, ritmul paselor și organizarea apărării. Experiența se bazează pe citirea adversarului și adaptarea jocului.",
  "De la contraatacuri la atacuri poziționale, fiecare partidă schimbă ritmul în funcție de stilul echipei. Controlul și anticiparea sunt la fel de importante ca finalizarea."],
 ["В матчах важны передачи, позиции игроков, отбор мяча и правильный момент для удара. Тактика может значить не меньше, чем реакция в быстрых эпизодах.",
  "При построении атаки важны свободные зоны, темп передач и организация защиты. Игра строится на чтении действий соперника и изменении тактики.",
  "От контратак до позиционного футбола — темп каждого матча зависит от подхода команды. Управление и предугадывание моментов столь же важны, как завершение атаки."]),
'combat':(
 ["Duelurile cer controlul distanței, atenție la atacurile adversarului și alegerea momentelor pentru apărare sau contraatac. Exersarea combinațiilor schimbă felul în care se desfășoară o confruntare.",
  "Acțiunea se decide prin timing, poziționare și înțelegerea mișcărilor personajelor. Nu este suficient să ataci continuu: blocajele și reacțiile rapide contează mult.",
  "Fiecare luptă devine un exercițiu de anticipare. Observarea adversarului, alegerea tehnicilor și controlul ritmului sunt mai importante decât apăsarea repetată a butoanelor."],
 ["В поединках важны дистанция, наблюдение за атаками соперника и момент для защиты или контратаки. Отработка комбинаций меняет ход столкновения.",
  "Исход боя зависит от тайминга, позиции и понимания движений персонажей. Постоянно атаковать недостаточно: блоки и своевременные ответы тоже имеют значение.",
  "Каждая схватка требует предугадывать действия врага. Наблюдение, выбор приёмов и контроль темпа полезнее бессистемного нажатия кнопок."]),
'fps':(
 ["Jocul se bazează pe precizia țintirii, deplasare și evaluarea rapidă a pericolelor. Poziția din care intri într-o confruntare poate conta la fel de mult ca alegerea armei.",
  "În secvențele de acțiune trebuie să urmărești mediul, să reacționezi la adversari și să alegi când avansezi sau te retragi. Ritmul alternează între mișcare și decizii tactice.",
  "Armele și spațiul în care are loc lupta influențează strategia: acoperirea, unghiurile de atac și reacția la schimbările de situație contează în fiecare confruntare."],
 ["Игра строится на точности стрельбы, перемещении и быстрой оценке угроз. Позиция перед столкновением может быть не менее важна, чем выбранное оружие.",
  "В динамичных эпизодах приходится следить за окружением, реагировать на противников и решать, когда наступать или отходить. Действие чередуется с тактическими решениями.",
  "Оружие и пространство боя влияют на подход: укрытия, направления атаки и реакция на изменение ситуации значимы в каждом столкновении."]),
'rpg':(
 ["Explorarea, dialogurile și confruntările oferă ritm unei aventuri în care merită să fii atent la lumea din jur. Dezvoltarea personajului și modul de abordare a misiunilor pot influența experiența.",
  "Un RPG combină descoperirea locurilor și a poveștilor cu alegeri despre cum abordezi obstacolele. Personajele, conflictele și sistemele de luptă formează împreună nucleul aventurii.",
  "Experiența nu se rezumă la o succesiune de lupte: misiunile, explorarea și progresul eroului se completează. Merită să urmărești atât povestea, cât și mecanicile de joc."],
 ["Исследование мира, диалоги и сражения задают ритм приключению, в котором важно замечать детали окружения. Развитие героя и подход к заданиям могут влиять на игровой опыт.",
  "RPG сочетает знакомство с локациями и историями с выбором способов преодолевать препятствия. Персонажи, конфликты и боевые системы вместе формируют основу приключения.",
  "Приключение не сводится к цепочке сражений: задания, исследование и развитие героя дополняют друг друга. Важны и история, и игровые механики."]),
'horror':(
 ["Tensiunea vine din explorarea unor spații nesigure, din sunete și din nesiguranța legată de ce urmează. Atenția la indicii și la traseele de retragere poate fi esențială.",
  "Atmosfera contează la fel de mult ca acțiunea. Jocul te încurajează să observi decorul, să interpretezi semnalele de pericol și să înaintezi chiar atunci când nu ai toate răspunsurile.",
  "Suspansul se construiește prin ritm, medii neliniștitoare și descoperirea treptată a poveștii. În astfel de experiențe, curiozitatea și prudența se află permanent în conflict."],
 ["Напряжение возникает при исследовании опасных мест, из-за звуков и неизвестности того, что ждёт впереди. Важно замечать подсказки и возможные пути отступления.",
  "Атмосфера здесь не менее значима, чем действие. Игроку предлагают изучать окружение, распознавать признаки опасности и двигаться дальше, даже не зная всех ответов.",
  "Саспенс создают темп, тревожные локации и постепенное раскрытие истории. Любопытство и осторожность в подобных играх постоянно сталкиваются."]),
'coop':(
 ["Colaborarea este o parte importantă a experienței: jucătorii trebuie să comunice, să își sincronizeze acțiunile și să observe cum se completează rolurile lor în momentele dificile.",
  "Provocările devin mai interesante atunci când împarți responsabilitățile și alegi o strategie comună. Coordonarea și reacția la situații neașteptate au un rol central.",
  "Accentul cade pe lucrul în echipă, pe observarea celorlalți și pe deciziile luate împreună. Reușita depinde de coordonare, nu numai de abilitățile individuale."],
 ["Сотрудничество важно для игрового процесса: участникам нужно общаться, согласовывать действия и понимать, как их роли дополняют друг друга в сложных ситуациях.",
  "Испытания интереснее, когда игроки распределяют обязанности и выбирают общую стратегию. Координация и реакция на неожиданные события играют ключевую роль.",
  "Главный акцент — на командной работе, внимании к партнёрам и совместных решениях. Успех зависит не только от личного мастерства, но и от согласованности."]),
'simulator':(
 ["Satisfacția vine din planificarea acțiunilor și din înțelegerea regulilor sistemului pe care îl controlezi. Rezultatele bune apar prin observație, ajustări și organizare atentă.",
  "Experiența pune accent pe decizii practice: ordinea sarcinilor, folosirea resurselor și reacția la situații schimbătoare. Progresul înseamnă să îți îmbunătățești treptat strategia.",
  "În loc să urmărești doar reflexele rapide, trebuie să organizezi activitățile și să vezi consecințele deciziilor. Este un tip de joc care răsplătește atenția la detalii."],
 ["Удовольствие приносит планирование действий и понимание правил управляемой системы. Хороший результат зависит от наблюдения, корректировок и организации.",
  "Игровой процесс строится на практических решениях: порядок задач, использование ресурсов и реакция на изменения влияют на итог. Прогресс требует постепенно улучшать стратегию.",
  "Здесь важнее не скорость реакции, а умение организовывать деятельность и видеть последствия решений. Такой формат поощряет внимание к деталям."]),
'stealth':(
 ["Observarea patrulelor, poziționarea și alegerea momentului de acțiune contează mai mult decât atacul direct. Un traseu ales cu grijă poate schimba complet desfășurarea misiunii.",
  "Misiunile invită la răbdare: examinezi spațiile, eviți pericolele și decizi când merită să îți asumi riscuri. Abordarea discretă pune accent pe planificare.",
  "Într-o aventură cu stealth, informația este o resursă importantă. Urmărirea mișcărilor adversarilor și utilizarea mediului te ajută să alegi între discreție și confruntare."],
 ["Наблюдение за патрулями, выбор позиции и момента действия зачастую важнее прямой атаки. Продуманный маршрут может полностью изменить ход задания.",
  "Задания требуют терпения: нужно изучать пространство, избегать угроз и решать, когда риск оправдан. Скрытное прохождение делает акцент на планировании.",
  "В приключении со стелсом информация особенно ценна. Наблюдение за противниками и использование окружения помогают выбирать между осторожностью и открытым столкновением."]),
'action':(
 ["Pe parcurs, povestea și momentele intense se completează cu explorarea decorurilor. Merită să urmărești cum fiecare confruntare sau obstacol schimbă ritmul aventurii.",
  "Experiența alternează descoperirea mediilor cu secvențe în care reacția și alegerea momentului de acțiune sunt importante. Accentul rămâne pe ceea ce faci efectiv în joc.",
  "Acțiunea nu înseamnă doar lupte: traseele, provocările și întâlnirile cu personaje diferite contribuie la ritmul aventurii. Observarea mediului poate deschide noi abordări."],
 ["По ходу игры история и напряжённые моменты сочетаются с исследованием локаций. Интересно наблюдать, как каждое столкновение или препятствие меняет темп приключения.",
  "Исследование окружения чередуется с эпизодами, где важны реакция и выбор момента для действия. Акцент остаётся на том, что игрок действительно делает.",
  "Экшен не сводится к боям: маршруты, испытания и встречи с персонажами формируют ритм приключения. Внимательность к окружению помогает находить новые подходы."]),
'narrative':(
 ["Povestea se desfășoară prin întâlniri, indicii și reacțiile personajelor. Fii atent la dialoguri și la detalii, deoarece ele dau sens evenimentelor dincolo de acțiunea imediată.",
  "Ritmul este construit în jurul descoperirii poveștii și al contextului în care se află personajele. Explorarea și dialogurile pot conta mai mult decât confruntările rapide.",
  "Un astfel de joc pune în prim-plan atmosfera, personajele și felul în care este prezentat conflictul. Micile detalii din decor ajută la înțelegerea întregii povești."],
 ["Сюжет раскрывается через встречи, подсказки и реакции персонажей. Обращайте внимание на диалоги и детали — они придают смысл событиям за пределами непосредственного действия.",
  "Темп строится вокруг постепенного раскрытия истории и обстоятельств героев. Исследование и диалоги здесь могут быть важнее быстрых столкновений.",
  "Такая игра выводит на первый план атмосферу, персонажей и подачу конфликта. Небольшие детали окружения помогают понять общую историю."]),
'party':(
 ["Sesiunile sunt construite în jurul unor provocări ușor de înțeles și al reacțiilor rapide la ceea ce se întâmplă pe ecran. Varietatea probelor schimbă ritmul jocului.",
  "Acest tip de experiență pune accent pe divertismentul accesibil și pe diferențele dintre provocări. Fiecare rundă este o ocazie de a încerca altă strategie sau alt ritm.",
  "Farmecul vine din alternarea probelor și din situațiile imprevizibile. Observarea regulilor fiecărei provocări contează mai mult decât memorarea unei singure combinații de comenzi."],
 ["Игровые сессии строятся вокруг понятных испытаний и быстрой реакции на происходящее. Разнообразие заданий меняет темп игры.",
  "Такой формат сочетает доступное развлечение с разными типами испытаний. Каждый раунд позволяет попробовать другой подход или ритм.",
  "Интерес рождается из смены заданий и неожиданных ситуаций. Понимание правил конкретного испытания важнее запоминания одной комбинации кнопок."]),
'vr':(
 ["Perspectiva apropiată a realității virtuale face importante orientarea în spațiu și interacțiunile cu mediul. Ritmul jocului depinde de cum observi și explorezi lumea din jur.",
  "În realitatea virtuală, felul în care privești și te miști este parte a experienței. Atenția la spațiu și la obiectele din jur contribuie la imersiune.",
  "Experiența VR schimbă relația cu decorul: mediul este observat din apropiere, iar interacțiunile cer atenție la poziționare și la spațiul din jur."],
 ["В виртуальной реальности особенно важны ориентация в пространстве и взаимодействие с окружением. Темп игры зависит от того, как вы осматриваете и исследуете мир.",
  "В VR взгляд и движение становятся частью игрового процесса. Внимание к пространству и предметам вокруг усиливает погружение.",
  "VR меняет восприятие окружения: мир рассматривается с близкого расстояния, а взаимодействия требуют внимания к положению и пространству вокруг."]),
'accessory':(
 ["Înainte de alegere, merită comparate modelul exact, compatibilitatea și tipul de utilizare. Denumirea produsului este punctul de plecare pentru verificarea configurației potrivite.",
  "Un accesoriu se alege în funcție de consola folosită, conectivitate și preferințele de control. Verificarea exactă a modelului este mai utilă decât compararea doar a culorilor.",
  "Pentru un accesoriu gaming, cele mai importante întrebări sunt compatibilitatea cu sistemul tău și rolul concret în sesiunea de joc. Merită verificată varianta exactă."],
 ["Перед выбором стоит сравнить точную модель, совместимость и назначение. Название товара — отправная точка для проверки подходящей конфигурации.",
  "Аксессуар выбирают с учётом консоли, способа подключения и предпочтений в управлении. Проверка конкретной модели полезнее сравнения только цветов.",
  "Для игрового аксессуара важнее всего совместимость с системой и реальная задача в игровой сессии. Стоит уточнить точную модификацию."]),
'console':(
 ["La alegerea unei console contează generația platformei, bibliotecile de jocuri compatibile și accesoriile pe care intenționezi să le folosești. Modelul concret este important pentru comparație.",
  "Consola reprezintă baza experienței de gaming: alegerea trebuie făcută ținând cont de jocurile dorite, controllere și tipul de utilizare. Verifică modelul exact.",
  "Pentru o consolă, diferențele dintre generații și configurații sunt mai utile decât un slogan comercial. Denumirea completă te ajută să identifici modelul potrivit."],
 ["При выборе консоли важны поколение платформы, совместимая библиотека игр и аксессуары, которые планируется использовать. Конкретная модель важна для сравнения.",
  "Консоль — основа игрового процесса: при выборе учитывают нужные игры, контроллеры и характер использования. Важно проверить точную модель.",
  "Для консоли различия поколений и конфигураций полезнее рекламного слогана. Полное название помогает определить подходящую модель."]),
}

# Longer second segment, varied by genre. This is gameplay context, not stock claims.
CONTEXT={
'platform':('Dacă îți plac jocurile în care înveți treptat regulile unui nivel și le aplici în secvențe tot mai solicitante, urmărește felul în care sunt construite provocările și libertatea de a experimenta.', 'Если нравятся игры, где нужно осваивать правила уровня и применять их в новых ситуациях, стоит обратить внимание на устройство испытаний и возможность экспериментировать.'),
'racing':('Pentru pasionații de curse, merită comparate tipul de vehicul, traseele și accentul pus pe competiție sau pe explorare. Aceste detalii schimbă considerabil senzația de condus.', 'Любителям гонок стоит учитывать тип транспорта, трассы и акцент на соревнованиях либо исследовании. Эти детали заметно меняют ощущения от вождения.'),
'football':('Este relevant pentru cei care apreciază construirea fazelor de joc, schimbarea tacticilor și competițiile sportive, nu doar rezultatul afișat la finalul meciului.', 'Подойдёт тем, кому интересны комбинационная игра, изменение тактики и спортивное соперничество, а не только итоговый счёт.'),
'combat':('Dacă preferi competițiile în care înveți stiluri diferite de luptă și reacționezi la tactica rivalului, urmărește personajele și ritmul duelurilor.', 'Если нравится осваивать разные стили боя и отвечать на тактику соперника, обратите внимание на персонажей и динамику поединков.'),
'fps':('Cei care apreciază acțiunea intensă pot analiza atmosfera misiunilor și combinația dintre reacțiile rapide și abordarea tactică. Tematica jocului îl diferențiază de alte shootere.', 'Любителям динамичного экшена стоит оценить атмосферу заданий и сочетание быстрой реакции с тактикой. Тематика отличает игру от других шутеров.'),
'rpg':('Dacă alegi un RPG pentru univers, personaje și modul de progres, merită să urmărești în special tema aventurii și libertatea de a explora, nu doar luptele.', 'Если выбираете RPG ради мира, персонажей и развития героя, обратите внимание на тему приключения и свободу исследования, а не только на сражения.'),
'horror':('Este o alegere pentru cei atrași de mister, narațiuni tensionate și explorarea atentă a unor locuri neobișnuite. Atmosfera este o parte centrală a experienței.', 'Это формат для тех, кого привлекают тайны, напряжённые сюжеты и внимательное исследование необычных мест. Атмосфера здесь — важная часть игры.'),
'coop':('Dacă îți place să rezolvi provocări alături de alți jucători, urmărește felul în care cooperarea este integrată în mecanici și în ritmul misiunilor.', 'Если нравится проходить испытания вместе с другими игроками, важно, как сотрудничество встроено в механики и темп заданий.'),
'simulator':('Acest tip de joc atrage persoanele care preferă procedurile, gestionarea și progresul măsurat prin sarcini rezolvate. Subiectul simulatorului contează mult pentru experiența oferită.', 'Такой формат интересен тем, кто любит процессы, управление и развитие через выполненные задачи. Тематика симулятора сильно влияет на впечатление.'),
'stealth':('Este interesant pentru cei care preferă libertatea de a analiza mediul și de a evita confruntările inutile. Tensiunea vine din planificarea fiecărui pas.', 'Подойдёт тем, кто любит изучать окружение и избегать лишних столкновений. Напряжение возникает из необходимости планировать каждый шаг.'),
'action':('Potrivit pentru cei atrași de aventuri dinamice, personaje memorabile și schimbarea frecventă a situațiilor. Tema și decorurile sunt cele care dau jocului identitate.', 'Подойдёт любителям динамичных приключений, ярких героев и частой смены ситуаций. Тема и локации придают игре её характер.'),
'narrative':('Dacă preferi experiențe în care povestea contează mai mult decât scorul, urmărește personajele și întrebările pe care le ridică universul jocului.', 'Если сюжет важнее набранных очков, обратите внимание на героев и вопросы, которые поднимает мир игры.'),
'party':('Pentru sesiuni relaxate, varietatea probelor și claritatea regulilor sunt esențiale. Tonul și stilul vizual contribuie la modul în care se simte fiecare rundă.', 'Для лёгких игровых сессий важны разнообразие испытаний и понятные правила. Настроение и визуальный стиль формируют впечатление от каждого раунда.'),
'vr':('Dacă alegi această experiență, verifică echipamentul de realitate virtuală necesar pentru versiunea exactă și asigură-te că ai spațiu suficient pentru o utilizare confortabilă.', 'При выборе проверьте, какое VR-оборудование требуется конкретной версии, и достаточно ли места для комфортной игры.'),
'accessory':('Descrierea produsului îți arată familia de dispozitive și designul, dar detaliile privind pachetul, starea reală și compatibilitatea trebuie confirmate înainte de comandă.', 'Описание помогает понять тип устройства и дизайн, но состав комплекта, фактическое состояние и совместимость нужно уточнять перед заказом.'),
'console':('Specificatiile exacte, accesoriile incluse și starea produsului nu trebuie presupuse din fotografie. Verifică aceste detalii în momentul confirmării comenzii.', 'Точные характеристики, комплектацию и состояние нельзя надёжно установить по фотографии. Уточняйте эти сведения при подтверждении заказа.'),
}

# Correct factual mistakes found in earlier short catalog copy before expanding it.
SOURCE_FIXES={
 'Still Wakes the Deep': (
  'Horror narativ pe o platformă petrolieră izolată din Marea Nordului, unde un muncitor încearcă să supraviețuiască unui pericol inexplicabil.',
  'Сюжетный хоррор на изолированной нефтяной платформе в Северном море, где рабочий пытается пережить необъяснимую угрозу.'),
 'FIFA 21': (
  'Simulare de fotbal din seria FIFA cu echipe și competiții ale ediției 2021, bazată pe meciuri, tactică și controlul jucătorilor.',
  'Футбольный симулятор серии FIFA с командами и турнирами выпуска 2021 года, основанный на матчах, тактике и управлении игроками.'),
 'Call of Duty: Black Ops IV': (
  'Shooter Call of Duty orientat spre modurile multiplayer, Zombies și Blackout, fără o campanie tradițională pentru un singur jucător.',
  'Шутер Call of Duty с упором на мультиплеер, Zombies и Blackout, без традиционной одиночной сюжетной кампании.'),
 'Rayman Legends (Hits)': (
  'Rayman Legends în linia PlayStation Hits: platformer colorat cu niveluri muzicale, obstacole creative și personaje memorabile.',
  'Rayman Legends в линейке PlayStation Hits: яркий платформер с музыкальными уровнями, необычными препятствиями и героями.'),
 'Uncharted: The Nathan Drake Collection (Hits)': (
  'Colecție cu primele trei jocuri Uncharted ale lui Nathan Drake, într-o versiune pentru PlayStation 4.',
  'Сборник первых трёх приключений Uncharted с Нейтаном Дрейком в версии для PlayStation 4.'),
 'The Nioh Collection': (
  'Colecție care reunește Nioh și Nioh 2, RPG-uri de acțiune samurai cunoscute pentru luptele solicitante.',
  'Сборник Nioh и Nioh 2 — самурайских экшен-RPG с требовательной боевой системой.'),
}

TITLE_GENRE={
 'super mario maker 2':'platform','it takes two':'coop','plateup!':'coop',
 'monopoly family fun pack':'party','spongebob squarepants: lights, camera, pants!':'party',
 'the quarry':'narrative','until dawn':'narrative','detroit: become human':'narrative',
 'the silent swan':'narrative','hidden agenda':'narrative',
 'fruit ninja vr':'vr','robinson: the journey (ps vr)':'vr','arashi: castles of sin (ps vr)':'vr',
 'predator: hunting grounds':'fps','tom clancy’s rainbow six siege':'fps',
 'road trip adventure':'racing','fifa street':'football',
 'minecraft':'simulator',
}

def norm(s):
 s=unicodedata.normalize('NFKC',s).casefold().replace('’',"'")
 return ' '.join(re.sub(r'[^\w]+',' ',s).split())


def genre(title, summary, cat):
 if cat=='consoles': return 'console'
 if cat=='accessories': return 'accessory'
 title_n=norm(title)
 for name,g in TITLE_GENRE.items():
  if norm(name)==title_n:return g
 t=norm(title+' '+summary)
 # Specificity first; avoid keywords such as 'luptă' misclassifying an RPG.
 for g,words in [
 ('vr',['realitate virtuala','realitate virtuală','vr ', 'vr)','ps vr']),
 ('football',['fifa','ea sports fc','fotbal','football manager','soccer']),
 ('racing',['raliur','mașin','masin','curse auto','curse futuriste','motocicl','curse arcade','camioane','mașină','pilotaj','formula 1','f1 22','racing','grid legends','assetto corsa','ride 5','tour de france','ciclism','sportiv de curse','wrc','skateboarding','tony hawk']),
 ('horror',['horror','groază','groaza','neliniști','survival horror','silent hill','resident evil','suspans','grotesc']),
 ('coop',['cooperativ','cooperative','echipă','echipa','lucru in echipa','lucru în echipă']),
 ('stealth',['infiltra','stealth','deghiz','agentul 47','hitman','assassin','splinter']),
 ('combat',['joc de lupte','fighting','dueluri','wrestling','ufc','box ','mma','street fighter','tekken','mortal kombat','dragon ball','smackdown','wwe']),
 ('fps',['shooter','lunetist','arma','call of duty','battlefield','doom','metro exodus','sniper elite','rainbow six','tir la persoana']),
 ('simulator',['simul','management','administr','gestiona','planific','strategie economic','museum','tranzacții','transport rutier','logistic']),
 ('platform',['platform','sărituri','saritur','sonic','mario','kirby','rayman','crash bandicoot','ratchet','little nightmares']),
 ('rpg',['rpg','rolul vikingului','lume deschisă','open world','open-world','fantasy','temnițe','temnite','personajului','monștri','monstri','magie']),
 ('narrative',['narativ','povest','dialog','deciz','aleger','mister','atmosferică','atmosferica']),
 ('party',['minijoc','mini-joc','party','petrecere','familie']),
 ]:
  if any(norm(w) in t for w in words):return g
 return 'action'


def read_facts(path):
 facts={}
 if not path.exists():return facts
 for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
  if not line or line.startswith('#'): continue
  parts=line.split('\t')
  if len(parts)!=3:raise ValueError(f'Invalid editorial line {path}:{i}')
  title,ro,ru=parts
  if not (ro.strip() and ru.strip()):raise ValueError(f'Untranslated fact {title}')
  k=norm(title)
  if k in facts:raise ValueError(f'Duplicate editorial title {title}')
  facts[k]=(ro.strip(),ru.strip())
 return facts


def words(s):return len(s.split())

def expand(summary,title,cat,language,detail,variant):
 g=genre(title, summary, cat)
 i=0 if language=='ro' else 1
 general=GENRES[g][i]
 context=CONTEXT[g][i]
 # Deterministic variation; never randomise text at page load or between builds.
 n=int(hashlib.sha256(title.casefold().encode('utf8')).hexdigest()[:8],16)
 seq=[summary.strip()]
 if detail and detail.strip():seq.append(detail.strip())
 seq.append(general[n%len(general)])
 seq.append(context)
 if words(' '.join(seq))<80:
  seq.append(general[(n+1)%len(general)])
 if words(' '.join(seq))<80:
  seq.append(general[(n+2)%len(general)])
 if words(' '.join(seq))<80:
  tail=('Compară tema, tipul de provocări și modul de utilizare cu alte produse similare înainte de a decide ce experiență ți se potrivește.' if language=='ro' else 'Сравните тему, характер испытаний и способ использования с похожими товарами, чтобы выбрать подходящий именно вам игровой опыт.')
  seq.append(tail)
 result=' '.join(x.rstrip('.')+'.' for x in seq if x.strip())
 # Keep per-product content concise enough not to drown product info.
 if words(result)>150:
  seq=seq[:-1]
  result=' '.join(x.rstrip('.')+'.' for x in seq if x.strip())
 return result


def prepare(root):
 facts=read_facts(Path(__file__).with_name('editorial-facts.tsv'))
 updates={};counts={'products':0,'expanded':0,'curated':0,'missing':0}
 for cat in CATS:
  paths=[root/'data'/f'{cat}{suffix}.json' for suffix in ('','_ru')]
  raw=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
  ros,rus=raw
  ru_byid={str(x['id']):x for x in rus}
  if len(ros)!=len(rus) or len(ru_byid)!=len(rus) or set(ru_byid)!={str(x['id']) for x in ros}:
   raise ValueError(f'{cat}: language catalogs do not match')
  for ro in ros:
   ru=ru_byid[str(ro['id'])]
   counts['products']+=1
   if ro.get('seo_copy_version')=='v41' and ru.get('seo_copy_version')=='v41':continue
   t=ro['title'];pair=facts.get(norm(t))
   if pair:counts['curated']+=1
   else:counts['missing']+=1
   for i,lang,entry in [(0,'ro',ro),(1,'ru',ru)]:
    old=entry.get('description','').strip()
    corrected=SOURCE_FIXES.get(t)
    if corrected:old=corrected[i]
    if len(old)<20:raise ValueError(f'Short source description for {t}/{lang}; install V40 first')
    if old.casefold().startswith(('adăugat recent. confirm','новое поступление. уточ')):
     raise ValueError(f'Placeholder not fixed by V40: {t}/{lang}')
    new=expand(old,t,cat,lang,pair[i] if pair else '',0)
    if not 78<=words(new)<=155:
     raise ValueError(f'Description size {words(new)} for {t}/{lang} ({cat})')
    if old not in new:raise ValueError(f'Original description was lost: {t}/{lang}')
    entry['description']=new
    entry['seo_copy_version']='v41'
   counts['expanded']+=1
  updates[paths[0]]=json.dumps(ros,ensure_ascii=False,indent=2)+'\n'
  # Store RU in original RO order, as V40 does, to keep catalog pairs aligned.
  updates[paths[1]]=json.dumps([ru_byid[str(p['id'])] for p in ros],ensure_ascii=False,indent=2)+'\n'
 return updates,counts


def main(root,check=False):
 root=root.resolve()
 if not (root/'playspot-v40'/'apply.py').exists():raise RuntimeError('V40 required')
 if not (root/'playspot-v29'/'generate.py').exists():raise RuntimeError('V29 generator required')
 updates,counts=prepare(root)
 changes={p:s for p,s in updates.items() if p.read_text(encoding='utf-8')!=s}
 if check:
  print('V41 PREVIEW:',counts,'JSON files to update',len(changes));return
 for p,s in changes.items():p.write_text(s,encoding='utf-8')
 print('V41 DATA:',counts,'JSON files updated',len(changes))

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--root',default='.');pa.add_argument('--check',action='store_true')
 a=pa.parse_args();main(Path(a.root),a.check)
