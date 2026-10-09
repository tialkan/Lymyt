"""Generate labelled guide illustrations; all connections follow firmware pins."""
from pathlib import Path
from html import escape
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'docs'))
from generate_breadboard import generate

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'integrations/tezatlas/assets'
OUT.mkdir(parents=True,exist_ok=True)
for stage in (1,2,3):
    generate(stage)
    (OUT/f'breadboard-{stage}.svg').write_text((ROOT/f'docs/breadboard-{stage}.svg').read_text())

def svg(name, title, body, note='Şematik gösterim · bağlantı için pin etiketlerini takip et.'):
    (OUT/(name+'.svg')).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" role="img"><title>{escape(title)}</title><rect width="1200" height="800" rx="20" fill="#fffdf8"/><g font-family="Arial,sans-serif" fill="#1d1a36"><text x="42" y="58" font-size="28" font-weight="700">{escape(title)}</text>{body}<text x="42" y="760" font-size="17">{escape(note)}</text></g></svg>''')
def box(x,y,w,h,label,color='#d5f2ee'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#1d1a36" stroke-width="2"/><text x="{x+w/2}" y="{y+30}" text-anchor="middle" font-size="21" font-weight="700">{escape(label)}</text>'
def text(x,y,s,size=18):return f'<text x="{x}" y="{y}" font-size="{size}">{escape(s)}</text>'

b=box(60,140,320,260,'NANO ESP32')+box(680,140,420,180,'SOL OLED / SSD1306')+box(680,430,420,180,'SAĞ OLED / SSD1306')
for i,(pin,dest,color) in enumerate([('A4','SDA (sol)','#3dbfb3'),('A5','SCL (sol)','#f0607f'),('A2','SDA (sağ)','#3dbfb3'),('A3','SCL (sağ)','#f0607f')]):
    y=205+i*45;v=210+(i%2)*45+(290 if i>=2 else 0)
    b+=text(85,y,pin)+f'<path d="M350 {y-5} H{460+i*35} V{v-5} H700" stroke="{color}" stroke-width="4" fill="none"/>'+text(730,v,dest)
b+=box(60,485,470,170,'ORTAK BESLEME','#fff0c7')+text(85,545,'3V3 → iki ekranın VCC pini')+text(85,585,'GND → iki ekranın GND pini')+text(680,670,'Her iki OLED 0x3C: iki ayrı I²C hattı.')
svg('oled-wiring','OLED seçeneği · aynı adres, ayrı hat',b,'Yalnız 4 pinli 128×64 SSD1306 I²C modülleri. SPI / SH1106 için bu çizimi kullanma.')
b=box(60,180,260,220,'NANO ESP32')+box(570,160,400,320,'4 BACAKLI BUTON','#fff0c7')
b+=text(85,260,'D2  INPUT_PULLUP')+text(85,330,'GND')
for x in [620,910]:
    b+=f'<path d="M{x} 245 V380" stroke="#1d1a36" stroke-width="5"/><circle cx="{x}" cy="245" r="9" fill="#1d1a36"/><circle cx="{x}" cy="380" r="9" fill="#1d1a36"/>'
b+='<path d="M320 255 H470 V245 H620 M320 330 H420 V550 H1020 V380 H910" stroke="#3dbfb3" stroke-width="5" fill="none"/>'
b+=text(640,300,'BASINCA BU İKİ GRUP')+text(670,330,'BİRBİRİNE BAĞLANIR')+text(600,440,'Aynı gruptaki iki bacak zaten bağlı.')+text(60,640,'Butonu breadboardun orta yarığını köprüleyecek şekilde tak.')+text(60,680,'Önce multimetreyle hangi bacakların zaten bağlı olduğunu bul.')
svg('button','Düğme · D2 → anlık buton → GND',b,'10×10 mm gövde açıklığı için uzatma başlığı / buton taşıyıcısı ayrıca ölçülmelidir.')
for stage in [1,2,3]:
    b=box(50,130,760,410,'50×100 mm DELİKLİ BAKIR PLAKET','#ebe3d2')
    for row in range(17):
        for col in range(38):
            x=80+col*18;y=190+row*18
            b+=f'<circle cx="{x}" cy="{y}" r="3.7" fill="#b68151"/>'
    b+=box(145,240,345,125,'USB-C ←  NANO SOKETLERİ','#d5f2ee')
    b+=text(155,226,'2×15 dişi soket · aralık 15,24 mm',15)
    if stage>=2:
        b+=box(560,170,190,170,'SOL / SAĞ', '#e7e3f7')+text(575,220,'VCC / GND / DIN',15)+text(575,250,'CLK ortak',15)+text(575,280,'CS/DC/RST/BUSY',15)+text(575,310,'ayrı kablo',15)
        b+='<path d="M180 380 H535 V235 H560 M300 380 V430 H535 V290 H560" fill="none" stroke="#3dbfb3" stroke-width="4"/>'
    if stage==3:
        b+=box(560,390,190,110,'LED / BUTON','#fff0c7')+text(574,449,'A0 → 330Ω → LED',14)+text(574,475,'D2 → buton → GND',14)
    notes=[['01 · Kartı kesmeden önce tüm parçaları kuru yerleştir.','Nano soketle sökülebilir; ekranlar kablolu kalır.','Kartın bakır pedleri birbirinden yalıtılmış olmalı.'],['02 · Soketleri lehimle; alt yüzde yalıtımlı kabloyla bağla.','Üst görünüş burada. Alt yüzü çevirince sol/sağ ters döner.','Üzerindeki pin adını takip et; çizimi alt yüze aynen kopyalama.'],['03 · Her hattı süreklilikle kontrol et; çapraz telleri yalıt.','3V3–GND kısa devre kontrolü → tek göz → iki göz → buton.','Ekranların kablosunu ayırabilecek konektörler kullan.']][stage-1]
    for i,n in enumerate(notes):b+=text(50,600+i*40,n,19)
    b+=text(850,180,'ÜSTTEN',24)+text(850,220,'YERLEŞİM',24)+text(850,290,'İz şeması değil.',18)+text(850,330,'Pin tablosuyla',18)+text(850,360,'birlikte kullan.',18)
    svg('perfboard-'+str(stage),'Lehimli plaket · '+str(stage)+'/3',b,'Düz, kesintisiz bakır levhada pinler kısa devre olur. İzolasyonlu delikli pertinaks seç.')
b=box(50,120,640,475,'ARKADAN YERLEŞİM · 150×100 mm','#e7e3f7')
b+=box(115,190,235,135,'SOL EKRAN','#fffdf8')+box(380,190,235,135,'SAĞ EKRAN','#fffdf8')
b+=box(95,375,335,155,'4×AA PİL YUVASI','#fff0c7')+text(115,430,'Ayrılan alan: 70×70×25 mm',16)+text(115,467,'Yalıtımlı, sabitlenmiş yuva',16)
b+=box(455,365,195,180,'PLAKET','#d5f2ee')+text(470,420,'100×50 mm',17)+text(470,455,'Derinlikte ayrı',17)+text(470,485,'yalıtılmış katman',17)
b+=text(730,190,'Gövde 150×100×55',24)+text(730,230,'Kapak 2,4 mm',20)+text(730,290,'Duvar: 2,4 mm',20)+text(730,335,'Kablo alanı: ≥8 mm',20)+text(730,380,'Ekran camına baskı yok',19)+text(730,425,'USB açıklığı: 20×14 mm',19)+text(730,470,'4×M3 vida / somun',19)+text(730,545,'Önce 60×44 mm',22)+text(730,578,'uyum testini yazdır.',22)
b+=text(50,655,'Pil alanı ve plaket arkada farklı derinliklerde yerleşir; kablo payını koru.',18)+text(50,692,'Bu bir ölçü deneme gövdesidir. Ekran, pil yuvası ve USB konumu gerçek parçayla ölçülmeli.',17)
svg('case-layout','3D gövde · ferah, açılabilir, ölçüye göre uyarlanabilir',b,'STL dosyaları mm birimindedir. Büyük 830 delikli breadboard bu gövdeye dahil değildir.')
b=box(50,200,230,130,'4× NiMH AA','#fff0c7')+box(350,200,230,130,'ANAHTAR','#fde2e7')+box(650,200,470,130,'5V BUCK-BOOST + KESME','#d5f2ee')
b+='<path d="M280 265 H350 M580 265 H650" stroke="#1d1a36" stroke-width="4"/>'
b+=box(650,420,470,130,'USB-C → NANO ESP32','#e7e3f7')+'<path d="M885 330 V420" stroke="#1d1a36" stroke-width="4"/>'
b+=text(60,450,'1,2V × 4 = nominal 4,8V',20)+text(60,500,'Haricî NiMH şarj cihazı',20)+text(60,590,'Regülatör: yaklaşık 4–6V girişte sabit 5V; en az 1A sürekli çıkış.',19)+text(60,630,'Pilleri VIN’e doğrudan bağlama. Nano pilleri şarj etmez.',19)+text(60,670,'Önce multimetreyle çıkışı doğrula; USB güç kaynaklarını paralelleme.',19)
svg('battery','AA pil seçeneği · önce kararlı 5V',b,'Regülatörün düşük gerilim kesmesi dört NiMH hücre için üretici sınırlarına göre ayarlanmalıdır.')
