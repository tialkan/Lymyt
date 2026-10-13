"""Photo-matched 30-pin ESP32 outside breadboard; every cable has a hole address."""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
LEFT=['3V3','GND','D15','D2','D4','RX2','TX2','D5','D18','D19','D21','RX0','TX0','D22','D23']
RIGHT=['VIN','GND','D13','D12','D14','D27','D26','D25','D33','D32','D35','D34','VN','VP','EN']
COLS=dict(zip('abcdefghij',[610,637,664,691,718,799,826,853,880,907]))
RED='#cf4249'; BLACK='#273743'; BLUE='#2678c9'
COLORS=[RED,BLACK,'#cf8711','#078b87','#8b59bf',BLUE,'#b0477f','#607933']
PIN_NAMES=['VCC','GND','DIN','CLK','CS','DC','RST','BUSY']
LEFT_ROWS=[1,2,3,4,5,6,7,8]
RIGHT_ROWS=[1,2,3,4,9,10,11,12]
ROWS={'3V3':1,'GND':2,'D23':3,'D18':4,'D27':5,'D26':6,'D25':7,'D34':8,'D33':9,'D32':10,'D14':11,'D35':12,'D4':14}
assert len(LEFT)==len(RIGHT)==15

def hole(addr):return COLS[addr[0]],270+(int(addr[1:])-1)*28

def text(x,y,s,size=21,color='#243646',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>'

def wire(a,b,color,via=(),socket=False,opacity=1):
    a=hole(a) if isinstance(a,str) else a;b=hole(b) if isinstance(b,str) else b
    pts=[a,*via,b];d='M'+' L'.join(f'{x},{y}' for x,y in pts)
    ends=''.join(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" stroke="white" stroke-width="1"/>' for x,y in [a,b])
    if socket:ends+=f'<rect x="{a[0]-7}" y="{a[1]-9}" width="14" height="18" rx="2" fill="#172731"/>'
    return f'<g opacity="{opacity}"><path d="{d}" stroke="white" stroke-width="9" fill="none"/><path d="{d}" stroke="{color}" stroke-width="4.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>{ends}</g>'

def board_pin(pin):
    if pin in LEFT:return 90,300+LEFT.index(pin)*38
    return 355,300+RIGHT.index(pin)*38

def generate(stage):
    title=['01 · Ortak besleme','02 · Sol göz','03 · İki e-ink · LED YOK','04 · İki e-ink + isteğe bağlı düğme'][stage-1]
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1600" viewBox="0 0 1600 1600">','<rect width="1600" height="1600" fill="#f4f7fa"/>','<g font-family="Arial,sans-serif">',text(60,65,'LYMYT / ESP32-WROOM',40),text(60,110,title,29),text(60,152,'30 pinli ESP32-WROOM geliştirme kartı · USB yukarı · kart breadboard DIŞINDA',23)]
    # Board pin positions match the user's photograph; sockets stand for female jumpers.
    s += ['<rect x="82" y="235" width="280" height="665" rx="14" fill="#203337" stroke="#0f2024" stroke-width="3"/>','<rect x="181" y="218" width="82" height="58" rx="6" fill="#becad0" stroke="#6b7f89"/>',text(222,252,'USB',19,'#243646','middle'),'<rect x="150" y="420" width="143" height="285" rx="5" fill="#b6c3c8" stroke="#72878d"/>',text(221,531,'ESP32',25,'#243646','middle'),text(221,566,'WROOM',21,'#243646','middle'),text(221,610,'30 pin',18,'#243646','middle')]
    for i,(l,r) in enumerate(zip(LEFT,RIGHT)):
        y=300+i*38
        for x in [90,355]:s.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#d7b865"/>')
        s.extend([text(105,y+6,l,19,'white'),text(340,y+6,r,19,'white','end')])
    s += [text(85,935,'Dişi uç → kart pini',22),text(85,967,'Erkek uç → breadboard deliği',21),text(85,1002,'17 sıra yeterli; güç rayı gerekmiyor.',19)]
    # Only terminal strips, no assumptions about split + / - power rails.
    s+=['<rect x="550" y="215" width="420" height="565" rx="22" fill="#dfe5e9" stroke="#a8b6c0"/>','<rect x="573" y="232" width="374" height="523" rx="12" fill="white"/>','<rect x="738" y="249" width="43" height="481" fill="#d4dce1"/>']
    for row in range(1,18):
        y=hole(f'a{row}')[1]
        s.extend([f'<path d="M610,{y} H718 M799,{y} H907" stroke="#e1e5e8" stroke-width="2"/>',text(592,y+6,str(row),16,anchor='end'),text(928,y+6,str(row),16)])
        for x in COLS.values():s.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#78858e"/>')
    for c,x in COLS.items():s.append(text(x,254,c,18,anchor='middle'))
    active=['GND','3V3']
    if stage>=2:active+=['D23','D18','D27','D26','D25','D34']
    if stage>=3:active+=['D33','D32','D14','D35']
    if stage>=4:active+=['D4']
    for i,pin in enumerate(active):
        x,y=board_pin(pin);dest=hole('a'+str(ROWS[pin]));color=RED if pin=='3V3' else BLACK if pin=='GND' else BLUE
        if x==90:
            # The left header cable goes around the board, never through it.
            lane=45+LEFT.index(pin)*1.7;under=1050+LEFT.index(pin)*4
            via=[(lane,y),(lane,under),(490+i*4,under),(490+i*4,dest[1])]
        else:via=[(390+RIGHT.index(pin)*9,y),(390+RIGHT.index(pin)*9,dest[1])]
        s.append(wire((x,y),dest,color,via,socket=True,opacity=1 if stage==1 or pin in ['3V3','GND'] else .72))
    def module(title,top,rows,col):
        ret=[f'<rect x="1120" y="{top}" width="410" height="355" rx="15" fill="white" stroke="#a8b6c0" stroke-width="2"/>',text(1144,top+37,title,25),text(1144,top+68,'Waveshare 1.54″ · siyah-beyaz',18),f'<rect x="1380" y="{top+105}" width="130" height="190" rx="8" fill="#e7ecef"/>',f'<ellipse cx="1445" cy="{top+186}" rx="39" ry="48" fill="#172731"/>',f'<circle cx="1457" cy="{top+170}" r="11" fill="white"/>']
        for i,(pin,row,color) in enumerate(zip(PIN_NAMES,rows,COLORS)):
            addr=col+str(row);end=(1129,top+101+i*30);x,y=hole(addr);lane=(987+i*7) if col=='c' else (1053+i*7)
            ret += [wire(addr,end,color,[(lane,y),(lane,end[1])]),text(1149,end[1]+6,f'{pin} ← {addr}',21)]
        return ret
    if stage>=2:s += module('SOL GÖZ · CODEX',230,LEFT_ROWS,'c')
    if stage>=3:s += module('SAĞ GÖZ · CLAUDE',625,RIGHT_ROWS,'d')
    if stage>=4:
        s += [text(1125,1085,'BUTON · iki ayrı bacak grubu',22),'<rect x="1240" y="1115" width="110" height="100" rx="10" fill="#4c606a"/>','<circle cx="1295" cy="1165" r="30" fill="#212c31"/>',wire('b14',(1240,1135),'#c9880c',[(1015,hole('b14')[1]),(1015,1135)]),wire('b2',(1240,1195),BLACK,[(1097,hole('b2')[1]),(1097,1195)]),text(1365,1141,'b14 / GPIO4',20),text(1365,1201,'b2 / GND',20)]
    if stage==1:
        tips=['3V3 → a1. Sol VCC=c1; sağ VCC=d1. Bu delikler aynı bağlı grupta.',
              'GND → a2. Sol GND=c2; sağ GND=d2. Tek kart pininden iki ekrana dağıtım.',
              'Kartın her pinine yalnız BİR dişi jumper tak; dağıtımı breadboard’da yap.']
    else:
        tips=['Ortak gruplar: sıra1=3V3, sıra2=GND, sıra3=DIN/GPIO23, sıra4=CLK/GPIO18.',
              'Sol: sıra5=CS27, 6=DC26, 7=RST25, 8=BUSY34.',
              'Sağ: sıra9=CS33, 10=DC32, 11=RST14, 12=BUSY35.' if stage>=3 else 'PanelCheckWroom yükle. Seri Monitör 115200: önce s, sonra küçük l gönder.']
    # Keep pin labels on top of any routed cables.
    for i,(l,r) in enumerate(zip(LEFT,RIGHT)):
        y=300+i*38
        s.extend([f'<rect x="100" y="{y-14}" width="47" height="26" fill="#203337"/>',
                  f'<rect x="294" y="{y-14}" width="51" height="26" fill="#203337"/>',
                  text(105,y+6,l,19,'white'),text(340,y+6,r,19,'white','end')])
    for i,t in enumerate(tips):s.append(text(65,1255+i*36,t,23))
    s += [text(65,1400,'Aynı sırada a–e bağlıdır; f–j ayrı gruptur. A–E tarafını kullanıyoruz.',23),text(65,1437,'Kablo kesişmesi bağlantı değildir. Bağlantı yalnız uçlardaki deliklerde oluşur.',22),text(65,1474,'Ekran ve buton terminal sırası temsilî: gerçek parçadaki pin adlarını izle.',22),text(65,1520,'Kablolarken USB çıkarılmış olsun. VIN ve 5V bu bağlantıda kullanılmıyor.',23),'</g></svg>']
    (OUT/f'wroom-breadboard-{stage}.svg').write_text('\n'.join(s)+'\n')
if __name__=='__main__':
    for stage in range(1,5):generate(stage)
    (OUT/'wroom-epaper-full.svg').write_text((OUT/'wroom-breadboard-3.svg').read_text())
