"""Exact hole positions for an isolated-pad 38×17, 2.54mm perfboard.

Top-view net endpoints, not etched PCB copper artwork. Each wire is insulated.
"""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'integrations/tezatlas/assets'
LEFT=['D13','3V3','B0','A0','A1','A2','A3','A4','A5','A6','A7','VUSB','B1','GND','VIN']
RIGHT=['D12','D11','D10','D9','D8','D7','D6','D5','D4','D3','D2','GND','RESET','D0','D1']
points={pin:(9+i,row) for row,pins in [(11,LEFT),(5,RIGHT)] for i,pin in enumerate(pins)}
points['GND']=(20,5)
pins=['VCC','GND','DIN','CLK','CS','DC','RST','BUSY']
nano_left=['3V3','GND','D11','D13','D10','D9','D8','D7']
nano_right=['3V3','GND','D11','D13','D6','D5','D4','D3']
colors=['#d84545','#1d1a36','#d39019','#1c9ca0','#966bd3','#3879cc','#bc5c91','#61783d']
def pt(c,r):return 80+(c-1)*20,160+(r-1)*20
def txt(x,y,value,size=15,color='#1d1a36'):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(value)}</text>'
for stage in [1,2,3]:
 b='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 950"><rect width="1200" height="950" fill="#fffdf8"/><g font-family="Arial,sans-serif">'
 b+=txt(42,55,f'LEHİMLİ BAKIR PLAKET / 0{stage}',29)+txt(42,92,'Üst görünüş · USB-C solda · her delik ayrı bir bakır ped',18)
 b+='<rect x="48" y="128" width="806" height="385" rx="8" fill="#ebe3d2" stroke="#1d1a36" stroke-width="2"/>'
 for r in range(1,18):
  for c in range(1,39):
   x,y=pt(c,r);b+=f'<circle cx="{x}" cy="{y}" r="4" fill="#b68151"/>'
  b+=txt(55,pt(1,r)[1]+4,str(r),10)
 for c in range(1,39):b+=txt(pt(c,1)[0]-4,144,str(c),10)
 b+='<rect x="235" y="248" width="322" height="106" rx="7" fill="#207c79" stroke="#155551" stroke-width="2"/><rect x="225" y="280" width="30" height="44" rx="4" fill="#b7c2c9"/>'
 b+=txt(322,307,'NANO ESP32',20,'#fff')+txt(880,165,'SOKETLER',19)+txt(880,205,'Üst: 9–23 / sıra 5',16)+txt(880,235,'Alt: 9–23 / sıra 11',16)+txt(880,275,'2×15 dişi soket',16)+txt(880,305,'15,24 mm sıra aralığı',16)
 for row,names in [(11,LEFT),(5,RIGHT)]:
  for i,name in enumerate(names):
   x,y=pt(9+i,row);b+=f'<circle cx="{x}" cy="{y}" r="5" fill="#e5c26b" stroke="#1d1a36"/>'
   b+=f'<text x="{x}" y="{y+(21 if row==11 else -9)}" font-size="10" fill="#1d1a36" text-anchor="middle">{name}</text>'
 if stage>=2:
  for row,targets,label in [(4,nano_left,'SOL'),(13,nano_right,'SAĞ')]:
   b+=txt(665,pt(29,row)[1]-27,label+' · 1×8 KONEKTÖR',14)
   for i,(pin,target,col) in enumerate(zip(pins,targets,colors)):
    x,y=pt(29+i,row);a,z=pt(*points[target]);bend=165+i*8 if row==4 else 470-i*8
    b+=f'<path d="M{a} {z} V{bend} H{x} V{y}" fill="none" stroke="#fff" stroke-width="6"/><path d="M{a} {z} V{bend} H{x} V{y}" fill="none" stroke="{col}" stroke-width="2.5"/>'
    for u,v in [(a,z),(x,y)]:b+=f'<circle cx="{u}" cy="{v}" r="4" fill="{col}"/>'
    b+=f'<text x="{x}" y="{y+19}" font-size="8" fill="#1d1a36" text-anchor="middle">{pin}</text>'
 if stage==3:
  b+=txt(880,355,'A0 → 330Ω → LED+',16)+txt(880,385,'LED− → GND',16)+txt(880,425,'D2 → buton → GND',16)
 captions=[['01 · Soketleri kuru yerleştir; Nano ile hizala, sonra Nano’yu çıkar.','Her delik ayrı ped olmalı. Şeritli veya düz kesintisiz bakır kart uygun değil.'],['02 · Alt yüzde yalıtımlı kabloyla belirtilen delik uçlarını birbirine bağla.','Çizgi kesişimi bağlantı değildir. Yalnız pin/delik ucunda bağlantı var.'],['03 · Her hattı ölç; komşu pedler ve 3V3–GND arasında kısa devre olmadığını doğrula.','İlk enerji testi: Nano → tek ekran → iki ekran → LED ve düğme.']][stage-1]
 for i,t in enumerate(captions):b+=txt(42,555+i*34,t,18)
 b+=txt(42,649,'SOL KONEKTÖR: 29–36 / sıra 4',19)+txt(610,649,'SAĞ KONEKTÖR: 29–36 / sıra 13',19)
 for i,(pin,l,r) in enumerate(zip(pins,nano_left,nano_right)):
  b+=txt(42+(i//4)*270,685+(i%4)*32,f'{pin} → {l} (sol) / {r} (sağ)',16)
 b+=txt(42,841,'Özel kart üzerindeki konektör sırası burada tanımlanır; ekranın hazır soket sırası değildir.',17)
 b+=txt(42,876,'Alt yüzü çevirince görünüş aynalanır. Pin adı ve süreklilik ölçümüyle ilerle.',17)
 b+=txt(42,915,'50×100mm nominal kart: kenar boşluğu değişebilir. 2,54mm adımı ve gerçek delik sayısını kontrol et.',15)
 b+='</g></svg>'
 (OUT/f'perfboard-{stage}.svg').write_text(b)
