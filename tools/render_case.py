"""Render the actual binary STL as a labelled, deterministic SVG preview."""
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
data=(ROOT/'enclosure/lymyt-body.stl').read_bytes()
count=struct.unpack_from('<I',data,80)[0]
faces=[]
for i in range(count):
    values=struct.unpack_from('<12fH',data,84+i*50)
    normal=values[:3];points=[values[3:6],values[6:9],values[9:12]]
    if sum(a*b for a,b in zip(normal,[-.6,.4,-1]))<=0:continue
    depth=sum(-.6*x+.4*y-z for x,y,z in points)/3
    vertices=' '.join(f'{295+(x-.6*z)*4.7:.2f},{640+(-y-.4*z)*4.7:.2f}' for x,y,z in points)
    color='#65bab3' if normal[2]<0 else '#439b95' if normal[0]<0 else '#88cec7'
    faces.append((depth,f'<polygon points="{vertices}" fill="{color}" stroke="{color}" stroke-width=".4"/>'))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800"><rect width="1200" height="800" fill="#fffdf8"/><g font-family="Arial,sans-serif" fill="#1d1a36"><text x="42" y="58" font-size="28" font-weight="700">LYMYT / LED’SİZ 3D GÖVDE</text><text x="42" y="97" font-size="19">150 × 100 × 55 mm · iki göz + düğme · 2.4 mm duvar</text>']
svg += [face for _,face in sorted(faces)]
svg += ['<text x="42" y="745" font-size="18">Gerçek STL geometrisi · WROOM kart tutucusu / USB konumu ölçüye göre uyarlanmalı.</text><text x="42" y="778" font-size="17">Ölçü deneme gövdesi; fiziksel baskı ve ekran uyumu henüz doğrulanmadı.</text></g></svg>']
(ROOT/'integrations/tezatlas/assets/case-3d.svg').write_text('\n'.join(svg))
print('Rendered',len(faces),'visible triangles from',count,'STL triangles')
