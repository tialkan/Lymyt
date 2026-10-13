"""Build the public source bundle from a strict allowlist, never personal config."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'integrations/tezatlas/assets'
FILES=['firmware/Lymyt/Lymyt.ino','firmware/Lymyt/BoardPins.h','firmware/Lymyt/config.example.h','firmware/Lymyt/config.wroom.example.h','firmware/Lymyt/Words.h','firmware/Lymyt/Learning.h','firmware/PanelCheck/PanelCheck.ino','firmware/PanelCheckWroom/PanelCheckWroom.ino','bridge/lymyt.py','data/words.json','tools/generate_words.py','tools/generate_wroom_breadboard.py','enclosure/generate.py','enclosure/lymyt-body.stl','enclosure/lymyt-fit-test.stl','enclosure/lymyt-back.stl','enclosure/lymyt.scad','docs/SECOND-OPINION.md','docs/WROOM-ASSEMBLY.md','web/index.html','web/style.css','web/app.js']
DIAGRAMS=['oled-wiring','breadboard-1','breadboard-2','battery','button','case-3d','case-layout','perfboard-1','perfboard-2','perfboard-3','wroom-breadboard-1','wroom-breadboard-2','wroom-breadboard-3','wroom-breadboard-4','wroom-epaper-full','wroom-oled']
with zipfile.ZipFile(OUT/'lymyt-source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for file in FILES:z.write(ROOT/file,'Lymyt/'+file)
    z.write(ROOT/'docs/PUBLIC-GUIDE.md','Lymyt/README.md')
    for name in DIAGRAMS:z.write(OUT/(name+'.svg'),'Lymyt/diagrams/'+name+'.svg')
    for name in ['wroom-breadboard-1','wroom-breadboard-2','wroom-breadboard-3','wroom-breadboard-4','wroom-epaper-full']:
        z.write(ROOT/'docs'/(name+'.png'),'Lymyt/docs/'+name+'.png')
    for name in ['wroom-epaper-full']:
        z.write(ROOT/'docs'/(name+'.svg'),'Lymyt/docs/'+name+'.svg')
with zipfile.ZipFile(OUT/'lymyt-source.zip') as z:
    assert z.testzip() is None
    assert not any(n.endswith('/config.h') or '/.lymyt/' in n for n in z.namelist())
    print(len(z.namelist()),'allowlisted files; ZIP checked; personal config excluded')
