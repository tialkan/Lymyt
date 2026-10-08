"""Generate physical placement diagrams; coordinates also define the wiring table."""
from pathlib import Path
from html import escape

OUT = Path(__file__).parent
LEFT = ['D13','3V3','B0','A0','A1','A2','A3','A4','A5','A6','A7','VUSB','B1','GND','VIN']
RIGHT = ['D12','D11','D10','D9','D8','D7','D6','D5','D4','D3','D2','GND','RESET','D0/RX','D1/TX']
COLS = dict(zip('abcdefghij', [230,262,294,326,358,454,486,518,550,582]))
def hole(address):
    return COLS[address[0]], 250 + (int(address[1:])-1)*28
def text(x,y,s,size=20,fill='#243646',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'
def line(x1,y1,x2,y2,color,width=4):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
def wire(start,end,color,route=None):
    x,y=hole(start); u,v=hole(end) if isinstance(end,str) else end
    points=[(x,y)]+(route or [])+[(u,v)]
    d='M'+' L'.join(f'{a},{b}' for a,b in points)
    return f'<path d="{d}" fill="none" stroke="white" stroke-width="8"/><path d="{d}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round"/>'+f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/><circle cx="{u}" cy="{v}" r="6" fill="{color}"/>'

# Eight labelled cable terminals; their order is explanatory, not the carrier's order.
pins=['VCC','GND','DIN','CLK','CS','DC','RST','BUSY']
left_holes=['b22','b23','i6','a5','j7','j8','j9','j10']
right_holes=['c22','c23','j6','b5','j11','j12','j13','j14']
colors=['#d84545','#26333d','#e69b19','#1c9ca0','#966bd3','#3879cc','#bc5c91','#61783d']

def generate(stage):
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1600" viewBox="0 0 1600 1600">', '<rect width="1600" height="1600" fill="#f4f7fa"/>','<g font-family="Arial, sans-serif">']
    svg += [text(70,75,'LYMYT / BREADBOARD',42),text(70,115,['1 · Önce tek göz','2 · İki göz','3 · LED ve ADXL345'][stage-1],28),text(70,155,'Üstten görünüş · USB-C yukarı · 830 delikli kartın ilk 30 sırası',22)]
    svg += ['<rect x="170" y="195" width="470" height="960" rx="22" fill="#e6e7e8" stroke="#abb3b9"/>','<rect x="190" y="215" width="430" height="920" rx="12" fill="#fff"/>','<rect x="380" y="232" width="52" height="870" fill="#d9dde1"/>']
    for col,x in COLS.items():
        svg.append(text(x,235,col,20,anchor='middle'))
        for row in range(1,31):
            y=hole(f'{col}{row}')[1]
            svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#7d858b"/>')
    for row in range(1,31):
        y=hole(f'a{row}')[1]
        svg.append(text(211,y+6,str(row),18,anchor='end'))
        svg.append(text(600,y+6,str(row),18))
    # 0.6 inch header separation: c to g = six 0.1 inch pitches.
    svg += ['<rect x="280" y="345" width="220" height="455" rx="8" fill="#207c79" stroke="#155551" stroke-width="3"/>','<rect x="350" y="332" width="80" height="52" rx="9" fill="#b7c2c9" stroke="#4e6676"/>',text(390,364,'USB-C',16,anchor='middle'),'<rect x="345" y="478" width="85" height="132" rx="5" fill="#bcc5c9"/>',text(389,535,'ESP32',18,anchor='middle'),text(389,567,'NORA',17,anchor='middle')]
    for i,(l,r) in enumerate(zip(LEFT,RIGHT)):
        y=hole(f'c{i+5}')[1]
        svg.extend([f'<circle cx="294" cy="{y}" r="6" fill="#e5c26b"/>',f'<circle cx="486" cy="{y}" r="6" fill="#e5c26b"/>',text(309,y+5,l,16,'white'),text(472,y+5,r,16,'white','end')])
    # Use terminal rows as power buses: no assumption about split power rails.
    for row,color,label in [(22,colors[0],'22 a–e = 3V3'),(23,colors[1],'23 a–e = GND')]:
        x,y=hole(f'a{row}'); svg.append(line(x,y,COLS['e'],y,color,7)); svg.append(text(70 if stage==3 else 660,(1330 if stage==3 else 1000)+(row-22)*30,label,21,color))
    svg += [wire('a6','a22',colors[0],[(150,390),(150,hole('a22')[1])]),wire('b18','a23',colors[1],[(130,hole('b18')[1]),(130,hole('a23')[1])])]
    def module(title,subtitle,top,holes):
        result=[f'<rect x="1010" y="{top}" width="490" height="330" rx="16" fill="#fff" stroke="#a9b5be" stroke-width="2"/>',text(1050,top+38,title,28),text(1050,top+65,subtitle,19),f'<rect x="1280" y="{top+95}" width="180" height="190" rx="7" fill="#e9edf0"/>',f'<ellipse cx="1370" cy="{top+170}" rx="55" ry="58" fill="#172c36"/>',f'<circle cx="1383" cy="{top+151}" r="15" fill="white"/>']
        for i,(pin,addr,color) in enumerate(zip(pins,holes,colors)):
            end=(1020,top+97+i*27)
            result += [text(1040,end[1]+6,f'{pin}  ←  {addr}',20),f'<circle cx="{end[0]}" cy="{end[1]}" r="6" fill="{color}"/>']
            x,y=hole(addr)
            if addr[0] in 'ab':
                route=[(95-i*5,y),(95-i*5,top-28-i*5),(900+i*10,top-28-i*5),(900+i*10,end[1])]
            else:
                route=[(690+i*24,y),(690+i*24,end[1])]
            result.append(('<g opacity="0.16">' if stage==3 else '<g>')+wire(addr,end,color,route)+'</g>')
        return result
    svg += module('SOL GÖZ · CODEX','Waveshare 1.54″ siyah-beyaz',250,left_holes)
    if stage>=2: svg += module('SAĞ GÖZ · CLAUDE','CS / DC / RST / BUSY ayrı',645,right_holes)
    if stage==3:
        # LED series path on separate strips, never across holes on the same strip.
        svg += [wire('a8','a24','#3879cc',[(75,hole('a8')[1]),(75,hole('a24')[1])])]
        x,y=hole('b24');u,v=hole('b27')
        svg += [line(x,y,u,v,'#876947'),f'<rect x="251" y="{y+20}" width="22" height="45" rx="6" fill="#dbbe8d" stroke="#876947"/>',text(340,y+26,'330 Ω',21),text(340,y+56,'b24 → b27',18)]
        x,y=hole('c27');u,v=hole('c28')
        svg += [line(x,y,u,v,'#687885'),f'<ellipse cx="{x}" cy="{y+10}" rx="13" ry="15" fill="#397fd4"/>',text(335,y+8,'LED + c27',20),text(335,v+12,'LED − c28',20),wire('a28','j16',colors[1],[(115,hole('a28')[1]),(115,1178),(620,1178),(620,hole('j16')[1])])]
        svg += [text(1000,1045,'ADXL345 · kart üzerindeki adlara göre',24)]
        adxl=[('VCC','d22',colors[0]),('GND','d23',colors[1]),('SDA','a12','#1c9ca0'),('SCL','a13','#e69b19'),('CS','e22',colors[0]),('SDO','e23',colors[1])]
        for i,(pin,addr,color) in enumerate(adxl):
            # List per-cable anchors: module header order varies between breakouts.
            svg += [text(1010,1082+i*31,f'{pin}  ←  {addr}',22,color)]
            x,y=hole(addr); end=(990,1076+i*31)
            if addr[0]=='a':
                route=[(100-i*12,y),(100-i*12,1205+i*15),(850+i*12,1205+i*15),(850+i*12,end[1])]
            else:
                route=[(735+i*22,y),(735+i*22,end[1])]
            svg.append(wire(addr,end,color,route))
        svg += [text(1000,1290,'CS ve SDO yalnız modülde varsa.',20),text(1000,1320,'SDA/SCL kabloları sol taraftaki',20),text(1000,1350,'a12 / a13 deliklerine gider.',20)]
    for row in range(1,31):
        y=hole(f'a{row}')[1]
        svg += [f'<rect x="594" y="{y-12}" width="27" height="23" fill="white"/>',text(600,y+6,str(row),18)]
    svg += [text(70,1255 if stage<3 else 1415,'Aynı sırada a–e bağlı; f–j bağlı. İki taraf birbirinden ayrıdır.',23),text(70,1290 if stage<3 else 1450,'Nano bacakları: c5–c19 ve g5–g19. Kablolar boş a/b ve i/j deliklerine.',22),text(70,1325 if stage<3 else 1485,'Modül terminal sırası temsilîdir: VCC / GND / DIN… baskısına bak, renge değil.',21),text(70,1375 if stage<3 else 1530,'Bağlarken USB çıkarılmış olmalı. VIN, VUSB, B0 ve B1 bu devrede boş.',22)]
    svg += ['</g></svg>']
    (OUT/f'breadboard-{stage}.svg').write_text('\n'.join(svg)+'\n')

if __name__=='__main__':
    for stage in (1,2,3): generate(stage)
