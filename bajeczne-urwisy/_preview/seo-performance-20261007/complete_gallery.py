from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
source_rows = json.loads((ROOT/'_preview/gallery-october-selection/source-review.json').read_bytes())
catalog_path = ROOT/'data/gallery-photos.json'
inventory_path = ROOT/'_preview/originals-inventory.json'
optimized_path = ROOT/'assets/optimized/manifest.json'
catalog = json.loads(catalog_path.read_bytes())
inventory = json.loads(inventory_path.read_bytes())
optimized = json.loads(optimized_path.read_bytes())
by_pixels = {r['pixels']: r for r in inventory}
seen = set(by_pixels)
names = {'ELF':'Elf', 'FIBI':'Fibi', 'FIFI':'Fifi', 'FIONA':'Fionka', 'GABI':'Gabi', 'GACEK':'Gacek'}
crop_by_label = {
    'ELF 03': [210,300,900,1200], 'ELF 05': [170,360,900,1200],
    'FIBI 02': [180,220,840,1120], 'FIBI 04': [200,300,900,1200],
    'FIBI 06': [180,280,900,1200], 'FIBI 07': [200,280,900,1200],
    'FIFI 01': [170,170,960,1280], 'FIFI 03': [200,140,900,1200], 'FIFI 04': [200,280,960,1280],
    'FIONA 03': [160,160,960,1280], 'FIONA 04': [200,180,960,1280],
    'GABI 01': [180,60,840,1120], 'GABI 04': [0,0,1200,1600],
    'GACEK 02': [180,200,900,1200], 'GACEK 04': [200,220,900,1200],
    'GACEK 05': [0,0,1200,1600], 'GACEK 06': [0,0,1200,1600]
}
new_ids=[]
added=[]
next_id=max(r['id'] for r in inventory)+1
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
sheet=Image.new('RGB',(1250,4*355),'#f6f3ed')
draw=ImageDraw.Draw(sheet)
for row in source_rows:
    if row['pixelHash'] in seen:
        continue
    seen.add(row['pixelHash'])
    label=row['label'];name=names[label.split()[0]]
    assert label in crop_by_label, label
    reused=next((r['src'] for r in row['existing'] if 'id' not in r),None)
    src=reused or 'assets/photos/chihuahua-2026-10/'+label.lower().replace(' ','-')+'.jpg'
    target=ROOT/src
    if not reused:
        assert not target.exists()
        shutil.copy2(row['source'],target)
    with Image.open(target) as image:
        photo=ImageOps.exif_transpose(image).convert('RGB')
        w,h=photo.size
        digest=sha256(target.read_bytes()).hexdigest()
        assert sha256(photo.tobytes()).hexdigest()==row['pixelHash']
        left,top,cw,ch=crop_by_label[label]
        assert 0<=left<=w-cw and 0<=top<=h-ch
        entry={'id':next_id,'breed':'chihuahua','src':src,'alt':f'{name}, Chihuahua z hodowli Bajeczne Urwisy',
               'width':w,'height':h,'crop':[left,top,cw,ch],
               'x':round(left/(w-cw)*100,3) if w>cw else 50,
               'y':round(top/(h-ch)*100,3) if h>ch else 50,
               'scale':round(min(w,h*.75)/cw,5),'fit':'cover','aliases':[]}
        catalog['photos'].append(entry)
        inventory.append({'id':next_id,'src':src,'size':[w,h],'sha':digest,'pixels':row['pixelHash']})
        new_ids.append(next_id);next_id+=1
        if src not in optimized:
            variants=[]
            for width in sorted({min(w,x) for x in (400,800,1200,1600)}):
                height=round(h*width/w)
                variant=ROOT/f'assets/optimized/{target.stem}-{digest[:12]}-{width}.webp'
                photo.resize((width,height),Image.Resampling.LANCZOS).save(variant,'WEBP',quality=86,method=5)
                variants.append({'src':variant.relative_to(ROOT).as_posix(),'width':width,'height':height,'bytes':variant.stat().st_size})
            optimized[src]={'originalBytes':target.stat().st_size,'variants':variants}
        i=len(added);x=10+(i%5)*250;y=10+(i//5)*355
        sheet.paste(photo.crop((left,top,left+cw,top+ch)).resize((234,312),Image.Resampling.LANCZOS),(x,y))
        draw.text((x,y+321),label,font=font,fill='#222')
        added.append({'label':label,'src':src,'source':row['source']})
assert len(added)==17
# Keep the ten selected cover portraits first, then the remaining supplied views.
order=catalog['galleryOrder']['chihuahua']
catalog['galleryOrder']['chihuahua']=order[:10]+new_ids+order[10:]
for path,value in [(catalog_path,catalog),(inventory_path,inventory),(optimized_path,optimized)]:
    old=path.read_bytes();nl='\r\n' if b'\r\n' in old else '\n'
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').replace('\n',nl).encode('utf8'))
(OUT/'additional-photos.json').write_text(json.dumps(added,ensure_ascii=False,indent=2),encoding='utf8')
sheet.save(OUT/'additional-crops.jpg',quality=92)
print('Added 17 distinct photos; gallery now has 176 Chihuahua photos.')
