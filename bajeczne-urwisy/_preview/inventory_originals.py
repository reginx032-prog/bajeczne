from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from hashlib import sha256
import json, re

ROOT = Path(__file__).resolve().parent.parent
files = sorted(p for p in (ROOT / 'assets/photos').rglob('*') if p.is_file() and p.suffix.lower() in ('.jpg','.jpeg','.png') and (re.match(r'^\d{8,}_', p.name) or re.match(r'^g\d+\.',p.name) or p.name.startswith(('chihuahua-2026-','puppy-','breed-chihuahua-longhair'))))
records=[]
groups={}
for p in files:
    im=ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    digest=sha256(im.tobytes()).hexdigest()
    record={'id':len(records)+1,'src':p.relative_to(ROOT).as_posix(),'size':list(im.size),'sha':sha256(p.read_bytes()).hexdigest(),'pixels':digest}
    small=im.resize((9,8)).convert('L')
    pixels=list(small.getdata())
    record['dhash']=hex(sum((pixels[y*9+x]>pixels[y*9+x+1]) << (y*8+x) for y in range(8) for x in range(8)))
    records.append(record)
    groups.setdefault(digest,[]).append(record['id'])
(ROOT/'_preview/originals-inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
unknown=[r for r in records if '/chihuahua-2026/' not in r['src']]
for start in range(0,len(unknown),30):
    chunk=unknown[start:start+30]
    sheet=Image.new('RGB',(1200,6*204),(245,242,236)); draw=ImageDraw.Draw(sheet)
    for j,r in enumerate(chunk):
        x=(j%5)*240;y=(j//5)*204
        im=ImageOps.exif_transpose(Image.open(ROOT/r['src'])).convert('RGB')
        im.thumbnail((230,175))
        sheet.paste(im,(x+(240-im.width)//2,y))
        draw.text((x+8,y+180),f"{r['id']} | {r['size'][0]}x{r['size'][1]}",fill='black')
    sheet.save(ROOT/f'_preview/originals-sheet-{start//30+1}.jpg',quality=92)
print(json.dumps({'files':len(records),'unknown':len(unknown),'sheets':(len(unknown)+29)//30,'duplicates':[v for v in groups.values() if len(v)>1]}))
