from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parent.parent
path=ROOT/'_preview/originals-inventory.json'
records=json.loads(path.read_text(encoding='utf8'))
known={r['src'] for r in records}
for p in sorted((ROOT/'assets/photos').glob('*')):
    if p.is_file() and p.suffix.lower() in ('.jpg','.jpeg') and p.relative_to(ROOT).as_posix() not in known:
        im=ImageOps.exif_transpose(Image.open(p)).convert('RGB')
        records.append({'id':len(records)+1,'src':p.relative_to(ROOT).as_posix(),'size':list(im.size),'sha':sha256(p.read_bytes()).hexdigest(),'pixels':sha256(im.tobytes()).hexdigest()})
path.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
for r in records[222:]:
    print(r['id'],r['src'].split('/')[-1], 'same:',[x['id'] for x in records[:222] if x['pixels']==r['pixels']])
ids=[1,196,53,59,76,77,80,116,118,117,119,120,113,219,220,115,221,222]
s=Image.new('RGB',(1500,((len(ids)+5)//6)*320),'white');d=ImageDraw.Draw(s)
for j,n in enumerate(ids):
    r=records[n-1];im=ImageOps.exif_transpose(Image.open(ROOT/r['src'])).convert('RGB');im.thumbnail((245,290));x=j%6*250;y=j//6*320;s.paste(im,(x,y));d.text((x+5,y+295),str(n),fill='black')
s.save(ROOT/'_preview/photo-variants.jpg',quality=94)
