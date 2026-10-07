import csv, json, math, pathlib, sys
from xml.sax.saxutils import escape
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from project_data import PARTS, PANELS, OPENINGS, STEPS
ROOT=pathlib.Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=landscape(A4);PAGE=0
c=canvas.Canvas(str(ROOT/'assembly_manual_ru.pdf'),pagesize=(W,H))
c.setTitle('ASTRA V2 — корпус витрины, детали и пошаговая сборка')
def txt(x,y,s,size=10,color='#203042',bold=False):
    c.setFillColor(color);c.setFont('DejaVuBold' if bold else 'DejaVu',size);c.drawString(x*mm,y*mm,s)
def para(x,y,w,content,size=10):
    p=Paragraph(escape(content).replace('\n','<br/>'),ParagraphStyle('body',fontName='DejaVu',fontSize=size,leading=size*1.45,textColor='#203042'))
    _,height=p.wrap(w*mm,1000);p.drawOn(c,x*mm,y*mm-height);return height/mm
def page(title,sub=''):
    global PAGE
    if PAGE:c.showPage()
    PAGE+=1
    c.setFillColor('#f7f8fa');c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor('#162635');c.rect(0,H-31*mm,W,31*mm,fill=1,stroke=0)
    txt(15,190,title,17,'#ffffff',True)
    if sub:txt(15,181,sub,8,'#c1ced8')
    txt(15,8,'ASTRA · V2 · мм · Документация прототипа; резьба и крепление требуют доработки',7)
    txt(277,8,str(PAGE),8)
def poly(pts,fill,stroke='#233342'):
    p=c.beginPath();p.moveTo(*pts[0])
    for pt in pts[1:]:p.lineTo(*pt)
    p.close();c.setFillColor(fill);c.setStrokeColor(stroke);c.setLineWidth(.45);c.drawPath(p,fill=1,stroke=1)
def iso(parts,x=18,y=40,width=163,height=123,active=None,explode=False):
    scale=min(width/1500,height/1000)*mm
    def project(v):a,b,d=v;return (x*mm+scale*(a+650-.5*b),y*mm+scale*(d+30+.22*b))
    # Back to front so smaller parts do not disappear behind the backing.
    for p in sorted(parts,key=lambda p:p['pos'][1],reverse=True):
        cx,cy,cz=p['pos'];sx,sy,sz=p['size']
        offset=-110 if explode and p['stage']==active else 0
        v=[project((cx+a*sx/2,cy+b*sy/2+offset,cz+d*sz/2)) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
        hot=p['stage']==active
        fill='#edb579' if hot else '#d2d9de'
        if p['material'].startswith('Акрил'):fill='#b4dcea'
        for inds,col in [([1,5,6,2],'#aa987e' if hot else '#aab6c0'),([3,2,6,7],'#f3c89b' if hot else '#e0e5e9'),([0,1,2,3],fill)]:poly([v[i] for i in inds],col)
        if hot:
            pt=project((cx,cy+offset-sy/2,cz));c.setFillColor('#642f06');c.setFont('DejaVuBold',7);c.drawCentredString(pt[0],pt[1],p['id'])
def front(x=32,y=32,s=.17,labels=True):
    def rect(px,pz,w,h,color,fill=False):
        c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(.6);c.rect((x+(px+600-w/2)*s)*mm,(y+(pz-h/2)*s)*mm,w*s*mm,h*s*mm,stroke=1,fill=fill)
    rect(0,400,1200,800,'#526678')
    for p in PARTS:
        if p['stage'] in [2,3,4,5]:rect(p['pos'][0],p['pos'][2],p['size'][0],p['size'][2],'#c59158',True)
    for name,px,pz,w,h in OPENINGS:
        if labels:
            txt(x+(px+600-w/2+8)*s,y+pz*s,name,7)
            txt(x+(px+600-w/2+8)*s,y+(pz-22)*s,f'{w} × {h}',7)
    def dim(x1,y1,x2,y2,label):
        c.setStrokeColor('#203042');c.line(x1*mm,y1*mm,x2*mm,y2*mm)
        for a,b in [(x1,y1),(x2,y2)]:c.line((a-1)*mm,(b-1)*mm,(a+1)*mm,(b+1)*mm)
        txt((x1+x2)/2-7,(y1+y2)/2+2,label,8)
    dim(x,y-7,x+1200*s,y-7,'1200')
    dim(x-7,y,x-7,y+800*s,'800')
def table(rows,x,y,widths,font=8,rowheight=9):
    for ri,row in enumerate(rows):
        xx=x
        for val,ww in zip(row,widths):
            c.setFillColor('#e1e7ec' if ri==0 else ('#fff' if ri%2 else '#edf1f4'));c.rect(xx*mm,(y-(ri+1)*rowheight)*mm,ww*mm,rowheight*mm,fill=1,stroke=0)
            txt(xx+2,y-ri*rowheight-rowheight+3,str(val),font,bold=(ri==0));xx+=ww

page('ASTRA / инструкция по сборке','Корпус из фанеры, декоративное дерево, съёмный акрил и подсветка')
preview=ROOT/'final_visual.png'
if preview.exists():c.drawImage(str(preview),16*mm,42*mm,width=177*mm,height=125*mm,preserveAspectRatio=True,anchor='c')
else:iso(PARTS,x=16,y=42,width=177,height=125)
para(201,164,79,'1200 × 800 мм — основная рама\nГлубина коробов 70 мм\nЗадник 18 мм; стенки 15 мм\nАкрил 4 мм\n\nКомплект содержит чертежи, список деталей, раскрой и 11 шагов сборки.\n\nЭто рабочий эскиз корпуса для прототипа. Производственный рельеф и расчёт креплений в комплект не входят.',11)
txt(16,25,'Объекты с пометкой CONCEPT в Blender не являются готовыми деталями для ЧПУ.',9,bold=True)

page('01 / фасад и чистые проёмы','Координаты: X — от центра; Z — от нижней кромки A01; Y — глубина')
front(x=32,y=30,s=.166)
para(240,164,42,'Внутренние размеры ниш указаны без стенок.\n\nДве левые ниши имеют общую полку.\n\nЦентр разделён на 120 / 130 / 120 мм.\n\nПравая ниша одна, 280 × 350 мм.\n\nОтдельная «правая средняя» секция из таблицы референса не добавлена: её положение не определено.',8)

page('02 / глубина и слои','Разрез условный, не в масштабе; лицевая сторона слева')
layers=[('Декор / буквы',65,24,'#c59158'),('Акрил 4',98,4,'#8bcada'),('Короба 70',111,70,'#d3af83'),('A01 / 18',190,18,'#ba9974'),('Крепление',220,18,'#8899a7')]
for name,x,width,col in layers:
    c.setFillColor(col);c.rect(x*mm,65*mm,width*mm,90*mm,fill=1,stroke=0);txt(x,160,name,8)
para(20,49,255,'Базовый пакет задник + короб + акрил = 18 + 70 + 4 = 92 мм. Накладной декор, буквы и рельеф выступают дальше; фактическую полную глубину измерять по финальным деталям. Крепление добавляет зазор от стены. Корона выходит за номинальную высоту 800 мм примерно на 14 мм.',10)
para(20,171,255,'Декоративные планки 30 мм установлены с перекрытием края коробов, а не добавлены целиком поверх акрила. Панели должны сниматься без демонтажа декора.',9)

for section,items in [('03 / деревянные детали',[p for p in PARTS if p['stage']<=5]),('04 / декор и акрил',[p for p in PARTS if p['stage']>=7])]:
    if section.startswith('03'):
        page('Слои / взрыв-схема','Вынос деталей условный; синий слой обозначает прозрачный акрил')
        img=ROOT/'exploded_layers.png'
        if img.exists():c.drawImage(str(img),15*mm,37*mm,width=192*mm,height=135*mm,preserveAspectRatio=True,anchor='c')
        else:iso(PARTS,x=15,y=40,width=188,height=126,active=8,explode=True)
        para(213,160,67,'A01 — задняя панель\nL / R / C / B — короба\nD — декоративная рама\nCONCEPT — резьба и буквы\nG01–G05 — акрил\n\nПортрет, трофеи и настенное крепление скрыты для ясности. На схеме панели показаны непрозрачными, чтобы было видно разделение слоёв.',10)
    page(section,'Длины заготовок окончательные для показанного корпуса; размеры резьбы уточняются отдельно')
    rows=[['ID','Деталь','Материал','X × Y × Z, мм','Центр X; Z']]
    for p in items:rows.append([p['id'],p['title'],p['material'],' × '.join(map(str,p['size'])),f"{p['pos'][0]}; {p['pos'][2]}"])
    table(rows,15,174,[18,85,42,60,62],font=7.5,rowheight=6.6)
    if items[0]['stage']>=7:para(16,70,262,'Акрил накладной: +10 мм к ширине и высоте чистого проёма. Нахлёст 5 мм с каждой стороны. Между двумя левыми панелями остаётся зазор 5 мм. Заготовки декора D01–D04 не описывают арку, портрет и отдельные узоры: эти элементы требуют собственного комплекта моделей после согласования.',10)

page('05 / материалы и раскрой','Распил по фактической толщине материала; не использовать толщину из этикетки без замера')
cuts=[]
for p in PARTS:
    if p['material']=='Фанера 15':cuts.append((p['id'],max(p['size'][0],p['size'][2])))
strips=[]
for code,length in sorted(cuts,key=lambda a:-a[1]):
    for strip in strips:
        used=sum(v for _,v in strip)+3*max(0,len(strip)-1)
        if used+3+length<=2440:strip.append((code,length));break
    else:strips.append([(code,length)])
for i,strip in enumerate(strips):
    y=153-i*24;txt(16,y+10,f'Полоса {i+1}: ширина 70 мм',9,bold=True);xx=16
    for code,length in strip:
        w=length/2440*263;c.setFillColor('#d9b58c');c.rect(xx*mm,y*mm,w*mm,8*mm,fill=1,stroke=0);txt(xx+1,y+2,f'{code} / {length}',6.5);xx+=w+3/2440*263
para(16,48,262,f'Фанера 15 мм: {len(strips)} полосы 2440 × 70 мм из одного листа 2440 × 1220, пропил 3 мм; остаток сохраняется. Это линейный план по длине, не программа станка. Фанера 18 мм: A01 1200 × 800 из отдельной заготовки. Дерево 30 мм: 2 шт. 800 × 38; 1124 × 25 и 1124 × 45; запас на отделку и орнамент — отдельно. French cleat: 2 заготовки 1000 × 40 × 18, скос 45° проектируется по месту.',9)

page('06 / разметка задней панели','Для переноса в мастерскую используйте drawings/front_layout.svg или front_layout.dxf')
front(x=22,y=31,s=.158,labels=False)
rows=[['Блок','Левый низ X; Z','Габарит с боковинами']]
for label,bounds in [('Левый',(-560,280,310,345)),('Правый',(250,280,310,380)),('Центр',(-215,280,430,180)),('Нижний',(-570,40,1140,230))]:
    xx,zz,w,h=bounds;rows.append([label,f'{xx+600}; {zz}',f'{w} × {h}'])
table(rows,219,163,[20,30,30],font=6.7,rowheight=10)
para(219,98,64,'Здесь X указан от левого края A01, Z — от нижнего.\n\nВ таблице деталей X указан от центра: прибавьте 600.\n\nСначала сухая сборка, затем сверление. Разметка не является утверждённой картой отверстий под крепёж.',9)

page('07 / LED и съёмный акрил','Магниты и блок питания сначала проверить на отдельном пробном узле')
front(x=22,y=32,s=.155,labels=False)
for code,name,x,z,w,h in PANELS:
    xx=22+(x+600)*.155;zz=32+z*.155
    c.setStrokeColor('#f59d29');c.setLineWidth(2)
    c.line((xx-w*.155/2)*mm,(zz+h*.155/2)*mm,(xx+w*.155/2)*mm,(zz+h*.155/2)*mm)
    for side in [-1,1]:c.line((xx+side*w*.155/2)*mm,(zz-h*.155/2)*mm,(xx+side*w*.155/2)*mm,(zz+h*.155/2)*mm)
para(219,165,65,'LED сверху и по двум бокам каждого проёма: суммарно 4,35 м без припуска.\n\nПример: 12 В, 9,6 Вт/м → 41,76 Вт. С запасом 25% нужен блок ≥52,2 Вт; пример выбора — 60 Вт. Пересчитать по выбранной ленте.\n\nПять ветвей подключаются параллельно к 12 В. Сетевую часть использовать готовую, сертифицированную; не собирать её внутри деревянного корпуса.',8.5)
para(17,24,265,'Провода проложить скрыто, с защитой кромок отверстий и разгрузкой натяжения. Доступ к блоку питания оставить сзади. Магниты: 20 шт. и 20 стальных площадок; окончательный диаметр, глубина гнезда и клей — по выбранному изделию и пробе удержания.',8)

page('08 / соединения и закупка','Выполнить пробный узел перед сверлением и склейкой готовых деталей')
table([['Позиция','Количество / требование'],['Шурупы 3,5 × 35','Ориентировочно 100 шт.; уточнить схему и пробное сверление'],['Столярный клей','По материалу и условиям; выдержка по инструкции'],['Магниты + стальные площадки','20 + 20; Ø4 в модели — только пример, не спецификация покупки'],['Акрил','4 мм; 5 отдельных панелей по G01–G05'],['LED + алюминиевый профиль','4,35 м чистой длины; купить с припуском, резать по меткам'],['Блок питания','Готовый 12 В / 60 Вт для примера ленты 9,6 Вт/м'],['Провод, клеммы, защита проходов','По току каждой ветви, длине и инструкции оборудования'],['Крепёж стены / French cleat','Выбрать после определения стены и полного веса']],16,173,[78,187],font=8,rowheight=9)
para(16,75,125,'Узел задника: головка снаружи A01 → 18 мм фанеры → торец 15-мм стенки короба. Шуруп 35 мм входит в стенку на 17 мм. Ось сверления — середина толщины стенки. Для крепления к A01 ориентир — шаг не более 150 мм, от концов не менее 30 мм; окончательно по пробе материала и нагрузке.',9)
para(153,75,127,'Узел акрила: накладная панель с нахлёстом 5 мм → приклеенная ответная стальная площадка → утопленный в кромку дерева магнит. Площадка и клей имеют толщину: уточнить фактическое положение панели. Если выбранный магнит не помещается в 15-мм кромке, нужен отдельный держатель и новая деталировка.',9)
txt(16,27,'Не затягивать шуруп в торец фанеры без пробного сверления. Несущая способность не рассчитана.',8,bold=True)

# Eleven Lego-style numbered stages.
stage_map=[None,1,2,3,4,5,6,7,8,9,10]
for number,((title,desc),stage) in enumerate(zip(STEPS,stage_map),1):
    page(f'Сборка / шаг {number:02d}',title)
    visible=[p for p in PARTS if stage is None or p['stage']<=stage]
    if stage==6:visible=[p for p in PARTS if p['stage']<=5]
    if number==1:
        for label,x,y,w,h,color in [('Фанера 18 → A01',19,99,79,56,'#b5c0c9'),('Фанера 15 → полосы 70',105,99,79,56,'#d7bc99'),('Дерево 30 → декор',19,58,79,28,'#b89265'),('Акрил 4 → G01–G05',105,58,79,28,'#acd3df')]:
            c.setFillColor(color);c.rect(x*mm,y*mm,w*mm,h*mm,fill=1,stroke=0);txt(x+3,y+h/2,label,8)
        txt(20,166,'Сначала материалы и заготовки — затем сухая сборка.',9)
    elif number==10:
        front(x=25,y=41,s=.125,labels=False)
        c.setFillColor('#e9aa69');c.rect(37.5*mm,121*mm,125*mm,5*mm,fill=1,stroke=0)
        txt(40,128,'W01 — планка корпуса, схема сзади',8)
        txt(28,28,'W02 крепится к стене. Угол 45° и сопряжение — по месту.',8)
    elif number==11 and preview.exists():
        c.drawImage(str(preview),15*mm,42*mm,width=173*mm,height=124*mm,preserveAspectRatio=True,anchor='c')
    else:
        iso(visible,x=15,y=42,width=173,height=124,active=stage,explode=stage in [2,3,4,5,7,8])
    para(196,166,85,desc,10)
    ids=[p['id'] for p in PARTS if p['stage']==stage]
    if ids:para(196,66,85,'Детали этого шага: '+', '.join(ids),9)
    txt(16,27,'Оранжевым выделены добавляемые детали; вынос вперёд условный.',8)
    if number==1:para(16,21,262,'Инструмент: пила с направляющей, угольник, рулетка, струбцины, дрель, пробные свёрла, шлифование; ЧПУ требуется для точного рельефа.',8)

page('09 / перед запуском в изготовление','Контрольный лист мастера — обязательные решения, которые нельзя получить из картинки')
checks=[
('Экспонаты','Записать ширину, высоту, глубину и вес каждого предмета. Глубина 70 мм может не вместить куртку, кепку и основания кубков.'),
('Дерево и толщина','Указать породу, влажность, фактическую толщину фанеры, отделку. Проверить крепёж на обрезке, направление волокон и прочность длинной полки.'),
('Рельеф для ЧПУ','Нужны отдельные утверждённые модели портрета, арки, логотипов и резьбы; выбрать фрезы и радиусы. Кривые в Blender не заменяют готовый CAM.'),
('Магниты и акрил','Выбрать фиксаторы, клей и способ снятия панелей; проверить сколы, удержание и зазоры на прототипе.'),
('Стена и нагрузка','Определить материал стены и полный вес. Проверить несущие крепления и профиль French cleat; нагрузка 40–50 кг из референса не подтверждена.'),
('Финальный контроль','Проверить геометрию, прогиб, устойчивость, нагрев LED, отсутствие острых кромок и обслуживание. Только после этого утверждать проект.')]
y=166
for heading,body in checks:
    txt(16,y,heading,11,bold=True);height=para(75,y+2,206,body,10);y-=max(24,height+9)
c.save()

# Machine-readable BOM, nominal 1:1 vector layout and rectangular blank DXF.
with (ROOT/'parts.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';');w.writerow(['ID','Наименование','Материал','X мм','Y мм','Z мм','Центр X мм','Центр Y мм','Центр Z мм','Этап','Примечание'])
    for p in PARTS:w.writerow([p['id'],p['title'],p['material'],*p['size'],*p['pos'],p['stage'],p['note']])
(ROOT/'parts.json').write_text(json.dumps(PARTS,ensure_ascii=False,indent=2),encoding='utf-8')
draw=ROOT/'drawings';draw.mkdir(exist_ok=True)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1500mm" height="1100mm" viewBox="-150 -150 1500 1100">','<rect x="-150" y="-150" width="1500" height="1100" fill="white"/>','<g font-family="DejaVu Sans, sans-serif" font-size="15">','<text x="0" y="-90">ASTRA V2 — разметка корпуса, мм; чертёж 1:1 при печати без масштабирования</text>','<rect x="0" y="0" width="1200" height="800" fill="none" stroke="#203042" stroke-width="2"/>']
dxf=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
def dxrect(layer,x,z,w,h):
    dxf.extend(['0','LWPOLYLINE','8',layer,'90','4','70','1'])
    for a,b in [(x,z),(x+w,z),(x+w,z+h),(x,z+h)]:dxf.extend(['10',str(a),'20',str(b)])
dxrect('BACK_A01',0,0,1200,800)
for p in PARTS:
    if p['stage'] not in [2,3,4,5]:continue
    x=p['pos'][0]+600-p['size'][0]/2;z=p['pos'][2]-p['size'][2]/2;w=p['size'][0];h=p['size'][2]
    svg.append(f'<rect x="{x}" y="{800-z-h}" width="{w}" height="{h}" fill="#ecd6b9" stroke="#6d4825" stroke-width="1"/>')
    svg.append(f'<text x="{x+2}" y="{800-z-h+12}">{p["id"]}</text>');dxrect(p['id'],x,z,w,h)
for name,x,z,w,h in OPENINGS:svg.append(f'<text x="{x+600-w/2+12}" y="{800-z}">{escape(name)} {w} × {h}</text>')
svg+=['<path d="M0 835H1200 M0 825V845 M1200 825V845" fill="none" stroke="black"/>','<text x="560" y="860">1200 мм</text>','<path d="M-35 0V800 M-45 0H-25 M-45 800H-25" fill="none" stroke="black"/>','<text x="-110" y="400">800 мм</text>','<path d="M0 920H100 M0 915V925 M100 915V925" stroke="black"/>','<text x="110" y="925">Контроль масштаба: 100 мм</text>','</g></svg>']
(draw/'front_layout.svg').write_text('\n'.join(svg),encoding='utf-8')
dxf+=['0','ENDSEC','0','EOF'];(draw/'front_layout.dxf').write_text('\n'.join(dxf)+'\n',encoding='ascii')
for p in PARTS:
    sx,sy,sz=p['size']
    # Profile in the broad face: all narrow plywood pieces are 70-mm strips.
    a,b=(max(sx,sz),70) if p['material']=='Фанера 15' else (sx,sz)
    s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{a+60}mm" height="{b+75}mm" viewBox="-30 -40 {a+60} {b+75}">
<rect x="-30" y="-40" width="{a+60}" height="{b+75}" fill="white"/>
<text x="0" y="-16" font-family="sans-serif" font-size="12">{p['id']} — {escape(p['title'])}; {a} × {b} мм; {escape(p['material'])}</text>
<rect x="0" y="0" width="{a}" height="{b}" fill="none" stroke="black" stroke-width="0.5"/>
<text x="0" y="{b+20}" font-family="sans-serif" font-size="10">Заготовка 1:1; без отверстий, припусков и рельефа. Проверить масштаб перед резкой.</text></svg>'''
    (draw/(p['id']+'_blank.svg')).write_text(s,encoding='utf-8')
(ROOT/'cut_plan.json').write_text(json.dumps(dict(strip_width_mm=70,stock_length_mm=2440,kerf_mm=3,strips=strips),ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF_PAGES',PAGE,'PARTS',len(PARTS),'CUT_STRIPS',len(strips))
