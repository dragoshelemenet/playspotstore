#!/usr/bin/env python3
"""V42: helpful bilingual editorial impressions for the PlaySpotStore product catalog.

Source material: existing V40 factual summaries + V41 curated title-specific notes.
Original editorial angles are illustrative commentary, not verified customer reviews.
No invented star ratings, schema.org Review, sales or product condition.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, unicodedata
from pathlib import Path

CATS=('ps2','ps4','ps5','nintendo','xbox','consoles','accessories')
CATEGORY={
 'ro':{'ps2':'Jocuri PS2','ps4':'Jocuri PS4','ps5':'Jocuri PS5','nintendo':'Jocuri Nintendo','xbox':'Jocuri Xbox','consoles':'Console PlayStation','accessories':'Accesorii gaming'},
 'ru':{'ps2':'Игры PS2','ps4':'Игры PS4','ps5':'Игры PS5','nintendo':'Игры Nintendo','xbox':'Игры Xbox','consoles':'Игровые консоли','accessories':'Игровые аксессуары'},
}

# Perspective on mechanics, not fictional firsthand testimony. Variation by title
# avoids V41's repeated filler. For each title the lead and factual details come
# from separate game-specific editorial source lines.
OPINION={
'platform':[
('Când obstacolele sunt bine construite, progresul pare să vină dintr-o mișcare învățată la momentul potrivit, nu din noroc. Este o plăcere pentru cei care apreciază precizia.', 'Когда препятствия продуманы, успех зависит от вовремя освоенного движения, а не от удачи. Это удовольствие для тех, кто ценит точность.'),
('Partea captivantă este să repeți o secvență și să observi cum un detaliu mic îți schimbă traseul. Ritmul poate cere mai multă răbdare decât sugerează grafica.', 'Интересно повторять участок и замечать, как небольшая деталь меняет маршрут. Такой ритм может потребовать больше терпения, чем обещает графика.'),
('Nivelurile au acel sentiment plăcut de „încă o încercare”, mai ales când înțelegi de ce a eșuat prima abordare. Este mai mult despre învățare decât despre grabă.', 'Уровни вызывают приятное желание попробовать ещё раз, особенно когда понимаешь причину ошибки. Это скорее обучение, чем гонка за скоростью.'),
('Mișcarea și micile descoperiri sunt motorul experienței; câteva secunde de explorare pot schimba felul în care abordezi un obstacol.', 'Движение и небольшие открытия задают настроение: несколько секунд исследования способны подсказать новый способ пройти препятствие.'),
('Atractiv este contrastul dintre decorurile prietenoase și secvențele în care reflexele chiar sunt puse la lucru. Când găsești ritmul corect, avansarea devine foarte satisfăcătoare.', 'Привлекает контраст дружелюбных декораций и моментов, когда действительно нужна реакция. Найденный ритм делает продвижение особенно приятным.'),
('Jocul este potrivit pentru cineva care preferă să descopere singur o soluție în loc să urmeze indicații pas cu pas. Micile reușite contează la fel de mult ca finalul.', 'Подойдёт тем, кто любит самостоятельно находить решение, а не идти по подсказкам. Небольшие достижения здесь не менее важны, чем финал.')],
'racing':[
('Plăcerea vine când traseul începe să aibă logică și fiecare viraj poate fi parcurs mai curat decât înainte. O cursă bună e despre control, nu doar despre viteză.', 'Удовольствие появляется, когда трасса становится понятной и каждый поворот удаётся проходить чище. Хорошая гонка — это контроль, а не только скорость.'),
('Miza este găsirea unui ritm: frânezi prea devreme și pierzi timp, prea târziu și compromiți următoarea secțiune. Tocmai această ajustare ține competiția interesantă.', 'Важно найти ритм: слишком раннее торможение отнимает время, позднее портит следующий участок. Именно эти поправки делают соревнование интересным.'),
('Se potrivește celor care se bucură să repete o probă pentru a obține o traiectorie mai bună. Micile îmbunătățiri se simt mai satisfăcător decât o victorie întâmplătoare.', 'Подойдёт любителям повторять заезд ради лучшей траектории. Небольшие улучшения ощущаются приятнее случайной победы.'),
('Într-o competiție strânsă, alegerea momentului pentru depășire dă mai multă emoție decât accelerația pe linie dreaptă. Controlul este partea care răsplătește exercițiul.', 'В напряжённой гонке момент для обгона волнует больше, чем разгон по прямой. Управление — та часть, где практика заметнее всего.'),
('Atmosfera curselor prinde viață când începi să observi particularitățile fiecărui circuit. Alegerea stilului potrivit poate transforma un tur modest într-unul reușit.', 'Атмосфера гонок раскрывается, когда замечаешь особенности каждого маршрута. Подходящий стиль может превратить обычный круг в удачный.'),
('Interesantă este diferența dintre a conduce spectaculos și a conduce eficient; nu întotdeauna aceeași manevră le oferă pe ambele.', 'Интересна разница между эффектной и эффективной ездой: одна и та же манёвренность не всегда даёт и то и другое.')],
'football':[
('Când o fază se construiește din câteva pase bine alese, satisfacția depășește un șut norocos. Jocul răsplătește observația și schimbările de ritm.', 'Когда атака складывается из нескольких точных передач, удовольствие больше, чем от случайного удара. Игра поощряет внимание и смену темпа.'),
('Partea care ține meciurile interesante este duelul tactic: un spațiu lăsat liber poate schimba scorul. Reacția rapidă contează, dar și citirea adversarului.', 'Интерес матчей в тактическом противостоянии: свободная зона может изменить счёт. Важна не только реакция, но и понимание соперника.'),
('Un meci memorabil nu e doar despre goluri: recuperarea la mijloc și o schimbare de flanc pot fi la fel de satisfăcătoare. Este genul de joc în care ai mereu ceva de ajustat.', 'Запоминающийся матч — не только голы: отбор в центре поля и смена фланга тоже радуют. Здесь постоянно есть что подстроить.'),
('Este plăcut când o echipă începe să se miște conform planului tău. Ritmul paselor și organizarea apărării pot conta la fel de mult ca starurile din atac.', 'Приятно, когда команда начинает действовать по твоему плану. Темп передач и оборона порой важнее звёзд нападения.'),
('Cel mai interesant e momentul în care schimbi tactica pentru că rivalii au găsit deja răspunsul la prima strategie. Asta dă sens fiecărui meci.', 'Самый интересный момент — смена тактики, когда соперник уже разгадал первый план. Это придаёт каждому матчу смысл.'),
('E o experiență pentru cine apreciază combinația dintre reflexe și planificarea fazelor, nu doar repetarea aceleiași pase către poartă.', 'Подойдёт тем, кто ценит сочетание реакции и продуманных атак, а не повторение одного паса к воротам.')],
'combat':[
('Un duel reușit seamănă mai mult cu o conversație decât cu o serie de lovituri: fiecare atac provoacă un răspuns. Tocmai citirea celuilalt jucător dă profunzime luptei.', 'Хороший поединок похож скорее на разговор, чем на набор ударов: каждое действие вызывает ответ. Именно понимание соперника добавляет глубину.'),
('Când o combinație învățată funcționează la momentul potrivit, victoria pare meritată. Este un gen în care progresul se vede în decizii, nu în numărul de butoane apăsate.', 'Когда изученная комбинация срабатывает вовремя, победа ощущается заслуженной. Прогресс здесь в решениях, а не количестве нажатий.'),
('Partea palpitantă este acel moment de ezitare când nu știi dacă adversarul va ataca sau se va apăra. Răbdarea poate câștiga un duel mai repede decât agresivitatea.', 'Волнует момент неопределённости: противник пойдёт в атаку или защитится? Терпение порой выигрывает поединок быстрее агрессии.'),
('În confruntările apropiate, un singur contraatac bine ales poate schimba totul. Dacă îți place să înveți personajele pe rând, există mult loc de perfecționare.', 'В близком бою один верный контрудар может всё изменить. Любителям постепенно изучать персонажей здесь есть чему учиться.'),
('Spectacolul vizual atrage atenția, dar satisfacția de durată vine din înțelegerea distanței și a momentului potrivit pentru o tehnică.', 'Зрелище привлекает взгляд, но долгое удовольствие даёт понимание дистанции и правильного момента для приёма.'),
('Merită privit ca o provocare de învățare: înfrângerile arată ce trebuie schimbat, iar fiecare personaj poate cere altă strategie.', 'Лучше воспринимать игру как обучение: поражения показывают, что изменить, а каждый персонаж может требовать иной стратегии.')],
'fps':[
('Momentele bune apar când o intrare riscantă este înlocuită de o mișcare bine gândită. Ritmul este intens, însă poziționarea oferă uneori un avantaj mai mare decât ținta perfectă.', 'Лучшие моменты возникают, когда рискованную атаку заменяет продуманный ход. Темп высок, но позиция иногда важнее идеальной меткости.'),
('Fiecare spațiu deschis invită la acțiune, dar acoperirea și observarea traseelor pot decide o confruntare. Este distractiv când reușești să fii cu un pas înainte.', 'Открытая зона зовёт в бой, однако укрытия и наблюдение за маршрутами решают схватку. Особенно приятно оказаться на шаг впереди.'),
('Adevărata tensiune apare atunci când trebuie să alegi între viteză și siguranță. Nu toate luptele se câștigă prin a trage primul.', 'Настоящее напряжение — в выборе между скоростью и безопасностью. Не все перестрелки выигрывает тот, кто стреляет первым.'),
('Sunetele, distanțele și schimbarea unghiurilor fac confruntările mai interesante decât o simplă probă de reflexe. Planificarea unei secvențe poate fi recompensa principală.', 'Звуки, дистанция и смена углов делают столкновения интереснее проверки рефлексов. Продуманное прохождение может быть главной наградой.'),
('Energia jocului vine din succesiunea rapidă de decizii: înaintezi, schimbi poziția sau păstrezi resursele. Acest ritm poate fi foarte captivant pentru pasionații de acțiune.', 'Энергия игры — в быстрой цепочке решений: наступать, менять позицию или беречь ресурсы. Такой ритм увлекает поклонников экшена.'),
('Dacă îți place să înțelegi structura unei arene sau a unei misiuni, aici observația poate fi la fel de valoroasă ca reflexele.', 'Если любишь разбираться в устройстве арены или миссии, наблюдательность здесь может быть не менее ценной, чем реакция.')],
'rpg':[
('Cele mai interesante momente apar adesea în afara misiunii principale, când un personaj secundar sau un loc uitat schimbă perspectiva asupra lumii. Curiozitatea este bine răsplătită.', 'Самые интересные моменты нередко вне основного задания, когда встреча или забытое место меняет взгляд на мир. Любопытство вознаграждается.'),
('Aventura capătă greutate când o alegere începe să aibă consecințe pentru erou sau pentru cei din jur. Ritmul este mai potrivit pentru explorare atentă decât pentru grabă.', 'Приключение становится значимее, когда выбор влияет на героя или окружающих. Здесь лучше неспешно исследовать мир, чем торопиться.'),
('Plăcerea vine din a-ți construi propriul stil și a descoperi cum reacționează lumea la el. Cine caută doar acțiune continuă ar putea rata partea cea mai interesantă.', 'Удовольствие — в собственном стиле игры и в том, как на него реагирует мир. Любители непрерывного экшена могут пропустить главное.'),
('Este genul de aventură în care ocolurile contează. O conversație, o încăpere ascunsă sau un personaj neașteptat pot rămâne în minte mai mult decât o luptă.', 'Здесь важны отклонения от главного пути. Разговор, скрытая комната или неожиданная встреча способны запомниться сильнее битвы.'),
('Ce atrage este combinația dintre dezvoltarea personajului și descoperirea treptată a universului. Un progres mic poate schimba surprinzător de mult următoarea confruntare.', 'Привлекает сочетание развития героя и постепенного открытия мира. Небольшой прогресс может неожиданно сильно изменить следующую схватку.'),
('Povestea și sistemele de joc se susțin reciproc atunci când alegerile contează. Este o experiență mai bogată pentru cei dispuși să observe detaliile.', 'История и механики работают вместе, когда решения действительно имеют значение. Это более глубокий опыт для внимательных игроков.')],
'horror':[
('Ce rămâne cu tine nu este neapărat un moment de sperietură, ci neliniștea dintre două pericole. Jocul are mai mult impact când înaintezi atent și asculți mediul.', 'Запоминается не столько внезапный испуг, сколько тревога между опасностями. Игра сильнее действует при осторожном движении и внимании к звукам.'),
('Senzația că nu deții toate informațiile face explorarea mai intensă. Cine caută doar lupte rapide ar putea pierde tocmai atmosfera care definește experiența.', 'Нехватка информации делает исследование напряжённее. Любители одной лишь стрельбы могут пропустить атмосферу, ради которой всё устроено.'),
('Atmosfera este construită din pauze, decoruri și indicii, nu doar din apariția monștrilor. Când lumea pare nesigură, până și o ușă obișnuită capătă greutate.', 'Атмосфера рождается из пауз, окружения и подсказок, а не только монстров. Когда мир кажется опасным, даже обычная дверь становится событием.'),
('Tensiunea funcționează prin anticipare: ai timp să bănuiești ceva, dar nu suficient să te pregătești complet. Acest ritm îl face memorabil.', 'Напряжение строится на ожидании: успеваешь заподозрить опасность, но не подготовиться полностью. Этот ритм запоминается.'),
('Un detaliu sonor sau un colț întunecat poate avea mai mult efect decât o confruntare mare. Este un tip de joc pentru cei care apreciază suspansul susținut.', 'Звук или тёмный угол могут подействовать сильнее большого боя. Такой формат понравится любителям постоянного саспенса.'),
('Curiozitatea și instinctul de a te retrage intră adesea în conflict. Tocmai dorința de a descoperi încă o piesă a misterului susține aventura.', 'Любопытство постоянно спорит с желанием отступить. Именно стремление раскрыть ещё одну часть тайны движет приключением.')],
'coop':[
('Când fiecare persoană are o responsabilitate clară, reușita comună se simte mai bine decât o victorie individuală. Comunicarea schimbă întregul ritm.', 'Когда у каждого ясная задача, общий успех приятнее личной победы. Общение полностью меняет темп игры.'),
('Cele mai amuzante situații apar când planul perfect se destramă și echipa trebuie să improvizeze. Aici greșelile pot deveni povești memorabile.', 'Самые забавные моменты — когда идеальный план рушится и команде приходится импровизировать. Ошибки могут стать лучшими историями.'),
('Un coechipier atent face uneori mai mult decât o armă sau o abilitate puternică. Experiența își arată farmecul prin coordonare.', 'Внимательный напарник иногда важнее сильного оружия или способности. Привлекательность игры раскрывается через согласованность.'),
('Provocările devin mai interesante când jucătorii își împart rolurile și își ajustează din mers planul. Recompensa vine din colaborare reală.', 'Испытания интереснее, когда игроки распределяют роли и меняют план на ходу. Награда — в настоящем сотрудничестве.'),
('Este o experiență care pune în valoare oamenii cu care joci: aceeași situație poate decurge diferit în funcție de comunicare.', 'Такая игра особенно раскрывается с людьми рядом: одна и та же ситуация меняется в зависимости от общения.'),
('Farmecul constă în micile decizii de echipă, nu doar în rezultatul final. De aici apar momentele pe care le povestești după sesiune.', 'Прелесть — в маленьких командных решениях, а не только финальном результате. Из этого и рождаются истории после игровой сессии.')],
'simulator':[
('Satisfacția vine din trecerea de la dezordine la un sistem care funcționează. Fiecare mică ajustare poate avea efecte vizibile mai târziu.', 'Удовольствие — превращать хаос в работающую систему. Небольшая поправка может заметно повлиять на результат позже.'),
('Nu viteza, ci răbdarea de a înțelege fiecare etapă aduce progresul. Este potrivit pentru cine se bucură să organizeze și să optimizeze.', 'Не скорость, а терпение помогает освоить каждый этап. Подойдёт тем, кто любит организовывать и улучшать процессы.'),
('Cele mai interesante momente apar când o soluție aparent simplă începe să creeze efecte neașteptate. Asta încurajează experimentarea.', 'Интересно наблюдать, как простое на вид решение приводит к неожиданным последствиям. Это поощряет эксперименты.'),
('Plăcerea vine din observarea rezultatului propriilor decizii. Pentru cine apreciază planificarea, progresul treptat poate fi mai captivant decât acțiunea rapidă.', 'Приятно видеть результат собственных решений. Любителям планирования постепенный прогресс может нравиться больше быстрого экшена.'),
('Este un joc despre detalii: ce pare minor la început poate deveni important mai târziu. Sesiunile răsplătesc atenția și organizarea.', 'Здесь важны детали: мелочь в начале может оказаться существенной позже. Игра вознаграждает внимание и порядок.'),
('Sentimentul de control crește pe măsură ce înțelegi regulile sistemului. Reușita ține de strategie și ajustări, nu de reflexe perfecte.', 'Ощущение контроля растёт вместе с пониманием правил системы. Успех зависит от стратегии и корректировок, а не идеальной реакции.')],
'stealth':[
('Cea mai satisfăcătoare victorie poate fi aceea în care nimeni nu observă că ai fost acolo. Nivelurile invită să găsești alternative la confruntare.', 'Самая приятная победа — та, после которой никто не заметил твоего присутствия. Уровни предлагают альтернативы прямому бою.'),
('Este interesant când un traseu observat din timp se dovedește mai valoros decât forța. Planificarea dă tensiune chiar și momentelor fără luptă.', 'Интересно, когда заранее изученный маршрут ценнее силы. Планирование добавляет напряжение даже эпизодам без боя.'),
('Farmecul este să transformi spațiul într-un aliat: uși, colțuri și rutinele adversarilor devin părți ale planului.', 'Удовольствие — сделать окружение союзником: двери, углы и привычки врагов становятся частью плана.'),
('Când o misiune poate fi rezolvată în mai multe feluri, descoperirea propriei metode dă senzația de libertate. Nu orice pericol trebuie înfruntat direct.', 'Когда у задания есть несколько решений, собственный способ даёт чувство свободы. Не каждую угрозу нужно встречать открыто.'),
('Momentele cu adevărat intense apar înainte de acțiune, când observi inamicii și aștepți fereastra potrivită. Răbdarea este o abilitate.', 'Самые напряжённые моменты — до действия, когда следишь за противниками и ждёшь подходящего момента. Терпение здесь тоже навык.'),
('Un plan bine gândit poate face o secvență dificilă să pară simplă. Tocmai posibilitatea de a improviza diferențiază această experiență.', 'Хороший план способен упростить сложный эпизод. Именно возможность импровизировать выделяет такую игру.')],
'action':[
('Cele mai bune momente combină energia confruntărilor cu locuri care merită explorate. Ritmul alert este atrăgător, dar detaliile din decor dau aventurii personalitate.', 'Лучшие моменты сочетают энергию схваток с местами, которые хочется исследовать. Быстрый темп привлекает, но детали мира придают приключению характер.'),
('Acțiunea este mai memorabilă atunci când obstacolele schimbă planul, nu doar cresc numărul inamicilor. Varietatea situațiilor face diferența.', 'Экшен запоминается сильнее, когда препятствия меняют план, а не просто увеличивают число врагов. Разнообразие ситуаций решает многое.'),
('Farmecul vine din alternanța dintre momentele spectaculoase și perioadele în care descoperi lumea. Este potrivit dacă vrei să faci mai mult decât să urmărești o poveste.', 'Прелесть в чередовании зрелища и открытия мира. Подойдёт тем, кто хочет участвовать в событиях, а не только смотреть историю.'),
('Când mecanicile sunt învățate, confruntările pot deveni un mic spectacol improvizat. Contează însă să fii atent la spațiu și la ritm.', 'Когда механики освоены, схватки превращаются в небольшое импровизированное шоу. Но пространство и темп всё равно важны.'),
('Interesant este felul în care diferite situații îți cer altă abordare. O aventură dinamică își păstrează farmecul prin surprize, nu doar prin intensitate.', 'Интересно, как разные ситуации требуют нового подхода. Динамичное приключение держится на сюрпризах, а не только напряжении.'),
('Acest tip de joc atrage când îți permite să descoperi propriul ritm între explorare și luptă. Micile variații fac experiența mai vie.', 'Такой формат привлекает возможностью найти свой ритм между исследованием и боем. Небольшие изменения делают приключение живее.')],
'narrative':[
('Cea mai puternică parte poate fi o conversație aparent măruntă, care schimbă felul în care privești un personaj. Este o experiență pentru cei atenți la povești.', 'Сильнее всего может подействовать маленький разговор, меняющий отношение к герою. Это опыт для тех, кто внимательно следит за историей.'),
('Momentele liniștite dau greutate evenimentelor dramatice, iar decorurile spun adesea lucruri pe care dialogurile le lasă nespuse.', 'Спокойные эпизоды усиливают драму, а окружение часто рассказывает то, о чём умалчивают диалоги.'),
('Nu este nevoie de acțiune neîntreruptă pentru a ține interesul viu. Misterul și relațiile dintre personaje pot face fiecare descoperire importantă.', 'Для интереса не нужен непрерывный экшен. Загадка и отношения героев делают каждое открытие значимым.'),
('Povestea este mai captivantă când nu îți oferă imediat toate răspunsurile. Ritmul deliberat lasă loc interpretării.', 'История увлекает сильнее, когда не даёт всех ответов сразу. Неторопливый ритм оставляет место для трактовки.'),
('Ce rămâne în minte este felul în care personajele reacționează la evenimente, nu doar ce se întâmplă efectiv. Atmosfera devine parte din poveste.', 'Запоминается то, как герои реагируют на события, а не только сами события. Атмосфера становится частью истории.'),
('Se potrivește celor care preferă tensiunea construită încet și poveștile cu personaje imperfecte, în locul unei serii constante de confruntări.', 'Подойдёт любителям постепенно нарастающего напряжения и неоднозначных персонажей, а не бесконечных боёв.')],
'party':[
('Cele mai reușite momente apar când regulile simple duc la situații complet neașteptate. Este o experiență care se bucură de umor și spontaneitate.', 'Лучшие моменты — когда простые правила рождают совершенно неожиданные ситуации. Игра держится на юморе и спонтанности.'),
('Nu perfecțiunea contează, ci energia momentului: o mică greșeală poate deveni partea cea mai amuzantă a rundei.', 'Здесь важна не идеальная игра, а настроение: маленькая ошибка может стать самым смешным моментом раунда.'),
('Farmecul este accesibilitatea: intri repede în ritm și începi să descoperi mici strategii fără să studiezi sisteme complicate.', 'Прелесть в доступности: быстро втягиваешься и находишь маленькие стратегии без изучения сложных правил.'),
('Provocările scurte pot deveni surprinzător de competitive, dar tonul rămâne unul relaxat. Este potrivit pentru sesiuni fără prea multă pregătire.', 'Короткие задания могут оказаться неожиданно соревновательными, но настроение остаётся лёгким. Подойдёт для игры без долгой подготовки.'),
('Este genul de joc în care o rundă mai puțin reușită poate fi mai memorabilă decât o victorie. Distracția vine din imprevizibil.', 'Иногда неудачный раунд запоминается сильнее победы. Развлечение рождается из непредсказуемости.'),
('Varietatea activităților ajută experiența să nu rămână blocată într-o singură rutină. Tonul jucăuș este un avantaj.', 'Разнообразие заданий не даёт застрять в одной рутине. Игривое настроение — явное достоинство.')],
'vr':[
('Atracția principală este sentimentul de prezență: mișcările și distanțele pot părea diferite față de jocurile pe ecran. Verifică însă accesoriile necesare ediției.', 'Главное — ощущение присутствия: движения и расстояния воспринимаются иначе, чем на обычном экране. Но стоит проверить оборудование для этой версии.'),
('Când lumea reacționează la mișcările tale, chiar și acțiunile simple devin mai implicante. Experiența depinde de sistemul VR compatibil.', 'Когда мир откликается на движения, даже простые действия увлекают сильнее. Опыт зависит от совместимой VR-системы.'),
('Interesant este felul în care perspectiva schimbă raportarea la spațiu. Pentru o utilizare confortabilă contează și echipamentul potrivit.', 'Любопытно, как новая перспектива меняет восприятие пространства. Для комфорта важно подходящее оборудование.'),
('Un moment obișnuit poate deveni memorabil prin imersiune. Înainte de comandă merită verificat exact ce dispozitive sunt necesare.', 'Обычный эпизод может запомниться благодаря погружению. Перед заказом стоит уточнить необходимые устройства.'),
('Această categorie pune mai mult accent pe interacțiune directă decât pe observarea pasivă a ecranului. Compatibilitatea este esențială.', 'Здесь важнее прямое взаимодействие, чем пассивное наблюдение за экраном. Совместимость принципиальна.'),
('Senzația de implicare poate fi surprinzătoare, dar experiența este strâns legată de setările și accesoriile potrivite.', 'Погружение может удивить, но результат сильно зависит от настроек и нужных аксессуаров.')],
'accessory':[
('Designul poate schimba plăcerea de a folosi un controller zi de zi, dar alegerea bună începe cu verificarea modelului și a stării reale.', 'Дизайн может добавить удовольствия от повседневного использования контроллера, но хороший выбор начинается с проверки модели и состояния.'),
('Detaliile care contează cel mai mult sunt ergonomia și compatibilitatea, nu doar aspectul din fotografie. Înainte de comandă merită confirmat exact ce primești.', 'Важнее всего эргономика и совместимость, а не только внешний вид на фото. Перед заказом стоит уточнить комплектацию.'),
('Este genul de accesoriu pe care îl apreciezi prin utilizarea practică. Fotografia nu poate confirma funcționarea butoanelor sau starea, așa că verificarea rămâne importantă.', 'Такие аксессуары оцениваются в реальном использовании. Фотография не подтверждает работу кнопок и состояние, поэтому проверка важна.'),
('Un accesoriu potrivit trebuie să se simtă firesc în mâini și să corespundă sistemului folosit. Specificațiile exacte trebuie confirmate, nu deduse din imagine.', 'Подходящий аксессуар должен быть удобен и работать с нужной системой. Точные характеристики стоит уточнить, а не угадывать по фотографии.'),
('Aspectul este doar prima impresie; compatibilitatea, comenzile și starea fizică sunt ceea ce îl face o alegere bună pe termen lung.', 'Внешний вид — только первое впечатление; совместимость, управление и физическое состояние определяют удачность покупки.'),
('Pentru un accesoriu folosit des, detaliile mici pot conta surprinzător de mult. Cere confirmarea modelului și a componentelor incluse.', 'У часто используемого аксессуара мелочи бывают важнее ожиданий. Уточняйте модель и входящие компоненты.')],
'console':[
('Versiunea și starea consolei contează mai mult decât aspectul exterior. O alegere bună începe cu verificarea modelului, a accesoriilor și a funcționării.', 'Версия и состояние консоли важнее внешнего вида. Разумный выбор начинается с проверки модели, аксессуаров и работоспособности.'),
('Pentru o consolă, diferența se face prin detaliile concrete ale exemplarului: ce include pachetul și în ce stare este aparatul. Nu le presupune din imagine.', 'Для консоли важны конкретные детали экземпляра: что входит в комплект и в каком состоянии устройство. Не стоит судить только по фото.')],
}

SOURCES={
 'facts':'playspot-v41/editorial-facts.tsv',
 'short':'playspot-v40/descriptions.tsv',
 'angles':'playspot-v42/review-angles.tsv',
}

def key(value: str)->str:
    s=unicodedata.normalize('NFKC',value).casefold().replace('’', "'")
    return ' '.join(re.sub(r'[^\w]+',' ',s).split())

def read_pairs(path: Path) -> dict[str,tuple[str,str]]:
    if not path.is_file():raise FileNotFoundError(path)
    out={}
    for line_number,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip() or line.startswith('#'):continue
        parts=line.split('\t')
        if len(parts)!=3:raise ValueError(f'{path}:{line_number}: expected title/RO/RU TSV')
        title,ro,ru=[s.strip() for s in parts]
        if not (title and len(ro)>25 and len(ru)>25):raise ValueError(f'{path}:{line_number}: empty copy')
        k=key(title)
        if k in out:raise ValueError(f'{path}:{line_number}: duplicate {title}')
        out[k]=(ro,ru)
    return out

def sentence(text: str)->str:
    # V41 descriptions always begin with an earlier factual product synopsis.
    m=re.search(r'(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚА-ЯЁ0-9])',text)
    return (text[:m.start()] if m else text).strip()

def end_period(text: str)->str:
    clean=text.strip()
    return clean if clean.endswith(('.', '!', '?')) else clean.rstrip(' .')+'.'

def overlap(a: str,b:str)->float:
    w1=set(key(a).split()); w2=set(key(b).split());return len(w1&w2)/max(1,min(len(w1),len(w2)))

def meta_desc(title: str,cat: str,lang:str,lead:str)->str:
    prefix=f'{title} | {CATEGORY[lang][cat]}: '
    # The existing V29 head() writes description[:165] into HTML.
    # Keep our whole source metadata under that cap so the visible meta,
    # OpenGraph text, source JSON and validator remain in sync.
    limit=160-len(prefix)
    if limit < 12:
        raise ValueError(f'Product/category title too long for a meaningful SEO meta description: {title}')
    snippet=lead.strip()
    if len(snippet)>limit:
        part=snippet[:limit].rsplit(' ',1)[0].rstrip(' ,;:—-')
        snippet=part if len(part)>=18 else snippet[:limit]
    return prefix+snippet

def genre(title: str,summary: str,cat: str)->str:
    if cat=='accessories':return 'accessory'
    if cat=='consoles':return 'console'
    t=key(title+' '+summary)
    checks=[
      ('vr',(' ps vr',' vr ','vr compatible','realitate virtuala','vr)')),
      ('football',('fifa','fc 25','fc 26','football manager','fotbal','soccer')),
      ('racing',('racing','raliu','wrc','forza','formula 1','f1 22','grid legends','need for speed','ride 5','tour de france','assetto corsa','driving','motocic','truck simulator','on the road','cars 2','tony hawk','skate','surf s up')),
      ('horror',('resident evil','silent hill','horror','groaza','groază','cron os','little nightmares','alan wake','daymare','until dawn','outlast','the quarry','still wakes','dead space','vampyr')),
      ('coop',('it takes two','plateup','back 4 blood','vermintide','cooperativ')),
      ('stealth',('hitman','assassin','dishonored','stealth','infiltrare','spy')),
      ('combat',('street fighter','mortal kombat','tekken','wwe','ufc','boxing','undisputed','dragon ball','dissidia','fighter','luptatori','lupte clasice')),
      ('fps',('call of duty','battlefield','doom','sniper elite','rainbow six','metro exodus','ghost recon','shooter','first person','robo cop')),
      ('simulator',('simulator','farming','museum','tropico','monopoly','logistics','manager','minecraft')),
      ('platform',('kirby','rayman','mario','sonic','ratchet','spongebob','crash of the','prince of persia','gunborg')),
      ('narrative',('detroit','hidden agenda','the silent swan','life is strange','uncharted')),
      ('rpg',('final fantasy','witcher','dark souls','nioh','greedfall','dragon s dogma','kingdom come','rpg','bloodborne','demon s souls','lies of p','hogwarts','expedition 33','diablo','monster hunter')),
      ('party',('party','minigame','mini joc','lights camera pants')),
    ]
    for g,terms in checks:
        if any(term in t for term in terms):return g
    return 'action'

def own_review(title:str,summary:str,cat:str,language:str,angles:dict)->str:
    pair=angles.get(key(title))
    if pair:return end_period(pair[0 if language=='ro' else 1])
    group=genre(title,summary,cat)
    samples=OPINION[group]
    n=int(hashlib.sha256((key(title)+cat).encode('utf-8')).hexdigest()[:8],16)
    return samples[n%len(samples)][0 if language=='ro' else 1]

def build_product(base:dict,lang:str,cat:str,short:dict,facts:dict,angles:dict,ro_title:str)->dict:
    out=base.copy()
    if out.get('seo_copy_version')=='v42':
        for attr in ('seo_meta_description','seo_editorial_review'):
            if not out.get(attr):raise ValueError(f'Incomplete V42 product {out.get("id")}: {attr}')
        # Repair previously generated V42 descriptions (which could be 166+ chars)
        # without touching the factual synopsis or editorial review.
        out['seo_meta_description']=meta_desc(out['title'],cat,lang,out['description'])
        return out
    if out.get('seo_copy_version')!='v41':
        raise ValueError(f'{out.get("id")} is not on V41 baseline (found {out.get("seo_copy_version")})')
    t=ro_title;k=key(t);ind=0 if lang=='ro' else 1
    short_summary=short.get(k)
    lead=end_period(short_summary[ind] if short_summary else sentence(out.get('description','')))
    if len(lead)<23:raise ValueError(f'{t} ({lang}) missing factual short summary')
    detail=facts.get(k)
    if detail is None:
        # Do not invent a feature not recorded in our source information.
        detailed=end_period(sentence(out['description']))
    else:detailed=end_period(detail[ind])
    review=own_review(t,lead,cat,lang,angles)
    # Keep the factual synopsis and the clearly labelled editorial experience separate.
    # Put title-specific details INTO the editorial section, not in both places.
    if key(lead)!=key(detailed) and overlap(lead,detailed)<=.84:
        review=detailed+' '+review
    elif key(t) not in angles:
        # If V41's only source note merely repeats the synopsis, avoid
        # showing that same sentence twice; anchor the commentary to the title.
        review=(('La '+t+', ') if lang=='ro' else ('В '+t+' '))+review[0].lower()+review[1:]
    if not (50<=len(review) and 26<=len(lead)):
        raise ValueError(f'Bad V42 editorial copy: {t}/{lang}')
    out['description']=lead
    out['seo_editorial_review']=review
    out['seo_meta_description']=meta_desc(out['title'],cat,lang,lead)
    out['seo_copy_version']='v42'
    return out

def patch_generator(source:str)->str:
    if 'V42_EDITORIAL_PRODUCT' in source:
        for token in ('seo_meta_description','seo_editorial_review','{review_html}','p42-editorial'):
            if token not in source:raise ValueError('Partial V42 generator patch: '+token)
        return source
    meta="    meta=f'{product[\"title\"]} | {catname}: {desc}'"
    if source.count(meta)!=1:raise ValueError('V40 meta generator anchor missing')
    source=source.replace(meta,meta+"\n    if product.get('seo_meta_description'): meta=compact(product['seo_meta_description'])",1)
    page='    page=head(title,meta,path,alt,lang,img,schema,ogtype="product")'
    if source.count(page)!=1:raise ValueError('V40 HTML generator anchor missing')
    review_code='''    # V42_EDITORIAL_PRODUCT: editorial commentary, not a verified customer review.
    impression=compact(product.get('seo_editorial_review'))
    heading=('Impresie editorială de gameplay' if lang=='ro' else 'Редакционные впечатления об игре')
    if cat in ('accessories','consoles'):
        heading=('La ce să fii atent' if lang=='ro' else 'На что обратить внимание')
    review_html=(f'<section class="p42-editorial" aria-label="{esc(heading)}">'
                 f'<h2>{esc(heading)}</h2><p>{esc(impression)}</p></section>') if impression else ''
'''
    source=source.replace(page,review_code+page,1)
    # In the generator HTML string, place commentary after details/ID, before the CTA/price.
    insert='</dl>\n<div class="seo-pricebox">'
    if source.count(insert)!=1:raise ValueError('V40 product facts and price block insertion point missing')
    source=source.replace(insert,'</dl>\n{review_html}\n<div class="seo-pricebox">',1)
    css='    page=page.replace(\'</head>\', \'<link rel="stylesheet" href="/playspot-v40.css?v=20261110-v40">\\n</head>\', 1)'
    # Leave V40 CSS intact and add the small editorial section CSS into generated product head.
    anchor="    return f'''{page}<body>{nav(cat,lang)}"
    # This anchor also appears in category_html; restrict the patch to product_html.
    product_start=source.find('def product_html(')
    if product_start<0:raise ValueError('V40 product_html function missing')
    product_section=source[product_start:]
    if product_section.count(anchor)!=1:
        raise ValueError('V40 product return template missing or ambiguous')
    product_section=product_section.replace(anchor,'''    if impression:
        page=page.replace('</head>', '<link rel="stylesheet" href="/playspot-v42.css?v=20261110-v42">\\n</head>', 1)
'''+anchor,1)
    source=source[:product_start]+product_section
    return source

def plan(root:Path,check=False)->tuple[dict[Path,str],dict]:
    root=root.resolve()
    for relative in ('playspot-v29/generate.py','playspot-v40/apply.py','playspot-v41/editorial-facts.tsv','index.html','ru.html'):
        if not (root/relative).is_file():raise FileNotFoundError(root/relative)
    short=read_pairs(root/SOURCES['short'])
    facts=read_pairs(root/SOURCES['facts'])
    angles=read_pairs(Path(__file__).with_name('review-angles.tsv'))
    changes={};total=0;seen=set();bespoke=0;new=0
    for cat in CATS:
        paths={lang:root/'data'/f'{cat}{"_ru" if lang=="ru" else ""}.json' for lang in ('ro','ru')}
        records={lang:json.loads(path.read_text(encoding='utf-8')) for lang,path in paths.items()}
        by_id={lang:{str(i['id']):i for i in items} for lang,items in records.items()}
        if len(records['ro'])!=len(records['ru']) or len(by_id['ro'])!=len(records['ro']) or len(by_id['ru'])!=len(records['ru']) or set(by_id['ro'])!=set(by_id['ru']):
            raise ValueError(cat+': language catalogs do not match')
        for item in records['ro']:
            pid=str(item['id'])
            if pid in seen:raise ValueError('Duplicate ID '+pid)
            seen.add(pid);total+=1
            for lang in ('ro','ru'):
                p=by_id[lang][pid]
                upd=build_product(p,lang,cat,short,facts,angles,item['title'])
                by_id[lang][pid]=upd
            if key(item['title']) in angles:bespoke+=1
            if item.get('seo_copy_version')=='v41':new+=1
        for lang,path in paths.items():
            output=[by_id[lang][str(i['id'])] for i in records['ro']]
            content=json.dumps(output,ensure_ascii=False,indent=2)+'\n'
            if content!=path.read_text(encoding='utf-8'):changes[path]=content
    if total<279:raise ValueError(f'Unexpectedly small catalog: {total}')
    genpath=root/'playspot-v29/generate.py'
    old=genpath.read_text(encoding='utf-8')
    updated=patch_generator(old)
    if updated!=old:changes[genpath]=updated
    stats={'products':total,'newly_upgraded':new,'bespoke_titles':bespoke,'other_editorial':total-bespoke,'data_files':sum(p.parent.name=='data' for p in changes),'generator_updated':genpath in changes}
    return changes,stats

def main(root:Path,check:bool=False)->None:
    changes,stats=plan(root)
    if check:
        print('V42 PREVIEW:',stats)
        return
    for path,content in changes.items():path.write_text(content,encoding='utf-8')
    print('V42 PRODUCT DATA:',stats)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--check',action='store_true')
    args=p.parse_args();main(Path(args.root),args.check)
